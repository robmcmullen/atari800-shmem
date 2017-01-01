#ifndef SHMEM_VIDEO_H_
#define SHMEM_VIDEO_H_

#include <stdio.h>

#include "config.h"

int SHMEM_Video_Initialise(int *argc, char *argv[]);
void SHMEM_Video_Exit(void);
void SHMEM_DebugVideo(unsigned char *);

#endif /* SHMEM_VIDEO_H_ */
