#!/usr/bin/env python3
"""
JAAN E JAHAN (OST) - Lyrics & Audio Player
Singer: Rahat Fateh Ali Khan
Lyrics: Qamar Nashad
Music: Naveed Nashad
YouTube: https://www.youtube.com/watch?v=KQzmQ02hHFI
"""

import os
import sys
import time
import signal
import platform
import subprocess
import shutil

# --- Color & Style Constants ---
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
ITALIC = "\033[3m"

# Beautiful Palette
EMERALD = "\033[38;5;48m"
LIGHT_GREEN = "\033[38;5;120m"
CYAN = "\033[38;5;51m"
AQUA = "\033[38;5;44m"
GOLD = "\033[38;5;220m"
ROSE = "\033[38;5;211m"
WHITE = "\033[38;5;255m"
GRAY = "\033[38;5;242m"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIO_FILE = os.path.join(BASE_DIR, "song.m4a")
AUDIO_PLAYER_BIN = os.path.join(BASE_DIR, "audio_player")
YOUTUBE_URL = "https://www.youtube.com/watch?v=KQzmQ02hHFI"
TOTAL_DURATION = 331  # ~ 5:31

# Audio player process reference for clean exit
player_process = None


def cleanup(sig=None, frame=None):
    """Gracefully terminate audio player and restore terminal."""
    global player_process
    print("\n\n" + RESET + EMERALD + "Stopping music playback... Goodbye! 💚" + RESET)
    if player_process:
        try:
            player_process.terminate()
            player_process.wait(timeout=1)
        except Exception:
            try:
                player_process.kill()
            except Exception:
                pass
    # Show cursor
    sys.stdout.write("\033[?25h\n")
    sys.stdout.flush()
    sys.exit(0)


signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGTERM, cleanup)


