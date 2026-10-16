###  교착상태(Deadlock) GitHub Issue 리포트

```markdown
[Bug] Deadlock - 멀티스레드 자원 순환 대기로 인한 프로세스 무응답(Hang) 장애
```

#### 0. 개념

- 둘 이상의 스레드 또는 프로세스가 각각 자원을 점유한 상태에서, 서로가 각기 다른 스레드가 점유하고 있는 자원을 무한히 기다리며 다음 처리를 진행하지 않는 교착 상태를 의미.

- 발생 조건 (4가지 모두가 존재해야 Deadlock 발생)
  - 상호 배제 : 하나의 공유자원에 두 개 이상의 프로세스가 접근 X
  - 점유 대기 : 하나의 자원을 점유하고 있는 프로세스가 다른 자원을 얻기 위해서는 요청을 하고 대기해야 함.
  - 비선점 : 특정 프로세스가 어떤 자원을 사용하고 있는데 해당 자원 사용이 끝나기 전까지 뺏을 수 X
  - 순환 대기: 프로세스들이 서로 사용하고 있는 자원에 대해서 순환적으로 대기하는 형태.

#### 1. Description (현상 설명)

  * `agent-leak-app` 실행 후 프로세스가 강제 종료되지 않고 `PID`는 유지되어 있으나, CPU 점유율이 0.0%로 정체되고 신규 로그 생성이 완전히 중단되는 무응답(Hang) 현상 서술.
  * `MULTI_THREAD_ENABLE=true` 설정 환경에서 멀티스레드 워커가 동시 작업을 수행할 때 발생함을 기록.

---

#### 2. Evidence & Logs (증거 자료)

  1. **스레드 락 대기 상태 증거 (`ps -L`)**: 모든 워커 스레드가 커널 락 대기 함수인 `futex_do_wait`에 진입해 멈춰 있음을 제시.

```bash
ps -L -o pid,lwp,stat,pcpu,wchan:20,comm -p $PID
top -H -b -n 1 -p $PID | tail -4
    PID     LWP STAT %CPU WCHAN                COMMAND
 558355  558355 SNl+  1.2 futex_do_wait        agent-leak-app-
 558355  558357 Sl+   0.0 futex_do_wait        agent-leak-app-
 558355  558742 SNl+  0.0 futex_do_wait        agent-leak-app-
 558355  558743 SNl+  0.0 futex_do_wait        agent-leak-app-
```
  2. **관제 스크립트(`monitor.log`) 정체 증거**: CPU 점유율이 0.0%로 고정되고, 로그 미갱신으로 `LOG_IDLE` 시간이 지속해서 증가하는 현상 표출.
```bash
[2026-10-13 14:29:32] PID:558355 STAT:S CPU: 0.0% RSS:36MB MEM: 0.4% LOG_IDLE:1009s
[2026-10-13 14:29:32] PID:612548 STAT:S CPU:% RSS:MB MEM:% LOG_IDLE:1009s
[2026-10-13 14:29:32] PID:612548 STAT:S CPU:% RSS:MB MEM:% LOG_IDLE:1009s
[2026-10-13 14:29:32] PID:612548 STAT:S CPU:% RSS:MB MEM:% LOG_IDLE:1009s
[2026-10-13 14:29:32] PID:558355 STAT:S CPU: 0.0% RSS:36MB MEM: 0.4% LOG_IDLE:1009s
[2026-10-13 14:29:35] PID:558355 STAT:S CPU: 0.0% RSS:36MB MEM: 0.4% LOG_IDLE:1012s
[2026-10-13 14:29:35] PID:558355 STAT:S CPU: 0.0% RSS:36MB MEM: 0.4% LOG_IDLE:1012s
[2026-10-13 14:29:36] PID:612733 STAT:S CPU:% RSS:MB MEM:% LOG_IDLE:1013s
[2026-10-13 14:29:36] PID:612740 STAT:S CPU:% RSS:MB MEM:% LOG_IDLE:1013s
[2026-10-13 14:29:36] PID:612740 STAT:S CPU:% RSS:MB MEM:% LOG_IDLE:1013s
```

---

#### 3. Root Cause Analysis (원인 분석)

  * **자원 경합 구조**: 스레드 1(`Shared_Memory_A` 점유 후 `Socket_Pool_B` 대기)과 스레드 2(`Socket_Pool_B` 점유 후 `Shared_Memory_A` 대기)가 서로 상대방이 쥐고 있는 자원을 무한히 기다리는 **순환 대기(Circular Wait)**가 원인.
  * **데드락 4대 조건 성립**:
    1. **상호 배제 (Mutual Exclusion)**: 락 자원을 단일 스레드만 독점 사용.
    2. **점유 대기 (Hold and Wait)**: 자원 하나를 쥔 채 추가 자원을 요청하며 대기.
    3. **비선점 (No Preemption)**: 타 스레드의 자원을 강제로 빼앗을 수 없음.
    4. **순환 대기 (Circular Wait)**: 대기 관계가 고리(Circle) 형태를 형성함.
  * 결과적으로 커널 수준의 `futex_do_wait` 대기열에서 스레드들이 갇혀 CPU 자원을 소모하지 못하고 완전히 얼어붙게 됨.

