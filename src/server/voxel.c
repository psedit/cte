/* Copyright 2019 Collaborative Text Editor. All rights reserved */
#include "voxel.h"

#include <stdio.h>
#include <stdlib.h>

void chunk_set(struct chunk *c, int32_t x, int32_t y, int32_t z, uint16_t type, uint16_t layer, const uint16_t *blocks)
{
	uint16_t count = 0;

	c->x = x;
	c->y = y;
	c->z = z;
	c->type = type;
	c->layer = layer;

	memcpy(c->data.blocks, blocks, CHUNK_BLOCKS * sizeof(uint16_t));

	for (unsigned i = 0; i < CHUNK_BLOCKS; ++i)
		if (blocks[i])
			++count;

	c->count = count;
}

void voxel_init(struct voxel *v)
{
	v->chunks = v->spawn = NULL;

	printf("children: %zu, %zu\n", sizeof(v->chunks->data.children), 8 * sizeof(struct chunk*));
}

void voxel_close(struct voxel *v)
{
	free(v->chunks);
	v->chunks = NULL;
}

struct chunk *voxel_get_chunk(const struct voxel *v, int32_t x, int32_t y, int32_t z)
{
	// FIXME stub
	return v->spawn;
}

int voxel_add_chunk(struct voxel *v, const struct chunk *c)
{
	// FIXME stub
	if (!(v->spawn = malloc(sizeof *c)))
		return 1;

	memcpy(v->spawn, c, sizeof *c);
	return 0;
}
