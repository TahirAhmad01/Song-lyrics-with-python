#!/usr/bin/env python3
"""
CHAL WAHAN JAATE HAIN (Seene Se Tum Mere) - Lyrics & Audio Player
Singer: Arijit Singh
Music: Amaal Mallik
Lyrics: Rashmi Virag
Starring: Tiger Shroff & Kriti Sanon
YouTube: https://www.youtube.com/watch?v=kNXKW4Toq_A
"""

import os
import sys
import time
import signal
import platform
import subprocess
import shutil

# --- Color & Style Constants (ANSI 256-color palette) ---
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
ITALIC = "\033[3m"

# Romantic Sunset & Dreamy Love Palette
CORAL = "\033[38;5;204m"       # Vibrant Warm Coral
ROSE = "\033[38;5;211m"        # Soft Romantic Rose
CRIMSON = "\033[38;5;197m"     # Deep Passionate Red/Pink
GOLD = "\033[38;5;220m"        # Warm Golden Glow
SUNSET = "\033[38;5;215m"      # Soft Peach / Sunset Orange
LAVENDER = "\033[38;5;141m"    # Dreamy Lavender
ORCHID = "\033[38;5;177m"      # Soft Orchid Pink
MAGENTA = "\033[38;5;201m"     # Electric Romance
SKY_BLUE = "\033[38;5;117m"    # Sky Blue (Aasman)
CYAN = "\033[38;5;51m"         # Bright Cyan
AQUA = "\033[38;5;44m"         # Soft Aqua
WHITE = "\033[38;5;255m"       # Pure White
GRAY = "\033[38;5;242m"        # Subtle Dim Gray

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIO_FILE = os.path.join(BASE_DIR, "song.m4a")
AUDIO_PLAYER_BIN = os.path.join(BASE_DIR, "audio_player")
YOUTUBE_URL = "https://www.youtube.com/watch?v=kNXKW4Toq_A"
TOTAL_DURATION = 167  # ~ 2:47

# Global audio player process reference for clean termination
player_process = None


def cleanup(sig=None, frame=None):
    """Gracefully terminate audio player and restore terminal."""
    global player_process
    print("\n\n" + RESET + CORAL + "Stopping music playback... Chal Wahan Jaate Hain... 💖🕊️" + RESET)
    if player_process:
        try:
            player_process.terminate()
            player_process.wait(timeout=1)
        except Exception:
            try:
                player_process.kill()
            except Exception:
                pass
    # Restore terminal cursor
    sys.stdout.write("\033[?25h\n")
    sys.stdout.flush()
    sys.exit(0)


signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGTERM, cleanup)


