import subprocess
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

def make_thumbnail(video_path, title, out_path="output/thumbnail.jpg"):
    # Videodan 1-ci saniyənin kadrını götür
    frame = "temp/frame.jpg"
    subprocess.run(
        ["ffmpeg", "-y", "-ss", "1", "-i", video_path, "-frames:v", "1", frame],
        check=True,
    )

    img = Image.open(frame).convert("RGB").resize((1280, 720))
    img = ImageEnhance.Brightness(img).enhance(0.5)  # yazı oxunsun deyə qaralt
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 90)

    # Uzun başlığı sətirlərə böl
    lines, line = [], ""
    for word in title.split():
        test = (line + " " + word).strip()
        if draw.textlength(test, font=font) <= 1100:
            line = test
        else:
            lines.append(line)
            line = word
    lines.append(line)

    y = (720 - len(lines) * 110) // 2
    for text in lines:
        x = (1280 - draw.textlength(text, font=font)) // 2
        draw.text((x, y), text, font=font, fill="white",
                  stroke_width=6, stroke_fill="black")
        y += 110

    img.save(out_path, quality=95)
    return out_path

if __name__ == "__main__":
    out = make_thumbnail("output/final.mp4", "Niyə göy mavidir?")
    print("Hazir:", out)