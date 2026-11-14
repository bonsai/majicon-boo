#ifndef UI_H
#define UI_H

#include <nds.h>

/* Pad layout: 4x4. Row 0 = REC 1..4, Row 1 = Play 1..4, Row 2 = Mute, etc. */
#define PAD_COLS         4
#define PAD_ROWS         4
#define PAD_REC_ROW      0
#define PAD_PLAY_ROW     1
#define PAD_MUTE_ROW     2

void ui_init(void);
void ui_update(void);

/* Touch: returns track index 0..3 for REC pads, or -1. */
int ui_get_touched_rec_pad(int *px, int *py);
int ui_get_touched_play_pad(int *px, int *py);
/* Currently held REC pad (for hold-to-record); -1 if not touching REC row */
int ui_get_held_rec_pad(void);
bool ui_is_touched(void);

void ui_draw_top(void);
void ui_draw_sub(void);

#endif /* UI_H */
