/* Copyright 2019 Collaborative Text Editor. All rights reserved */
#include "ini.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <xt/string.h>

static size_t str_hash(const void *key)
{
	size_t hash = 5381;
	const unsigned char *str = key;
	unsigned c;

	while ((c = *str++))
		hash = ((hash << 5) + hash) + c;

	return hash;
}

static bool str_cmp(const void *a, const void *b)
{
	return strcmp((const char*)a, (const char*)b) == 0;
}

int ini_read(struct ini *i, const char *name)
{
	char buf[INI_BUFSZ];
	FILE *f;

	if (!(f = fopen(name, "r")))
		return IE_NOENT;

	if (xtHashmapCreate(&i->params, INI_CAP_INIT, str_hash, str_cmp)) {
		fclose(f);
		return IE_NOMEM;
	}
	xtHashmapSetFlags(&i->params, XT_HASHMAP_FREE_ITEM);

	while (fgets(buf, sizeof buf, f)) {
		char *key, *value;
		size_t n;

		n = strlen(buf);
		if (n)
			buf[n - 1] = '\0';

		// ignore whitespace and skip empty or comment lines
		xtStringTrim(buf);
		if (!*buf || *buf == '#' || *buf == ';')
			continue;

		// try parsing `key = value'
		if (!(key = strtok(buf, "=")))
			continue;

		xtStringTrim(key);

		if (!(value = strtok(NULL, "=")))
			continue;

		xtStringTrim(value);

		if (!(key = strdup(key)))
			continue;
		if (!(value = strdup(value))) {
			free(key);
			continue;
		}

		xtHashmapAdd(&i->params, key, value);
	}

	{
	void *key, *value;
	// dump all entries
	while (xtHashmapForeach(&i->params, &key, &value))
		printf("%s=\"%s\"\n", (char*)key, (char*)value);
	}

	fclose(f);
	return 0;
}

void ini_close(struct ini *i)
{
	xtHashmapDestroy(&i->params);
}

const char *ini_get_key(const struct ini *i, const char *key)
{
	void *value;

	if (xtHashmapGetValue(&i->params, key, &value))
		return NULL;
	return value;
}

int ini_get_str(const struct ini *i, const char *key, char *dst, size_t size)
{
	void *value;

	if (xtHashmapGetValue(&i->params, key, &value))
		return 1;

	xtstrncpy(dst, value, size);
	return 0;
}

unsigned ini_get_uint(const struct ini *i, const char *key, unsigned def)
{
	// TODO add support for different base numbers
	char buf[32];
	unsigned v;

	if (ini_get_str(i, key, buf, sizeof buf) || sscanf(buf, "%u", &v) != 1)
		return def;
	return v;
}

int ini_get_int(const struct ini *i, const char *key, int def)
{
	// TODO add support for different base numbers
	char buf[32];
	int v;

	if (ini_get_str(i, key, buf, sizeof buf) || sscanf(buf, "%d", &v) != 1)
		return def;
	return v;
}
