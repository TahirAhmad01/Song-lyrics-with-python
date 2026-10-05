#!/usr/bin/env python3
"""
KHAMOSHIYAN (Title Track) - Lyrics & Audio Player
Singer: Arijit Singh
Music: Jeet Gannguli
Lyrics: Rashmi Singh
Movie: Khamoshiyan (2015)
YouTube: https://www.youtube.com/watch?v=Mv3SZDP7QUo
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

# Aesthetic Color Palette (Moody Romance & Diamond Ice)
CYAN = "\033[38;5;51m"
AQUA = "\033[38;5;44m"
ICE_BLUE = "\033[38;5;159m"
SKY_BLUE = "\033[38;5;117m"
LAVENDER = "\033[38;5;141m"
PURPLE = "\033[38;5;135m"
GOLD = "\033[38;5;220m"
ROSE = "\033[38;5;211m"
EMERALD = "\033[38;5;48m"
WHITE = "\033[38;5;255m"
GRAY = "\033[38;5;242m"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIO_FILE = os.path.join(BASE_DIR, "song.m4a")
AUDIO_PLAYER_BIN = os.path.join(BASE_DIR, "audio_player")
YOUTUBE_URL = "https://www.youtube.com/watch?v=Mv3SZDP7QUo"
TOTAL_DURATION = 196  # ~ 3:16

# Audio player process reference for clean exit
player_process = None


def cleanup(sig=None, frame=None):
    """Gracefully terminate audio player and restore terminal."""
    global player_process
    print("\n\n" + RESET + CYAN + "Stopping music playback... Khamoshiyan... 💙" + RESET)
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

    print(f"{CYAN}⬇️  Downloading song audio from YouTube...{RESET}")
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

    print(f"{ICE_BLUE}✓ Audio downloaded successfully!{RESET}\n")
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
                tmp_slice = f"/tmp/khamoshiyan_slice_{int(start_offset)}.m4a"
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
{CYAN}{BOLD}❄️✨ Khamoshiyan (Title Track) ✨❄️{RESET}
{AQUA}{BOLD}Song:{RESET} {WHITE}Khamoshiyan{RESET}
{AQUA}{BOLD}Singer:{RESET} {GOLD}Arijit Singh{RESET}
{AQUA}{BOLD}Music:{RESET} {ICE_BLUE}Jeet Gannguli{RESET}
{AQUA}{BOLD}Lyrics:{RESET} {ROSE}Rashmi Singh{RESET}
{AQUA}{BOLD}Movie:{RESET} {LAVENDER}Khamoshiyan (2015){RESET}
{AQUA}{BOLD}Label:{RESET} {SKY_BLUE}Sony Music Entertainment India{RESET}
{ICE_BLUE}Sit back and let the silence speak... 💙{RESET}
{CYAN}❄️💎❄️💎❄️💎❄️💎❄️💎❄️💎❄️💎❄️💎❄️💎❄️💎❄️💎❄️💎❄️💎❄️💎❄️💎❄️{RESET}
"""
    print(banner)


