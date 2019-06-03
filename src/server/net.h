/* Copyright 2019 Collaborative Text Editor. All rights reserved */

/**
 * Common network interface between server and client.
 */

#ifndef NET_H
#define NET_H

#include "config.h"

#include <xt/utils.h>
#include <xt/socket.h>

// FIXME add checks if library officially supports xtSocketTCPWriteFully
int xtSocketTCPReadFully(xtSocket sock, void *restrict buf, uint16_t buflen, uint16_t *restrict bytesRead, unsigned retryCount);
int xtSocketTCPWriteFully(xtSocket sock, const void *restrict buf, uint16_t buflen, uint16_t *restrict bytesSent, unsigned retryCount);

#include <stdint.h>
#include <xt/endian.h>

#define NET_PACKET_SIZE 1044
#define NET_HEADER_SIZE 4
#define NET_MESSAGE_SIZE 256

// Network packet Types
#define NT_TEXT 0
#define NT_QUERY 1
#define NT_CHUNK 2
#define NT_USERMOD 3
#define NT_LOGIN 4
#define NT_MAX 4

// Network text recipient special numbers
#define NET_TEXT_RECP_ALL USER_ID_INVALID
#define NET_TEXT_TYPE_USER 0
#define NET_TEXT_TYPE_SERVER 1

#define NET_QUERY_WHO 0

#define NET_USERMOD_PUT 1

struct net_usermod {
	uint16_t z, y, x;
	uint16_t id;
	uint32_t query;
};

struct net_login {
	char name[SHADOW_USER_NAMESZ];
	char passwd[SHADOW_PASSWD_MAX];
};

struct net_chunk {
	int32_t x, y, z;
	uint16_t type, layer;
	uint16_t blocks[CHUNK_BLOCKS];
};

struct net_text {
	uint16_t recipient, type;
	char text[NET_MESSAGE_SIZE];
};

struct net_pkg {
	uint16_t type, length;
	union pdata {
		struct net_text text;
		struct net_chunk chunk;
		uint32_t query;
		struct net_usermod mod;
		struct net_login login;
	} data;
};

void net_pkg_init2(struct net_pkg *p, unsigned type);
void net_pkg_init(struct net_pkg *p, unsigned type, ...);

/* Packet endian conversion. */
void net_pkg_ntoh(struct net_pkg *p);
void net_pkg_hton(struct net_pkg *p);

#endif
