
import asyncio
from pathlib import Path
import edge_tts

RATE = "+0%"

VOICES = {
    "🇦🇿 Azərbaycan — Babək": "az-AZ-BabekNeural",
    "🇦🇿 Azərbaycan — Banu": "az-AZ-BanuNeural",
    "🇹🇷 Türk — Ahmet": "tr-TR-AhmetNeural",
    "🇹🇷 Türk — Emel": "tr-TR-EmelNeural",
    "🇬🇧 English — Guy": "en-US-GuyNeural",
    "🇬🇧 English — Jenny": "en-US-JennyNeural",
    "🇺🇸 English — Christopher": "en-US-ChristopherNeural",
}


async def make_voice(text, path, voice="az-AZ-BabekNeural", rate="+0%"):
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    communicate = edge_tts.Communicate(
        text,
        voice,
        rate=rate
    )

    await communicate.save(str(output_path))


def generate_voice(text, path, voice="az-AZ-BabekNeural", rate="+0%"):
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(make_voice(text, path, voice, rate))

    raise RuntimeError(
        "Artıq işləyən async event loop var. "
        "generate_voice funksiyasını sinxron rejimdə çağırmaq olmaz."
    )


if __name__ == "__main__":
    text = "Salam! Bu, YouTube agentimin ilk səsidir."

    generate_voice(
        text,
        "data/audio/test.mp3",
        "az-AZ-BabekNeural",
        "+0%"
    )

    print("Səs hazırdır: data/audio/test.mp3")