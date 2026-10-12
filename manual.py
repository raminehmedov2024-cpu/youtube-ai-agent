import re


def split_scenes(text):
    """Mətni boş sətirlərə görə səhnələrə bölür."""
    scenes = [
        s.strip()
        for s in re.split(r"\n\s*\n", text)
        if s.strip()
    ]

    return scenes


def get_keywords(niche, scenes):
    """Hər səhnə üçün video axtarış açar sözü yaradır."""
    base = niche.strip()

    return [
        f"{base} {scene[:80]}"
        for scene in scenes
    ]