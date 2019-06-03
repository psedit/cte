/* Copyright 2019 Collaborative Text Editor. All rights reserved */

#include <assert.h>
#include <errno.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <inttypes.h>
#include <netdb.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <sys/epoll.h>
#include <sys/mman.h>
#include <arpa/inet.h>
#include <unistd.h>

#include "dbg.h"
#include "config.h"
#include "net.h"
#include "ini.h"
#include "voxel.h"
#include "../net.c"

#define EPOLL_SIZE 16
#define MAX_EVENTS (2 * MAX_PEERS)
#define MAX_PEERS 16
// Maximum delay in ms if we have pending packets
#define SEND_DELAY 10

#define SEND_QUEUESZ 256

#define DEFAULT_MOTD "There is no message of the day..."

static char hostname[256] = "Test server";
static unsigned max_users;
static char motd[NET_MESSAGE_SIZE] = DEFAULT_MOTD;

static int world_fd = -1;
static void *world_data = MAP_FAILED;
static unsigned world_size = 0;

struct voxel voxel;

#define ARRAY_SIZE(a) (sizeof(a)/sizeof(a[0]))

// FIXME redesign user password database
// for now, just create a list with some hardcoded users
#define USER_NAMESZ 80

struct user {
	char name[USER_NAMESZ];
	//char hash[XT_BCRYPT_KEY_LENGTH];
} users[] = {
	{"root"}, {"methos"}, {"admbot"}, {"slave"}
};

uint16_t user_try_login(const char *name, const char *passwd)
{
	for (uint16_t i = 0; i < ARRAY_SIZE(users); ++i)
		if (!strcmp(name, users[i].name))
			return i;

	return USER_ID_INVALID;
}

static int sockfd = -1;
static int efd = -1;

#define str(x) #x
#define stre(x) str(x)

#define SERVER_DEFAULT_SETTINGS \
	"; Multiverse server configuration settings\n" \
	"port = " stre(DEFAULT_PORT) "\n" \
	"max_users = 16\n" \
	"hostname = Dinnur Blaster\n" \
	"motd = " DEFAULT_MOTD "\n"

static struct epoll_event events[MAX_EVENTS];
// continuous global peer id counter
static unsigned peer_id = 0;

struct netbuf {
	struct net_pkg msg;
	unsigned size;
};

struct peer {
	int fd; // primary key
	unsigned id; // second key (used for detecting changes)
		     // e.g. message thread sents message back to network
		     // thread but the backing peer has been changed.
	uint16_t user_id;
	// network buffer
	struct netbuf net;
};

// XXX use avl tree
// network thread user heap
// the network thread is the only thread allowed to gain access to this!
static struct sheap {
	struct peer data[MAX_PEERS];
	size_t size, cap;
} peers;

// output queue that caches pending messages
// FIXME resizing is not supported!
static struct send_queue {
	// NOTE netbuf messages are in network byte order
	struct netbuf data[SEND_QUEUESZ];
	unsigned dest[SEND_QUEUESZ];
	size_t head, tail, size, cap;
} pending;

static void sheap_init(struct sheap *h)
{
	h->size = 0;
	h->cap = MAX_PEERS;
	for (unsigned i = 0; i < MAX_PEERS; ++i) {
		h->data[i].fd = -1;
		h->data[i].user_id = USER_ID_INVALID;
	}
}

static void send_queue_init(struct send_queue *q)
{
	q->head = q->tail = 0;
	q->size = 0;
	q->cap = SEND_QUEUESZ;
}

/** Postpone network packet for another run. */
static int send_queue_push(struct send_queue *q, const struct peer *dest, const struct net_pkg *p, unsigned out)
{
	struct netbuf *item;

	if (q->size == q->cap)
		return 1;

	item = &q->data[q->head];
	item->msg = *p;
	item->size = out;
	q->dest[q->head] = dest->id;

	q->head = (q->head + 1) % q->cap;
	++q->size;

	return 0;
}

static unsigned sheap_find_id(const struct sheap *h, unsigned id);
static int sheap_removei(struct sheap *h, unsigned i);

