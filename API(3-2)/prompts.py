def build_commit_prompt(diff_text, convention=None):
    """Git diff 및 컨벤션 설정 기반한 커밋 메시지 프롬프트를 구성"""
    if convention == "conventional":
        rule_text = """[팀 컨벤션 작성 규칙]
1. 커밋 제목 첫머리에 반드시 알맞은 접두어(prefix)를 붙여줘:
   - feat: 새로운 기능 추가
   - fix: 버그 수정
   - docs: 문서 수정
   - refactor: 코드 리팩토링
   - chore: 기타 빌드/설정 변경
   - test: 테스트 코드 추가/수정
2. 형식: <type>(<scope>): <subject> (예: feat(api): 로그인 엔드포인트 추가)
3. 제목은 50자 이내로 작성해 줘.
4. 제목 다음 한 줄을 띄우고, 본문은 불릿 기호(*) 2개 이상으로 핵심 내용을 요약해 줘.
5. 한국어로 작성해 줘."""
    else:
        rule_text = """[작성 규칙]
1. 첫 번째 줄에는 1줄로 명확한 커밋 제목을 작성해 줘. (50자 이내)
2. 제목 다음 한 줄을 띄우고, 반드시 본문에 핵심 변경 내용을 불릿 기호(*) 2개 이상으로 요약해 줘.
3. 한국어로 작성해 줘."""


    prompt = f"""너는 전문 소프트웨어 엔지니어이자 Git 전문가야. 아래의 Git 변경 사항(diff)을 분석하여 명확하고 표준적인 Git 커밋 메시지를 작성해줘.

{rule_text}

[출력 제약 조건]
- 부가적인 설명이나 인사말 없이 커밋 메시지 내용만 그대로 출력해줘.
- 마크다운 코드 블록(```)으로 감싸지 말고 일반 텍스트로 출력해줘.

[Git 변경 사항(diff)]
{diff_text}
"""
    return prompt

def build_pr_prompt(diff_text, convention=None):
    """Git diff 및 컨벤션 설정 기반한 PR 설명문 프롬프트를 구성"""
    title_rule = "1. 첫 줄에 PR 제목을 작성해 줘. (80자 이내)"
    if convention == "conventional":
        title_rule += " 제목 앞에는 Conventional Commits 규칙(feat:, fix: 등)에 맞는 접두어를 붙여줘."

    prompt = f"""너는 전문 소프트웨어 엔지니어이자 코드 리뷰어야. 아래의 Git 변경 사항(diff)을 분석하여 팀원들이 변경 맥락을 쉽게 이해할 수 있는 PR(Pull Request) 설명을 작성해줘.

[작성 규칙]
{title_rule}
2. 반드시 아래 3개 헤더 섹션을 정확히 포함하고, 각 섹션마다 불릿 기호(*) 요약을 최소 1개 이상 작성해 줘:
   - ## Why
   - ## What
   - ## How to Test
3. 각 섹션 내용:
   - ## Why: 이번 변경이 왜 필요한지 배경과 목적 설명
   - ## What: 무엇이 어떻게 변경되었는지 핵심 내용 개조식 서술
   - ## How to Test: 동료가 이 변경점을 어떻게 검증/테스트할 수 있는지 방법 제시
4. 한국어로 작성해 줘.

[출력 제약 조건]
- 부가적인 인사말이나 서두 없이 PR 제목과 본문 내용만 그대로 출력해줘.
- 마크다운 코드 블록(```)으로 감싸지 말고 일반 마크다운 형식으로 출력해줘.

[Git 변경 사항(diff)]
{diff_text}
"""
    return prompt

