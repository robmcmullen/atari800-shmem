#ifndef SHMEM_INIT_H_
#define SHMEM_INIT_H_

#include "screen.h"

#define SHMEM_INPUT_OFFSET 0
#define SHMEM_INPUT_SIZE 128
#define SHMEM_SOUND_OFFSET (SHMEM_INPUT_SIZE)
#define SHMEM_SOUND_SIZE 512
#define SHMEM_VIDEO_OFFSET (SHMEM_SOUND_OFFSET + SHMEM_SOUND_SIZE)
#define SHMEM_VIDEO_SIZE (Screen_WIDTH * Screen_HEIGHT)
#define SHMEM_TOTAL_SIZE (SHMEM_INPUT_SIZE + SHMEM_SOUND_SIZE + SHMEM_VIDEO_SIZE)

extern unsigned char *shared_memory;

int SHMEM_Initialise(void);
void SHMEM_Exit(void);
int SHMEM_UseMemory(unsigned char *, int);
int SHMEM_AcquireMemory(void);
void SHMEM_ReleaseMemory(void);
unsigned char *SHMEM_GetInputArray(void);
unsigned char *SHMEM_GetSoundArray(void);
unsigned char *SHMEM_GetVideoArray(void);

typedef void (*callback_ptr)();

#endif /* SHMEM_INIT_H_ */
