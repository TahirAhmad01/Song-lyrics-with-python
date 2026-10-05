# 🎶 Khamoshiyan (Title Track) - Synchronized Lyrics & Audio Player

A terminal song player that plays the official audio of **Khamoshiyan (Title Track)** sung by **Arijit Singh** while animating the lyrics line-by-line in the console synchronized with the music.

---

## 🎵 Song Information
* **Song:** Khamoshiyan (Title Track)
* **Movie:** Khamoshiyan (2015)
* **Singer:** Arijit Singh
* **Music / Composer:** Jeet Gannguli
* **Lyrics:** Rashmi Singh
* **Music Label:** Sony Music Entertainment India
* **YouTube Source:** [Watch on YouTube](https://www.youtube.com/watch?v=Mv3SZDP7QUo)

---

## ✨ Features
1. **Synced Audio & Lyrics**: Plays the song through your OS audio player while printing lyrics with typewriter animations at the exact vocal timestamps.
2. **Visual Aesthetics**: Rich ANSI terminal colors (Ice Blue ❄️, Cyan & Diamond 💎, Lavender, Gold, Rose) with real-time dynamic track progress bar `[01:23 / 03:16] ━━━━●────`.
3. **Cross-Platform Playback**:
   - **macOS**: Native compiled AVFoundation player with high-precision seeking (and `afplay` fallback)
   - **Windows**: PowerShell native `System.Media.SoundPlayer`
   - **Linux**: `ffplay`, `mpv`, `paplay`, or `aplay`
4. **Auto-Downloader**: Uses `yt-dlp` to download high-fidelity audio stream automatically if `song.m4a` is not present.
5. **Interactive Controls**:
   - `Ctrl + C`: Clean and instant stop (kills audio process and restores terminal cursor).

---

## 🚀 How to Run

### 1. Run the Player
```bash
python3 Khamoshiyan/play_song.py
```
Or from within the `Khamoshiyan` folder:
```bash
cd Khamoshiyan
python3 play_song.py
```
Press `[ENTER]` when prompted, sit back, and enjoy the song with lyrics!

### 2. Optional Command-Line Flags
* **Start at any specific second** (audio seeks directly to that second):
  ```bash
  python3 Khamoshiyan/play_song.py --start 41
  ```
  *(Example: `--start 41` jumps to Chorus 1, `--start 82` jumps to Verse 2, `--start 151` jumps to Chorus 2)*

* **Auto-start** (starts immediately without pressing Enter):
  ```bash
  python3 Khamoshiyan/play_song.py --auto
  ```

* **Fast Preview** (preview all lyrics and formatting in terminal without waiting for playback):
  ```bash
  python3 Khamoshiyan/play_song.py --preview
  ```

---

## 📦 Requirements
* Python 3.8+
* `yt-dlp` (already configured in `requirements.txt`)
