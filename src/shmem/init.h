#ifndef SHMEM_INIT_H_
#define SHMEM_INIT_H_

#include "atari.h"
#include "screen.h"
#ifdef SOUND
#include "sound.h"
#endif

#define SHMEM_INPUT_OFFSET 0
#define SHMEM_INPUT_SIZE 128
#define SHMEM_VIDEO_OFFSET (SHMEM_INPUT_SIZE)
#define SHMEM_VIDEO_SIZE (Screen_WIDTH * Screen_HEIGHT)
#define SHMEM_SOUND_OFFSET (SHMEM_VIDEO_OFFSET + SHMEM_VIDEO_SIZE)
#define SHMEM_SOUND_SIZE 2048
#define SHMEM_TOTAL_SIZE (SHMEM_INPUT_SIZE + SHMEM_SOUND_SIZE + SHMEM_VIDEO_SIZE)

extern unsigned char *shared_memory;

typedef struct {
	ULONG frame_count; /* read-only from client; overwritten every frame */
	UBYTE main_semaphore; /* 0=input ready, 1=screen ready, 0xff=exit emulator */
	UBYTE keychar;
	UBYTE keycode;
	UBYTE special;
	UBYTE shift;
	UBYTE control;
	UBYTE start;
	UBYTE select;
	UBYTE option;
	UBYTE joy0;
	UBYTE trig0;
	UBYTE joy1;
	UBYTE trig1;
	UBYTE joy2;
	UBYTE trig2;
	UBYTE joy3;
	UBYTE trig3;
	UBYTE mousex;
	UBYTE mousey;
	UBYTE mouse_buttons;
	UBYTE mouse_mode;
} input_template_t;

int SHMEM_Initialise(void);
void SHMEM_Exit(void);
int SHMEM_UseMemory(unsigned char *, int);
int SHMEM_AcquireMemory(void);
void SHMEM_ReleaseMemory(void);
input_template_t *SHMEM_GetInputArray(void);
void SHMEM_TakeInputArraySnapshot(void);
input_template_t *SHMEM_GetInputArraySnapshot(void);
#ifdef SOUND
Sound_setup_t *SHMEM_GetSoundArray(void);
#endif
unsigned char *SHMEM_GetVideoArray(void);

unsigned char *SHMEM_DebugGetFakeMemory(void);
typedef void (*callback_ptr)(unsigned char *);

#endif /* SHMEM_INIT_H_ */
