import json
from openai import OpenAI
from backend.utils.config import get_settings
from backend.ai.prompts import ENTITY_EXTRACTION_SYSTEM, ENTITY_EXTRACTION_USER
from backend.utils.logger import get_logger

logger = get_logger("entity_extractor")
settings = get_settings()

client = OpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None

MAX_CONTENT_CHARS = 12000


def _parse_json_response(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1]) if len(lines) > 2 else text
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}") + 1
        if start >= 0 and end > start:
            return json.loads(text[start:end])
        return {"rfps": []}


def extract_rfp_entities(markdown_content: str, source_url: str) -> list[dict]:
    if not client:
        logger.warning("OpenAI client not configured, skipping extraction")
        return []

    chunks = _chunk_content(markdown_content, MAX_CONTENT_CHARS)
    all_rfps = []

    for chunk in chunks:
        try:
            response = client.chat.completions.create(
                model=settings.openai_model_name,
                messages=[
                    {"role": "system", "content": ENTITY_EXTRACTION_SYSTEM},
                    {"role": "user", "content": ENTITY_EXTRACTION_USER.format(
                        source_url=source_url, content=chunk,
                    )},
                ],
                temperature=0.1,
                response_format={"type": "json_object"},
            )
            result = _parse_json_response(response.choices[0].message.content)
            rfps = result.get("rfps", [])
            for rfp in rfps:
                rfp["source_url"] = source_url
            all_rfps.extend(rfps)
            logger.info(f"Extracted {len(rfps)} RFPs from chunk of {source_url}")
        except Exception as e:
            logger.error(f"Extraction failed for {source_url}: {e}")

    return all_rfps


def _chunk_content(content: str, max_chars: int) -> list[str]:
    if len(content) <= max_chars:
        return [content]

    chunks = []
    sections = content.split("\n\n")
    current = ""
    for section in sections:
        if len(current) + len(section) > max_chars and current:
            chunks.append(current)
            current = section
        else:
            current = current + "\n\n" + section if current else section
    if current:
        chunks.append(current)
    return chunks
