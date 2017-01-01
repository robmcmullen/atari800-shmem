/*
 * shmem/main.c - Shared memory port code - main interface
 *
 * Copyright (c) 2001-2002 Jacek Poplawski
 * Copyright (C) 2001-2014 Atari800 development team (see DOC/CREDITS)
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

#include "config.h"
#include <stdio.h>
#include <string.h>

/* Atari800 includes */
#include "atari.h"
#include "../input.h"
#include "log.h"
#include "monitor.h"
#include "platform.h"
#ifdef SOUND
#include "../sound.h"
#endif
#include "videomode.h"
#include "shmem/init.h"
#include "shmem/input.h"
#include "shmem/video.h"

int PLATFORM_Configure(char *option, char *parameters)
{
	return TRUE;
}

void PLATFORM_ConfigSave(FILE *fp)
{
	;
}

int PLATFORM_Initialise(int *argc, char *argv[])
{
	int i, j;
	int help_only = FALSE;

	for (i = j = 1; i < *argc; i++) {
		if (strcmp(argv[i], "-help") == 0) {
			help_only = TRUE;
		}
		argv[j++] = argv[i];
	}
	*argc = j;

	if (!help_only) {
		if (!SHMEM_Initialise()) {
			return FALSE;
		}
	}

	if (!SHMEM_Video_Initialise(argc, argv)
#ifdef SOUND
		|| !Sound_Initialise(argc, argv)
#endif
		|| !SHMEM_Input_Initialise(argc, argv))
		return FALSE;

	return TRUE;
}

int PLATFORM_Exit(int run_monitor)
{
	Log_flushlog();

	if (run_monitor) {
#ifdef SOUND
		Sound_Pause();
#endif
		if (MONITOR_Run()) {
	#ifdef SOUND
			Sound_Continue();
	#endif
			return 1;
		}
	}
	SHMEM_Exit();

	return 0;
}

int start_shmem(int argc, char **argv, unsigned char *raw, int len, callback_ptr cb)
{
	int i;
	for (i = 0; i < argc; i++) {
		printf("arg #%d: %s\n", i, argv[i]);
	}
	printf("raw=%lx, len=%d\n", raw, len);
	if (raw) SHMEM_UseMemory(raw, len);

	/* initialise Atari800 core */
	if (!Atari800_Initialise(&argc, argv))
		return 3;

	/* main loop */
	i = 0;
	for (;;) {
		INPUT_key_code = PLATFORM_Keyboard();
		SHMEM_Mouse();
		Atari800_Frame();
		if (Atari800_display_screen)
			PLATFORM_DisplayScreen();
		i++;
		if (i > 100) {
			if (cb) {
				unsigned char *fake_shared_memory = SHMEM_DebugGetFakeMemory();
				printf("fake %lx\n", fake_shared_memory);
				SHMEM_DebugVideo(fake_shared_memory);
				printf("shared %lx\n", shared_memory);
				SHMEM_DebugVideo(shared_memory);
				//memcpy(shared_memory, fake_shared_memory, SHMEM_TOTAL_SIZE);
				printf("callback=%lx\n", cb);
				(*cb)(shared_memory);
			}
		}
	}
}

int main(int argc, char **argv)
{
	start_shmem(argc, argv, NULL, 0, NULL);
}

/*
vim:ts=4:sw=4:
*/