---

#### 4. Workaround & Verification (조치 및 검증)

  * **임시 조치**: 멈춰있는 데드락 프로세스를 `pkill`로 강제 정리한 뒤, `~/.bash_profile` 내 `MULTI_THREAD_ENABLE` 값을 `false`로 전환.
    ```bash
    pkill -f agent-leak-app
    sed -i 's/^export MULTI_THREAD_ENABLE=.*/export MULTI_THREAD_ENABLE=false/' ~/.bash_profile
    source ~/.bash_profile
    ```
  * **Before & After 검증 결과**:
    * **Before (`MULTI_THREAD_ENABLE=true`)**: 락 대기로 인해 `futex_do_wait` 상태에 빠지며 `LOG_IDLE`이 27초 이상 지속 상승함.
    * **After (`MULTI_THREAD_ENABLE=false`)**: 자원 경합 요인이 제거되어 `WAITING/BLOCKED`가 0건이 되고, `LOG_IDLE`이 0~1초로 유지되며 순차적으로 작업이 완료됨.
  * **근본적 해결 제안**:
    * **락 오름차순 정렬**: 모든 스레드에서 락 획득 순서를 동일하게 강제하여 **순환 대기** 조건을 차단.
    * **임계 구역 최소화**: 락의 범위를 줄이거나, 자원을 얻지 못하면 기존 락을 반납하고 재시도하는 타임아웃 기법 도입.



**MULTI_THREAD_ENABLE=true**

```bash
pkill -9 -f agent-leak-app
pkill -9 -f monitor.sh
> /var/log/agent-app/agent_app.log
> /var/log/agent-app/monitor.log
sed -i 's/^export MULTI_THREAD_ENABLE=.*/export MULTI_THREAD_ENABLE=true/' ~/.bash_profile
source ~/.bash_profile


(sleep 2; while ~/agent-app/bin/monitor.sh > /dev/null; do sleep 3; done) &$AGENT_HOME/agent-leak-app-arm64
```

```bash
ps -ef | grep agent-leak | grep -v grep

PID=$(pgrep -n -x agent-leak-app-)
ps -L -o pid,lwp,stat,pcpu,wchan:20,comm -p $PID
top -H -b -n 1 -p $PID | tail -4

stat -c '%y %s bytes' $AGENT_LOG_DIR/agent_app.log
sleep 30
stat -c '%y %s bytes' $AGENT_LOG_DIR/agent_app.log


tail -n 10 $AGENT_LOG_DIR/agent_app.log

```

<img src="/images/deadlock_PID_thread.png" alt="PID및 스레드 상태 진단" width="850">

---

<img src="/images/deadlock_final_log.png" alt="마지막 로그 지점" width="850">

- PID 모두 유지
- 스레드 3개 모두 futex_wait (락 대기), CPU 0.0%(자원 얻지 못해 완전 동결)
- 모든 워커 스레드(LWP 558355, 558357, 558742, 558743)의 대기 커널 함수가 무한 대기 상태(for lock 얻고 싶어서)



**MULTI_THREAD_ENABLE=false**



<img src="/images/deadlock_after.png" alt="THREAD:False" width="850">

---
<img src="/images/Deadlock_PID_after.png" alt="THREAD:False" width="850">

---
<img src="/images/deadlock_after_.png" alt="THREAD:False" width="850">

- 파일 크기가 14857 bytes에서 16154 bytes로 증가하였고 수정 시각도 최신 시간으로 갱신 => 로그가 멈추지 않고 정상적으로 계속 기록

- MemoryWorker의 힙 메모리 추이(Current Heap: 400MB → 500MB)와 CpuWorker의 부하 및 쿨다운 상태(Current Load: 50.00% → 37.29%) 로그가 타임스탬프와 함께 끊김 없이 기록

- 스레드별 CPU 사용률도 1.3%, 0.9% 등으로 정상 측정되며 활성화
- 워커 스레드들(LWP 669313, 669314 등)의 커널 대기 함수가 무한 락 대기 상태인 futex_do_wait 고착에서 벗어나, poll_schedule_timeout 등 정상적인 주기적 대기 및 폴링 상태로 전환


| 항목 | true (교착상태 발생) | false (정상 해소) |
| --- | --- | --- |
| **로그** | `WAITING ... BLOCKED` 이후 정지| 계속 기록|
| **스레드** | 모두 `futex_wait`<br> |워커`do_select`<br> |
| **CPU** | 0.0% 고정| 0.9 ~ 1.3%|
| **LOG_IDLE** | 8s → 56s| 1s|

