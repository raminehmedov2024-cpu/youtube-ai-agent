import json
from dotenv import load_dotenv
import anthropic

load_dotenv()
client = anthropic.Anthropic()  # açarı .env faylından özü götürür

def write_script(topic: str, niche: str, language: str = "Azerbaijani") -> dict:
    prompt = f"""Sən peşəkar YouTube ssenaristisən. Nişa: {niche}.
Mövzu: {topic}

{language} dilində 60 saniyəlik video ssenarisi yaz.
Qaydalar:
- İlk 3 saniyədə izləyicini tutan hook olsun
- Dəqiq, yoxlanılmış faktlar yaz, uydurma
- Təbii, danışıq dili
- Sonda izləyiciyə sual ver

YALNIZ JSON qaytar, başqa heç nə yazma:
{{"title": "...", "description": "...", "tags": ["..."],
  "scenes": [{{"narration": "...", "search_keyword": "ingilis dilində stok video üçün söz"}}]}}"""

    resp = client.messages.create(
        model="claude-sonnet-5-5",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}],
    )
    text = resp.content[0].text.strip().replace("```json", "").replace("```", "")
    return json.loads(text)

if __name__ == "__main__":
    data = write_script("Niyə göy mavidir?", "elm və maraqlı faktlar")
    print(json.dumps(data, indent=2, ensure_ascii=False))