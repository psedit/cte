#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <stdbool.h>
#include <endian.h>

#include <arpa/inet.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <unistd.h>

#include "../config.h"

int sockfd = -1;
struct sockaddr sa;

static int reuse(int fd)
{
	int val = 1;
	return setsockopt(fd, SOL_SOCKET, SO_REUSEADDR, (const char*)&val, sizeof val);
}

bool sockaddr_init(struct sockaddr *sa, const char *addr, uint16_t port)
{
	char buf[32], *sep;

	if ((sep = strchr(addr, ':'))) {
		if (sizeof buf <= (unsigned)(sep - addr))
			return false;
		strncpy(buf, addr, sep - addr);
		buf[sep - addr] = '\0';
	} else {
		strncpy(buf, addr, sizeof buf);
		buf[sizeof buf - 1] = '\0';
	}

	if (inet_pton(AF_INET, buf, &((struct sockaddr_in*) sa)->sin_addr) != 1)
		return false;

	((struct sockaddr_in*)sa)->sin_port = htobe16(sep ? (unsigned short)strtoul(++sep, NULL, 10) : port);
	return true;
}

int main(int argc, char **argv)
{
	if (argc != 2 || !sockaddr_init(&sa, argv[1], DEFAULT_PORT)) {
		fprintf(stderr, "usage: %s address\n", argc > 0 ? argv[0] : "test");
		return 1;
	}

	if ((sockfd = socket(AF_INET, SOCK_STREAM, 0)) == -1) {
		perror("sock create");
		return 1;
	}
	if (reuse(sockfd)) {
		perror("sock reuse");
		return 1;
	}
	if (connect(sockfd, &sa, sizeof(struct sockaddr_in))) {
		perror("cannot connect");
		return 1;
	}

	puts("connected");
	// TODO talk to server...

	close(sockfd);
	return 0;
}
