#include "ui.h"
#include "audio.h"
#include "sequencer.h"
#include <stdio.h>
#include <string.h>

#define SUB_WIDTH   256
#define SUB_HEIGHT  192
#define PAD_W       (SUB_WIDTH / PAD_COLS)
#define PAD_H       (SUB_HEIGHT / PAD_ROWS)

static PrintConsole s_top_console;
static PrintConsole s_sub_console;
static touchPosition s_touch;

void ui_init(void) {
	videoSetMode(MODE_0_2D);
	videoSetModeSub(MODE_0_2D);
	vramSetBankA(VRAM_A_MAIN_BG);
	vramSetBankC(VRAM_C_SUB_BG);
	vramSetBankH(VRAM_H_SUB_BG);

	consoleInit(&s_top_console, 0, BgType_Text4bpp, BgSize_T_256x256, 31, 0, true, true);
	consoleInit(&s_sub_console, 1, BgType_Text4bpp, BgSize_T_256x256, 30, 0, false, true);
	consoleSelect(&s_top_console);
}

void ui_update(void) {
	scanKeys();
	touchRead(&s_touch);
}

int ui_get_touched_rec_pad(int *px, int *py) {
	if (!(keysDown() & KEY_TOUCH)) return -1;
	int tx = s_touch.px;
	int ty = s_touch.py;
	int col = tx / PAD_W;
	int row = ty / PAD_H;
	if (row != PAD_REC_ROW || col < 0 || col >= PAD_COLS) return -1;
	if (px) *px = tx;
	if (py) *py = ty;
	return col;
}

int ui_get_held_rec_pad(void) {
	if (!(keysHeld() & KEY_TOUCH)) return -1;
	int tx = s_touch.px;
	int ty = s_touch.py;
	int col = tx / PAD_W;
	int row = ty / PAD_H;
	if (row != PAD_REC_ROW || col < 0 || col >= PAD_COLS) return -1;
	return col;
}

int ui_get_touched_play_pad(int *px, int *py) {
	if (!(keysDown() & KEY_TOUCH)) return -1;
	int tx = s_touch.px;
	int ty = s_touch.py;
	int col = tx / PAD_W;
	int row = ty / PAD_H;
	if (row != PAD_PLAY_ROW || col < 0 || col >= PAD_COLS) return -1;
	if (px) *px = tx;
	if (py) *py = ty;
	return col;
}

bool ui_is_touched(void) {
	return (keysHeld() & KEY_TOUCH) != 0;
}

/* Draw: top = info + simple waveform hint; sub = 4x4 pad labels */
void ui_draw_top(void) {
	consoleSelect(&s_top_console);
	consoleClear();
	iprintf("\n  4-Track Voicer/Looper\n  BPM: %d\n\n", sequencer_get_bpm());
	for (int i = 0; i < NUM_TRACKS; i++) {
		Track *t = audio_get_track(i);
		const char *st = "empty";
		if (t->state == TRACK_RECORDING) st = "REC";
		else if (t->state == TRACK_READY) st = "ready";
		else if (t->state == TRACK_PLAYING) st = "play";
		iprintf("  Tr%d: %s (%lu)\n", i + 1, st, (unsigned long)(t->length / 2));
	}
}

void ui_draw_sub(void) {
	consoleSelect(&s_sub_console);
	consoleClear();
	iprintf("  [REC1][REC2][REC3][REC4]\n  [P1]  [P2]  [P3]  [P4]\n  [Mute...]\n  Touch: hold=rec, tap=play");
}
