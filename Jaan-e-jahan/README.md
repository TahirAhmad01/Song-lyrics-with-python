# 🎶 Jaan E Jahan OST - Synchronized Lyrics & Audio Player

A terminal song player that plays the official audio of **Jaan E Jahan OST** sung by **Rahat Fateh Ali Khan** while animating the lyrics line-by-line in the console synchronized with the music.

---

## 🎵 Song Information
* **Song:** Jaan E Jahan OST
* **Singer:** Rahat Fateh Ali Khan
* **Lyrics:** Qamar Nashad
* **Music / Composer:** Naveed Nashad
* **Uploaded By:** `@M__U__N`
* **YouTube Source:** [Watch on YouTube](https://www.youtube.com/watch?v=KQzmQ02hHFI)

---

## ✨ Features
1. **Synced Audio & Lyrics**: Plays the song through your OS audio player while printing lyrics with typewriter animations at the exact vocal timestamps.
2. **Visual Aesthetics**: Rich ANSI terminal colors (Emerald Green 💚, Cyan & Diamond 💎, Gold, Rose) with real-time dynamic track progress bar `[01:23 / 05:31] ━━━━●────`.
3. **Cross-Platform Playback**:
   - **macOS**: Built-in `afplay` (zero external dependencies required)
   - **Windows**: PowerShell native `System.Media.SoundPlayer`
   - **Linux**: `ffplay`, `mpv`, `paplay`, or `aplay`
4. **Auto-Downloader**: Uses `yt-dlp` to download high-fidelity audio stream automatically if `song.m4a` is not present.
5. **Interactive Controls**:
   - `Ctrl + C`: Clean and instant stop (kills audio process and restores terminal cursor).

---

## 🚀 How to Run

### 1. Run the Player
```bash
python3 play_song.py
```
Press `[ENTER]` when prompted, sit back, and enjoy the song with lyrics!

### 2. Optional Command-Line Flags
* **Start at any specific second** (audio seeks directly to that second):
  ```bash
  python3 play_song.py --start 39
  ```
  *(Example: `--start 39` jumps to the first Chorus, `--start 97` jumps to Verse 1, `--start 138` jumps to Verse 2)*

* **Auto-start** (starts immediately without pressing Enter):
  ```bash
  python3 play_song.py --auto
  ```

* **Fast Preview** (preview all lyrics and formatting in terminal without waiting for the full 5 minutes):
  ```bash
  python3 play_song.py --preview
  ```

---

## 📦 Requirements
* Python 3.8+
* `yt-dlp` (already configured in `requirements.txt`)
