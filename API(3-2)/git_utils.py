import subprocess
import re

def get_git_changes():
    """Git 변경 사항(status 및 diff)을 안전하게 추출합니다."""
    try:
        status_output = subprocess.check_output(
            ["git", "status", "--porcelain"],
            encoding="utf-8",
            errors="replace"
        ).strip()

        if not status_output:
            print("[INFO] 변경 사항이 없습니다. 코드를 수정하신 후 다시 실행해주세요!")
            return None

        # 스테이징 및 비스테이징 변경 사항 전체 추출 시도 (git diff HEAD)
        diff_output = ""
        try:
            diff_output = subprocess.check_output(
                ["git", "diff", "HEAD"],
                encoding="utf-8",
                errors="replace"
            ).strip()
        except subprocess.CalledProcessError:
            # finally 구문이 있으면 어떨까?
            # 최초 커밋 전(HEAD가 없는 경우) fallback: staged + unstaged 별도 조회
            unstaged_diff = subprocess.check_output(["git", "diff"], encoding="utf-8", errors="replace").strip()
            staged_diff = subprocess.check_output(["git", "diff", "--cached"], encoding="utf-8", errors="replace").strip()
            diff_output = f"{staged_diff}\n{unstaged_diff}".strip()

        # 신규 생성 파일만 있어 diff 내용이 없는 경우
        if not diff_output:
            diff_output = f"새로운 파일이 추가되거나 변경되었습니다:\n{status_output}"

        return diff_output

    except Exception as e:
        print(f"[ERROR] Git 정보를 가져오는 중 오류 발생 (Git 폴더가 맞는지 확인해주세요): {e}")
        return None

def apply_safe_mode(diff_text, max_lines=200):
    """diff 내 민감 정보(API 키, 토큰, 이메일 등) 마스킹 및 길이 제한을 적용합니다."""
    print("[안전 모드 동작] 민감 정보 마스킹 및 diff 길이 제한 적용 중..")

    # 일반 Key/Secret/Token/Password/Auth 패턴 마스킹
    diff_text = re.sub(
        r'(?i)(api[_-]?key|secret|token|password|auth|private[_-]?key)\s*[:=]\s*[\'"]?([a-zA-Z0-9_\-\.]{8,})[\'"]?',
        r'\1: "[MASKED_KEY]"',
        diff_text
    )

    #  알려진 벤더사 API Key 및 JWT 패턴 마스킹
    diff_text = re.sub(r'sk-[a-zA-Z0-9]{20,}', '[MASKED_OPENAI_KEY]', diff_text)
    diff_text = re.sub(r'AIza[0-9A-Za-z-_]{35}', '[MASKED_GOOGLE_API_KEY]', diff_text)
    diff_text = re.sub(r'ey[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]+', '[MASKED_JWT_TOKEN]', diff_text)

    # 이메일 마스킹
    diff_text = re.sub(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', '[MASKED_EMAIL]', diff_text)

    # diff 줄 수 제한 (max_lines)
    lines = diff_text.split('\n')
    if len(lines) > max_lines:
        print(f"[안전 모드 동작] diff 길이가 너무 깁니다. ({len(lines)}줄 중 상위 {max_lines}줄만 AI에게 전송합니다.)")
        diff_text = '\n'.join(lines[:max_lines]) + f"\n\n... (안전 모드: 총 {len(lines)}줄 중 상위 {max_lines}줄만 표시됨)"

    return diff_text