/* Try to send first pending network packet. */
static int send_queue_retry(struct send_queue *q)
{
	struct netbuf *item;
	ssize_t n;
	unsigned char *data;
	uint16_t rem;

	// Do nothing if no work available
	if (!q->size)
		return 1;

	// If peer is not connected anymore, drop packet
	unsigned i = sheap_find_id(&peers, q->dest[q->tail]);
	if (i == peers.cap)
		goto done;

	// Peer still connected; grab information to send.
	const struct peer *p = &peers.data[i];
	item = &q->data[q->tail];
	data = (unsigned char*)&item->msg + item->size;
	rem = xtbe16toh(item->msg.length) + NET_HEADER_SIZE - item->size;

	if ((n = write(p->fd, data, rem)) < 0)
		if (errno != EAGAIN && errno != EWOULDBLOCK) {
			int err;

			if (errno == EPIPE)
				fprintf(stderr, "send_queue_retry: remote closed fd %d\n", p->fd);
			else
				fprintf(stderr, "send_queue_retry: failed to write fd %d\n", p->fd);
			close(p->fd);
			err = sheap_removei(&peers, i);
			assert(!err);
			return 1;
		}
done:
	q->tail = (q->tail + 1) % q->cap;
	--q->size;
	return 0;
}

/** Try to send pending network packets and return number of flushed packets. */
static unsigned send_queue_flush(struct send_queue *q)
{
	unsigned n = 0;
	while (!send_queue_retry(q))
		++n;
	return n;
}

static void peer_init(struct peer *p, int fd)
{
	p->fd = fd;
	p->id = peer_id++;
	p->user_id = USER_ID_INVALID;
}

static void sheap_dump(const struct sheap *h)
{
	printf("sheap dump\npeers = %zu\ncapacity = %zu\n", h->size, h->cap);

	for (unsigned i = 0; i < h->cap; ++i) {
		const struct peer *p = &h->data[i];
		if (p->fd != -1)
			printf("(%d,%u,%u) ", p->fd, p->id, (unsigned)p->user_id);
	}
	putchar('\n');
}

static int sheap_put(struct sheap *h, const struct peer *p)
{
	if (h->size >= h->cap)
		return 1;

	for (unsigned i = 0; i < h->cap; ++i)
		if (h->data[i].fd == -1) {
			// found a slot
			h->data[i] = *p;
			// Clear network buffer just in case
			memset(&h->data[i].net, 0, sizeof p->net);
			h->size++;
			break;
		}

	//sheap_dump(h);
	return 0;
}

static int sheap_removei(struct sheap *h, unsigned i)
{
	assert(i < h->cap);

	if (!h->size)
		return 1;

	// Change element to make sure it becomes new minimum.
	h->data[i].fd = -1;
	h->data[i].user_id = USER_ID_INVALID;
	h->size--;
	//sheap_dump(h);
	return 0;
}

static unsigned sheap_find(const struct sheap *h, int fd)
{
	for (unsigned i = 0; i < h->cap; ++i)
		if (h->data[i].fd == fd)
			return i;
	return h->cap;
}

static unsigned sheap_find_id(const struct sheap *h, unsigned id)
{
	for (unsigned i = 0; i < h->cap; ++i)
		if (h->data[i].id == id && h->data[i].fd != -1)
			return i;
	return h->cap;
}

static int sheap_remove(struct sheap *h, int fd)
{
	unsigned i = sheap_find(h, fd);
	assert(i < h->cap);
	int ret = i < h->cap ? sheap_removei(h, i) : 1;
	return ret;
}

// TODO create list of users (preferably as binary min sheap)
/*
 * we need two lists: the first one is only available to the main thread
 * the second one is only available to the worker thread (or: worker threads?)
 * this is because by the time a message has been processed,
 * the peer and its associated fd may have been closed. or worse: a new peer
 * may have taken its place. this would disrupt the network greatly and we have
 * to make sure this doesn't happen.
 */

static void net_stop(void);

static void cleanup(void)
{
	net_stop();
	if (efd != -1) {
		close(efd);
		efd = -1;
	}
	if (sockfd != -1) {
		close(sockfd);
		sockfd = -1;
	}
	if (world_data != MAP_FAILED) {
		munmap(world_data, world_size);
		world_data = MAP_FAILED;
		world_size = 0;
	}
	if (world_fd != -1) {
		close(world_fd);
		world_fd = -1;
	}

	voxel_close(&voxel);
}

// TODO design world file format, user accounts etc. etc.

#define B_AIR   0
#define B_STONE 1

// just some arbitrary number to get started on the real engine
// Chunk DIMension SiZe
#define C_DIMSZ 8
#define W_CHUNKSZ (C_DIMSZ * C_DIMSZ * C_DIMSZ)

// world data
// just a static chunk for now
// NOTE order is x,y,z!

