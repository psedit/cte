#ifndef COMMON_NET_H
#define COMMON_NET_H

#include <sys/socket.h>
#include <sys/types.h>
#include <fcntl.h>
#include <unistd.h>

static int nonblock(int fd)
{
	int flags;
	if ((flags = fcntl(fd, F_GETFL, 0)) == -1)
		return -1;
	flags |= O_NONBLOCK;
	return fcntl(fd, F_SETFL, flags) == -1;
}

static int reuse(int fd)
{
	int val = 1;
	return setsockopt(fd, SOL_SOCKET, SO_REUSEADDR, (const char*)&val, sizeof val);
}

static int keep_alive(int fd)
{
	int val = 1;
	return setsockopt(fd, SOL_SOCKET, SO_KEEPALIVE, (const char*)&val, sizeof val);
}

#endif
