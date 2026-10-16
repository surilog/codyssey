###  OOM 리포트

```markdown
[Bug] OOM Crash - 메모리 누수에 의한 MemoryGuard 보호 정책 프로세스 강제 종료
```

#### 0. 개념

* **원인**
  - 설정 오류
  - 과부하(사용량 초과)
  - 버그(JVM)등

* **정의**
: Heap 메모리에 할당된 데이터를 다 사용한 후에도 해제하지 않고 지속적으로 쌓아두면 메모리 사용량이 계속 증가

* **궁극적인 원인 분석**
  - 힙 덤프 분석 => 적절하게 힙 덤프가 떨어지도록 옵션을 설정
    - (ex) `kill -9` 스스로 죽임
    - (ex)  **힙 덤프를 떨어드리는 옵션 예시추가**

* **설명 아키텍처**
  * OOM현상이 나타는 아키텍처 추가
---
#### 1. Description (현상 설명)

  * `agent-leak-app` 실행 후 시간 경과에 따라 물리 메모리(RSS) 점유량이 지속 상승하다가, 설정된 임계치(`MEMORY_LIMIT=256MB`)에 도달하면 `SELF-TERMINATED` 메시지와 함께 예고 없이 강제 종료되는 현상 발생
  
  * 약 33초 경과 시점에서 프로세스가 비상 종료(`exit 137`)됨을 확인

---

#### 2. Evidence & Logs (증거 자료)
* **필수 포함 증거 3가지**:
  1. **`MEMORY_LIMIT : 255 ` 관제 수치**: 3초 간격으로 RSS 메모리가 약 25MB씩 선형적으로 급격히 증가하는 추이 기록.
   


  2. **핵심 종료 로그 발췌**: 메모리 한계 초과 및 강제 종료 관련 로그 서술.

  
     ```text
     2026-10-08 07:03:50,682 [CRITICAL] [MemoryGuard] Memory limit exceeded (275MB >= 256MB)
     2026-10-08 07:03:50,683 [CRITICAL] [MemoryGuard] Self-terminating process 118 to prevent system instability.
     >>> SYSTEM STATUS: SELF-TERMINATED (Memory Limit Exceeded) <<<
     ```
  3. **`MEMORY_LIMIT` 변경 전후 생존 시간 비교 표**:
     | MEMORY_LIMIT | 생존 시간 | 결과 및 종료 코드 |
     | :--- | :--- | :--- |
     | `128MB` | 약 17초 | SELF-TERMINATED (exit 137) |
     | `256MB` | 약 33초 | SELF-TERMINATED (exit 137) |
     | `512MB` | 2분 이상 지속 생존 | 정상 동작 (Memory Cache Flushed) |

     <img src="/images/OOM_512_app_log.png" alt="MEMEORY_LIMIT 변경 후" width="850">

---

#### 3. Root Cause Analysis (원인 분석)

  * **애플리케이션 결함**: 힙(Heap) 메모리에 할당된 데이터를 다 사용한 후에도 해제(Release)하지 않고 지속적으로 적재하는 메모리 누수(Memory Leak) 결함 존재.
  * **보호 정책 동작**: 물리 메모리가 `MEMORY_LIMIT` 수치에 도달하자, 시스템 전체의 다운이나 불안정을 방지하기 위해 애플리케이션의 `MemoryGuard` 정책이 프로세스를 비상 종료(`SIGKILL`, exit 137)시킴.

---

#### 4. Workaround & Verification (조치 및 검증)

  * **임시 조치**: `~/.bash_profile` 내 `MEMORY_LIMIT` 수치를 256MB에서 512MB로 상향 조정.
  * **Before & After 검증**:
    * **Before (256MB)**: 275MB 도달 시 강제 종료 (생존 시간 33초).
    * **After (512MB)**: 525MB 도달 시 종료되지 않고 `Memory Cache Flushed` 로그와 함께 메모리를 비워내며(517MB ➔ 17MB) 2분 이상 안정적으로 동작 유지.
  * **근본적 해결 제안**: 환경변수 조정은 당장의 종료를 미루는 임시 조치이므로, 소스 코드 내에서 불필요한 데이터를 주기적으로 삭제(Eviction/Pop)하거나 TTL을 설정하는 코드 리팩토링 및 메모리 프로파일링이 필요함.


