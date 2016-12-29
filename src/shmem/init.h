#ifndef SHMEM_INIT_H_
#define SHMEM_INIT_H_

#define SHMEM_INPUT_OFFSET 0
#define SHMEM_INPUT_SIZE 128
#define SHMEM_SOUND_OFFSET (SHMEM_INPUT_SIZE + 256)
#define SHMEM_SOUND_SIZE 512
#define SHMEM_VIDEO_OFFSET (SHMEM_SOUND_OFFSET + SHMEM_SOUND_SIZE + 512)

extern unsigned char *shared_memory;

int SHMEM_Initialise(void);
void SHMEM_Exit(void);
int SHMEM_AcquireMemory(void);
void SHMEM_ReleaseMemory(void);
unsigned char *SHMEM_GetInputArray(void);
unsigned char *SHMEM_GetSoundArray(void);
unsigned char *SHMEM_GetVideoArray(void);

#endif /* SHMEM_INIT_H_ */
