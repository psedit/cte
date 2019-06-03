/* Copyright 2019 Collaborative Text Editor. All rights reserved */

/**
 * Common shell interface for terminal client and visual client.
 */

#ifndef SHELL_H
#define SHELL_H

#include "net.h"
#include "voxel.h"

#include <stdint.h>

#include <xt/thread.h>

int net_pkg_send(struct net_pkg *p);

/* Send text message to server. */
int cmd_say(const char *msg);
/* Ask information from server. */
int cmd_query(unsigned type);

int cmd_put(uint16_t z, uint16_t y, uint16_t x, uint16_t id);

int cmd_login(const char *name, const char *passwd);

void show_error(const char *str);

extern int net_pkg_process(struct net_pkg *pkg);

/* Worker thread main routine for handling all incoming network data from server. */
void *event_loop(struct xtThread *t, void *arg);

#endif