def ensure_audio_file():
    """Check if song.m4a exists, otherwise download it via yt-dlp."""
    if os.path.exists(AUDIO_FILE) and os.path.getsize(AUDIO_FILE) > 100000:
        return AUDIO_FILE

    print(f"{EMERALD}⬇️  Downloading song audio from YouTube...{RESET}")
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

    print(f"{LIGHT_GREEN}✓ Audio downloaded successfully!{RESET}\n")
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
            # Preferred: Native AVFoundation player (supports exact seek)
            native_player = ensure_macos_audio_player()
            if native_player:
                player_process = subprocess.Popen(
                    [native_player, file_path, str(float(start_offset))],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                return player_process

            # Fallback for Darwin: afconvert slice if start_offset > 0
            if start_offset > 0.0:
                tmp_slice = f"/tmp/song_slice_{int(start_offset)}.m4a"
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
            # Windows PowerShell playback
            ps_cmd = f'(New-Object System.Media.SoundPlayer "{file_path}").PlaySync()'
            player_process = subprocess.Popen(
                ["powershell", "-c", ps_cmd],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        else:
            # Linux players with seek support
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


def format_time(seconds):
    """Format seconds into MM:SS format."""
    m, s = divmod(max(0, int(seconds)), 60)
    return f"{m:02d}:{s:02d}"


def print_banner():
    """Print the track info header."""
    os.system("clear" if os.name != "nt" else "cls")
    # Hide cursor
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()

    banner = f"""
{EMERALD}{BOLD}💚Uploaded By @M__U__N💚{RESET}
{CYAN}{BOLD}Song:{RESET} {WHITE}Jaan E Jahan Ost{RESET}
{CYAN}{BOLD}Singer:{RESET} {GOLD}Rahat Fateh Ali Khan{RESET}
{CYAN}{BOLD}Lyrics:{RESET} {ROSE}Qamar Nashad{RESET}
{CYAN}{BOLD}Music:{RESET} {AQUA}Naveed Nashad{RESET}
{LIGHT_GREEN}Thanks for your LOVE&SUPPORT🙏{RESET}
{EMERALD}💚💎💚💎💚💎💚💎💚💎💚💎💚💎💚💎💚💎💚💎💚💎💚💎💚💎💚💎💚💎💚{RESET}
"""
    print(banner)


# --- EXACT AUDIO TIMELINE (VERIFIED DOWN TO VOCAL ONSETS) ---
# Format: (timestamp, duration, text, color, is_highlight)
LYRICS_TIMELINE = [
    # Intro Music
    (0.0, 13.0, "🎶 [ Instrumental Intro - Flute & Strings ] 🎶", GRAY, False),

    # Section 1: Opening Verses
    (13.5, 4.2, "Is Pyaar Mein, Jo Jal Gaya", LIGHT_GREEN, False),
    (18.0, 4.2, "Samjho Khuda, Use Mil Gaya", LIGHT_GREEN, False),
    (22.5, 4.2, "Tere Zikr Mein Mera Zikr Ho", AQUA, False),
    (27.0, 4.5, "Phir Haathon Se, Ye Dil Gayaa", AQUA, False),
    (32.0, 6.5, "💚💎💚", EMERALD, True),

    # Chorus / Hook 1
    (39.0, 4.0, "Tera Ishq Jooo,", GOLD, True),
    (43.5, 6.0, "Tariiii Huaaaaaa", GOLD, True),
    (50.0, 4.2, "Banke Lahuuuuuu", ROSE, True),
    (54.5, 5.2, "Jariii Huaaaaaa", ROSE, True),

    (60.0, 4.2, "Ragon Mein Daudeeee", CYAN, False),
    (64.5, 4.2, "Junoon Bankar", CYAN, False),
    (69.0, 5.0, "Tu Saath Rehnaaaa aa", LIGHT_GREEN, False),
    (74.5, 5.5, "Sukoon Bankarrr", LIGHT_GREEN, False),
    (80.5, 4.0, "Tera Ishq Joooooo", GOLD, True),
    (84.8, 5.5, "Taaari Huaaaaa", GOLD, True),
    (90.5, 6.0, "💚💎💚", EMERALD, True),

    # Interlude
    (91.5, 5.0, "🎵 [ Interlude Melodic Rhythm ] 🎵", GRAY, False),

    # Verse 1
    (97.0, 4.0, "Tanha Tanha Kyun Marna hai", WHITE, False),
    (101.2, 3.5, "Aaj ji Le Zaraaa", WHITE, False),
    (104.8, 3.8, "Ishq Laazim Tab Hota", AQUA, False),
    (109.0, 4.5, "Raazi Ho Khuda", AQUA, False),

    (114.0, 3.8, "Mere Dil Ka Tere Dil Se", ROSE, False),
    (118.0, 3.8, "Mere Dil Ka Tere Dil Se", ROSE, False),
    (122.0, 3.8, "Aisa Raabtaaaa", ROSE, True),
    (126.0, 3.8, "Toote Dil Ki Tu Hi Tamannaaa", LIGHT_GREEN, False),
    (130.0, 3.8, "Toote Dil Ki Tu Hi Tamannaaa", LIGHT_GREEN, False),
    (134.0, 3.8, "Tu Hi Aasraaaa", LIGHT_GREEN, True),
    (137.5, 1.0, "💚💎💚", EMERALD, True),

    # Verse 2
    (138.0, 4.2, "Tu Hi Meri, Pehli Tamanna", CYAN, False),
    (142.5, 4.2, "Tu Hi Aakhri Chahat Hai", CYAN, False),
    (147.0, 4.8, "Ishq Ye Mera, Paak Hai Itna", WHITE, False),
    (152.0, 4.8, "Jaise Koi Aayat Hai", WHITE, False),

    (157.0, 5.5, "Tujhko Mere, Saath Hai Rehnaaa", LIGHT_GREEN, False),
    (163.0, 4.8, "Tujhko Mere, Saath Hai Rehna", LIGHT_GREEN, False),
    (168.0, 6.2, "Jaise Rehti Aadat Haiii", LIGHT_GREEN, True),

    # Chorus 2
    (174.5, 4.5, "Tera Ishq Joooo,", GOLD, True),
    (179.5, 5.2, "Taari Huaaaaa", GOLD, True),
    (185.0, 4.5, "Banke Lahuuuuuu,", ROSE, True),
    (190.0, 8.0, "Jariii Huaaaaaa", ROSE, True),
    (198.5, 1.5, "💎💚💎", EMERALD, True),

    # Interlude / Credits Section
    (200.0, 8.0, "🎵 [ Instrumental Interlude - Sarangi & Strings ] 🎵", GRAY, False),
    (210.0, 6.0, "Singer: Rahat Fateh Ali Khan", GOLD, False),
    (217.0, 6.0, "Lyrics: Qamar Nashad", ROSE, False),
    (224.0, 6.0, "Composer: Naveed Nashad", AQUA, False),
    (231.0, 7.5, "💎💚💎", EMERALD, True),

    # Verse 3 / Emotion Section
    (239.0, 5.2, "Ek Main Hoon Yaad Hai Teri", WHITE, False),
    (244.5, 4.8, "Aur Alam-e-Tanhaai", WHITE, False),
    (249.5, 4.8, "Dard Diye Hai Itne Tune", ROSE, False),
    (254.5, 5.2, "Jaan Labon Tak Aayi", ROSE, True),

    (260.0, 4.8, "Waqt Thehar Ja, Bas Do Pal Kooo", CYAN, False),
    (265.0, 4.8, "Waqt Thehar Ja, Bas Do Pal Ko", CYAN, False),
    (270.0, 5.2, "Woh Milne Ko Aayi", LIGHT_GREEN, True),

    # Final Chorus
    (275.5, 3.8, "Tera Ishq Jooooo,", GOLD, True),
    (279.5, 5.5, "Tari Huaaaaaa", GOLD, True),
    (285.5, 4.2, "Bankeee Lahuuuuuuu", ROSE, True),
    (290.0, 12.0, "Jariii Huaaaaaaaaa", ROSE, True),

    # Outro
    (303.0, 1.5, "💚💎💚💎💚💎💚💎💚💎", EMERALD, True),
    (305.0, 5.0, "If you like track give👍", GOLD, True),
    (310.5, 6.0, "Thank You For Watching 💚💚💚", LIGHT_GREEN, True),
    (317.0, 14.0, "🎶 [ Outro Music & Melodic Fade ] 🎶", GRAY, False),
]


def play():
    """Main execution loop for song playback and synchronized lyrics display."""
    import argparse
    parser = argparse.ArgumentParser(description="Jaan E Jahan OST Lyrics Player")
    parser.add_argument("--auto", action="store_true", help="Start automatically without waiting for Enter")
    parser.add_argument("--start", type=float, default=0.0, help="Start playback at specific second offset")
    parser.add_argument("--preview", action="store_true", help="Fast preview mode (no waiting, display test)")
    args = parser.parse_args()

    audio_path = ensure_audio_file()
    print_banner()

    start_offset = max(0.0, min(float(args.start), float(TOTAL_DURATION - 2)))

    if not args.auto and not args.preview and start_offset == 0.0:
        try:
            input(f"{AQUA}▶  Press [ENTER] to play the song with synchronized lyrics... {RESET}")
        except EOFError:
            pass
    print()

    # Launch audio player with exact start_offset
    if not args.preview:
        start_audio_playback(audio_path, start_offset=start_offset)

    # Reference start clock locked to audio playback position
    start_time = time.time() - start_offset

    idx = 0
    total_lines = len(LYRICS_TIMELINE)

    # Fast-forward to the current start offset
    while idx < total_lines and LYRICS_TIMELINE[idx][0] + LYRICS_TIMELINE[idx][1] <= start_offset:
        idx += 1

    try:
        while idx < total_lines:
            target_time, duration, text, color, is_hl = LYRICS_TIMELINE[idx]
            elapsed = time.time() - start_time

            # If before target time, update the top clock and sleep briefly
            if not args.preview and elapsed < target_time:
                time.sleep(min(target_time - elapsed, 0.03))
                continue

            # Target timestamp arrived! Display header time
            curr_str = format_time(elapsed if not args.preview else target_time)
            tot_str = format_time(TOTAL_DURATION)
            pct = min(100, int(((elapsed if not args.preview else target_time) / TOTAL_DURATION) * 100))

            bar_len = 25
            filled = int((pct / 100) * bar_len)
            bar = "━" * filled + "●" + "─" * (bar_len - filled)

            sys.stdout.write(f"\r{GRAY}[{curr_str} / {tot_str}] {EMERALD}{bar}{RESET} {DIM}{pct}%{RESET}\n")
            sys.stdout.flush()

            # Smooth Clock-Synced Typewriter Effect:
            # We progress strictly by wall-clock time so that NO CLOCK DRIFT occurs!
            prefix = "   "
            sys.stdout.write(prefix + color + (BOLD if is_hl else ""))
            sys.stdout.flush()

            chars = list(text)
            n_chars = len(chars)

            if args.preview:
                # Fast render
                sys.stdout.write("".join(chars) + RESET + "\n")
                sys.stdout.flush()
                time.sleep(0.04)
            else:
                line_start_clk = target_time
                type_duration = max(0.4, duration * 0.70)
                printed_idx = 0

                while printed_idx < n_chars:
                    curr_elapsed = time.time() - start_time
                    time_into_line = curr_elapsed - line_start_clk
                    progress_frac = min(1.0, max(0.0, time_into_line / type_duration))
                    target_chars = int(progress_frac * n_chars)

                    # Print any newly reached characters
                    while printed_idx < target_chars and printed_idx < n_chars:
                        sys.stdout.write(chars[printed_idx])
                        printed_idx += 1
                        sys.stdout.flush()

                    if printed_idx >= n_chars:
                        break

                    time.sleep(0.02)

                sys.stdout.write(RESET + "\n")
                sys.stdout.flush()

            idx += 1

        if not args.preview:
            # Wait for remaining audio to conclude
            while time.time() - start_time < TOTAL_DURATION:
                elapsed = time.time() - start_time
                curr_str = format_time(elapsed)
                tot_str = format_time(TOTAL_DURATION)
                pct = min(100, int((elapsed / TOTAL_DURATION) * 100))
                bar_len = 25
                filled = int((pct / 100) * bar_len)
                bar = "━" * filled + "●" + "─" * (bar_len - filled)
                sys.stdout.write(f"\r{GRAY}[{curr_str} / {tot_str}] {EMERALD}{bar}{RESET} {DIM}{pct}%{RESET}   ")
                sys.stdout.flush()
                time.sleep(0.5)

        print("\n\n" + EMERALD + "✨ Song Finished! Thank you for listening! ✨" + RESET + "\n")

    except KeyboardInterrupt:
        cleanup()
    finally:
        sys.stdout.write("\033[?25h\n")
        sys.stdout.flush()


if __name__ == "__main__":
    play()
