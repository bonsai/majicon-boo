#include <nds.h>
#include "audio.h"
#include "sequencer.h"
#include "ui.h"
#include <stdio.h>

int main(int argc, char **argv) {
	(void)argc;
	(void)argv;

	/* Default to ARM9 */
	sysSetCartOwner(BUS_OWNER_ARM9);
	sysSetCardOwner(BUS_OWNER_ARM9);

	videoSetMode(MODE_0_2D);
	videoSetModeSub(MODE_0_2D);
	vramSetBankA(VRAM_A_MAIN_BG);
	vramSetBankC(VRAM_C_SUB_BG);

	audio_init();
	sequencer_init();
	ui_init();

	/* State: which track is being recorded (touch-and-hold) */
	int recording_track = -1;

	while (1) {
		swiWaitForVBlank();
		ui_update();
		sequencer_tick();

		/* Touch REC pad: hold to record, release to stop */
		int held_rec = ui_get_held_rec_pad();
		if (held_rec >= 0) {
			if (recording_track != held_rec) {
				if (recording_track >= 0)
					audio_stop_record(recording_track);
				audio_start_record(held_rec);
				recording_track = held_rec;
			}
		} else {
			if (recording_track >= 0) {
				audio_stop_record(recording_track);
				recording_track = -1;
			}
		}

		/* Tap PLAY pad: play once (instant sampler) */
		{
			int play = ui_get_touched_play_pad(NULL, NULL);
			if (play >= 0)
				audio_play_once(play);
		}

		/* L = loop all ready tracks (optional); R = stop all */
		u16 keys = keysDown();
		if (keys & KEY_L) {
			for (int i = 0; i < NUM_TRACKS; i++)
				audio_play_loop(i);
		}
		if (keys & KEY_R) {
			for (int i = 0; i < NUM_TRACKS; i++)
				audio_stop(i);
		}
		if (keys & KEY_START)
			break;

		ui_draw_top();
		ui_draw_sub();
	}

	audio_shutdown();
	return 0;
}
