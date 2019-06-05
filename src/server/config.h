/* Copyright 2019 Collaborative Text Editor. All rights reserved */

/* Simple common configuration settings. */
#ifndef CONFIG_H
#define CONFIG_H

#include <stdint.h>

#define DEFAULT_PORT 25659

#define USER_ID_INVALID UINT16_MAX
#define SERVER_SETTINGS "config.ini"

/* client specific stuff */
#define CONNECT_TRIES 3
#define WRITE_TRIES 3

#define SHADOW_USER_NAMESZ 64

#define SHADOW_PASSWD_MIN 8
#define SHADOW_PASSWD_MAX 64

// 8**3
#define CHUNK_BLOCKS 512

#endif
