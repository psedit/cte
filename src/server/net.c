/* Copyright 2019 Collaborative Text Editor. All rights reserved */
#include "net.h"

#include <assert.h>
#include <stddef.h>
#include <stdarg.h>
#include <string.h>

#include <xt/string.h>
#include <xt/error.h>

#include "voxel.h"

// Default retry count for TCP I/O
#define XT_SOCKET_TCP_IO_TRIES 16

static const uint16_t nt_tblsz[] = {
	[NT_TEXT   ] = sizeof(struct net_text),
	[NT_QUERY  ] = sizeof(uint32_t),
	[NT_CHUNK  ] = sizeof(struct net_chunk),
	[NT_USERMOD] = sizeof(struct net_usermod),
	[NT_LOGIN  ] = sizeof(struct net_login),
};

void net_pkg_init2(struct net_pkg *p, unsigned type)
{
	assert(type <= NT_MAX);

	p->type = type;
	p->length = nt_tblsz[type];

	memset(&p->data, 0, sizeof(union pdata));
}

static void net_pkg_init_chunk(struct net_chunk *c, va_list args)
{
	c->x = va_arg(args, int32_t);
	c->y = va_arg(args, int32_t);
	c->z = va_arg(args, int32_t);
	c->type = va_arg(args, unsigned);
	c->layer = va_arg(args, unsigned);
	memcpy(c->blocks, va_arg(args, uint16_t*), CHUNK_BLOCKS * sizeof(uint16_t));
}

static void net_pkg_init_usermod(struct net_usermod *mod, va_list args)
{
	unsigned query = va_arg(args, unsigned);

	mod->query = query;

	switch (query) {
	case NET_USERMOD_PUT:
		mod->z = va_arg(args, unsigned);
		mod->y = va_arg(args, unsigned);
		mod->x = va_arg(args, unsigned);
		mod->id = va_arg(args, unsigned);
		break;
	}
}

static void net_pkg_init_text(struct net_text *msg, va_list args)
{
	msg->recipient = va_arg(args, unsigned);
	msg->type = va_arg(args, unsigned);
	xtstrncpy(msg->text, va_arg(args, const char*), NET_MESSAGE_SIZE);
}

void net_pkg_init(struct net_pkg *p, unsigned type, ...)
{
	va_list args;
	va_start(args, type);

	net_pkg_init2(p, type);

	switch (type) {
	case NT_TEXT:
		net_pkg_init_text(&p->data.text, args);
		break;
	case NT_QUERY:
		p->data.query = va_arg(args, unsigned);
		break;
	case NT_CHUNK:
		net_pkg_init_chunk(&p->data.chunk, args);
		break;
	case NT_USERMOD:
		net_pkg_init_usermod(&p->data.mod, args);
		break;
	case NT_LOGIN:
		xtstrncpy(p->data.login.name, va_arg(args, const char*), SHADOW_USER_NAMESZ);
		xtstrncpy(p->data.login.passwd, va_arg(args, const char*), SHADOW_PASSWD_MAX);
		break;
	}

	va_end(args);
}

/** Convert received network packet to host byte endian order and sanitize (i.e. null terminate) strings. */
static void pdata_ntoh(union pdata *p, uint16_t type)
{
	switch (type) {
	case NT_TEXT:
		p->text.recipient = xtbe16toh(p->text.recipient);
		p->text.type = xtbe16toh(p->text.type);
		p->text.text[NET_MESSAGE_SIZE - 1] = '\0';
		break;
	case NT_LOGIN:
		p->login.name[SHADOW_USER_NAMESZ - 1] = '\0';
		p->login.passwd[SHADOW_PASSWD_MAX - 1] = '\0';
		break;
	case NT_QUERY:
		p->query = xtbe32toh(p->query);
		break;
	case NT_CHUNK:
		p->chunk.x = xtbe32toh(p->chunk.x);
		p->chunk.y = xtbe32toh(p->chunk.y);
		p->chunk.z = xtbe32toh(p->chunk.z);
		p->chunk.type = xtbe16toh(p->chunk.type);
		p->chunk.layer = xtbe16toh(p->chunk.layer);

		for (unsigned i = 0; i < CHUNK_BLOCKS; ++i)
			p->chunk.blocks[i] = xtbe16toh(p->chunk.blocks[i]);
		break;
	case NT_USERMOD:
		p->mod.z = xtbe16toh(p->mod.z);
		p->mod.y = xtbe16toh(p->mod.y);
		p->mod.x = xtbe16toh(p->mod.x);
		p->mod.id = xtbe16toh(p->mod.id);
		p->mod.query = xtbe32toh(p->mod.query);
		break;
	default: assert(0);
	}
}

