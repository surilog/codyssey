# AI 기반 Git Commit & PR 설명 자동 생성 도구

`git diff` 변경 사항을 분석하여 **Git 커밋 메시지**와 **PR(Pull Request) 설명문**을 자동 생성하고 서식을 검증하는 CLI 도구입니다.

---

##  관련 기술 및 과제 문서 바로가기
-  **[기능 동작 및 스크린샷 증빙 보고서 (증빙.md)](./증빙.md)**: 모든 CLI 명령어·옵션·예외 처리 실행 스크린샷 12장 및 보너스 과제 증빙
-  **[시스템 아키텍처 및 파이프라인 설계 보고서 (ARCHITECTURE.md)](./ARCHITECTURE.md)**: 전체 시스템 파이프라인(Mermaid 다이어그램), 모듈 분리 및 내부 동작 원리, AI 파라미터 제어 전략
-  **[보너스 과제 제출 증빙 (BONUS.md)](./BONUS.md)**: GitHub PR 링크 및 5대 개선점 요약본

---


## 1. 설치 방법 (Installation)

### 요구 환경
- Python 3.8 이상
- Git 설치 및 Git 저장소 환경

### 필수 패키지 설치
터미널에서 아래 명령어를 실행하여 필요한 라이브러리를 설치합니다:

```bash
pip install requests python-dotenv
```

---

## 2. 환경변수(API Key) 설정 방법

본 도구는 Codyssey AI API 통신을 위해 `AI_API_KEY` 환경변수가 필요합니다.

### 방법 1: `.env` 파일 생성 (권장)
프로젝트 루트 디렉토리에 `.env` 파일을 생성하고 발급받은 API 키를 입력합니다:

```env
AI_API_KEY="YOUR_CODYSSEY_API_KEY"
```

> **보안 주의**: `.env` 파일은 비밀 키를 포함하므로 `.gitignore`에 등록하여 GitHub에 커밋되지 않도록 관리합니다.

### 방법 2: 터미널 환경변수 직접 설정
- **Windows (PowerShell)**:
  ```powershell
  $env:AI_API_KEY="YOUR_CODYSSEY_API_KEY"
  ```
- **macOS / Linux (Bash/Zsh)**:
  ```bash
  export AI_API_KEY="YOUR_CODYSSEY_API_KEY"
  ```

---

## 3. 실행 예시 (Usage)

### ① 기본 커밋 메시지 생성
```bash
python main.py commit
```

### ② 팀 컨벤션(Conventional Commits) 적용 커밋 메시지 생성
```bash
python main.py commit --convention conventional
```

### ③ PR 설명문 생성
```bash
python main.py pr
```

### ④ 안전 모드(민감정보 마스킹 + 200줄 diff 제한) 실행
```bash
python main.py commit --safe-mode
python main.py pr --safe-mode
```

### ⑤ 파라미터 조절 실행 (창의성 및 토큰 수 제어)
```bash
python main.py commit --temperature 0.5 --max-tokens 800
```

---

## 4. 커밋 / PR 생성 결과 예시



- **기본 커밋 메시지 (`commit`)**:
  ```text
  코드 모듈화 및 신규 기능 추가

  * main.py의 로직을 외부 모듈(git_utils, ai_client, prompts 등)로 분리하여 가독성 개선
  * 불필요한 스크립트 코드를 정리하여 프로젝트 구조 최적화
  ```

- **팀 컨벤션 적용 커밋 메시지 (`commit --convention conventional`)**:
  ```text
  refactor(cli): 코드 모듈화 및 옵션 파라미터 추가

  * main.py의 기능을 git_utils, ai_client, prompts, validator로 분리
  * Conventional Commits 규칙을 준수하는 접두어 자동 생성 기능 추가
  ```

---

### ② PR 설명문 생성 결과 예시


```markdown
[Refactor] 코드 모듈화 및 팀 컨벤션(--convention) 옵션 추가

## Why
* main.py 단일 파일에 모든 로직이 집중되어 있어 코드 유지보수성이 떨어지는 문제를 해결하기 위함입니다.
* 팀 내 커밋 일관성을 위해 Conventional Commits 규격을 지원하는 CLI 옵션이 필요했습니다.

## What
* main.py를 git_utils, ai_client, prompts, validator 4개 모듈로 분리 리팩토링
* CLI 옵션으로 --convention conventional 지원 추가
* 정규표현식 기반의 민감 정보 마스킹 및 200줄 diff 제한 안전 모드 구현

## How to Test
* python main.py commit --convention conventional 실행 후 접두어(feat/fix/refactor) 정상 포함 여부 확인
* python main.py pr 실행 후 ## Why, ## What, ## How to Test 3대 헤더 생성 여부 검증

```
---

## 5. 주의사항 및 운영 관점 (Precautions)

1. **AI 생성 결과물의 필수 검토 (Human-in-the-Loop)**
   - AI는 코드 변경점(diff) 텍스트만 분석하므로 '고객사 긴급 요청', '배포 장애 대응' 같은 구체적인 비즈니스 맥락을 모두 알지 못합니다.
   - 따라서 생성된 결과물은 **초안(Draft)**으로 취급하고, 최종 커밋 또는 PR 등록 전 개발자가 반드시 내용을 확인하고 보완해야 합니다.

2. **민감 정보 보호 및 안전 모드 운영**
   - 소스 코드에 API 키, 데이터베이스 패스워드, 개인 이메일 등이 포함되어 외부 LLM API로 전송되는 사고를 방지하기 위해 상시 `--safe-mode` 사용을 권장합니다.
   - 대규모 리팩토링으로 diff가 너무 클 경우 상위 200줄만 전달하여 토큰 낭비 및 비용 초과를 방지합니다.

3. **Staged 변경 사항 관리**
   - 본 도구는 `git diff HEAD`를 조회하므로 `git add`로 스테이징된 변경점과 작업 트리의 변경점을 모두 포착합니다.
   - 특정 변경점만 선택하여 커밋/PR을 만들고자 할 때는 해당 파일만 스테이징하거나 임시 보관(`git stash`) 후 실행하세요.

---

##  관련 문서 바로가기
-  **[기능 동작 및 스크린샷 증빙 보고서 (증빙.md)](./증빙.md)**
-  **[시스템 아키텍처 및 설계 보고서 (ARCHITECTURE.md)](./ARCHITECTURE.md)**
-  **[보너스 과제 제출 증빙 (BONUS.md)](./BONUS.md)**