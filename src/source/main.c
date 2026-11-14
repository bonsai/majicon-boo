#include <nds.h>
#include <filesystem.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <dirent.h>

// --- Configuration ---
#define MAX_FILES 32
#define STREAM_BUFFER_SIZE (32 * 1024) // 32KB buffer
#define HALF_BUFFER (STREAM_BUFFER_SIZE / 2)

// --- Structs ---
typedef struct {
    char name[64];
    char path[128];
} SoundFile;

typedef struct {
    FILE* file;
    u8* buffer;
    int channel;
    u32 sampleRate;
    u8 format; // SoundFormat_16Bit or SoundFormat_8Bit
    u32 dataSize;
    u32 bytesRead;
    bool playing;
    bool filling_lower; // Next fill target
} AudioStream;

// --- Globals ---
SoundFile file_list[MAX_FILES];
int file_count = 0;
AudioStream stream;
int selected_file = -1;

// --- Helper Functions ---
void scan_files() {
    DIR* dir = opendir("nitro:/veep/HIVE");
    if (dir) {
        struct dirent* ent;
        while ((ent = readdir(dir)) != NULL) {
            if (strstr(ent->d_name, ".wav") || strstr(ent->d_name, ".WAV")) {
                if (file_count < MAX_FILES) {
                    strncpy(file_list[file_count].name, ent->d_name, 63);
                    snprintf(file_list[file_count].path, 127, "nitro:/veep/HIVE/%s", ent->d_name);
                    file_count++;
                }
            }
        }
        closedir(dir);
    } else {
        printf("Failed to open directory nitro:/veep/HIVE\n");
    }
}

// Simple WAV parser
bool open_stream(const char* path) {
    if (stream.playing) {
        soundKill(stream.channel);
        if (stream.file) fclose(stream.file);
        stream.playing = false;
    }

    FILE* f = fopen(path, "rb");
    if (!f) return false;

    // Read Header
    char id[5];
    u32 size;
    u16 format_tag, channels;
    u32 sample_rate, byte_rate;
    u16 block_align, bits_per_sample;

    fseek(f, 20, SEEK_SET);
    fread(&format_tag, 2, 1, f);
    fread(&channels, 2, 1, f);
    fread(&sample_rate, 4, 1, f);
    fread(&byte_rate, 4, 1, f);
    fread(&block_align, 2, 1, f);
    fread(&bits_per_sample, 2, 1, f);

    // Find Data chunk
    fseek(f, 12, SEEK_SET); // Skip RIFF header
    // Search for "data"
    while (true) {
        if (fread(id, 1, 4, f) != 4) break;
        id[4] = 0;
        fread(&size, 4, 1, f);
        if (strcmp(id, "data") == 0) {
            break;
        }
        fseek(f, size, SEEK_CUR);
    }

    stream.file = f;
    stream.dataSize = size;
    stream.bytesRead = 0;
    stream.sampleRate = sample_rate;
    
    if (bits_per_sample == 16) stream.format = SoundFormat_16Bit;
    else stream.format = SoundFormat_8Bit;

    // Initial Fill
    stream.buffer = (u8*)malloc(STREAM_BUFFER_SIZE);
    if (!stream.buffer) {
        fclose(f);
        return false;
    }

    size_t read = fread(stream.buffer, 1, STREAM_BUFFER_SIZE, stream.file);
    stream.bytesRead += read;

    // Start Sound
    stream.channel = soundPlaySample(stream.buffer, stream.format, stream.dataSize, stream.sampleRate, 127, 64, true, 0);
    
    // Hack: soundPlaySample sets loop to false by default for unknown length?
    // We want to loop the buffer
    SCHANNEL_REPEAT_POINT(stream.channel) = 0;
    SCHANNEL_LENGTH(stream.channel) = STREAM_BUFFER_SIZE >> 2; // Words
    SCHANNEL_CR(stream.channel) |= SCHANNEL_ENABLE | SCHANNEL_REPEAT; // Force repeat

    stream.playing = true;
    stream.filling_lower = false; // Next need to fill lower half (when cursor is in upper) -> Wait, logic below

    return true;
}

