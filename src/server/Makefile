.PHONY: default all clean

CC=gcc
CFLAGS=-Wall -Wextra -pedantic -std=gnu11 $(shell pkg-config --cflags xtcommon)
LDLIBS=$(shell pkg-config --libs xtcommon)
LDFLAGS?=
DEBUG_LDLIBS?=
DEBUG_LDFLAGS?=

ifdef STRICT
	CFLAGS += -Werror
endif
ifdef DEBUG
	CFLAGS += -g -DDEBUG
ifeq ($(DEBUG),2)
	CFLAGS += -fsanitize=address $(shell pkg-config --libs check)
	DEBUG_LDLIBS += $(shell pkg-config --libs check)
	DEBUG_LDFLAGS += -fsanitize=address
endif
else
	CFLAGS += -O3
endif

SDL_LDLIBS = $(shell pkg-config --cflags --libs sdl2 gl) -lSDL2_image

default: server client
all: server client
net.o: net.h
server: server.o net.o ini.o voxel.o
	$(CC) $(DEBUG_LDFLAGS) $(DEBUG_LDLIBS) server.o net.o ini.o voxel.o -o server $(LDFLAGS) $(LDLIBS)
client: client.o net.o shell.o voxel.o
	$(CC) $(DEBUG_LDFLAGS) $(DEBUG_LDLIBS) client.o net.o shell.o voxel.o -o client $(LDFLAGS) $(LDLIBS)

clean:
	rm -f server client *.o
