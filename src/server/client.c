/* Copyright 2019 Collaborative Text Editor. All rights reserved */

// TODO write roadmap

#include <assert.h>
#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <termios.h>
#include <unistd.h>

#include <xt/error.h>
#include <xt/os_macros.h>
#include <xt/socket.h>
#include <xt/thread.h>
#include <xt/string.h>
#include <xt/time.h>

#if XT_IS_LINUX
#include <errno.h>
#endif

#include "dbg.h"
#include "config.h"
#include "net.h"
#include "shell.h"

xtSocket sockfd = XT_SOCKET_INVALID_FD;
static struct xtSockaddr sa;
static struct xtThread t_event;
// XXX do we have to remember whether xtSocketInit has successfully been called?

static void cleanup(void)
{
	if (sockfd != XT_SOCKET_INVALID_FD)
		xtSocketClose(&sockfd);
	xtSocketDestruct();
}

int net_pkg_process(struct net_pkg *pkg)
{
	switch (pkg->type) {
	case NT_TEXT:
		puts(pkg->data.text.text);
		break;
	case NT_CHUNK:
		break;
	default:
		dbgf("pkg_process: todo process type: %hu, size: %hu\n", pkg->type, pkg->length);
		// TODO drop connection
		assert(0);
		break;
	}
	return 0;
}

void show_error(const char *str)
{
	fprintf(stderr, "%s\n", str);
}

/* Ensure command is of form `cmd args...'. */
static bool cmd_starts(const char *line, const char *cmd, const char **args)
{
	if (xtStringStartsWith(line, cmd)) {
		const unsigned char *ptr = (const unsigned char*)line + strlen(cmd);

		if (!*ptr || !isspace(*ptr)) {
			*args = NULL;
			return false;
		}
		while (*ptr && isspace(*ptr))
			++ptr;

		*args = (const char*)ptr;
		return true;
	}
	return false;
}

static void parse_put(char *args)
{
	unsigned z, y, x, id;
	xtStringTrimWords(args);
	if (sscanf(args, "%u %u %u %u", &z, &y, &x, &id) != 4) {
		fputs("put: bad args\n", stderr);
		return;
	}
	cmd_put(z, y, x, id);
}

static int handle_login(void)
{
	char name[SHADOW_USER_NAMESZ], passwd[SHADOW_PASSWD_MAX];

	fputs("name: ", stdout);
	if (!fgets(name, sizeof name, stdin))
		return 0;

	xtStringTrimWords(name);

	struct termios old, new;

	/* Turn echoing off and fail if we can’t. */
	if (tcgetattr(STDIN_FILENO, &old) != 0)
		return 1;
	new = old;
	new.c_lflag &= ~ECHO;
	if (tcsetattr(STDIN_FILENO, TCSAFLUSH, &new) != 0)
		return 1;

	/* Read the password. */
	fputs("passwd: ", stdout);

	if (!fgets(passwd, sizeof passwd, stdin))
		return 0;
	putchar('\n');

	xtStringTrim(passwd);

	/* Restore terminal. */
	(void)tcsetattr(STDIN_FILENO, TCSAFLUSH, &old);

	return cmd_login(name, passwd);
}

/* Run user command. */
static int run_cmd(char *line, size_t n)
{
	const char *args;
	(void)n;
	if (!strcmp(line, "quit"))
		return -1;
	if (!strcmp(line, "who")) {
		cmd_query(NET_QUERY_WHO);
		return 0;
	} else if (cmd_starts(line, "say", &args)) {
		if (args)
			cmd_say(args);
		return 0;
	} else if (cmd_starts(line, "put", &args)) {
		if (args)
			parse_put((char*)args);
		return 0;
	} else if (!strcmp(line, "login")) {
		handle_login();
		return 0;
	}
	fputs("unknown command\n", stderr);
	return 1;
}

/* Keep asking user for command input. */
static void input_loop(void)
{
	char line[256];
	size_t in;
	int err;
	while (xtStringReadLine(line, sizeof line, &in, stdin)) {
		xtStringTrim(line);
		if ((err = run_cmd(line, in)) < 0)
			return;
	}
}

/* Spawn worker threads. */
static int start_workers(void)
{
	int err;
	if ((err = xtThreadCreate(&t_event, event_loop, NULL, 0, 0))) {
		xtPerror("spawn event_loop", err);
		goto fail;
	}
	err = 0;
fail:
	return err;
}

/* Terminate worker threads. */
static int join_workers(void)
{
	int err;
#if XT_IS_LINUX
	if ((err = pthread_cancel(t_event.nativeThread)))
		if (err != ESRCH) {
			xtPerror("stop event_loop", err);
			goto fail;
		}
	if ((err = xtThreadJoin(&t_event, NULL))) {
		xtPerror("join event_loop", err);
		goto fail;
	}
#else
	/*
	 * windoze does not properly support thread cancellation...
	 * so we cannot join the thread and just let the main thread terminate
	 * and hope nothing happens...
	 */
#endif
	err = 0;
fail:
	return err;
}

int main(int argc, char **argv)
{
	int err = 1;
	atexit(cleanup);
	if (argc != 2) {
		fprintf(stderr,
			"usage: %s address\n", argc > 0 ? argv[0] : "client"
		);
		goto fail;
	}
	if (!xtSocketInit()) {
		fputs("main: internal error\n", stderr);
		goto fail;
	}
	if ((err = xtSocketCreate(&sockfd, XT_SOCKET_PROTO_TCP))) {
		xtPerror("sock create", err);
		goto fail;
	}
	if ((err = xtSocketSetSoReuseAddress(sockfd, true)))  {
		xtPerror("sock reuse", err);
		goto fail;
	}
	if ((err = xtSocketSetSoKeepAlive(sockfd, true)))  {
		xtPerror("sock keep alive", err);
		goto fail;
	}
	if ((err = !xtSockaddrFromString(&sa, argv[1], DEFAULT_PORT))) {
		xtPerror("sockaddr init", err);
		goto fail;
	}
	for (unsigned i = 0; i < CONNECT_TRIES; ++i) {
		puts("connecting...");
		if (!(err = xtSocketConnect(sockfd, &sa)))
			goto connected;
		xtSleepMS(1000);
	}
	xtPerror("could not connect", err);
	goto fail;
connected:
	puts("connected");
	if ((err = start_workers()))
		goto fail;
	input_loop();
	if ((err = join_workers()))
		goto fail;
	err = 0;
fail:
	cleanup();
	return err;
}