static uint16_t *world = NULL;

#define WORLD_SIZE (CHUNK_BLOCKS * sizeof(uint16_t))

static int world_init(void)
{
	struct stat st;
	int trunc = 0;
	static uint16_t w[W_CHUNKSZ];
	// create default world data
	// clean chunk and fill bottom layer with stone
	for (size_t i = 0; i < W_CHUNKSZ; ++i)
		w[i] = B_AIR;
	for (size_t y = 0; y < C_DIMSZ; ++y)
		for (size_t x = 0; x < C_DIMSZ; ++x)
			w[y * C_DIMSZ + x] = B_STONE;

	// TODO choose most appropiate mode
	world_fd = open("world", O_CREAT | O_RDWR, 0644);
	// TODO check if perms really are 0644 or use chmod to force this
	if (world_fd == -1) {
		perror("no world");
		return 1;
	}
	if (fstat(world_fd, &st)) {
		perror("fstat");
		return 1;
	}
	if (st.st_size != WORLD_SIZE) {
		// world corrupt or invalid: resize and populate
		if (ftruncate(world_fd, WORLD_SIZE)) {
			perror("ftruncate");
			return 1;
		}
		trunc = 1;
	}
	world_data = mmap(NULL, WORLD_SIZE, PROT_READ | PROT_WRITE, MAP_FILE | MAP_SHARED, world_fd, 0);
	if (world_data == MAP_FAILED) {
		if (trunc)
			return unlink("world");
	}
	world_size = WORLD_SIZE;
	// populate after truncating
	if (trunc)
		memcpy(world_data, w, WORLD_SIZE);
	world = world_data;
	return 0;
}

static int net_pkg_send(struct net_pkg *pkg, unsigned id);

static void incoming(void)
{
	while (1) {
		struct sockaddr in_addr;
		int err, infd;
		unsigned i;
		struct net_pkg pkg;
		socklen_t in_len = sizeof in_addr;
		// XXX is getnameinfo vulnerable?
		char hbuf[NI_MAXHOST], sbuf[NI_MAXSERV];

		if ((infd = accept(sockfd, &in_addr, &in_len)) == -1) {
			if (errno != EAGAIN && errno != EWOULDBLOCK)
				perror("accept");
			break;
		}

		// setup incoming connection and drop if errors occur
		if (!getnameinfo(&in_addr, in_len,
				hbuf, sizeof hbuf,
				sbuf, sizeof sbuf,
				NI_NUMERICHOST | NI_NUMERICSERV))
			printf("incoming: fd %d from %s:%s\n", infd, hbuf, sbuf);
		else
			printf("incoming: fd %d from unknown\n", infd);

		if (nonblock(infd)) {
			perror("nonblock");
			goto reject;
		}
		// XXX is this a good idea?
		if (reuse(infd)) {
			perror("reuse");
			goto reject;
		}
		if (keep_alive(infd)) {
			perror("keep alive");
			goto reject;
		}
		// first add the peer, then register the epoll_event
		struct peer p;
		peer_init(&p, infd);

		if (sheap_put(&peers, &p)) {
			fprintf(stderr, "incoming: sheap_put failed fd %d\n", infd);
			goto reject;
		}

		struct epoll_event ev;
		memset(&ev, 0, sizeof ev);

		ev.data.fd = infd;
		ev.events = EPOLLIN | EPOLLET;

		if (epoll_ctl(efd, EPOLL_CTL_ADD, infd, &ev)) {
			perror("epoll_ctl");
			err = sheap_remove(&peers, infd);
			assert(!err);
reject:
			fprintf(stderr, "incoming: reject fd %d\n", infd);
			close(infd);
		}

		// send spawn chunk
		i = sheap_find(&peers, infd);
		assert(i < peers.cap);

		net_pkg_init(&pkg, NT_CHUNK, 0, 0, 0, CHUNK_TYPE_STATIC, 0, world);

		if ((err = net_pkg_send(&pkg, peers.data[i].id))) {
			fprintf(stderr, "incoming: drop fd %d\n", infd);
			close(infd);
		}
	}
}

