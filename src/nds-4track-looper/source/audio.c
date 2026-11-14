#include "audio.h"
#include <stdlib.h>
#include <string.h>

static Track s_tracks[NUM_TRACKS];
static u8 *s_mic_buffer;
static u32 s_mic_buffer_size;
static int s_recording_track = -1;

/* Double buffer: ARM7 fills half at a time; we copy to current track */
static void mic_handler(void *data, int length) {
	if (s_recording_track < 0 || s_recording_track >= NUM_TRACKS) return;
	Track *t = &s_tracks[s_recording_track];
	if (t->state != TRACK_RECORDING || !t->buffer) return;
	if (t->length + length > TRACK_BYTES) return;

	DC_InvalidateRange(data, length);
	dmaCopy(data, t->buffer + t->length, length);
	t->length += length;
}

void audio_init(void) {
	int i;
	memset(s_tracks, 0, sizeof(s_tracks));
	s_recording_track = -1;

	/* Allocate track buffers (16-bit PCM = 2 bytes per sample) */
	for (i = 0; i < NUM_TRACKS; i++) {
		s_tracks[i].buffer = (u8 *)malloc(TRACK_BYTES);
		s_tracks[i].length = 0;
		s_tracks[i].state = TRACK_EMPTY;
		s_tracks[i].soundId = -1;
		if (!s_tracks[i].buffer) {
			/* TODO: handle alloc fail */
		}
	}

	/* Mic double buffer: ~2 frames at 16kHz 16-bit, 30fps -> 16000*2*2/30 ~= 2134, round up */
	s_mic_buffer_size = (SAMPLE_RATE * 2 * 2) / 30;
	if (s_mic_buffer_size < 256) s_mic_buffer_size = 256;
	s_mic_buffer = (u8 *)malloc(s_mic_buffer_size);
	if (!s_mic_buffer) { /* TODO */ }

	soundEnable();
}

void audio_shutdown(void) {
	int i;
	soundMicOff();
	for (i = 0; i < NUM_TRACKS; i++) {
		if (s_tracks[i].soundId >= 0) {
			soundKill(s_tracks[i].soundId);
			s_tracks[i].soundId = -1;
		}
		free(s_tracks[i].buffer);
		s_tracks[i].buffer = NULL;
		s_tracks[i].state = TRACK_EMPTY;
	}
	free(s_mic_buffer);
	s_mic_buffer = NULL;
	s_recording_track = -1;
}

void audio_start_record(int track_index) {
	if (track_index < 0 || track_index >= NUM_TRACKS) return;
	Track *t = &s_tracks[track_index];
	if (!t->buffer || s_recording_track >= 0) return;

	soundMicOff();
	t->length = 0;
	t->state = TRACK_RECORDING;
	s_recording_track = track_index;
	soundMicRecord(s_mic_buffer, s_mic_buffer_size, MicFormat_12Bit, SAMPLE_RATE, mic_handler);
}

void audio_stop_record(int track_index) {
	if (track_index < 0 || track_index >= NUM_TRACKS) return;
	if (s_recording_track != track_index) return;

	soundMicOff();
	s_tracks[track_index].state = (s_tracks[track_index].length > 0) ? TRACK_READY : TRACK_EMPTY;
	s_recording_track = -1;
}

void audio_play_once(int track_index) {
	if (track_index < 0 || track_index >= NUM_TRACKS) return;
	Track *t = &s_tracks[track_index];
	if (t->state != TRACK_READY && t->state != TRACK_PLAYING) return;
	if (t->length == 0) return;

	if (t->soundId >= 0) {
		soundKill(t->soundId);
		t->soundId = -1;
	}
	soundEnable();
	t->soundId = soundPlaySample(t->buffer, SoundFormat_16Bit, t->length,
		SAMPLE_RATE, 127, 64, false, 0);
	t->state = TRACK_PLAYING;
}

void audio_play_loop(int track_index) {
	if (track_index < 0 || track_index >= NUM_TRACKS) return;
	Track *t = &s_tracks[track_index];
	if (t->state != TRACK_READY && t->state != TRACK_PLAYING) return;
	if (t->length == 0) return;

	if (t->soundId >= 0) {
		soundKill(t->soundId);
		t->soundId = -1;
	}
	soundEnable();
	t->soundId = soundPlaySample(t->buffer, SoundFormat_16Bit, t->length,
		SAMPLE_RATE, 127, 64, true, 0);
	t->state = TRACK_PLAYING;
}

void audio_stop(int track_index) {
	if (track_index < 0 || track_index >= NUM_TRACKS) return;
	Track *t = &s_tracks[track_index];
	if (t->soundId >= 0) {
		soundKill(t->soundId);
		t->soundId = -1;
	}
	if (t->state == TRACK_PLAYING)
		t->state = TRACK_READY;
}

void audio_mute(int track_index) {
	audio_stop(track_index);
}

void audio_unmute(int track_index) {
	/* Caller can call audio_play_loop again if needed */
}

Track *audio_get_track(int track_index) {
	if (track_index < 0 || track_index >= NUM_TRACKS) return NULL;
	return &s_tracks[track_index];
}

int audio_get_recording_track(void) {
	return s_recording_track;
}