# --- EXACT AUDIO TIMELINE (MATCHED TO VOCAL ONSETS) ---
# Format: (timestamp, duration, text, color, is_highlight)
LYRICS_TIMELINE = [
    # Acoustic Intro
    (0.0, 8.5, "🎶 [ Acoustic Guitar & Ambient Piano Intro ] 🎶", GRAY, False),

    # Verse 1
    (8.8, 5.2, "Khamoshiyan aawaaz hain", ICE_BLUE, False),
    (14.2, 5.0, "Tum sunne toh aao kabhi", ICE_BLUE, False),
    (19.4, 5.2, "Chhoo kar tumhein khil jaayengi", LAVENDER, False),
    (24.8, 5.0, "Ghar inko bulaao kabhi", LAVENDER, False),

    # Pre-Chorus 1
    (30.0, 5.0, "Beqaraar hain baat karne ko", ROSE, False),
    (35.2, 5.5, "Kehne do inko zara...", ROSE, True),
    (40.2, 1.0, "❄️💙❄️", CYAN, True),

    # Chorus 1
    (41.2, 4.8, "Khamoshiyan...", GOLD, True),
    (46.0, 5.2, "Teri meri khamoshiyan", GOLD, True),
    (51.4, 4.8, "Khamoshiyan...", AQUA, True),
    (56.4, 5.8, "Lipti hui khamoshiyan", AQUA, True),
    (62.5, 2.5, "💎❄️💎", ICE_BLUE, True),

    # Instrumental Interlude
    (65.0, 16.5, "🎵 [ Instrumental Interlude - Flute & Violin Solo ] 🎵", GRAY, False),

    # Verse 2
    (82.2, 8.5, "Kya uss gali mein kabhi tera jaana hua", WHITE, False),
    (91.0, 8.2, "Jahan se zamane ko guzre zamana hua?", WHITE, False),
    (99.5, 7.8, "Mera samay toh wahin pe hai thehra hua", ICE_BLUE, False),
    (107.5, 8.5, "Bataun tumhein kya, mere saath kya kya hua", ICE_BLUE, False),

    (116.5, 5.8, "Mmm, khamoshiyan ek saaz hai", LAVENDER, False),
    (122.5, 5.8, "Tum dhun koi laao zara", LAVENDER, False),
    (128.5, 5.8, "Khamoshiyan alfaaz hain", CYAN, False),
    (134.5, 5.5, "Kabhi aa, gunguna le zara", CYAN, False),

    # Pre-Chorus 2
    (140.2, 5.0, "Beqaraar hain baat karne ko", ROSE, False),
    (145.4, 5.6, "Kehne do inko zara, haan haan", ROSE, True),
    (150.5, 1.0, "❄️💙❄️", CYAN, True),

    # Chorus 2
    (151.4, 4.8, "Khamoshiyan...", GOLD, True),
    (156.2, 5.0, "Teri meri khamoshiyan", GOLD, True),
    (161.4, 4.8, "Khamoshiyan...", AQUA, True),
    (166.4, 5.0, "Lipti hui khamoshiyan", AQUA, True),

    # Final Refrain
    (171.5, 4.8, "Khamoshiyan...", GOLD, True),
    (176.4, 4.8, "Teri meri khamoshiyan", GOLD, True),
    (181.4, 4.8, "Khamoshiyan...", AQUA, True),
    (186.4, 6.2, "Lipti hui khamoshiyan...", AQUA, True),

    # Outro
    (192.8, 3.4, "🎶 [ Melodic Guitar & Piano Fade Out ] 🎶", GRAY, False),
]


def play():
    """Main execution loop for song playback and synchronized lyrics display."""
    import argparse
    parser = argparse.ArgumentParser(description="Khamoshiyan Lyrics Player")
    parser.add_argument("--auto", action="store_true", help="Start automatically without waiting for Enter")
    parser.add_argument("--start", type=float, default=0.0, help="Start playback at specific second offset")
    parser.add_argument("--preview", action="store_true", help="Fast preview mode (no waiting, display test)")
    args = parser.parse_args()

    audio_path = ensure_audio_file()
    print_banner()

    start_offset = max(0.0, min(float(args.start), float(TOTAL_DURATION - 2)))

    if not args.auto and not args.preview and start_offset == 0.0:
        try:
            input(f"{CYAN}▶  Press [ENTER] to play the song with synchronized lyrics... {RESET}")
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

    # Fast-forward to current start offset
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

            sys.stdout.write(f"\r{GRAY}[{curr_str} / {tot_str}] {CYAN}{bar}{RESET} {DIM}{pct}%{RESET}\n")
            sys.stdout.flush()

            # Smooth Clock-Synced Typewriter Effect:
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
                sys.stdout.write(f"\r{GRAY}[{curr_str} / {tot_str}] {CYAN}{bar}{RESET} {DIM}{pct}%{RESET}   ")
                sys.stdout.flush()
                time.sleep(0.5)

        print("\n\n" + CYAN + "✨ Song Finished! Thank you for listening! 💙 ✨" + RESET + "\n")

    except KeyboardInterrupt:
        cleanup()
    finally:
        sys.stdout.write("\033[?25h\n")
        sys.stdout.flush()


if __name__ == "__main__":
    play()
