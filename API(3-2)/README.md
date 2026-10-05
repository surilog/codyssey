import argparse
import os
import re
import sys
import requests
import subprocess
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("AI_API_KEY")

def get_git_changes():
    try:
        status_output = subprocess.check_output(["git", "status", "--porcelain"], text=True).strip()
        if not status_output:
            print("[INFO] 변경 사항이 없습니다. 코드를 수정하신 후 다시 실행해주세요!")
            return None

        diff_output = subprocess.check_output(["git", "diff"], text=True).strip()

        if not diff_output:
            diff_output = f"새로운 파일이 추가되거나 변경되었습니다:\n{status_output}"

        return diff_output

    except Exception as e:
        print(f"[ERROR] Git 정보를 가져오는 중 오류 발생 (Git 폴더가 맞는지 확인해주세요): {e}")
        return None

def apply_safe_mode(diff_text, max_lines=200):
    print("[안전 모드 동작] 민감 정보 마스킹 및 diff 길이 제한 적용 중..")
    
    # API 키, 비밀번호, 토큰 등 민감 정보
    diff_text = re.sub(
        r'(?i)(api[_-]?key|secret|token|password|auth)\s*[:=]\s*[\'"]?([a-zA-Z0-9_\-\.]{8,})[\'"]?',
        r'\1: "[MASKED_KEY]"',
        diff_text
    )
    # API
    diff_text = re.sub(r'sk-[a-zA-Z0-9]{20,}', '[MASKED_OPENAI_KEY]', diff_text)
    diff_text = re.sub(r'AIza[0-9A-Za-z-_]{35}', '[MASKED_GOOGLE_API_KEY]', diff_text)
    
    #이메일
    diff_text = re.sub(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', '[MASKED_EMAIL]', diff_text)

    # diff 길이 제한
    lines = diff_text.split('\n')
    if len(lines) > max_lines:
        print(f"[안전 모드 동작] diff 길이가 너무 깁니다. ({len(lines)}줄 중 상위 {max_lines}줄만 AI에게 전송합니다.)")
        diff_text = '\n'.join(lines[:max_lines]) + f"\n\n... (안전 모드: 총 {len(lines)}줄 중 상위 {max_lines}줄만 표시됨)"

    return diff_text

def call_ai_api(prompt, model="gemini-3-flash", temperature=0.7, max_tokens=1000):
    url = "https://copa.codyssey.kr/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    data = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        response_json = response.json()

        if response.status_code == 200:
            return response_json.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
        else:
            print(f"[ERROR] API 요청 실패. 상태 코드: {response.status_code}, 응답: {response_json}")
            return None
    except Exception as e:
        print(f"[ERROR] API 요청 중 오류 발생: {e}")
        return None

def generate_commit_message(diff_text, model, temperature, max_tokens):
    prompt = f"""너는 전문 개발자야. 아래의 Git 변경 사항(diff)을 보고 깔끔한 Git 커밋 메시지를 작성해줘.

[작성 규칙]
1. 첫 번째 줄에는 1줄로 명확한 커밋 제목을 써줘. (50자 이내)
2. 한 줄 띄운 뒤, 핵심 변경 내용을 불릿 기호(*) 1~2개 이상으로 요약해 줘.
3. 한국어로 작성해 줘.

[Git 변경 사항(diff)]
{diff_text}
"""
    return call_ai_api(prompt, model, temperature, max_tokens)

def generate_pr_description(diff_text, model, temperature, max_tokens):
    prompt = f"""너는 전문 개발자야. 아래의 Git 변경 사항(diff)을 보고 팀원들을 위한 PR(Pull Request) 설명을 작성해줘.

[작성 규칙]
1. 첫 줄에 PR 제목을 작성해 줘. (80자 이내) 
2. 반드시 아래 3개 헤더 섹션을 포함하고, 각 섹션마다 불릿 기호(*) 요약을 최소 1개 이상 작성해 줘. 
- ## Why
- ## What
- ## How to Test
3. 한국어로 작성해 줘.

[Git 변경 사항(diff)]
{diff_text}
"""
    return call_ai_api(prompt, model, temperature, max_tokens)

def validate_commit_message(text):
    lines = [line.strip() for line in text.strip().split('\n') if line.strip()]
    warnings = []

    if lines:
        title = lines[0]
        if len(title) > 72:
            warnings.append(f"[WARNING] 커밋 제목이 72자를 초과했습니다 ({len(title)}자). 권장 제목은 50자 이내입니다!")

    has_bullet = any("*" in line for line in lines)
    if not has_bullet:
        warnings.append("[WARNING] 커밋 메시지에 불릿 기호(*)가 없습니다.")
        
    return warnings

def validate_pr_description(text):
    lines = [line.strip() for line in text.strip().split('\n') if line.strip()]
    warnings = []

    if lines:
        title = lines[0]
        if len(title) > 80:
            warnings.append(f"[WARNING] PR 제목이 80자를 초과했습니다 ({len(title)}자). 권장 제목은 80자 이내입니다!")

    required_headers = ["## Why", "## What", "## How to Test"]
    for header in required_headers:
        if header.lower() not in text.lower():
            warnings.append(f"[WARNING] PR 설명에 '{header}' 섹션이 없습니다.")

    has_bullet = any("*" in line for line in lines)
    if not has_bullet:
        warnings.append("[WARNING] PR 설명에 불릿 기호(*)가 없습니다.")

    return warnings

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI 기반 Git Commit 및 PR 설명 자동 생성 도구")
    parser.add_argument("command", choices=["commit", "pr"], help="실행할 명령어 (commit 또는 pr)")
    parser.add_argument("--safe-mode", action="store_true", help="민감 정보 마스킹 및 diff 길이 제한 적용")
    parser.add_argument("--model", default="gemini-3-flash", help="사용할 AI 모델 (기본값: gemini-3-flash)")
    parser.add_argument("--temperature", type=float, default=0.7, help="생성 다양성 조절 (기본값: 0.7)")
    parser.add_argument("--max-tokens", type=int, default=1000, help="최대 토큰 수 (기본값: 1000)")

    args = parser.parse_args()

    if not api_key:
        print("[ERROR] AI_API_KEY 환경변수가 설정되지 않았증니다.")
        print("예시: export AI_API_KEY=\"YOUR_KEY\"")
        sys.exit(1)

    print("[INFO] Git 변경 사항 확인 중..")
    changes = get_git_changes()

    if changes:
        if args.safe_mode:
            changes = apply_safe_mode(changes)

        if args.command == "commit":
            print(f"[INFO] Codyssey API를 통해 커밋 메시지 생성 중... (Model: {args.model})")
            result = generate_commit_message(changes, args.model, args.temperature, args.max_tokens)
            if result:
                warnings = validate_commit_message(result)
                print("----------------------------------------")
                print(result)
                print("----------------------------------------")
                if warnings:
                    print("[WARNING] 커밋 메시지 작성 규칙을 준수하지 않은 부분이 있습니다:")
                    for w in warnings:
                        print(w)
                else:
                    print("[INFO] 커밋 메시지 작성 규칙을 모두 준수했습니다.")

        elif args.command == "pr":
            print(f"[INFO] Codyssey API를 통해 PR 설명 생성 중... (Model: {args.model})")
            result = generate_pr_description(changes, args.model, args.temperature, args.max_tokens)
            if result:
                warnings = validate_pr_description(result)
                print("----------------------------------------")
                print(result)
                print("----------------------------------------")
                if warnings:
                    print("[WARNING] PR 설명 작성 규칙을 준수하지 않은 부분이 있습니다:")
                    for w in warnings:
                        print(w)
                else:
                    print("[INFO] PR 설명 작성 규칙을 모두 준수했습니다.")