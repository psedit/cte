/* Copyright 2019 Collaborative Text Editor. All rights reserved */

#ifndef DBG_H
#define DBG_H

#ifndef DEBUG
#define NDEBUG
#endif

#include <assert.h>

#if DEBUG
#include <stdio.h>

#define dbgf(f, ...) printf(f, ## __VA_ARGS__)
#define dbgs(s) puts(s)

#else
#define dbgf(f, ...) ((void)0)
#define dbgs(s) ((void)0)
#endif

#endif
