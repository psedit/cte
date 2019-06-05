/* Copyright 2019 Collaborative Text Editor. All rights reserved */

#ifndef INI_H
#define INI_H

#define INI_BUFSZ 4096
#define INI_CAP_INIT 32

#define IE_NOENT 1
#define IE_NOMEM 2

#include <xt/hashmap.h>

/* Really simplistic dumb INI reader. Sections are not supported! */
struct ini {
	struct xtHashmap params;
};

int ini_read(struct ini *i, const char *name);
void ini_close(struct ini *i);

const char *ini_get_key(const struct ini *i, const char *key);
int ini_get_str(const struct ini *i, const char *key, char *dst, size_t size);
unsigned ini_get_uint(const struct ini *i, const char *key, unsigned def);
int ini_get_int(const struct ini *i, const char *key, int def);

#endif
