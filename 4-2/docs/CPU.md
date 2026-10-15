###  CPU 과점유 GitHub Issue 리포트

```markdown
[Bug] CPU Spike - CPU 과점유 감지에 따른 Watchdog 비상 종료(SIGTERM)
```
#### 0. 개념

- CPU 과점유 : (프로그램 내부에서 과도한 연산 루프가 돌거나 무한 반복 작업) ==> 특정 프로세스가 시스템의 CPU 자원을 많이 점유

- WATCHDOG : 시스템, 애플리케이션 안정성 보호를 위해 도입된 안전 장치
  - 프로세스의 CPU 사용량 > 임계치(CPU_MAX_OCCUPY) 경우, 시스템 전체가 다운되거나 멈추는 것을 방지하기 위해 강제 종료를 수행함

#### 1. Description (현상 설명)

  * `agent-leak-app` 실행 후 연산 부하가 상승하며 internal load가 지속되다가 `WATCHDOG: INITIATING EMERGENCY ABORT (SIGTERM)` 메시지와 함께 프로세스가 강제 종료되는 현상 기록.
  * `CPU_MAX_OCCUPY=80` (또는 50% 초과) 설정 환경에서 실행 시 약 30초 후 종료되며 exit 코드 `143`을 반환함 서술.

---

#### 2. Evidence & Logs (증거 자료)

  1. **핵심 종료 로그 발췌**: 내부 Load 수치 상승 및 Watchdog 비상 종료 로그 첨부.
     ```text
     2026-10-08 07:25:10,102 [WARNING] [SafetyGuard] CPU Threshold Violated! Current Load: 54.14%
     2026-10-08 07:25:10,105 [CRITICAL] [Watchdog] WATCHDOG: INITIATING EMERGENCY ABORT (SIGTERM)
     >>> SYSTEM STATUS: EMERGENCY ABORT (CPU Limit Exceeded) <<<
     ```
  2. **관제 수치 및 분석**:
     * 프로세스의 측정이 약 1.7%로 작게 잡히는 이유는 부하 작업이 3.1초마다 0.1초 동안만 54% 부하로 실행되기 때문임 
     * 시스템 전체 idle 수치는 99.6%~99.8%로 영향이 없으나 대상 프로세스의 내부 부하 지표만 급상승함을 제시.
  3. **설정값 변경 전후 수치 비교 표**:
     | CPU_MAX_OCCUPY | 최고 Load | 결과 | 생존 시간 | 종료 코드 |
     | :--- | :--- | :--- | :--- | :--- |
     | `100` | 50.75% | WATCHDOG SIGTERM | 24초 | 143 |
     | `80` | 55.51% | WATCHDOG SIGTERM | 34초 | 143 |
     | `30` | 30.00% | 정상 동작 (Cooldown 유지) | 1분 53초 이상 | - |

---

#### 3. Root Cause Analysis (원인 분석)

  * **연산 부하 발생**: 프로세스 내부 연산 루프가 실행되며 CPU 부하가 상승하는 과점유 현상 발생.
  * **Watchdog 보호 정책 동작**: `CPU_MAX_OCCUPY` 설정값과 별개로 애플리케이션 내부의 `Watchdog` 안전장치는 부하가 약 50%를 초과하는 순간 전체 시스템 다운을 방지하기 위해 `SIGTERM` 시그널(exit 143)을 발송해 프로세스를 강제 종료시킴.

---

#### 4. Workaround & Verification (조치 및 검증)

  * **임시 조치**: `~/.bash_profile` 내 `CPU_MAX_OCCUPY` 수치를 기존 80%에서 30%로 하향 조정.
    ```bash
    sed -i 's/^export CPU_MAX_OCCUPY=.*/export CPU_MAX_OCCUPY=30/' ~/.bash_profile
    source ~/.bash_profile
    ```
  * **Before & After 검증 결과**:
    * **Before (`CPU_MAX_OCCUPY=80`)**: 부하 55.51% 도달 시 Watchdog에 의해 `SIGTERM` 강제 종료 (생존 34초).
    * **After (`CPU_MAX_OCCUPY=30`)**: 부하가 30%에 도달하면 `Peak reached` ➔ `Cooldown` 모드로 전환되어 부하를 5%까지 식히는 과정을 반복하며 종료 없이 1분 53초 이상 지속 동작함.
  * **근본적 해결 제안**: 소스 코드 내 비효율적 연산 루프 최적화, 작업 실행 주기(Interval) 조정, CPU 프로파일링을 통한 병목 지점 개선, 또는 cgroups/Docker CPU Limit을 통한 하드웨어 차원의 자원 제한 제안.


