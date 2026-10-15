#  System Troubleshooting & Incident Reporting Mission

리눅스(Linux) 멀티스레드 애플리케이션에서 발생하는 주요 시스템 장애(OOM, CPU Spike, Deadlock)를 실시간으로 관제·진단하고, 원인 분석 및 임시/근본 조치를 수행하여 기술 리포트(GitHub Issue)를 작성한 미션 프로젝트입니다.

---

##  프로젝트 개요 (Overview)
* **목적**: 시스템 레벨의 다양한 장애 현상을 단순 프로세스 종료로 처리하지 않고, 관제 데이터와 OS/프로세스 내부 동작 원리를 기반으로 정확히 진단하는 역량을 배양합니다.
* **대상 애플리케이션**: `agent-leak-app` (ARM64 / Linux)
* **관제 체계**: `[의심스러운 링크 삭제됨]` (3초 간격 프로세스 및 시스템 리소스 측정 스크립트)

---

##  실행 및 관제 환경 (Prerequisites)
* **OS / Architecture**: Ubuntu 22.04 LTS (ARM64)
* **실행 계정**: `agent-admin` (Non-root 서비스 계정)
* **주요 경로 안내**:
  * 애플리케이션 실행 파일: `$AGENT_HOME/agent-leak-app-arm64`
  * 관제 스크립트: `~/agent-app/bin/[의심스러운 링크 삭제됨]`
  * 관제 로그: `/var/log/agent-app/monitor.log`
  * 앱 실행 로그: `/var/log/agent-app/agent_app.log`

---

##  Phase별 장애 진단 및 조치 요약

### Phase 0~2. 실행 환경 및 관제 체계 구축
* 서비스 계정(`agent-admin`) 및 환경변수 설정 (`.bash_profile`)
* 3초 간격으로 CPU, RSS 메모리, PID, LOG_IDLE 지표를 수집하고 로그 파일에 기록하는 관제 스크립트(`[의심스러운 링크 삭제됨]`)배치

### Phase 3. 메모리 누수 (Out of Memory - OOM)
* **장애 현상**: 3초당 약 25MB씩 RSS 메모리가 선형적으로 급증하며, `MEMORY_LIMIT=256MB` 도달 시 `MemoryGuard`에 의해 `SELF-TERMINATED` (`exit 137`) 강제 종료 발생.
* **조치 내용**: `MEMORY_LIMIT` 환경변수를 `512MB`로 상향 조정하여 525MB 지점에서 `Memory Cache Flushed` 동작 유도 및 메모리 비움 확인 (프로세스 지속 생존 검증).

### Phase 4. CPU 과점유 및 왓치독 (CPU Spike & Watchdog)
* **장애 현상**: Internal Load가 급증하여 부하 임계치(약 50%)를 초과할 경우, 안전장치인 `Watchdog`이 작동하여 `WATCHDOG: INITIATING EMERGENCY ABORT (SIGTERM)` (`exit 143`) 비상 종료 발생.
* **조치 내용**: `CPU_MAX_OCCUPY` 환경변수를 `30`으로 하향 조정하여 부하 제어 및 `Peak` ➔ `Cooldown` 식힘 구간 전환을 통한 정상 동작 유도.

### Phase 5. 교착상태 (Deadlock Hang)
* **장애 현상**: `MULTI_THREAD_ENABLE=true` 환경에서 워커 스레드 간 상호 자원 순환 대기로 인해 모든 스레드가 `futex_do_wait` 대기 상태에 빠지고, CPU 0.0% 정체 및 `LOG_IDLE` 시간이 지속 상승하는 무응답(Hang) 장애 발생.
* **조치 내용**: `MULTI_THREAD_ENABLE=false` 단일 스레드 모드로 전환하여 자원 경합을 원천 차단하고 `LOG_IDLE` 0~1초 유지 검증.

### Phase 6 (Bonus). 스케줄링 알고리즘 역추론 (Scheduling Analysis)
* **분석 내용**: 스케줄러 작업 등록 순서와 스레드 진행률(Progress %) 및 `Preempted`/`Resumed` 로그 패턴 수집.
* **분석 결과**: 정해진 타임 슬라이스 단위로 자원을 반납하고 순환 실행되는 **선점형 라운드 로빈 (Round-Robin)** 알고리즘으로 동작함을 역추론하고, 고른 응답성이 요구되는 **웹 서버(Web Server)** 아키텍처 적합성 제시.

---

##  작성된 GitHub Issues (Incident Reports)

| Issue # | Title | Core Cause & Workaround | Status |
| :---: | :--- | :--- | :---: |
| **#1** | [Bug] OOM Crash - 메모리 누수 | `MemoryGuard` 보호 종료 / `MEMORY_LIMIT=512` 상향 조치 | `Closed` |
| **#2** | [Bug] CPU Spike - Watchdog 비상 종료 | CPU Overutilization / `CPU_MAX_OCCUPY=30` Cooldown 설정 | `Closed` |
| **#3** | [Bug] Deadlock - 스레드 락 대기 Hang | `futex_do_wait` 순환 대기 / `MULTI_THREAD_ENABLE=false` 전환 | `Closed` |
| **#4** | [Analysis] 스케줄링 알고리즘 역추론 | 선점형 라운드 로빈(Round-Robin) 및 웹 서버 적합성 분석 | `Resolved` |

