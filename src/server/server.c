#include <stdio.h>
#include <arpa/inet.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <unistd.h>

#include "../config.h"

int sockfd = -1;

static int reuse(int fd)
{
	int val = 1;
	return setsockopt(fd, SOL_SOCKET, SO_REUSEADDR, (const char*)&val, sizeof val);
}

void event_loop(void)
{
	struct sockaddr in_addr;
	int err, infd;
	socklen_t in_len = sizeof in_addr;

	while ((infd = accept(sockfd, &in_addr, &in_len)) != -1) {
		puts("incoming connection");
		// TODO handle client...
		close(infd);
	}
}

int main(int argc, char **argv)
{
	struct sockaddr_in sa;

	if (argc != 2) {
		fprintf(stderr, "usage: %s file\n", argc > 0 ? argv[0] : "server");
		return 1;
	}

	// TODO make non-blocking
	if ((sockfd = socket(AF_INET, SOCK_STREAM, 0)) == -1) {
		perror("sock create");
		return 1;
	}
	if (reuse(sockfd)) {
		perror("sock reuse");
		return 1;
	}

	sa.sin_family = AF_INET;
	sa.sin_addr.s_addr = INADDR_ANY;
	sa.sin_port = htons(DEFAULT_PORT);

	if (bind(sockfd, (struct sockaddr*)&sa, sizeof sa) < 0) {
		perror("sock bind");
		return 1;
	}
	if (listen(sockfd, SOMAXCONN)) {
		perror("sock listen");
		return 1;
	}

	event_loop();

	close(sockfd);
	return 0;
}