#### 확인
---
**MEMORY_LIMIT=256**

```bash
pkill -9 -f agent-leak-app
pkill -9 -f monitor.sh
> /var/log/agent-app/agent_app.log
> /var/log/agent-app/monitor.log
sed -i 's/^export MEMORY_LIMIT=.*/export MEMORY_LIMIT=256/' ~/.bash_profile
source ~/.bash_profile


(sleep 2; while ~/agent-app/bin/monitor.sh > /dev/null; do sleep 3; done) &$AGENT_HOME/agent-leak-app-arm64
```

<img src="/images/OOM_before.png" alt="Agent READY확인" width="850">

---

<img src="/images/exit_before_OOM.png" alt="OOM 확인[Memory Guard]" width="850">

---

<img src="/images/OOM_PID.png" alt="PROCESS down" width="850">

---

* RSS가 3초마다 약 25MB씩 증가 (41MB → 266MB)
* CPU, 스레드 수는 변화 없음
* 275MB에서 Self-terminating process 3200, exit 137

---
**MEMORY_LIMIT=512**

* 실행
```bash
pkill -9 -f agent-leak-app
pkill -9 -f monitor.sh
> /var/log/agent-app/agent_app.log
> /var/log/agent-app/monitor.log
sed -i 's/^export MEMORY_LIMIT=.*/export MEMORY_LIMIT=512/' ~/.bash_profile
source ~/.bash_profile

(sleep 2; while ~/agent-app/bin/monitor.sh > /dev/null; do sleep 3; done) &$AGENT_HOME/agent-leak-app-arm64
```


<img src="/images/OOM_512_Ready.png" alt="Agent READY확인" width="850">

--- 

<img src="/images/OOM_512_heap.png" alt="HEAP 경고 확인" width="850">

- log기록
```bash
tail -f /var/log/agent-app/monitor.log
```
<img src="/images/OOM_525.png" alt="monitor.log 기록 확인" width="850">

---


```bash
ps -o pid,etime,rss,vsz,stat,cmd -p $(pgrep -n -x agent-leak-app-)

top -b -d 3 -n 15 -p $(pgrep -n -x agent-leak-app-)
```
- ps와 top명령어 확인

<img src="/images/512_top_ps.png" alt="ps, top 명령어 확인" width="850">


- 525MB에서 종료 대신 Memory Cache Flushed, RSS 517MB → 188MB
- 이후 같은 속도로 다시 증가


한도를 올리면 종료는 피하지만 메모리 증가 자체는 그대로임을 알 수 있음


#### 궁극적인 원인 분석
- 힙 덤프 분석을 통해 적절하게 힙 덤프가 떨어지도록 옵션을 설정

* **근본적인 해결**
  * 코드 리팩토링(애플리케이션 레벨)
    - 메모리 누수 원인 제거 : 사용 후 해제되지 않은 힙, 컬렉션(List,MAP) 등에 지속적으로 데이터를 쌓는 로직을 수정
    - 주기적 데이터 정리: 캐시, 임시 저장소에 TTL(Time to Live)설정을 통해 if 한도 초과 시 => 오래된 데이터 삭제
  * 인프라 및 운영 관점의 보완 조치
    - 컨테이너/OS레밸의 리소스 제한(Cgroups):
    애플리케이셔 내부의 'Memory guard'뿐 아니라 운영체제나 도커 컨테이너 자체에 메모리 제한을 설정 => 전체 시스템 다운 방지, 해당 컨테이너만 재가동 되게 함
    - 모니터링 및 알람 연동: monitor.sh와 같은 관제 스크립트나 ARM을 통해 물리 메모리(RSS)가 특정 임계치를 넘을 때 개발자에게 슬랙이나 이메일로 경고 알림