void update_stream() {
    if (!stream.playing) return;

    u32 cursor = soundChannelGetCursor(stream.channel);
    
    // Double Buffer Logic
    // If cursor is in Upper Half (>= HALF_BUFFER), we can update Lower Half
    // If cursor is in Lower Half (< HALF_BUFFER), we can update Upper Half

    bool in_upper = (cursor >= HALF_BUFFER);
    
    static bool lower_updated = false;
    static bool upper_updated = false;

    if (in_upper && !lower_updated) {
        // Cursor is in upper, update lower
        size_t read = fread(stream.buffer, 1, HALF_BUFFER, stream.file);
        stream.bytesRead += read;
        if (read < HALF_BUFFER) {
             // End of file, handle loop or stop? Stop for now
             if (stream.bytesRead >= stream.dataSize) {
                 // Stop
                 soundKill(stream.channel);
                 stream.playing = false;
                 fclose(stream.file);
                 free(stream.buffer);
                 return;
             }
        }
        lower_updated = true;
        upper_updated = false;
        DC_FlushRange(stream.buffer, HALF_BUFFER); // Flush cache
    }
    else if (!in_upper && !upper_updated) {
        // Cursor is in lower, update upper
        size_t read = fread(stream.buffer + HALF_BUFFER, 1, HALF_BUFFER, stream.file);
        stream.bytesRead += read;
        if (read < HALF_BUFFER) {
             if (stream.bytesRead >= stream.dataSize) {
                 soundKill(stream.channel);
                 stream.playing = false;
                 fclose(stream.file);
                 free(stream.buffer);
                 return;
             }
        }
        upper_updated = true;
        lower_updated = false;
        DC_FlushRange(stream.buffer + HALF_BUFFER, HALF_BUFFER);
    }
}

void draw_ui() {
    // Console is on TOP
    consoleSelect(&topScreen);
    consoleClear();
    printf("\n\n  VEEP - NDS Player\n");
    printf("  =================\n");
    if (selected_file >= 0) {
        printf("\n  Now Playing:\n  %s\n", file_list[selected_file].name);
        printf("\n  SampleRate: %ld Hz\n", stream.sampleRate);
    } else {
        printf("\n  Select a track below\n");
    }

    // Bottom Screen: Draw Buttons (Using Console for now for simplicity, or just text grid)
    consoleSelect(&bottomScreen);
    consoleClear();
    printf("Select Track:\n\n");
    
    for (int i = 0; i < file_count; i++) {
        // Simple 2-column layout logic
        // But console is linear.
        // Let's just list them.
        if (i == selected_file) printf("* ");
        else printf("  ");
        
        // Truncate name
        char name[20];
        strncpy(name, file_list[i].name, 19);
        name[19] = 0;
        printf("%d: %s\n", i+1, name);
    }
}

PrintConsole topScreen;
PrintConsole bottomScreen;

int main(void) {
    // Init Video
    videoSetMode(MODE_0_2D);
    videoSetModeSub(MODE_0_2D);
    
    vramSetBankA(VRAM_A_MAIN_BG);
    vramSetBankC(VRAM_C_SUB_BG);
    
    consoleInit(&topScreen, 3,BgType_Text4bpp, BgSize_T_256x256, 31, 0, true, true);
    consoleInit(&bottomScreen, 3,BgType_Text4bpp, BgSize_T_256x256, 31, 0, false, true);

    // Init Filesystem
    if (!nitroFSInit(NULL)) {
        consoleSelect(&topScreen);
        printf("NitroFS Init Failed!\n");
        while(1);
    }

    // Init Audio
    soundEnable();

    // Scan Files
    scan_files();

    // Init UI
    draw_ui();

    while(1) {
        scanKeys();
        touchPosition touch;
        touchRead(&touch);
        
        if (keysDown() & KEY_TOUCH) {
            // Calculate which item was touched
            // Font height is 8px? 
            // We started list at line 2.
            // Each item is 1 line.
            int row = touch.py / 8;
            int index = row - 2;
            
            if (index >= 0 && index < file_count) {
                selected_file = index;
                open_stream(file_list[index].path);
                draw_ui();
            }
        }
        
        update_stream();
        swiWaitForVBlank();
    }
    
    return 0;
}