static int net_pkg_send_peer(struct net_pkg *pkg, const struct peer *p, int hton)
{
	int err = 0;
	ssize_t n;
	unsigned size;

	if (hton) {
		size = NET_HEADER_SIZE + pkg->length;
		net_pkg_hton(pkg);
	} else {
		size = NET_HEADER_SIZE + xtbe16toh(pkg->length);
	}

	if ((n = write(p->fd, pkg, size)) < 0) {
		if (errno != EAGAIN && errno != EWOULDBLOCK) {
			if (errno == EPIPE)
				// drop peer
				fprintf(stderr, "net_pkg_send_peer: remote closed fd %d\n", p->fd);
			else
				fprintf(stderr, "net_pkg_send_peer: failed to write fd %d\n", p->fd);
			return 1;
		}
		// XXX not sure about the number of written bytes...
		// just assume nothing has been sent.
		// setting this to zero makes sure we postpone the whole message
		n = 0;
	}
	if (n != size) {
		printf("net_pkg_send_peer: postpone fd %d: %zd/%u bytes\n", p->fd, n, size);
		if ((err = send_queue_push(&pending, p, pkg, (unsigned)n)))
			fprintf(stderr, "net_pkg_send_peer: cannot postpone fd %d\n", p->fd);
	}
	return err;
}

static int net_pkg_send(struct net_pkg *pkg, unsigned id)
{
	unsigned i = sheap_find_id(&peers, id);
	if (i == peers.cap)
		// XXX what is correct error handling?
		return 1;

	return net_pkg_send_peer(pkg, &peers.data[i], 1);
}

static int net_pkg_broadcast(struct net_pkg *pkg)
{
	int err;
	net_pkg_hton(pkg);
	for (unsigned i = 0; i < peers.cap; ++i) {
		const struct peer *p = &peers.data[i];
		if (p->fd == -1)
			continue;
		if (net_pkg_send_peer(pkg, p, 0)) {
			close(p->fd);
			err = sheap_removei(&peers, i);
			assert(!err);
			// XXX keep track of this to return 1 at end of loop?
		}
	}
	return 0;
}

static int net_pkg_text(struct net_pkg *pkg, unsigned i)
{
	const struct peer *p = &peers.data[i];
	char copy[NET_MESSAGE_SIZE];
	struct net_text *msg = &pkg->data.text;

	printf("msg from fd %d, id %u: %s\n", p->fd, p->id, msg->text);
	strcpy(copy, msg->text);

	// Put username in there if the user is logged in
	if (p->user_id != USER_ID_INVALID) {
		snprintf(msg->text, NET_MESSAGE_SIZE, "%s: %s", users[p->user_id].name, copy);
	} else {
		snprintf(msg->text, NET_MESSAGE_SIZE, "%u: %s", p->id, copy);
	}

	// XXX default policy: broadcast message to everyone
	return net_pkg_broadcast(pkg);
}

static int net_pkg_query(struct net_pkg *pkg, unsigned i)
{
	const struct peer *p = &peers.data[i];
	char msg[NET_MESSAGE_SIZE];
	struct net_pkg out;

	printf("query from fd %d, id %u\n", p->fd, p->id);

	switch (pkg->data.query) {
	case NET_QUERY_WHO:
		snprintf(msg, NET_MESSAGE_SIZE, "players online: %zu", peers.size);
		net_pkg_init(&out, NT_TEXT, 0, NET_TEXT_TYPE_SERVER, msg);
		return net_pkg_send(&out, p->id);
	default:
		fprintf(stderr, "bad query from fd %d\n", p->fd);
		break;
	}

	return 1;
}

static int net_pkg_usermod(struct net_pkg *pkg, unsigned i)
{
	const struct peer *p = &peers.data[i];
	struct net_usermod *m = &pkg->data.mod;
	struct net_pkg out;

	if (p->user_id == USER_ID_INVALID) {
		net_pkg_init(&out, NT_TEXT, 0, NET_TEXT_TYPE_SERVER, "permission denied");
		return net_pkg_send(&out, p->id);
	}

	switch (m->query) {
	case NET_USERMOD_PUT:
		if (m->z >= C_DIMSZ || m->y >= C_DIMSZ || m->x >= C_DIMSZ) {
			fprintf(stderr, "usermod pos out of range from fd %d\n", p->fd);
			return 0;
		}
		printf("put: %" PRIu16 ",%" PRIu16 ",%" PRIu16 ": %" PRIX16 "\n", m->z, m->y, m->x, m->id);
		world[m->z * C_DIMSZ * C_DIMSZ + m->y * C_DIMSZ + m->x] = m->id;
		net_pkg_init(&out, NT_CHUNK, 0, 0, 0, CHUNK_TYPE_STATIC, 0, world);
		return net_pkg_broadcast(&out);
	default:
		fprintf(stderr, "bad usermod from fd %d\n", p->fd);
		return 1;
	}

	return 0;
}