#### 확인
---
**CPU_MAC_OCCUPY=100**

<img src="./images/CPU_100.png" alt="CPU_MAX_OCCUPY=100" width="850">


**CPU_MAC_OCCUPY=80**

```bash
pkill -9 -f agent-leak-app
pkill -9 -f monitor.sh
> /var/log/agent-app/agent_app.log
> /var/log/agent-app/monitor.log
sed -i 's/^export CPU_MAX_OCCUPY=.*/export CPU_MAX_OCCUPY=80/' ~/.bash_profile
source ~/.bash_profile


(sleep 2; while ~/agent-app/bin/monitor.sh > /dev/null; do sleep 3; done) &$AGENT_HOME/agent-leak-app-arm64
```

```bash
tail -f /var/log/agent-app/monitor.log
```

```bash
top -b -d 3 -n 15 -p $(pgrep -n -x agent-leak-app-)
```
<img src="./images/CPU_memory.png" alt="WATCHDOG" width="850">

---

<img src="./images/CPU_top_log.png" alt="top_CPU 급상승" width="850">

- 앱 Current Load 5% → 55.51%, 프로세스 CPU 0.3% → 2.0%
- 시스템 idle은 99.3~96.8%로 변화 없음
- Load 55.51%에서 CPU Threshold Violated! → WATCHDOG ... (SIGTERM), exit 143
- Tasks: 0 total : 임계치 초과 시 왓치독(Watchdog) 보호 조치 등에 의해 프로세스가 강제 종료됨을 보여줌

측정값이 작은 이유: 부하 작업이 약 3.1초마다 0.1초 동안만 실행됩니다. 54% × 0.1초 / 3.1초 ≈ 1.7%로 측정값과 같습니다.



---

**CPU_MAC_OCCUPY=30**

<img src="./images/cpu쿨다운.png" alt="CPU_MAC_OCUUPY30" width="850">

---
<img src="./images/CPU_30_log.png" alt="Watchdog 종료 없음" width="850">

- 30%에서 Peak reached → 5%까지 cooldown → 다시 증가를 반복
- Watchdog 종료 없음


#### 궁극적인 원인 분석
- 힙 덤프 분석을 통해 적절하게 힙 덤프가 떨어지도록 옵션을 설정

* **근본적인 해결**
  * 소스코드 및 알고리즘 최적화(애플리케이션 레벨)
    - 비 효율성 연산 및 무한 루프를 효율적인 구조로 변경
    - 작업주기 조정 : 부하 유발하는 작업의 타이머, 실행 간격을 조정=> CPU점유 빈도를 낮춤

  * CPU 프로파일링 및 병목 구간 진단
    - 프로 파일링 툴 활용: pref, 언어별 CPU 프로파일러 등을 사용하여 **정밀 추적**
    - 스레드 경쟁 최소화 : 멀테 스레드 환경에서 락(Lock) 대기나 불 필요한 스레드 동기화로 인한 CPU 낭비 점검

  * 인프라 및 운영관점의 자원제어
    - 프로세스 우선순위 조정 => 해당 프로세스의 우선순위를 낮춤 => CPU를 과도하게 점유해도 운영체제나 핵심 시스템 서비스가 영향 X
    - 자원 할당 제한(Cgroup/Docker limits): 도커나 OS 컨테이너 설정(--cpus)를 통해 특정 프로세스가 사용할 수 있는 최대 CPU코어 수나 사용률을 물리적으로 제한하여 시스템 전체의 다운 방지