/* Copyright 2019 Collaborative Text Editor. All rights reserved */

#ifndef VOXEL_H
#define VOXEL_H

#include "config.h"

#include <stdint.h>

#define CHUNK_TYPE_EMPTY 0
#define CHUNK_TYPE_STATIC 0x01
#define CHUNK_TYPE_USER 0x02

struct metadata {
	uint16_t type, state;
	uint16_t simple[CHUNK_BLOCKS];
};

struct chunk {
	int32_t x, y, z;
	uint16_t type, layer;
	struct chunk *parent;
	struct metadata *meta;
	// XXX what to do if ref > 1
	uint16_t ref; // reference counting
	uint16_t count; // number of present blocks if static type
	union {
		uint16_t blocks[CHUNK_BLOCKS];
		struct chunk *children[8];
	} data;
};

void chunk_set(struct chunk *c, int32_t x, int32_t y, int32_t z, uint16_t type, uint16_t layer, const uint16_t *blocks);

// currently, the server can run only one voxel/world at a time
// XXX do we want to have multiple voxels/worlds running?
struct voxel {
	struct chunk *chunks, *spawn;
};

void voxel_init(struct voxel *v);
void voxel_close(struct voxel *v);

int voxel_write(struct voxel *v, const char *name);
int voxel_read(struct voxel *v, const char *name);

#define VE_NOMEM 1

int voxel_put(struct voxel *v, int32_t x, int32_t y, int32_t z, uint16_t id);
int voxel_touch(struct voxel *v, int32_t x, int32_t y, int32_t z);

int voxel_set_spawn(struct voxel *v, int32_t x, int32_t y, int32_t z);

struct chunk *voxel_get_chunk(const struct voxel *v, int32_t x, int32_t y, int32_t z);

int voxel_add_chunk(struct voxel *v, const struct chunk *c);

#endif
