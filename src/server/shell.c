/* Copyright 2019 Collaborative Text Editor. All rights reserved */

#include <stdio.h>
#include <unistd.h>

#include <xt/error.h>
#include <xt/string.h>
#include <xt/socket.h>

#include "dbg.h"
#include "shell.h"
#include "config.h"

extern xtSocket sockfd;

int net_pkg_send(struct net_pkg *p)
{
	uint16_t dummy;
	uint16_t size = NET_HEADER_SIZE + p->length;

	net_pkg_hton(p);

	return xtSocketTCPWriteFully(sockfd, p, size, &dummy, WRITE_TRIES);
}

int cmd_say(const char *msg)
{
	struct net_pkg p;

	net_pkg_init(&p, NT_TEXT, NET_TEXT_RECP_ALL, NET_TEXT_TYPE_USER, msg);

	return net_pkg_send(&p);
}

int cmd_query(unsigned type)
{
	struct net_pkg p;

	net_pkg_init(&p, NT_QUERY, type);

	return net_pkg_send(&p);
}

int cmd_put(uint16_t z, uint16_t y, uint16_t x, uint16_t id)
{
	struct net_pkg p;

	net_pkg_init(&p, NT_USERMOD, NET_USERMOD_PUT, z, y, x, id);

	return net_pkg_send(&p);
}

int cmd_login(const char *name, const char *passwd)
{
	struct net_pkg p;

	net_pkg_init(&p, NT_LOGIN, name, passwd);

	return net_pkg_send(&p);
}

void *event_loop(struct xtThread *t, void *arg)
{
	int err;
	char buf[256];
	struct net_pkg pkg;

	(void)t;
	(void)arg;

	while (1) {
		uint16_t in, n;

		// keep reading the packet header
		for (in = 0; in != NET_HEADER_SIZE; in += n)
			if ((err = xtSocketTCPRead(sockfd, &pkg, NET_HEADER_SIZE - in, &n))) {
				if (err != XT_ESHUTDOWN) {
					xtsnprintf(buf, sizeof buf, "event_loop: %s", xtGetErrorStr(err));
					_exit(1);
				}
				show_error("server stopped");
				_exit(0);
				return NULL;
			}

		uint16_t length = xtbe16toh(pkg.length);

		// now that we have the header, figure out remaining data
		dbgf("event_loop: grab %hu bytes...\n", length);

		union pdata *data = &pkg.data;

		for (in = 0; in != length; in += n) {
			if ((err = xtSocketTCPRead(sockfd, data, length - in, &n))) {
				if (err != XT_ESHUTDOWN)
					xtPerror("event_loop", err);
				return NULL;
			}
			dbgf("event_loop: got %hu/%hu bytes...\n", in + n, length);
		}

		net_pkg_ntoh(&pkg);
		net_pkg_process(&pkg);
	}
	return NULL;
}
