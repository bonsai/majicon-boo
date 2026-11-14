#include "sequencer.h"
#include <stdlib.h>

static int s_bpm = DEFAULT_BPM;
static u32 s_tick_count = 0;
static u32 s_next_beat_time = 0;
static bool s_beat_this_frame = false;

/* Simple timer: 1 beat = 60*60/BPM centiseconds (approx). Use VBlank count. */
#define TIMER_CENTISEC_PER_BEAT  (60 * 60 / DEFAULT_BPM)

void sequencer_init(void) {
	s_bpm = DEFAULT_BPM;
	s_tick_count = 0;
	s_next_beat_time = 0;
	s_beat_this_frame = false;
}

void sequencer_set_bpm(int bpm) {
	if (bpm < MIN_BPM) bpm = MIN_BPM;
	if (bpm > MAX_BPM) bpm = MAX_BPM;
	s_bpm = bpm;
}

int sequencer_get_bpm(void) {
	return s_bpm;
}

bool sequencer_tick(void) {
	s_beat_this_frame = false;
	/* Use frame count as cheap timer: 60 frames/sec, 4 beats per bar at 120 BPM = 2 beats/sec -> 30 frames/beat */
	u32 frames_per_beat = 60 * 60 / (u32)s_bpm;
	s_tick_count++;
	if (s_next_beat_time == 0)
		s_next_beat_time = s_tick_count + frames_per_beat;
	if (s_tick_count >= s_next_beat_time) {
		s_next_beat_time += frames_per_beat;
		s_beat_this_frame = true;
		return true;
	}
	return false;
}

u32 sequencer_get_tick_count(void) {
	return s_tick_count;
}