static int user_online(uint16_t id)
{
	for (unsigned i = 0; i < peers.cap; ++i) {
		const struct peer *p = &peers.data[i];
		if (p->fd != -1 && p->user_id == id)
			return 1;
	}
	return 0;
}

static int net_pkg_login(struct net_pkg *pkg, unsigned i)
{
	struct peer *p = &peers.data[i];
	char msg[NET_MESSAGE_SIZE];
	struct net_pkg out;
	uint16_t id;

	if ((id = user_try_login(pkg->data.login.name, pkg->data.login.passwd)) != USER_ID_INVALID && !user_online(id)) {
		// good: set user to online
		snprintf(msg, NET_MESSAGE_SIZE, "Welcome, %s. %s", pkg->data.login.name, motd);
		printf("login (%d,%u) as uid: %u\n", p->fd, p->id, id);
		p->user_id = id;
	} else {
		// bad: invalid name, invalid passwd or already logged in
		snprintf(msg, NET_MESSAGE_SIZE, "invalid credentials\n");
	}

	net_pkg_init(&out, NT_TEXT, 0, NET_TEXT_TYPE_SERVER, msg);
	return net_pkg_send(&out, p->id);
}

static int net_pkg_process(struct net_pkg *pkg, unsigned i)
{
	const struct peer *p = &peers.data[i];

	switch (pkg->type) {
	case NT_TEXT:
		return net_pkg_text(pkg, i);
	case NT_QUERY:
		return net_pkg_query(pkg, i);
	case NT_USERMOD:
		return net_pkg_usermod(pkg, i);
	case NT_LOGIN:
		return net_pkg_login(pkg, i);
	default:
		printf("net_pkg_process: bad packet from fd %d\n", p->fd);
		return 1;
	}

	return 0;
}

// TODO check buffer sizes
static int peer_handle(int fd, unsigned char *buf, unsigned n)
{
	int err = 0;
	dbgf("event_process: process fd %d (size: %u)\n", fd, n);
	// find fd and append message
	unsigned i = sheap_find(&peers, fd);
	assert(i < peers.cap);
	struct netbuf *net = &peers.data[i].net;
	// remaining number of bytes that fit in buffer
	unsigned rem = NET_PACKET_SIZE - net->size;
	// number of bytes to copy to buffer
	unsigned copy = n > rem ? rem : n;
	//printf("(i,rem,copy) = (%u,%u,%u)\n", i, rem, copy);
	unsigned char *dest = ((unsigned char*)&net->msg) + net->size;
	//printf("%p,%p,%p\n", &net->msg.type, &net->msg, dest);
	memcpy(dest, buf, copy);
	net->size += copy;
	// check if we received a full packet
	// first, we have to make sure the header is fully received
	//printf("(net->size, pkgsize) = (%u,%u)\n", net->size, (unsigned)net->msg.length + NET_HEADER_SIZE);
	unsigned len = (unsigned)xtbe16toh(net->msg.length) + NET_HEADER_SIZE;
	if (net->size >= NET_HEADER_SIZE && net->size >= len) {
		// received a full packet
		// convert endianness and process message
		net_pkg_ntoh(&net->msg);
		// TODO move this to worker thread(s)
		err = net_pkg_process(&net->msg, i);
		// move remaining data to front
		memmove(&net->msg, dest, net->size - len);
		net->size -= len;
	}
	return err;
}

static int event_process(struct epoll_event *ev)
{
	// Filter invalid/error events
	if ((ev->events & EPOLLERR) || (ev->events & EPOLLHUP) || !(ev->events & EPOLLIN))
		return 1;

	// Process incoming events
	int fd = ev->data.fd;
	if (sockfd == fd) {
		incoming();
		return 0;
	}

	while (1) {
		int err;
		ssize_t n;
		unsigned char buf[NET_PACKET_SIZE];
		if ((n = read(fd, buf, sizeof buf)) < 0) {
			if (errno != EAGAIN && errno != EWOULDBLOCK) {
				fprintf(stderr,
					"event_process: read error fd %d: %s\n",
					fd, strerror(errno)
				);
				goto drop;
			}
			break;
		} else if (!n) {
			printf("event_process: remote closed fd %d\n", fd);
			close(fd);

			err = sheap_remove(&peers, fd);
			assert(!err);
			break;
		}
		if (!peer_handle(fd, buf, (unsigned)n))
			continue;
drop:
		printf("event_process: drop fd %d\n", fd);
		close(fd);

		err = sheap_remove(&peers, fd);
		assert(!err);
		break;
	}

	return 0;
}

