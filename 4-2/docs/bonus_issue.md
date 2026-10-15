
#### 1. 선점형 라운드 로빈(Round-Robin) 케이스 예시
> (실시간 테스트 중 `Preempted`/`Resumed` 로그가 수차례 발생한 경우)

```markdown
[Analysis] 로그 패턴 분석을 통한 선점형 라운드 로빈 스케줄링 알고리즘 역추론

#### 1. Description (로그 관찰 개요)
`agent-leak-app` 애플리케이션의 정상 실행 상태에서 출력되는 워커(Worker) 스레드들의 실행 타임스탬프와 진행률(Progress %) 로그 데이터를 수집하여, 런타임 스케줄러가 스레드를 할당하는 알고리즘 규칙을 역추적했습니다.

#### 2. Evidence & Logs (증거 자료)
* **스케줄러 작업 등록 순서**: `Registered Tasks: ['Thread-A', 'Thread-B', 'Thread-C']`
* **로그 패턴 분석 (Application Log Snapshot)**:
  ```text
  2026-10-12 14:00:36,180 [INFO] [Thread-A] Task Started. Calculating... (20%)
  2026-10-12 14:00:36,232 [INFO] [Thread-A] Calculating... (40%)
  2026-10-12 14:00:36,284 [INFO] [Thread-A] Preempted. Progress saved at (40%)  <-- Thread-A 중단
  2026-10-12 14:00:36,336 [INFO] [Thread-B] Task Started. Calculating... (20%)
  2026-10-12 14:00:36,388 [INFO] [Thread-B] Calculating... (40%)
  2026-10-12 14:00:36,441 [INFO] [Thread-B] Preempted. Progress saved at (40%)  <-- Thread-B 중단
  2026-10-12 14:00:36,492 [INFO] [Thread-C] Task Started. Calculating... (20%)
  2026-10-12 14:00:36,545 [INFO] [Thread-C] Calculating... (40%)
  2026-10-12 14:00:36,598 [INFO] [Thread-C] Preempted. Progress saved at (40%)  <-- Thread-C 중단
  2026-10-12 14:00:36,650 [INFO] [Thread-A] Resumed. Calculating... (60%)       <-- Thread-A 재개
  ```
* **스위칭 이벤트 수치**: `Preempted` / `Resumed` 발생 건수 총 34건 집계.

#### 3. Algorithm Inference (알고리즘 역추론 및 결론)
1. **FCFS (선착순) 소거**: 먼저 등록된 Thread-A가 100% 완료되기 전에 40% 지점에서 CPU를 반납하고 Thread-B로 넘어가므로 FCFS가 아닙니다.
2. **비선점형 Priority 소거**: 비선점형 방식이라면 한 번 실행을 개시한 스레드가 작업 완료 시까지 CPU를 독점해야 하나, 스위칭 이벤트가 34건 발생했으므로 비선점형이 아닙니다.
3. **선점형 Round-Robin 확정**: 각 스레드가 정해진 타임 슬라이스(약 20%~40% 진행 분량) 동안 CPU를 점유한 후 다음 스레드에 제어권을 양보(`Preempted`)하며 순환 실행되는 시분할 선점형 알고리즘입니다.

#### 4. Technical Analysis & Architecture (기술적 장단점 및 아키텍처 분석)
* **장점**: 모든 스레드가 CPU 자원을 공평하게 분배받아 특정 스레드가 자원을 독점하거나 대기 시간이 무한정 길어지는 기아(Starvation) 현상을 방지합니다.
* **단점**: 스레드 간 자주 교체되는 과정에서 컨텍스트 스위칭(Context Switching) 오버헤드가 발생합니다.
* **적합한 아키텍처**: 사용자 요청에 대해 고르고 빠른 응답 시간이 필수적인 **웹 서버(Web Server)** 및 대화형 시스템에 적합합니다.
