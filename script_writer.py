import json
from dotenv import load_dotenv
import anthropic

load_dotenv()
client = anthropic.Anthropic()


def write_script(topic, niche, language="Azerbaijani"):
    prompt = f"""Sən peşəkar YouTube ssenaristisən. Nişa: {niche}.
Mövzu: {topic}

{language} dilində təxminən 60-90 saniyəlik video ssenarisi yaz.
Qaydalar:
- İlk 3 saniyədə izləyicini tutan hook olsun
- Dəqiq, yoxlanılmış faktlar yaz, uydurma
- Təbii, danışıq dili
- Sonda izləyiciyə sual ver
- 6-8 səhnə olsun, hər səhnədə 1-2 qısa cümlə
- Hər səhnə üçün 3 FƏRQLİ vizual açar söz yaz (ingilis dilində, 1-3 söz).
  Açar sözlər stok videoda real görünə bilən konkret şeylər olsun,
  məsələn "ocean waves", "night city traffic", "microscope lab".
  Mücərrəd söz yazma (məsələn "success", "knowledge").

YALNIZ JSON qaytar, başqa heç nə yazma:
{{"title": "...", "description": "...", "tags": ["..."],
  "scenes": [{{"narration": "...", "search_keywords": ["shot one", "shot two", "shot three"]}}]}}"""

    resp = client.messages.create(
        model="claude-sonnet-5-5",
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}],
    )
    text = "".join(b.text for b in resp.content if b.type == "text").strip()
    text = text.replace("```json", "").replace("```", "")
    data = json.loads(text)

    # pipeline üçün: açar sözləri " | " ilə birləşdir
    for s in data.get("scenes", []):
        kws = s.get("search_keywords") or [s.get("search_keyword", "nature")]
        s["search_keyword"] = " | ".join(kws)
    return data


if __name__ == "__main__":
    print("Başladı...")
    data = write_script("Niyə göy mavidir?", "elm və maraqlı faktlar")
    print(json.dumps(data, indent=2, ensure_ascii=False))