static void pdata_hton(union pdata *p, uint16_t type)
{
	switch (type) {
	case NT_TEXT:
		p->text.recipient = xthtobe16(p->text.recipient);
		p->text.type = xthtobe16(p->text.type);
		break;
	case NT_LOGIN:
		break;
	case NT_QUERY:
		p->query = xthtobe32(p->query);
		break;
	case NT_CHUNK:
		p->chunk.x = xthtobe32(p->chunk.x);
		p->chunk.y = xthtobe32(p->chunk.y);
		p->chunk.z = xthtobe32(p->chunk.z);
		p->chunk.type = xthtobe16(p->chunk.type);
		p->chunk.layer = xthtobe16(p->chunk.layer);

		for (unsigned i = 0; i < CHUNK_BLOCKS; ++i)
			p->chunk.blocks[i] = xthtobe16(p->chunk.blocks[i]);
		break;
	case NT_USERMOD:
		p->mod.z = xthtobe16(p->mod.z);
		p->mod.y = xthtobe16(p->mod.y);
		p->mod.x = xthtobe16(p->mod.x);
		p->mod.id = xthtobe16(p->mod.id);
		p->mod.query = xthtobe32(p->mod.query);
		break;
	default: assert(0);
	}
}

void net_pkg_ntoh(struct net_pkg *p)
{
	p->type = xtbe16toh(p->type);
	p->length = xtbe16toh(p->length);

	pdata_ntoh(&p->data, p->type);
}

void net_pkg_hton(struct net_pkg *p)
{
	uint16_t type = p->type;

	p->type = xthtobe16(type);
	p->length = xthtobe16(p->length);

	pdata_hton(&p->data, type);
}

void net_check(void)
{
#if DEBUG
	assert(offsetof(struct net_pkg, data) == NET_HEADER_SIZE);
	assert(sizeof(struct net_pkg) == NET_PACKET_SIZE);
#endif
}

// FIXME add checks if library officially supports xtSocketTCPWriteFully
int xtSocketTCPReadFully(xtSocket sock, void *restrict buf, uint16_t buflen, uint16_t *restrict bytesRead, unsigned retryCount)
{
	int err;
	uint16_t size = 0, in = 0, rem = buflen;
	unsigned char *ptr = buf;

	if (!retryCount)
		retryCount = XT_SOCKET_TCP_IO_TRIES;

	for (unsigned i = 0; i < retryCount; ++i) {
		err = xtSocketTCPRead(sock, ptr, rem, &size);
		if (err)
			goto fail;

		in += size;
		if (in >= buflen)
			break;

		rem -= buflen;
		ptr += buflen;
	}

	if (!err && in < buflen)
		err = XT_EAGAIN;
fail:
	*bytesRead = in;
	return err;
}

int xtSocketTCPWriteFully(xtSocket sock, const void *restrict buf, uint16_t buflen, uint16_t *restrict bytesSent, unsigned retryCount)
{
	int err;
	uint16_t size = 0, out = 0, rem = buflen;
	const unsigned char *ptr = buf;

	if (!retryCount)
		retryCount = XT_SOCKET_TCP_IO_TRIES;

	for (unsigned i = 0; i < retryCount; ++i) {
		err = xtSocketTCPWrite(sock, ptr, rem, &size);
		if (err)
			goto fail;

		out += size;
		if (out >= buflen)
			break;

		rem -= out;
		ptr += out;
	}

	if (!err && out < buflen)
		err = XT_EAGAIN;
fail:
	*bytesSent = out;
	return err;
}
