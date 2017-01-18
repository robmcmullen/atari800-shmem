/*
 * shmem/video.c - Shared memory specific port code - video display
 *
 * Copyright (c) 2001-2002 Jacek Poplawski
 * Copyright (C) 2001-2010 Atari800 development team (see DOC/CREDITS)
 * Copyright (c) 2016-2017 Rob McMullen
 *
 * This file is part of the Atari800 emulator project which emulates
 * the Atari 400, 800, 800XL, 130XE, and 5200 8-bit computers.
 *
 * Atari800 is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * Atari800 is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with Atari800; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
*/

#include <stdio.h>
#include <string.h>

#include "platform.h"
#include "screen.h"
#include "shmem/video.h"
#include "shmem/init.h"

int frame_count;

unsigned int debug_video;

void PLATFORM_DisplayScreen(void)
{
	unsigned char *src, *dest;
	int x, y;
	int x_offset;
	int x_count;

	if (debug_video)
		printf("display frame #%d (%d-%d, %d-%d)\n", frame_count, Screen_visible_x1, Screen_visible_x2, Screen_visible_y1, Screen_visible_y2);

	/* set up screen copy of middle 336 pixels to shared memory buffer */
	x = Screen_visible_x2 - Screen_visible_x1;
	x_count = x;
	x_offset = (Screen_WIDTH - x) / 2;
	y = Screen_visible_y2 - Screen_visible_y1;

	src = (unsigned char *)Screen_atari + x_offset;
	dest = SHMEM_GetVideoArray();
	x_offset *= 2;

	/* slow, simple copy */
	while (y > 0) {
		x = x_count;
		while (x > 0) {
			*dest++ = *src++;
			x--;
		}
		src += x_offset;
		y--;
	}

	if (debug_video) {
	/* let emulator stabilize, then print out sample of screen bytes */
		if (frame_count > 100) {
			SHMEM_DebugVideo(SHMEM_GetVideoArray());
		}
	}
}

void SHMEM_DebugVideo(unsigned char *mem) {
	int x, y;

	printf("frame %d\n", frame_count);
	mem += (336 * 24) + SHMEM_VIDEO_OFFSET;
	for (y = 0; y < 24; y++) {
		for (x = 8; x < 87; x++) {
			/*printf(" %02x", src[x]);*/
			/* print out text version of screen, assuming graphics 0 memo pad boot screen */
			unsigned char c = mem[x];
			if (c == 0)
				printf(" ");
			else if (c == 0x94)
				printf(".");
			else if (c == 0x9a)
				printf("X");
			else
				printf("?");
		}
		putchar('\n');
		mem += 336;
	}
}

int SHMEM_Video_Initialise(int *argc, char *argv[]) {
	int i, j;

	frame_count = 0;
	debug_video = FALSE;
	for (i = j = 1; i < *argc; i++) {
		if (strcmp(argv[i], "-shmem-debug-video") == 0)
			debug_video = TRUE;
		else {
			argv[j++] = argv[i];
		}
	}
	*argc = j;
	return TRUE;
}

void SHMEM_Video_Exit(void) {

}
