#ifndef SHMEM_H_
#define SHMEM_H_

#include <stdio.h>

/* shared memory locations */
#define SHMEM_STROBE 0
#define SHMEM_KEYCHAR 1
#define SHMEM_KEYCODE 2
#define SHMEM_SPECIAL 3
#define SHMEM_SHIFT 4
#define SHMEM_CONTROL 5
#define SHMEM_START 6
#define SHMEM_SELECT 7
#define SHMEM_OPTION 8
#define SHMEM_JOY_0 9
#define SHMEM_TRIG_0 10
#define SHMEM_JOY_1 11
#define SHMEM_TRIG_1 12
#define SHMEM_JOY_2 13
#define SHMEM_TRIG_2 14
#define SHMEM_JOY_3 15
#define SHMEM_TRIG_3 16
#define SHMEM_MOUSE_X 17
#define SHMEM_MOUSE_Y 18
#define SHMEM_MOUSE_BUTTONS 19
#define SHMEM_MOUSE_MODE 20

        /* Sound sample rate - number of frames per second: 1000..65535. */
#define SHMEM_SOUND_FREQ 128

        /* Number of bytes per each sample, also determines sample format:
           1 = unsigned 8-bit format.
           2 = signed 16-bit system-endian format. */
#define SHMEM_SOUND_SAMPLE_SIZE 130

        /* Number of audio channels: 1 = mono, 2 = stereo. */
#define SHMEM_SOUND_CHANNELS 132

        /* Length of the hardware audio buffer in milliseconds. */
#define SHMEM_SOUND_BUFFER_MS 134

        /* Size of the hardware audio buffer in frames. Computed internally,
           equals freq * buffer_ms / 1000. */
#define SHMEM_SOUND_BUFFER_FRAMES 136


#define SHMEM_FLAG_DELTA_MOUSE 0
#define SHMEM_FLAG_DIRECT_MOUSE 1

extern unsigned char *input_array;

int SHMEM_Input_Initialise(int *argc, char *argv[]);

void SHMEM_Mouse(void);

#endif /* SHMEM_H_ */
