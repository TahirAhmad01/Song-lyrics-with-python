# 💖 Chal Wahan Jaate Hain - Synchronized Lyrics & Audio Player

A terminal song player that plays the official audio of **Chal Wahan Jaate Hain (Seene Se Tum Mere)** sung by **Arijit Singh** while animating both **English (Romanized)** and **Hindi (Devanagari)** lyrics line-by-line in the console, synchronized in real time with the music.

---

## 🎵 Song Information
* **Song:** Chal Wahan Jaate Hain (Seene Se Tum Mere)
* **Singer:** Arijit Singh
* **Music / Composer:** Amaal Mallik
* **Lyrics:** Rashmi Virag
* **Starring:** Tiger Shroff & Kriti Sanon
* **Music Label:** T-Series
* **YouTube Source:** [Watch on YouTube](https://www.youtube.com/watch?v=kNXKW4Toq_A)

---

## ✨ Features
1. **Dual Hindi & English Lyrics**: Plays synchronized lyrics displaying both **English (Romanized)** and **Hindi (Devanagari)** text.
2. **Smooth Typewriter Animation**: Line-by-line real-time typewriter animations tuned to the exact vocal onset of Arijit Singh.
3. **Visual Aesthetics**: Romantic sunset palette (Warm Coral, Soft Rose, Crimson, Golden Glow, Lavender, Sky Blue) with dynamic progress bar `[00:43 / 02:47] ━━━━●──── 26%`.
4. **Cross-Platform Playback**:
   - **macOS**: Native compiled AVFoundation player with high-precision seeking (and `afplay` fallback).
   - **Windows**: PowerShell native `System.Media.SoundPlayer`.
   - **Linux**: `ffplay`, `mpv`, or `aplay`.
5. **Auto-Downloader**: Uses `yt-dlp` to download high-fidelity audio stream automatically if `song.m4a` is not present.
6. **Language Modes**:
   - `--mode both` (Default): Shows both Romanized English and Hindi Devanagari lines.
   - `--mode en`: Romanized English only.
   - `--mode hi`: Hindi Devanagari only.
7. **Interactive Controls**:
   - `Ctrl + C`: Clean and instant stop (kills audio process and restores terminal cursor).

---

## 🚀 How to Run

### 1. Run the Player
```bash
python3 Chal-wahan-jaate-hain/play_song.py
```
Or from within the `Chal-wahan-jaate-hain` directory:
```bash
cd Chal-wahan-jaate-hain
python3 play_song.py
```
Press `[ENTER]` when prompted, sit back, and enjoy the song with lyrics!

---

### 2. Optional Command-Line Flags

* **Language Mode** (`both`, `en`, or `hi`):
  ```bash
  # Display both English and Hindi (Default):
  python3 Chal-wahan-jaate-hain/play_song.py --mode both

  # Display English / Romanized Hindi only:
  python3 Chal-wahan-jaate-hain/play_song.py --mode en

  # Display Hindi (हिंदी) only:
  python3 Chal-wahan-jaate-hain/play_song.py --mode hi
  ```

* **Start at any specific second or MM:SS** (audio seeks directly to that second):
  ```bash
  python3 Chal-wahan-jaate-hain/play_song.py --start 30
  # Or with MM:SS:
  python3 Chal-wahan-jaate-hain/play_song.py --start 00:30
  ```
  *(Example: `--start 11` jumps to Verse 1, `--start 49` jumps to Verse 2, `--start 80` jumps to Verse 3, `--start 99` jumps to the Climax Refrain)*

* **Set End Time** (stop playback cleanly at any second or MM:SS):
  ```bash
  python3 Chal-wahan-jaate-hain/play_song.py --start 11 --end 60
  # Or with MM:SS:
  python3 Chal-wahan-jaate-hain/play_song.py --start 00:11 --end 01:00
  ```

* **Set Playback Duration** (play for N seconds from start):
  ```bash
  python3 Chal-wahan-jaate-hain/play_song.py --start 11 --duration 45
  ```

* **Auto-start** (starts immediately without pressing Enter):
  ```bash
  python3 Chal-wahan-jaate-hain/play_song.py --auto
  ```

* **Fast Preview** (preview all lyrics and formatting in terminal without waiting for playback):
  ```bash
  python3 Chal-wahan-jaate-hain/play_song.py --preview
  ```

---

## 📜 Lyrics Reference (Hindi & English)

### Verse 1
> **EN:** Seene se tum mere aake lag jao na  
> **HI:** सीने से तुम मेरे आके लग जाओ ना  
> **EN:** Darte ho kyun zaraa paas to aao na  
> **HI:** डरते हो क्यों ज़रा पास तो आओ ना  

### Refrain / Hook
> **EN:** Hmm, seene se tum mere aake lag jao na  
> **HI:** हूँ.. सीने से तुम मेरे आके लग जाओ ना  
> **EN:** Darte ho kyun zaraa paas to aao na  
> **HI:** डरते हो क्यों ज़रा पास तो आओ ना  
> **EN:** Dhun meri dhadkanon ki suno...  
> **HI:** धुन मेरी धड़कनों की सुनो...  

### Verse 2
> **EN:** Koyi subah wahan raat se na mile  
> **HI:** कोई सुबह वहां रात से ना मिले  
> **EN:** Udke wahan chalo aao tum hum chalein  
> **HI:** उड़ के वहां चलो आओ तुम हम चलें  
> **EN:** Hmm, koyi subah wahan raat se na mile  
> **HI:** हूँ.. कोई सुबह वहां रात से ना मिले  
> **EN:** Udke wahan chalo aao tum hum chalein  
> **HI:** उड़ के वहां चलो आओ तुम हम चलें  

### Verse 3
> **EN:** Koyi subah wahan raat se na mile  
> **HI:** कोई सुबह वहां रात से ना मिले  
> **EN:** Udke wahan chalo aao tum hum chalein  
> **HI:** उड़ के वहां चलो आओ तुम हम चलें  
> **EN:** Pankh laya hoon main ud chalo...  
> **HI:** पंख लाया हूँ मैं उड़ चलो...  

### Climax & Outro
> **EN:** Seene se tum mere aake lag jao na  
> **HI:** सीने से तुम मेरे आके लग जाओ ना  
> **EN:** Darte ho kyun zaraa paas to aao na  
> **HI:** डरते हो क्यों ज़रा पास तो आओ ना  
> **EN:** Hmm, seene se tum mere aake lag jao na  
> **HI:** हूँ.. सीने से तुम मेरे आके लग जाओ ना  
> **EN:** Darte ho kyun zaraa paas to aao na  
> **HI:** डरते हो क्यों ज़रा पास तो आओ ना  
> **EN:** Dhun meri dhadkanon ki suno...  
> **HI:** धुन मेरी धड़कनों की सुनो...  

---

## 📦 Requirements
* Python 3.8+
* `yt-dlp` (configured in `requirements.txt`)

