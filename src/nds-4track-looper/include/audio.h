#ifndef AUDIO_H
#define AUDIO_H

#include <nds.h>

/* 16kHz, 16-bit mono. 1 sec = 32000 bytes. 10 sec/track = 320000 bytes */
#define SAMPLE_RATE      16000
#define BYTES_PER_SEC    (SAMPLE_RATE * 2)
#define TRACK_SECONDS    10
#define TRACK_BYTES      (BYTES_PER_SEC * TRACK_SECONDS)
#define NUM_TRACKS       4

/* Track state */
typedef enum {
	TRACK_EMPTY,
	TRACK_RECORDING,
	TRACK_READY,
	TRACK_PLAYING
} TrackState;

typedef struct {
	u8 *buffer;           /* PCM 16-bit mono buffer */
	u32 length;           /* bytes used */
	TrackState state;
	int soundId;          /* soundPlaySample id, or -1 */
} Track;

void audio_init(void);
void audio_shutdown(void);

/* Start/stop recording on track (0..3). Touch-and-hold style. */
void audio_start_record(int track_index);
void audio_stop_record(int track_index);

/* Play once (no loop) */
void audio_play_once(int track_index);
/* Play with BPM-synced loop */
void audio_play_loop(int track_index);
void audio_stop(int track_index);

/* Mute/unmute (stop playback but keep data) */
void audio_mute(int track_index);
void audio_unmute(int track_index);

Track *audio_get_track(int track_index);
int audio_get_recording_track(void);  /* -1 if none */

#endif /* AUDIO_H */
