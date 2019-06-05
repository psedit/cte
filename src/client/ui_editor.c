/*
 * Simple SDL based text editor
 */

#include <SDL2/SDL.h>
#include <SDL2/SDL_image.h>
#include <GL/gl.h>

#include <stdio.h>

// hack for windows...
#ifdef main
#undef main
#endif

#define GLYPH_WIDTH 9
#define GLYPH_HEIGHT 16
#define GLYPH_ROW_SIZE 32
#define GLYPH_COL_SIZE 8

#define FONT_NAME "cp437.png"

#define WIDTH 640
#define HEIGHT 480

SDL_Window *win;
SDL_GLContext ctx;

unsigned img_init = 0;

static Uint32 timer;

#define TEXTURES 1

#define TEX_FONT 0

static GLuint tex[TEXTURES];
static unsigned tex_w[TEXTURES], tex_h[TEXTURES];

static void gfx_load(unsigned i, const char *name)
{
	SDL_Surface *surf;
	int mode = GL_RGB;
	GLuint texture = tex[i];

	surf = IMG_Load(name);
	if (!surf) {
		fprintf(stderr, "Could not load \"%s\": %s\n", name, IMG_GetError());
		exit(1);
	}
	if (surf->w <= 0 || surf->h <= 0) {
		fprintf(stderr, "Bogus dimensions: %d, %d\n", surf->w, surf->h);
		exit(1);
	}

	glBindTexture(GL_TEXTURE_2D, texture);

	//printf("%s: bpp = %d\n", name, surf->format->BytesPerPixel);
	// Not completely correct, but good enough
	if (surf->format->BytesPerPixel == 4)
		mode = GL_RGBA;

	glTexImage2D(GL_TEXTURE_2D, 0, mode, surf->w, surf->h, 0, mode, GL_UNSIGNED_BYTE, surf->pixels);

	tex_w[i] = (unsigned)surf->w;
	tex_h[i] = (unsigned)surf->h;

	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);

	SDL_FreeSurface(surf);
}

static void gfx_init(void)
{
	glGenTextures(TEXTURES, tex);

	gfx_load(0, FONT_NAME);
}

static void gfx_free(void)
{
	glDeleteTextures(TEXTURES, tex);
}

static void draw_ch(GLfloat x, GLfloat y, int ch)
{
	GLfloat u0, u1, v0, v1;
	GLfloat s0, s1, t0, t1;

	ch &= 0xff;

	u0 = x; u1 = x + GLYPH_WIDTH;
	v0 = y; v1 = y + GLYPH_HEIGHT;

	s0 = (ch % GLYPH_ROW_SIZE) / (GLfloat)GLYPH_ROW_SIZE;
	s1 = ((ch % GLYPH_ROW_SIZE) + 1) / (GLfloat)GLYPH_ROW_SIZE;

	t0 = (ch / GLYPH_ROW_SIZE) / (GLfloat)GLYPH_COL_SIZE;
	t1 = ((ch / GLYPH_ROW_SIZE) + 1) / (GLfloat)GLYPH_COL_SIZE;

	glTexCoord2f(s0, t0); glVertex2f(u0, v0);
	glTexCoord2f(s1, t0); glVertex2f(u1, v0);
	glTexCoord2f(s1, t1); glVertex2f(u1, v1);
	glTexCoord2f(s0, t1); glVertex2f(u0, v1);
}

static void draw_str(GLfloat x, GLfloat y, const char *str)
{
	for (GLfloat xp = x; *str; ++str) {
		if (*str == '\n')
			do {
				x = xp;
				y += GLYPH_HEIGHT;
				++str;
			} while (*str == '\n');

		draw_ch(x, y, *str);
		x += GLYPH_WIDTH;
	}
}

static void display(Uint32 ticks)
{
	glClearColor(0, 0, 0, 0);
	glClear(GL_COLOR_BUFFER_BIT);

	glMatrixMode(GL_PROJECTION);
	glLoadIdentity();
	glOrtho(0, WIDTH, HEIGHT, 0, -1, 1);

	glMatrixMode(GL_MODELVIEW);
	glLoadIdentity();

	glBindTexture(GL_TEXTURE_2D, tex[TEX_FONT]);
	glEnable(GL_TEXTURE_2D);
	glEnable(GL_BLEND);
	glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
	glColor3f(0, 1, 0);
	glBegin(GL_QUADS);
	draw_str(0, 0, "dit\nis\neen\ntest");
	glEnd();

	glDisable(GL_BLEND);
	glDisable(GL_TEXTURE_2D);
}

static int mainloop(void)
{
	glViewport(0, 0, WIDTH, HEIGHT);
	glClearColor(0, 0, 0, 0);

	timer = SDL_GetTicks();

	while (1) {
		SDL_Event ev;

		while (SDL_PollEvent(&ev)) {
			switch (ev.type) {
			case SDL_QUIT:
				return 0;
			case SDL_KEYDOWN:
				if (ev.key.keysym.sym == 'q')
					return 0;
			}
		}

		Uint32 next = SDL_GetTicks();
		display(next - timer);
		timer = next;

		SDL_GL_SwapWindow(win);
	}

	return 1;
}

int main(int argc, char *argv[])
{
	int ret = 1;

	SDL_Init(SDL_INIT_VIDEO);              // Initialize SDL2

	// Create an application window with the following settings:
	win = SDL_CreateWindow(
		"Text demo",                  // window title
		SDL_WINDOWPOS_UNDEFINED,           // initial x position
		SDL_WINDOWPOS_UNDEFINED,           // initial y position
		WIDTH,
		HEIGHT,
		SDL_WINDOW_OPENGL                  // flags - see below
	);

	// Check that the window was successfully created
	if (!win) {
		// In the case that the window could not be made...
		printf("Could not create window: %s\n", SDL_GetError());
		goto err_win;
	}
	if (!(ctx = SDL_GL_CreateContext(win))) {
		fprintf(stderr, "Could not create GL context: %s\n", SDL_GetError());
		goto err_gl;
	}

	SDL_GL_SetSwapInterval(1);

	int flags = IMG_INIT_JPG | IMG_INIT_PNG;

	if ((IMG_Init(flags) & flags) != flags) {
		fprintf(stderr, "Could not initialize image libraries: %s\n", IMG_GetError());
		goto err_img;
	}
	img_init = 1;
	gfx_init();

	ret = mainloop();

	gfx_free();
	if (img_init)
		IMG_Quit();

	ret = 0;
err_img:
	// Close and destroy the window
	SDL_GL_DeleteContext(ctx);
err_gl:
	SDL_DestroyWindow(win);
err_win:
	SDL_Quit();
	return ret;
}
