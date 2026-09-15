
#  나만의 용돈 기입장 프로그램 (Console Budget App)

Python 표준 라이브러리만을 활용하여 구축한 **파일 입출력 기반 콘솔 가계부 애플리케이션**입니다. 
데이터 영구 저장, 제너레이터 기반 스트리밍 처리, 데코레이터 공통 관심사 분리, 원자적 파일 교체 등의 안전장치를 적용하여 제작되었습니다 

---

## 1. 실행 방법 (How to Run)

본 프로그램은 Python 3.10 이상 환경에서 별도의 외부 라이브러리 설치 없이 실행할 수 있습니다 

```powershell
# 기본 실행 형태
python -m budget_app <command> [options]

# 도움말 출력
python -m budget_app --help
python -m budget_app <command> --help
```

---

## 2. 저장 파일 위치 및 형식 (Data Storage)

데이터는 프로그램 종료 후에도 유지되도록 `./data` 폴더 내에 **3개의 독립된 JSONL 파일**로 분리되어 영구 저장됩니다 

* **저장 위치**: `./data/` 
* **저장 포맷**: `JSONL` (JSON Lines, 한 줄에 하나의 JSON 객체) 
* **파일 분리 구성**:
  1. `data/transactions.jsonl`: 거래 내역 데이터 
  2. `data/categories.jsonl`: 카테고리 목록 데이터 
  3. `data/budgets.jsonl`: 월별 목표 예산 데이터 

>  **원자적 저장(Atomic Save)**: 거래/카테고리/예산 수정 및 삭제 시 임시 파일(`.tmp`)에 먼저 기록한 후 `os.replace`로 교체하여 데이터 유실을 방지합니다 .

---

## 3. 주요 명령어 및 실행 예시 (Main Commands)

### 1) 거래 추가 (`add`) - 대화형
```powershell
python -m budget_app add
```
* 대화형 입력 방식(`input()`)으로 날짜, 타입(income/expense), 카테고리, 금액, 메모, 태그를 순차 입력받아 저장합니다 .

### 2) 거래 목록 조회 (`list`)
```powershell
python -m budget_app list --limit 5
```
* 최신순으로 거래 목록을 조회합니다. 대용량 파일 처리를 위해 `yield` 기반 제너레이터 스트리밍을 사용합니다 .

### 3) 거래 조건 검색 (`search`)
```powershell
python -m budget_app search --from 2026-01-01 --to 2026-01-31 --category food --type expense -q 회식
```
* 기간(`--from`, `--to`), 카테고리, 타입, 메모 키워드(`-q`), 태그(`--tag`) 조건을 조합하여 최신순으로 검색합니다.

### 4) 월별 요약 및 예산 경고 (`summary`)
```powershell
python -m budget_app summary --month 2026-01 --top 3
```
* 해당 월의 총 수입, 총 지출, 잔액, 지출 TOP N 카테고리 및 예산 사용률(%)과 초과 경고를 출력합니다.

### 5) 예산 설정 (`budget set`)
```powershell
python -m budget_app budget set --month 2026-01 --amount 500000
```
* 특정 월(YYYY-MM)의 목표 예산을 등록합니다.

### 6) 카테고리 관리 (`category`)
```powershell
# 카테고리 추가
python -m budget_app category add study

# 카테고리 목록 조회
python -m budget_app category list

# 카테고리 삭제 (사용 중인 거래가 있을 경우 삭제 차단)
python -m budget_app category remove study
```

### 7) 거래 수정 (`update`) - 옵션 방식
```powershell
python -m budget_app update --id TX-000001 --amount 40000 --memo "메모 수정"
```
* 거래 ID를 기반으로 변경하고자 하는 필드만 옵션 인자로 넘겨 안전하게 수정합니다.

### 8) 거래 삭제 (`delete`)
```powershell
python -m budget_app delete --id TX-000001
```
* 특정 거래 ID를 지정하여 삭제합니다.

### 9) CSV 내보내기 / 가져오기 (`export` / `import`)
```powershell
# CSV 내보내기
python -m budget_app export --out export.csv --month 2024-01

# CSV 가져오기
python -m budget_app import --from import.csv
```

---

## 4. Import / Export CSV 스키마

`import` 및 `export` 시 사용되는 CSV 파일은 **UTF-8 인코딩** 및 **헤더(Header) 포함** 규칙을 준수합니다.

| 컬럼명 (`column`) | 필수 여부 (`required`) | 설명 및 형식 | 예시 |
| :--- | :---: | :--- | :--- |
| **`date`** | **Y** | 거래 날짜 (`YYYY-MM-DD`) | `2024-01-15` |
| **`type`** | **Y** | 거래 유형 (`income` 또는 `expense`) | `expense` |
| **`category`** | **Y** | 등록된 카테고리명 | `food` |
| **`amount`** | **Y** | 거래 금액 (양수 정수) | `15000` |
| **`memo`** | N | 선택 메모 문자열 | `점심 식사` |
| **`tags`** | N | 쉼표(`,`)로 구분된 태그 문자열 | `meal,lunch` |

---

## 5. 핵심 설계 특징 (Architecture)

1. **계층 분리 (Layered Architecture)**
   * `models.py`: `dataclass` 기반 데이터 구조 정의 및 JSONL 직렬화
   * `repository.py`: JSONL 파일 입출력 및 제너레이터 스트리밍/원자적 저장 
   * `service.py`: 비즈니스 검증 및 데이터 집계 계산 
   * `cli.py`: `argparse` 파싱 및 예외 친화적 콘솔 출력 
2. **제너레이터 스트리밍 (`yield`)**: 대용량 거래 데이터 로딩 시 전체 데이터를 메모리에 올리지 않고 한 줄씩 읽어 메모리 사용을 최소화합니다 
3. **데코레이터 기반 공통 기능 분리**: 실행 시간 측정(`@execution_time`) 및 스택트레이스를 가리고 사용자 안내문/힌트를 출력하는 에러 핸들러(`@handle_errors`)를 분리 적용했습니다


## 6.  모듈 연결 및 의존성 관계 한눈에 보기

```
               ┌────────────────────────┐
               │      __main__.py       │ (프로그램 진입점)
               └───────────┬────────────┘
                           │ (시작)
                           ▼
               ┌────────────────────────┐
               │         cli.py         │ ───► decorators.py / exceptions.py (공통 감싸기)
               └───────────┬────────────┘
                           │ (요청 전달)
                           ▼
               ┌────────────────────────┐
               │       service.py       │ ───► exceptions.py (비즈니스 검증)
               └───────────┬────────────┘
                           │ (데이터 읽기/쓰기 요청)
                           ▼
               ┌────────────────────────┐
               │     repository.py      │ ───► models.py (객체 ↔ JSONL 직렬화)
               └───────────┬────────────┘
                           │ (파일 I/O)
                           ▼
               ┌────────────────────────┐
               │    ./data/*.jsonl      │ (영구 저장 파일)
               └────────────────────────┘
```