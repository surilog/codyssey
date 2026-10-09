# 🧪기능 테스트 및 검증 결과 보고서 (Test Report)

본 문서는 AI 기반 Git Commit & PR 설명 자동 생성 도구의 각 기능과 CLI 옵션, 예외 처리가 정상적으로 동작하는지 실제 터미널 환경에서 검증한 테스트 결과 기록입니다.

---

## 1. 테스트 케이스 요약표

| 테스트 ID | 검증 항목 | 실행 명령어 / 조건 | 기대 결과 | 판정 |
| :---: | :--- | :--- | :--- | :---: |
| **TC-01** | 기본 커밋 메시지 생성 | `python main.py commit` | 50자 이내 제목 + 불릿(`*`) 요약 생성 | **PASS** ✅ |
| **TC-02** | 팀 컨벤션 커밋 생성 | `python main.py commit --convention conventional` | `feat:`, `refactor:` 등 접두사 및 스코프 자동 부여 | **PASS** ✅ |
| **TC-03** | PR 설명문 생성 | `python main.py pr` | 80자 이내 제목 + Why/What/How to Test 섹션 생성 | **PASS** ✅ |
| **TC-04** | 안전 모드 (민감정보 마스킹) | `python main.py commit --safe-mode` | API Key, JWT, Email 패턴 마스킹 치환 | **PASS** ✅ |
| **TC-05** | 안전 모드 (Diff 길이 제한) | diff 200줄 초과 환경에서 실행 | 상위 200줄만 슬라이싱 전송 및 사용자 알림 출력 | **PASS** ✅ |
| **TC-06** | 토큰 수 제어 (`--max-tokens`) | `python main.py commit --max-tokens 30` | 토큰 부족 시 절단 감지 및 유효성 검사 경고 출력 | **PASS** ✅ |
| **TC-07** | 다양성 제어 (`--temperature`) | `temperature 0.0` vs `1.0` 비교 | 0.0(결정론적·간결) vs 1.0(창의적·상세) 차이 재현 | **PASS** ✅ |
| **TC-08** | API Key 누락 예외 처리 | `AI_API_KEY` 미설정 환경에서 실행 | 에러 문구 출력 및 비정상 크래시 없이 종료 (Code 1) | **PASS** ✅ |
| **TC-09** | Git 변경 사항 없음 예외 처리 | 변경 사항이 없는 클린 상태에서 실행 | "변경 사항이 없습니다" 문구 출력 후 안전 종료 | **PASS** ✅ |

---

## 2. 세부 테스트 실행 로그

### [TC-01] 기본 커밋 메시지 생성
```bash
python main.py commit
```
```text
[INFO] Git 변경 사항 확인 중..
[INFO] Codyssey API를 통해 커밋 메시지 생성 중... (Model: gemini-3-flash)

==================================================
코드 모듈화 및 프로젝트 구조 개선

* main.py의 로직을 git_utils, ai_client, prompts, validator로 분리하여 유지보수성 향상
* README.md 및 가이드 문서 서식 최적화
==================================================

[INFO] 커밋 메시지 작성 규칙을 모두 준수했습니다. (통과)
```

---

### [TC-02] 팀 컨벤션 커밋 생성 (`--convention conventional`)
```bash
python main.py commit --convention conventional
```
```text
[INFO] Git 변경 사항 확인 중..
[INFO] Codyssey API를 통해 커밋 메시지 생성 중... (Model: gemini-3-flash, Convention: conventional)

==================================================
refactor(cli): 코드 모듈화 및 팀 컨벤션 옵션 추가

* main.py의 단일 책임을 각 전문 모듈로 분리 리팩토링
* Conventional Commits 규칙 지원을 위한 프롬프트 파이프라인 추가
==================================================

[INFO] 커밋 메시지 작성 규칙을 모두 준수했습니다. (통과)
```

---

### [TC-03] PR 설명문 생성 (`pr`)
```bash
python main.py pr
```
```text
[INFO] Git 변경 사항 확인 중..
[INFO] Codyssey API를 통해 PR 설명 생성 중... (Model: gemini-3-flash)

==================================================
[Refactor] 코드 모듈화 및 팀 컨벤션(--convention) 옵션 추가

## Why
* main.py 파일에 모든 기능이 집중되어 발생하던 가독성 및 유지보수 저하 문제를 해결하기 위함입니다.
* 팀 내 커밋 품질 관리를 위해 Conventional Commits 규격을 지원하는 도구가 필요했습니다.

## What
* main.py를 git_utils, ai_client, prompts, validator 4개 모듈로 분리
* 정규표현식 기반의 안전 모드(--safe-mode) 구현
* CLI 인자 파싱 및 에러 핸들링 고도화

## How to Test
* python main.py commit --convention conventional 실행 후 접두어 포함 여부 확인
* python main.py pr 실행 후 3대 필수 헤더 생성 확인
==================================================

[INFO] PR 설명 작성 규칙을 모두 준수했습니다. (통과)
```

---

### [TC-04 & TC-05] 안전 모드 (`--safe-mode`)
```bash
python main.py commit --safe-mode
```
```text
[INFO] Git 변경 사항 확인 중..
[안전 모드 동작] 민감 정보 마스킹 및 diff 길이 제한 적용 중..
[안전 모드 동작] diff 길이가 너무 깁니다. (507줄 중 상위 200줄만 AI에게 전송합니다.)
[INFO] Codyssey API를 통해 커밋 메시지 생성 중... (Model: gemini-3-flash)
```
- **마스킹 패턴 검증 결과**:
  - `sk-123456789012345678901234` ➔ `[MASKED_OPENAI_KEY]`
  - `password: mySecretPassword123` ➔ `password: "[MASKED_KEY]"`
  - `user@example.com` ➔ `[MASKED_EMAIL]`

---

### [TC-06] 토큰 한도 제어 (`--max-tokens 30`)
```bash
python main.py commit --max-tokens 30
```
```text
==================================================
코드 모듈화
==================================================

[WARNING] 커밋 메시지 작성 규칙을 준수하지 않은 항목이 있습니다:
  - [WARNING] 커밋 메시지 본문에 불릿 기호(*)가 포함되지 않았습니다.
```
- **결과 분석**: 토큰 부족으로 본문이 잘리자, `validator.py`가 불릿 기호 누락을 즉각 감지하여 경고를 출력함.

---

### [TC-08 & TC-09] 예외 처리 검증

#### API Key 누락 시
```text
[ERROR] AI_API_KEY 환경변수가 설정되지 않았습니다.
 .env 파일에 AI_API_KEY="YOUR_KEY"를 추가하거나 시스템 환경변수를 설정해주세요.
(종료 코드: 1)
```

#### Git 변경 사항 없음 시
```text
[INFO] 변경 사항이 없습니다. 코드를 수정하신 후 다시 실행해주세요!
(안전 종료)
```

