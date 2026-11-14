# Vinyl Wav Player (Yane Player) Specification

## 1. Overview
A premium, vintage-inspired web-based audio player specifically designed for `.wav` files. The player mimics the aesthetics and mechanical behavior of a traditional vinyl turntable.

## 2. Technical Stack
- **Frontend**: HTML5, CSS3 (Vanilla), JavaScript (ES6+).
- **Audio Engine**: Web Audio API (for frequency analysis and real-time visualization).
- **Typography**: Google Fonts (Outfit, Playfair Display).

## 3. Core Features

### 3.1. Visual Experience
- **Turntable Design**: A dark-themed player with a realistic vinyl record and metallic gold accents.
- **Glassmorphism**: A semi-transparent control panel utilizing backdrop filters.
- **Dynamic Animations**:
  - **Vinyl Rotation**: Spins at approximately 33.3 RPM when music is playing.
  - **Tonearm Logic**: The stylus moves onto the record when playback starts and returns to the rest position when stopped.
  - **Status LED**: A glowing indicator that changes color/intensity based on the player state (Playing, Paused, Idle).

### 3.2. Audio Functionality
- **File Support**: Optimized for `.wav` format.
- **Playback Control**: Play, Pause, and Stop functionality.
- **Volume Modulation**: A slider to adjust gain in real-time.
- **Visualizer**: A 30-bar frequency visualizer that reacts to the audio spectrum using the `AnalyserNode`.

### 3.3. UX & Shortcuts
- **Drag & Click**: The vinyl record itself acts as a play/pause trigger.
- **Keyboard Shortcut**: `Spacebar` toggles playback.
- **Real-time Metadata**: Displays filename on the record label and the control panel.

## 4. Design Constants
- **Primary Color**: `#d4af37` (Metallic Gold)
- **Background**: `#121212` (Deep Charcoal)
- **Rotation Speed**: `1.81s` per revolution (33.3 RPM)
