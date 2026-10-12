import subprocess

# Bunları panel dəyişir
WIDTH, HEIGHT = 1920, 1080
EFFECT_VF = ""
STYLE = (
    "FontName=Arial,FontSize=16,Bold=1,PrimaryColour=&H00FFFFFF,"
    "OutlineColour=&H00000000,BorderStyle=1,Outline=2,Shadow=0,"
    "Alignment=2,MarginV=50"
)


def make_video(video_path, audio_path, out_path, srt_path=None):
    vf = (
        f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=increase,"
        f"crop={WIDTH}:{HEIGHT}"
    )
    if EFFECT_VF:
        vf += "," + EFFECT_VF
    if srt_path:
        vf += f",subtitles={srt_path}:force_style='{STYLE}'"

    cmd = [
        "ffmpeg", "-y",
        "-stream_loop", "-1", "-i", video_path,
        "-i", audio_path,
        "-map", "0:v:0", "-map", "1:a:0",
        "-vf", vf,
        "-c:v", "libx264", "-preset", "fast", "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-shortest",
        out_path,
    ]
    subprocess.run(cmd, check=True)
    return out_path


if __name__ == "__main__":
    out = make_video("data/video/test.mp4", "data/audio/test.mp3", "output/test_video.mp4")
    print("Hazir:", out)