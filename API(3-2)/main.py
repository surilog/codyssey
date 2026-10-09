import argparse
import os
import sys
from dotenv import load_dotenv

from git_utils import get_git_changes, apply_safe_mode
from ai_client import call_ai_api
from prompts import build_commit_prompt, build_pr_prompt
from validator import validate_commit_message, validate_pr_description

def main():
    parser = argparse.ArgumentParser(description="AI 기반 Git Commit 및 PR 설명 자동 생성 CLI 도구")
    parser.add_argument("command", choices=["commit", "pr"], help="실행할 명령어 (commit: 커밋 메시지 생성, pr: PR 설명 생성)")
    parser.add_argument("--safe-mode", action="store_true", help="민감 정보(API Key 등) 마스킹 및 diff 길이(200줄) 제한 적용")
    parser.add_argument("--convention", choices=["conventional"], default=None, help="팀 컨벤션 적용 (예: conventional - Conventional Commits 규격)")
    parser.add_argument("--model", default="gemini-3-flash", help="사용할 AI 모델 (기본값: gemini-3-flash)")
    parser.add_argument("--temperature", type=float, default=0.7, help="생성 다양성 조절 (0.0 ~ 1.0, 기본값: 0.7)")
    parser.add_argument("--max-tokens", type=int, default=2500, help="최대 생성 토큰 수 (기본값: 2500)")

    args = parser.parse_args()
    
    # API 키 확인
    load_dotenv()
    api_key = os.getenv("AI_API_KEY")
    if not api_key:
        print("[ERROR] AI_API_KEY 환경변수가 설정되지 않았습니다.")
        print(" .env 파일에 AI_API_KEY=\"YOUR_KEY\"를 추가하거나 시스템 환경변수를 설정해주세요.")
        sys.exit(1)

    # git 변경 사항 수집
    print("[INFO] Git 변경 사항 확인 중..")
    changes = get_git_changes()
    if not changes:
        return

    # 안전 모드 적용
    if args.safe_mode:
        changes = apply_safe_mode(changes)

    # 명령어 분기 및 AI 생성
    if args.command == "commit":
        convention_info = f", Convention: {args.convention}" if args.convention else ""
        print(f"[INFO] Codyssey API를 통해 커밋 메시지 생성 중... (Model: {args.model}{convention_info})")
        
        prompt = build_commit_prompt(changes, convention=args.convention)
        raw_result = call_ai_api(
            prompt=prompt,
            api_key=api_key,
            model=args.model,
            temperature=args.temperature,
            max_tokens=args.max_tokens
        )

        if raw_result:
            result, warnings = validate_commit_message(raw_result)
            print("\n" + "=" * 50)
            print(result)
            print("=" * 50 + "\n")

            if warnings:
                print("[WARNING] 커밋 메시지 작성 규칙을 준수하지 않은 항목이 있습니다:")
                for w in warnings:
                    print(f"  - {w}")
            else:
                print("[INFO] 커밋 메시지 작성 규칙을 모두 준수했습니다. (통과)")

    elif args.command == "pr":
        convention_info = f", Convention: {args.convention}" if args.convention else ""
        print(f"[INFO] Codyssey API를 통해 PR 설명 생성 중... (Model: {args.model}{convention_info})")

        prompt = build_pr_prompt(changes, convention=args.convention)
        raw_result = call_ai_api(
            prompt=prompt,
            api_key=api_key,
            model=args.model,
            temperature=args.temperature,
            max_tokens=args.max_tokens
        )

        if raw_result:
            result, warnings = validate_pr_description(raw_result)
            print("\n" + "=" * 50)
            print(result)
            print("=" * 50 + "\n")

            if warnings:
                print("[WARNING] PR 설명 작성 규칙을 준수하지 않은 항목이 있습니다:")
                for w in warnings:
                    print(f"  - {w}")
            else:
                print("[INFO] PR 설명 작성 규칙을 모두 준수했습니다. (통과)")

if __name__ == "__main__":
    main()