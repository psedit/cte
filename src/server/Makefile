.PHONY: default clean

CC=gcc
CXX=g++
CFLAGS=-Wall -Wextra -pedantic -std=gnu11
CXXFLAGS=-Wall -Wextra -pedantic -std=c++11
LDLIBS=-lstdc++
LDFLAGS?=
DEBUG_LDLIBS?=
DEBUG_LDFLAGS?=

ifdef STRICT
	CFLAGS += -Werror
	CXXFLAGS += -Werror
endif
ifdef DEBUG
	CFLAGS += -g -DDEBUG
	CXXFLAGS += -g -DDEBUG
ifeq ($(DEBUG),2)
	CFLAGS += -fsanitize=address $(shell pkg-config --libs check)
	CXXFLAGS += -fsanitize=address $(shell pkg-config --libs check)
	DEBUG_LDLIBS += $(shell pkg-config --libs check)
	DEBUG_LDFLAGS += -fsanitize=address
endif
else
	CFLAGS += -O3
	CXXFLAGS += -O3
endif

default: server
server: server.o
	$(CC) $(DEBUG_LDFLAGS) $(DEBUG_LDLIBS) server.o -o server $(LDFLAGS) $(LDLIBS)
test: test.o
	$(CC) $(DEBUG_LDFLAGS) $(DEBUG_LDLIBS) test.o -o test $(LDFLAGS) $(LDLIBS)

clean:
	rm -f server test *.o
