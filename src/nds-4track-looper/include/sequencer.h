#ifndef SEQUENCER_H
#define SEQUENCER_H

#include <nds.h>

#define DEFAULT_BPM      120
#define MIN_BPM          60
#define MAX_BPM          180

void sequencer_init(void);
void sequencer_set_bpm(int bpm);
int sequencer_get_bpm(void);

/* Call every frame; returns true on beat (for sync) */
bool sequencer_tick(void);
u32 sequencer_get_tick_count(void);

#endif /* SEQUENCER_H */