static int event_loop(void)
{
	int dt = -1;
	while (1) {
		int n, i;
		// XXX what to do when call gets interrupted?
		// if server runs on laptop and you suspend and resume the
		// machine, this call gets interrupted (probably errno = EINTR)

		// use different timeout than `-1' if pending packets have to be sent
		n = epoll_wait(efd, events, MAX_EVENTS, dt);
		if (n == -1) {
			if (errno == EINTR)
				continue;
			// TODO figure out correct handling (e.g. wait or die?)
			// just die for now
			perror("epoll_wait");
			return 1;
		}
		for (i = 0; i < n; ++i)
			if (event_process(&events[i])) {
				int err;
				fprintf(stderr,
					"event_process: bad event %d: %s\n",
					i, strerror(errno)
				);
				close(events[i].data.fd);
				err = sheap_remove(&peers, events[i].data.fd);
				assert(!err);
			}
		// FIXME not strictly correct usage because we try twice in a row for pending packets before waiting...
		send_queue_flush(&pending);
		dt = pending.size ? SEND_DELAY : -1;
	}
	return 0;
}

static struct sigaction sigpipe, sigpipe_old;

static int net_init(void)
{
	sigpipe.sa_handler = SIG_IGN;
	sigemptyset(&sigpipe.sa_mask);
	sigpipe.sa_flags = 0;
	return sigaction(SIGPIPE, &sigpipe, &sigpipe_old);
}

static void net_stop(void)
{
	sigaction(SIGPIPE, &sigpipe_old, NULL);
}

static int ini_create(const char *name)
{
	FILE *f = fopen(name, "wb");
	if (!f) {
		perror("ini_create");
		return 1;
	}
	fputs(SERVER_DEFAULT_SETTINGS, f);
	fclose(f);
	return 0;
}

static int ini_init(const char *name)
{
	int err = 1;
	struct ini ini;

	if ((err = ini_read(&ini, SERVER_SETTINGS))) {
		if (err == IE_NOENT && (err = ini_create(name)) == 0)
			return 0;

		perror("ini_read");
		return 1;
	}

	ini_get_str(&ini, "hostname", hostname, sizeof hostname);
	max_users = ini_get_uint(&ini, "max_users", MAX_PEERS);
	ini_get_str(&ini, "motd", motd, sizeof motd);

	ini_close(&ini);
	return 0;
}

int main(void)
{
	int err = 1;
	struct epoll_event ev;
	struct sockaddr_in sa;

	atexit(cleanup);

	sheap_init(&peers);
	send_queue_init(&pending);
	voxel_init(&voxel);

	net_check();

	if ((err = ini_init(SERVER_SETTINGS)))
		goto fail;

	printf("Starting server \"%s\"...\n", hostname);
	printf("max users: %u\n", max_users);

	if ((err = world_init())) {
		perror("world_init");
		goto fail;
	}

	if ((err = net_init())) {
		perror("net_init");
		goto fail;
	}
	// create socket and wait for incoming peers
	// create reusing nonblocking bind_to_any listening socket
	if ((sockfd = socket(AF_INET, SOCK_STREAM | SOCK_NONBLOCK, 0)) == -1) {
		perror("sock create");
		goto fail;
	}
	if ((err = reuse(sockfd))) {
		perror("sock reuse");
		goto fail;
	}

	sa.sin_family = AF_INET;
	sa.sin_addr.s_addr = INADDR_ANY;
	sa.sin_port = htons(DEFAULT_PORT);

	if ((err = bind(sockfd, (struct sockaddr*)&sa, sizeof sa)) < 0) {
		perror("sock bind");
		goto fail;
	}
	if ((err = listen(sockfd, SOMAXCONN))) {
		perror("sock listen");
		goto fail;
	}

	// setup epoll shizzle
	if ((efd = epoll_create(EPOLL_SIZE)) == -1) {
		perror("sock epoll create");
		goto fail;
	}

	memset(&ev, 0, sizeof ev);

	ev.data.fd = sockfd;
	ev.events = EPOLLIN | EPOLLET;

	if ((err = epoll_ctl(efd, EPOLL_CTL_ADD, sockfd, &ev))) {
		perror("epoll_ctl");
		goto fail;
	}

	err = event_loop();
fail:
	cleanup();
	return err;
}
