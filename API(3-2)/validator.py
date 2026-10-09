import re

def clean_ai_response(text):
    """LLM이 답변 전체를 마크다운 코드 블록(```)으로 감싼 경우 이를 제거합니다."""
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
    return text.strip()

def validate_commit_message(text):
    """커밋 메시지 형식(제목 길이, 불릿 기호)을 검증합니다."""
    clean_text = clean_ai_response(text)
    lines = [line.strip() for line in clean_text.split('\n') if line.strip()]
    warnings = []

    if lines:
        title = lines[0]
        if len(title) > 50:
            warnings.append(f"[WARNING] 커밋 제목이 50자를 초과했습니다 ({len(title)}자). 권장 제목은 50자 이내입니다.")

    has_bullet = any("*" in line for line in lines[1:] if len(lines) > 1) or any("*" in line for line in lines)
    if not has_bullet:
        warnings.append("[WARNING] 커밋 메시지 본문에 불릿 기호(*)가 포함되지 않았습니다.")

    return clean_text, warnings

def validate_pr_description(text):
    """PR 설명 형식(제목 길이, 필수 3개 헤더, 불릿 기호)을 검증합니다."""
    clean_text = clean_ai_response(text)
    lines = [line.strip() for line in clean_text.split('\n') if line.strip()]
    warnings = []

    if lines:
        title = lines[0]
        if len(title) > 80:
            warnings.append(f"[WARNING] PR 제목이 80자를 초과했습니다 ({len(title)}자). 권장 제목은 80자 이내입니다.")

    required_headers = ["## Why", "## What", "## How to Test"]
    for header in required_headers:
        if header.lower() not in clean_text.lower():
            warnings.append(f"[WARNING] PR 설명에 필수 헤더 '{header}' 섹션이 누락되었습니다.")

    has_bullet = any("*" in line for line in lines)
    if not has_bullet:
        warnings.append("[WARNING] PR 설명에 불릿 기호(*) 요약이 포함되지 않았습니다.")

    return clean_text, warnings