def ensure_audio_file():
    """Check if song.m4a exists, otherwise download it via yt-dlp."""
    if os.path.exists(AUDIO_FILE) and os.path.getsize(AUDIO_FILE) > 100000:
        return AUDIO_FILE

    print(f"{CORAL}⬇️  Downloading song audio from YouTube...{RESET}")
    print(f"{GRAY}URL: {YOUTUBE_URL}{RESET}\n")

    try:
        import yt_dlp
        ydl_opts = {
            'format': 'ba[ext=m4a]/ba',
            'outtmpl': AUDIO_FILE,
            'quiet': False,
            'no_warnings': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([YOUTUBE_URL])
    except Exception:
        # Fallback to CLI
        subprocess.run(
            [sys.executable, "-m", "yt_dlp", "-f", "ba[ext=m4a]/ba", "-o", AUDIO_FILE, YOUTUBE_URL],
            check=True
        )

    if not os.path.exists(AUDIO_FILE):
        print(f"\033[91mError: Could not obtain {AUDIO_FILE}. Please check your internet connection.\033[0m")
        sys.exit(1)

    print(f"{GOLD}✓ Audio downloaded successfully!{RESET}\n")
    return AUDIO_FILE


def ensure_macos_audio_player():
    """Ensure the native AVFoundation audio player binary is compiled for seeking."""
    if os.path.exists(AUDIO_PLAYER_BIN) and os.access(AUDIO_PLAYER_BIN, os.X_OK):
        return AUDIO_PLAYER_BIN

    objc_src = """#import <Foundation/Foundation.h>
#import <AVFoundation/AVFoundation.h>
#import <signal.h>

static AVAudioPlayer *globalPlayer = nil;

void sig_handler(int sig) {
    if (globalPlayer) {
        [globalPlayer stop];
    }
    exit(0);
}

int main(int argc, const char * argv[]) {
    @autoreleasepool {
        if (argc < 2) return 1;
        signal(SIGINT, sig_handler);
        signal(SIGTERM, sig_handler);

        NSString *path = [NSString stringWithUTF8String:argv[1]];
        double offset = argc > 2 ? atof(argv[2]) : 0.0;
        NSURL *url = [NSURL fileURLWithPath:[path stringByStandardizingPath]];
        NSError *err = nil;
        globalPlayer = [[AVAudioPlayer alloc] initWithContentsOfURL:url error:&err];
        if (err || !globalPlayer) {
            return 1;
        }
        [globalPlayer prepareToPlay];
        if (offset > 0.0) {
            globalPlayer.currentTime = offset;
        }
        [globalPlayer play];
        while (globalPlayer.isPlaying) {
            [[NSRunLoop currentRunLoop] runUntilDate:[NSDate dateWithTimeIntervalSinceNow:0.05]];
        }
    }
    return 0;
}
"""
    try:
        p = subprocess.Popen(
            ["clang", "-O2", "-framework", "Foundation", "-framework", "AVFoundation", "-x", "objective-c", "-", "-o", AUDIO_PLAYER_BIN],
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        p.communicate(objc_src.encode('utf-8'))
        if p.returncode == 0 and os.path.exists(AUDIO_PLAYER_BIN):
            os.chmod(AUDIO_PLAYER_BIN, 0o755)
            return AUDIO_PLAYER_BIN
    except Exception:
        pass
    return None


def start_audio_playback(file_path, start_offset=0.0):
    """Start audio player in the background from exact start_offset."""
    global player_process
    system = platform.system()

    try:
        if system == "Darwin":
            native_player = ensure_macos_audio_player()
            if native_player:
                player_process = subprocess.Popen(
                    [native_player, file_path, str(float(start_offset))],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                return player_process

            if start_offset > 0.0:
                tmp_slice = f"/tmp/chal_wahan_slice_{int(start_offset)}.m4a"
                frame_offset = int(start_offset * 44100)
                cmd = ["afconvert", file_path, tmp_slice, "-d", "aac", "--offset", str(frame_offset)]
                subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
                file_path = tmp_slice

            player_process = subprocess.Popen(
                ["afplay", file_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        elif system == "Windows":
            ps_cmd = f'(New-Object System.Media.SoundPlayer "{file_path}").PlaySync()'
            player_process = subprocess.Popen(
                ["powershell", "-c", ps_cmd],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        else:
            if shutil.which("ffplay"):
                args = ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet"]
                if start_offset > 0.0:
                    args.extend(["-ss", str(start_offset)])
                args.append(file_path)
                player_process = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            elif shutil.which("mpv"):
                args = ["mpv", "--no-video"]
                if start_offset > 0.0:
                    args.extend([f"--start={start_offset}"])
                args.append(file_path)
                player_process = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            elif shutil.which("aplay"):
                player_process = subprocess.Popen(["aplay", file_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        print(f"{GRAY}[Warning: Audio player could not be launched ({e}). Continuing lyrics display...]{RESET}")

    return player_process


def parse_time(val):
    """Parse float seconds or MM:SS / HH:MM:SS string into seconds."""
    if val is None:
        return None
    val_str = str(val).strip()
    if ":" in val_str:
        parts = val_str.split(":")
        if len(parts) == 2:
            return float(parts[0]) * 60 + float(parts[1])
        elif len(parts) == 3:
            return float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
    return float(val_str)


def format_time(seconds):
    """Format seconds into MM:SS format."""
    m, s = divmod(max(0, int(seconds)), 60)
    return f"{m:02d}:{s:02d}"


def print_banner():
    """Print the track info header."""
    os.system("clear" if os.name != "nt" else "cls")
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()

    banner = f"""
{CORAL}{BOLD}💖✨ Chal Wahan Jaate Hain ✨💖{RESET}
{ROSE}{BOLD}Song:{RESET} {WHITE}Chal Wahan Jaate Hain (Seene Se Tum Mere){RESET}
{ROSE}{BOLD}Singer:{RESET} {GOLD}Arijit Singh{RESET}
{ROSE}{BOLD}Music:{RESET} {SUNSET}Amaal Mallik{RESET}
{ROSE}{BOLD}Lyrics:{RESET} {LAVENDER}Rashmi Virag{RESET}
{ROSE}{BOLD}Starring:{RESET} {CYAN}Tiger Shroff & Kriti Sanon{RESET}
{ROSE}{BOLD}Label:{RESET} {AQUA}T-Series{RESET}
{CORAL}{ITALIC}"Aasman ke pare ek jahan hai kahin... Pyar karne chalo..." 🕊️✨{RESET}
{CORAL}💖✨💖✨💖✨💖✨💖✨💖✨💖✨💖✨💖✨💖✨💖✨💖✨💖✨💖✨💖✨💖{RESET}
"""
    print(banner)


# --- EXACT AUDIO TIMELINE (MATCHED TO VOCAL ONSETS) ---
# Format: (timestamp, duration, text_en, text_hi, color, is_highlight)
LYRICS_TIMELINE = [
    # Intro Instrumental
    (0.0, 11.2,
     "🎶 [ Acoustic Guitar & Romantic Piano Intro ] 🎶",
     "🎶 [ गिटार और पियानो का मधुर संगीत ] 🎶",
     GRAY, False),

    # Verse 1: Initial Hook
    (11.2, 7.0,
     "Seene se tum mere aake lag jao na",
     "सीने से तुम मेरे आके लग जाओ ना",
     CORAL, False),

    (18.2, 7.2,
     "Darte ho kyun zaraa paas to aao na",
     "डरते हो क्यों ज़रा पास तो आओ ना",
     ROSE, False),

    # Musical Fill
    (25.4, 4.4,
     "🎸 [ Gentle Guitar Strums & Soft Beats ] 🎸",
     "🎸 [ मधुर गिटार और ताल ] 🎸",
     GRAY, False),

    # Verse 1 Reprise (Melodic Accent)
    (29.8, 7.2,
     "Hmm, seene se tum mere aake lag jao na",
     "हूँ.. सीने से तुम मेरे आके लग जाओ ना",
     GOLD, True),

    (37.0, 6.8,
     "Darte ho kyun zaraa paas to aao na",
     "डरते हो क्यों ज़रा पास तो आओ ना",
     SUNSET, True),

    (43.8, 6.0,
     "Dhun meri dhadkanon ki suno...",
     "धुन मेरी धड़कनों की सुनो...",
     MAGENTA, True),

    # Verse 2: The Dreamy World
    (49.8, 6.0,
     "Koyi subah wahan raat se na mile",
     "कोई सुबह वहां रात से ना मिले",
     SKY_BLUE, False),

    (55.8, 6.0,
     "Udke wahan chalo aao tum hum chalein",
     "उड़ के वहां चलो आओ तुम हम चलें",
     AQUA, False),

    (61.8, 6.0,
     "Hmm, koyi subah wahan raat se na mile",
     "हूँ.. कोई सुबह वहां रात से ना मिले",
     SKY_BLUE, True),

    (67.8, 6.0,
     "Udke wahan chalo aao tum hum chalein",
     "उड़ के वहां चलो आओ तुम हम चलें",
     AQUA, True),

    # Soulful Flute Solo Interlude
    (73.8, 7.0,
     "🎵 [ Soulful Flute Solo & Melodic Strings ] 🎵",
     "🎵 [ बांसुरी की मधुर तान और संगीत ] 🎵",
     GRAY, False),

    # Verse 3: Flying to Love
    (80.8, 5.8,
     "Koyi subah wahan raat se na mile",
     "कोई सुबह वहां रात से ना मिले",
     ORCHID, False),

    (86.6, 5.8,
     "Udke wahan chalo aao tum hum chalein",
     "उड़ के वहां चलो आओ तुम हम चलें",
     LAVENDER, False),

    (92.4, 7.0,
     "Pankh laya hoon main ud chalo...",
     "पंख लाया हूँ मैं उड़ चलो...",
     GOLD, True),

    # Climax Verse / Passionate Refrain
    (99.5, 6.8,
     "Seene se tum mere aake lag jao na",
     "सीने से तुम मेरे आके लग जाओ ना",
     CORAL, True),

    (106.3, 6.8,
     "Darte ho kyun zaraa paas to aao na",
     "डरते हो क्यों ज़रा पास तो आओ ना",
     ROSE, True),

    # Romantic Interlude
    (113.1, 4.0,
     "💖 [ Soft Acoustic Beats & Warm Chords ] 💖",
     "💖 [ धड़कन और संगीत का संगम ] 💖",
     GRAY, False),

    # Final Refrain
    (117.1, 7.0,
     "Hmm, seene se tum mere aake lag jao na",
     "हूँ.. सीने से तुम मेरे आके लग जाओ ना",
     GOLD, True),

    (124.1, 7.0,
     "Darte ho kyun zaraa paas to aao na",
     "डरते हो क्यों ज़रा पास तो आओ ना",
     SUNSET, True),

    (131.1, 7.5,
     "Dhun meri dhadkanon ki suno...",
     "धुन मेरी धड़कनों की सुनो...",
     MAGENTA, True),

    # Outro Fade Out
    (138.6, 28.4,
     "🕊️ [ Outro - Soulful Vocalizing & Gentle Fade Out ] 🕊️",
     "🕊️ [ आलाप और संगीत का सुरीला समापन ] 🕊️",
     GRAY, False),
]


def play():
    """Main execution loop for song playback and synchronized dual Hindi/English lyrics display."""
    import argparse
    parser = argparse.ArgumentParser(description="Chal Wahan Jaate Hain - Synchronized Lyrics & Audio Player")
    parser.add_argument("--auto", action="store_true", help="Start automatically without waiting for Enter")
    parser.add_argument("--start", type=str, default="0", help="Start playback at specific second offset or MM:SS (e.g. 11 or 00:11)")
    parser.add_argument("--end", type=str, default=None, help="Stop playback at specific second offset or MM:SS (e.g. 60 or 01:00)")
    parser.add_argument("--duration", type=str, default=None, help="Duration to play in seconds or MM:SS (e.g. 45 or 00:45)")
    parser.add_argument("--mode", type=str, choices=["both", "en", "hi"], default="both",
                        help="Lyrics language mode: 'both' (English + Hindi), 'en' (English/Roman only), 'hi' (Hindi only)")
    parser.add_argument("--preview", action="store_true", help="Fast preview mode (no waiting, display test)")
    args = parser.parse_args()

    audio_path = ensure_audio_file()
    print_banner()

    start_raw = parse_time(args.start) or 0.0
    start_offset = max(0.0, min(float(start_raw), float(TOTAL_DURATION - 2)))

    end_raw = parse_time(args.end)
    if args.duration is not None:
        dur_val = parse_time(args.duration)
        if dur_val is not None:
            end_raw = start_offset + dur_val

    if end_raw is not None:
        effective_end = max(start_offset + 1.0, min(float(end_raw), float(TOTAL_DURATION)))
    else:
        effective_end = float(TOTAL_DURATION)

    mode_labels = {
        "both": "English (Romanized) + Hindi (Devanagari)",
        "en": "English / Romanized Hindi",
        "hi": "Hindi (हिंदी)"
    }
    print(f" {GRAY}Language Mode:{RESET} {GOLD}{mode_labels[args.mode]}{RESET}\n")

    if not args.auto and not args.preview and start_offset == 0.0:
        try:
            input(f"{CORAL}▶  Press [ENTER] to play the song with synchronized lyrics... {RESET}")
        except EOFError:
            pass
    print()

    # Launch audio player with exact start_offset
    if not args.preview:
        start_audio_playback(audio_path, start_offset=start_offset)

    # Reference clock locked to audio playback position
    start_time = time.time() - start_offset

    idx = 0
    total_lines = len(LYRICS_TIMELINE)

    # Fast-forward to current start offset
    while idx < total_lines and LYRICS_TIMELINE[idx][0] + 1.0 <= start_offset:
        idx += 1

    try:
        while idx < total_lines:
            target_time, duration, text_en, text_hi, color, is_hl = LYRICS_TIMELINE[idx]
            elapsed = time.time() - start_time

            # Check if playback reached the user-requested end time
            if not args.preview and elapsed >= effective_end:
                break
            if target_time >= effective_end:
                break

            # If before target time, wait smoothly while updating clock
            if not args.preview and elapsed < target_time:
                wait_time = min(target_time - elapsed, 0.03)
                if elapsed + wait_time > effective_end:
                    time.sleep(max(0, effective_end - elapsed))
                    break
                time.sleep(wait_time)
                continue

            # Target timestamp arrived! Display header time & progress bar
            curr_val = elapsed if not args.preview else target_time
            curr_str = format_time(curr_val)
            tot_str = format_time(TOTAL_DURATION)
            pct = min(100, int((curr_val / TOTAL_DURATION) * 100))

            bar_len = 25
            filled = int((pct / 100) * bar_len)
            bar = "━" * filled + "●" + "─" * (bar_len - filled)

            bullet = "💖 " if is_hl else "✦ "
            sys.stdout.write(f"\r{GRAY}[{curr_str} / {tot_str}] {CORAL}{bar}{RESET} {DIM}{pct}%{RESET}\n")
            sys.stdout.flush()

            # Smooth Synchronized Typewriter Animation
            if args.preview:
                # Fast render for preview mode
                if args.mode in ("both", "en"):
                    sys.stdout.write(f"   {color}{BOLD if is_hl else ''}{bullet}{text_en}{RESET}\n")
                if args.mode in ("both", "hi"):
                    sub_indent = "     " if is_hl else "    "
                    hi_color = SUNSET if color == GOLD else (LAVENDER if color == MAGENTA else ROSE)
                    sys.stdout.write(f"   {hi_color}{sub_indent}{text_hi}{RESET}\n")
                sys.stdout.write("\n")
                sys.stdout.flush()
                time.sleep(0.05)
            else:
                line_start_clk = target_time
                type_duration = max(0.4, duration * 0.70)

                # English Line
                if args.mode in ("both", "en"):
                    sys.stdout.write(f"   {color}{BOLD if is_hl else ''}{bullet}")
                    sys.stdout.flush()

                    chars_en = list(text_en)
                    n_en = len(chars_en)
                    printed_idx = 0

                    # If mode is both, allocate ~50% of type duration to EN, 50% to HI
                    en_duration = (type_duration * 0.55) if args.mode == "both" else type_duration

                    while printed_idx < n_en:
                        curr_elapsed = time.time() - start_time
                        if curr_elapsed >= effective_end:
                            break
                        time_into = curr_elapsed - line_start_clk
                        frac = min(1.0, max(0.0, time_into / max(0.1, en_duration)))
                        target_chars = int(frac * n_en)

                        while printed_idx < target_chars and printed_idx < n_en:
                            sys.stdout.write(chars_en[printed_idx])
                            printed_idx += 1
                            sys.stdout.flush()

                        if printed_idx >= n_en:
                            break
                        time.sleep(0.02)

                    sys.stdout.write(RESET + "\n")
                    sys.stdout.flush()

                # Hindi Line
                if args.mode in ("both", "hi"):
                    sub_indent = "     " if (is_hl and args.mode == "both") else ("    " if args.mode == "both" else f"{bullet}")
                    hi_color = SUNSET if color == GOLD else (LAVENDER if color == MAGENTA else ROSE)

                    sys.stdout.write(f"   {hi_color}{sub_indent}")
                    sys.stdout.flush()

                    chars_hi = list(text_hi)
                    n_hi = len(chars_hi)
                    printed_idx = 0

                    hi_start_clk = (line_start_clk + type_duration * 0.45) if args.mode == "both" else line_start_clk
                    hi_duration = (type_duration * 0.55) if args.mode == "both" else type_duration

                    while printed_idx < n_hi:
                        curr_elapsed = time.time() - start_time
                        if curr_elapsed >= effective_end:
                            break
                        time_into = curr_elapsed - hi_start_clk
                        frac = min(1.0, max(0.0, time_into / max(0.1, hi_duration)))
                        target_chars = int(frac * n_hi)

                        while printed_idx < target_chars and printed_idx < n_hi:
                            sys.stdout.write(chars_hi[printed_idx])
                            printed_idx += 1
                            sys.stdout.flush()

                        if printed_idx >= n_hi:
                            break
                        time.sleep(0.02)

                    sys.stdout.write(RESET + "\n")
                    sys.stdout.flush()

                # Blank line between stanzas for readability
                sys.stdout.write("\n")
                sys.stdout.flush()

                if time.time() - start_time >= effective_end:
                    break

            idx += 1

        if not args.preview:
            # Wait for remaining audio to conclude up to effective_end
            while time.time() - start_time < effective_end:
                elapsed = time.time() - start_time
                curr_str = format_time(elapsed)
                tot_str = format_time(TOTAL_DURATION)
                pct = min(100, int((elapsed / TOTAL_DURATION) * 100))
                bar_len = 25
                filled = int((pct / 100) * bar_len)
                bar = "━" * filled + "●" + "─" * (bar_len - filled)
                sys.stdout.write(f"\r\033[K{GRAY}[{curr_str} / {tot_str}] {CORAL}{bar}{RESET} {DIM}{pct}%{RESET}")
                sys.stdout.flush()
                time.sleep(0.15)
            sys.stdout.write("\n")
            sys.stdout.flush()

        # Stop audio if process is still running
        if player_process:
            try:
                player_process.terminate()
                player_process.wait(timeout=0.5)
            except Exception:
                try:
                    player_process.kill()
                except Exception:
                    pass

        if end_raw is not None and effective_end < TOTAL_DURATION:
            print("\n\n" + CORAL + f"✨ Reached end time [{format_time(effective_end)}]. Playback finished! 💖 ✨" + RESET + "\n")
        else:
            print("\n\n" + CORAL + "✨ Song Finished! Thank you for listening! 💖🕊️ ✨" + RESET + "\n")

    except KeyboardInterrupt:
        cleanup()
    finally:
        sys.stdout.write("\033[?25h\n")
        sys.stdout.flush()


if __name__ == "__main__":
    play()

