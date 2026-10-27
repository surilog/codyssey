# Redis 엔진, 메모리 정책 및 명령어 처리 핵심 정리

본 문서는 필기 노트와 소스 코드 분석을 바탕으로, **Mini-Redis의 중앙 관제탑(`mini_redis.py`)의 삼각 공조 메커니즘**, **UTF-8 바이트 단위 메모리 추적 모델과 LRU Eviction**, **단일 엔트리 OOM 및 덮어쓰기 메모리 누수 트러블슈팅**, **최소 힙 기반 지연 만료(Lazy Invalidation)**, **1:N 발행-구독(Pub/Sub) 브로커 설계**, 그리고 **`shlex` 기반 REPL CLI와 Redis 6대 표준 응답 규격**을 총정리한 학습 문서입니다.

---

## 1. Mini-Redis 중앙 제어 엔진 (`mini_redis.py`)

`mini_redis.py`는 스스로 모든 데이터를 직접 저장하지 않고, 하위의 3대 핵심 자료구조 객체를 지휘하여 데이터베이스의 핵심 연산을 $O(1)$ 및 $O(\log N)$에 완수합니다.

```text
               ┌─────────────────────────────────────────┐
               │        Mini-Redis 중앙 관제 엔진         │
               └─────────────────────────────────────────┘
                 /                  |                  \
       지시 1: 데이터 저장     지시 2: 캐시 신선도    지시 3: 만료시간 감시
                /                   |                   \
               ▼                    ▼                    ▼
     ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
     │  1. HashMap (db) │ │2.DoublyList (lru)│ │ 3. MinHeap (ttl) │
     │  - O(1) 초고속 조회│ │- O(1) 최근 사용  │ │- O(log N) 스케줄러│
     │  - [LRU 노드 주소] │ │- Head: 최신(MRU) │ │- Root: 최단 만료 │
     │    자체를 값에 보관│ │- Tail: 낡음(LRU) │ │  O(1) 선제 감시  │
     └──────────────────┘ └──────────────────┘ └──────────────────┘
```

### 1) 왜 HashMap의 Value에 Node 포인터를 저장하는가? (LRU $O(1)$의 비밀)
- 일반적인 큐나 배열로 LRU를 관리하면, 특정 키가 조회되었을 때 해당 키를 찾아 맨 앞으로 옮기기 위해 전체를 순회해야 하므로 **$O(N)$의 치명적 지연**이 발생합니다.
- Mini-Redis는 `HashMap`의 Value 자리에 단순 데이터 문자열이 아니라 **이중 연결 리스트의 `Node` 메모리 주소(참조)**를 저장합니다.
- `GET` 요청 시:
  1. `HashMap`에서 Key로 해당 노드 주소를 **$O(1)$**에 즉시 찾습니다.
  2. `DoublyLinkedList.move_to_front(node)`를 호출하여 앞뒤 포인터만 재연결함으로써 **$O(1)$**만에 맨 앞으로 순간이동시킵니다.
  3. **결과:** 검색과 캐시 순서 갱신 모두를 완벽한 **$O(1)$**에 완수합니다.

---

## 2. 메모리 관리 모델 및 트러블슈팅

### 1) 개수 제한에서 바이트 단위 모델로의 전환
초기의 단순 키 개수 제한 방식에서 실제 Redis와 동일한 **UTF-8 바이트 단위 총 용량(`used_memory`) 추적 모델**로 전환했습니다.

$$\text{used\_memory} = \sum \Big( \operatorname{len}(\operatorname{utf8}(key)) + \operatorname{len}(\operatorname{utf8}(value)) \Big)$$

```python
def _get_bytes(self, key: str, value: str) -> int:
    # 포인터/노드 오버헤드는 배제하고 순수 텍스트 페이로드 바이트만 정밀 합산
    return len(str(key).encode('utf-8')) + len(str(value).encode('utf-8'))
```

---

### 2) LRU 캐시 강제 축출 (Eviction) 루프
- **발동 조건**: `maxmemory > 0 and used_memory > maxmemory`
- **동작 흐름**:
  1. `self.lru_list.remove_back()`을 호출해 가장 오랫동안 참조되지 않은 꼬리 노드(`dummy_tail.prev`)를 $O(1)$에 잘라냅니다.
  2. 축출된 노드의 바이트 크기를 가계부에서 차감합니다: `self.used_memory -= self._get_bytes(oldest_node.key, oldest_node.value)`
  3. `self.db.remove(oldest_node.key)`로 해시맵에서도 동기화하여 삭제합니다.
  4. `self.evicted_keys += 1` 카운터를 증가시킵니다.
  5. `used_memory <= maxmemory`가 될 때까지 이 과정을 반복합니다.

---

### 3) 🛠️ 실전 트러블슈팅 포인트 (필기 노트 13, 14장 핵심)

#### ① 단일 엔트리 OOM (Out Of Memory) 사전 방어
- **문제 상황**: 새로 들어올 단일 데이터의 크기 자체가 `maxmemory` 한도보다 큰 경우 (`entry_bytes > self.maxmemory`).
- **해결 원칙**: 기존 캐시 데이터를 전부 다 지워도 새 데이터를 담을 수 없습니다. 따라서 **기존 데이터를 절대 1건도 삭제하지 말고, 저장을 즉시 거부하며 OOM 에러를 반환**해야 합니다.
```python
if self.maxmemory > 0 and entry_bytes > self.maxmemory:
    return f"(error) OOM command not allowed when used_memory > '{self.maxmemory}'"
```

#### ② 기존 키 덮어쓰기 메모리 누수 방어 (3단계 가계부 정산 원칙)
- **문제 상황**: `"username": "Tom"`(11바이트)이 존재하는 상태에서 사용자가 `"Christopher"`(20바이트)로 덮어쓸 때, 새 바이트만 무조건 더하면 이미 사라진 옛날 11바이트가 장부에 유령처럼 남아 **메모리 누수와 조기 OOM**이 터집니다.
- **해결 원칙 (반드시 3단계를 순서대로 수행)**:
  1. **기존 바이트 차감**: `self.used_memory -= self._get_bytes(lru_node.key, lru_node.value)`
  2. **값 수정**: `lru_node.value = value`
  3. **새 바이트 합산**: `self.used_memory += entry_bytes`
  4. **순서 갱신**: `self.lru_list.move_to_front(lru_node)`

#### ③ 만료 키 및 명시적 삭제(`DEL`) 시 3대 저장소 동시 정리
- `DEL` 명령 또는 TTL 만료 시, 3대 저장소 중 한 곳이라도 정리를 빠뜨리면 데이터 불일치가 발생합니다:
  1. **가계부 차감**: `self.used_memory -= self._get_bytes(...)`
  2. **LRU 큐 정리**: `self.lru_list.remove_node(lru_node)`
  3. **해시맵 정리**: `self.db.remove(key)`
  4. **만료 장부 정리**: `self.key_ttl.pop(key, None)`

---

## 3. TTL (Time-To-Live) 만료 시간 처리 정책

### 1) 선제적 만료 정리: `_clean_expired()`
- 모든 조회/수정 명령(`GET`, `SET`, `DEL`, `EXPIRE`, `KEYS` 등)은 **실제 작업에 들어가기 전 가장 먼저 `_clean_expired()`를 호출**합니다.
- 만료된 데이터가 검색 결과에 노출되는 왜곡을 방지하기 위한 **지연 만료(Lazy Expiration / Passive Expiration)** 정책입니다.

```python
def _clean_expired(self) -> None:
    current_time = time.time()
    while not self.ttl_heap.is_empty():
        peek_item = self.ttl_heap.peek()
        if peek_item is None:
            break
        expire_at, key = peek_item

        # 1. 힙의 루트(최단 만료 시각)가 아직 미래라면?
        if expire_at > current_time:
            break  # 뒤에 있는 수만 개 데이터는 볼 것도 없이 즉시 O(1) 종료!

        # 2. 만료 시각이 도달한 노드 꺼내기
        self.ttl_heap.pop()

        # 3. 고스트 노드(무효화된 만료 데이터) 필터링
        if hasattr(self, "key_ttl") and key in self.key_ttl and self.key_ttl[key] != expire_at:
            continue  # 중간에 덮어써졌거나 연장된 과거 찌꺼기이므로 무시

        # 4. 실제 DB, LRU 리스트에서 제거 및 메모리 차감
        lru_node = self.db.get(key)
        if lru_node:
            self.used_memory -= self._get_bytes(lru_node.key, lru_node.value)
            self.lru_list.remove_node(lru_node)
            self.db.remove(key)
```

### 2) 힙 지연 무효화 (Lazy Invalidation) 전략
- **배경**: 최소 힙의 루트 확인은 $O(1)$이지만, 힙 중간에 위치한 특정 키의 만료 시각을 수정하거나 삭제하려면 배열 전체를 선형 탐색해야 하므로 **$O(N)$의 치명적 병목**이 생깁니다.
- **해결책**:
  - `SET`으로 키가 덮어써지거나 `DEL`로 지워져도 힙 내부는 건드리지 않고 방치합니다.
  - 별도의 가계부 딕셔너리(`self.key_ttl[key] = 최신시각`)에만 적어둡니다.
  - 힙의 루트로 올라왔을 때 `self.key_ttl[key] != expire_at` 조건을 통해 **유효하지 않은 옛날 노드면 조용히 `continue`로 버립니다.**

### 3) 덮어쓰기 시 기존 TTL 초기화 규칙
- 사용자가 `SET key value` (TTL 옵션 생략) 명령으로 기존 키를 덮어쓰면, **기존에 걸려 있던 타이머는 해제되어 "영구 보관 키"**로 바뀌어야 합니다.
- 따라서 `set()` 메서드 내부에서 `ttl is None`일 때 `self.key_ttl.pop(key, None)`을 실행하여 기존 만료 스케줄을 제거합니다.

### 4) Redis 표준 상태 코드
- `EXPIRE key seconds`: 키가 없으면 `0`, 정상 설정 시 `1` 반환. (`seconds <= 0`이면 즉시 삭제 후 `1` 반환)
- `TTL key`: 키가 없으면 `-2`, 키는 있으나 TTL이 없으면 `-1`, 남아있으면 남은 초 `(integer) N` 반환.

---

## 4. 실시간 메시징 브로커 (`pubsub.py`)

카카오톡 단체 채팅방이나 유튜브 알림처럼 **1:N 비동기 메시지 방송**을 지원하는 모듈입니다. 파이썬 내장 `dict`나 `set` 없이 직접 구현한 3대 자료구조를 결합했습니다.

```text
[장부 1: self.channels (HashMap)] ──> 채널 중심 장부
  "news" ───> [DoublyLinkedList] ───> [Subscriber A] <=====> [Subscriber B]

[장부 2: self.client_channels (HashMap)] ──> 클라이언트 중심 장부
  "cli_client" ───> [DoublyLinkedList] ───> ["news"] <=====> ["sports"]

[Subscriber 객체 내부]
  ├── client_id: "cli_client"
  └── message_queue: Queue()  <── linear_structures.py에서 구현한 선입선출 큐!
```

### 1) 왜 HashMap을 2개로 양방향 매핑했는가?
1. **`self.channels`**: 특정 채널에 메시지를 발행(`publish`)할 때, 채널명을 키로 구독자 연결 리스트를 찾아 $O(1)$에 일제히 브로드캐스팅하기 위함.
2. **`self.client_channels`**: 특정 클라이언트가 현재 구독 중인 채널 수(`chan_list.size`)를 $O(1)$에 파악하고, 구독 취소(`unsubscribe`) 시 역방향 전수 조사를 방지하기 위함.

### 2) `curr` vs `curr.value` (택배 상자 비유)
- 연결 리스트를 순회할 때 `curr`는 앞뒤 포인터(`prev`, `next`)를 가진 **포장 상자(Node)**입니다.
- 진짜 우편함(`message_queue`)을 가진 알맹이는 상자 내부인 **`curr.value` (Subscriber 객체)**입니다.
- 따라서 반드시 `subscriber = curr.value`로 꺼낸 뒤 `subscriber.message_queue.enqueue((channel, message))`를 호출해야 합니다.

### 3) 유령 채널 메모리 누수 방지
- 어떤 채널에서 마지막 구독자가 탈퇴하여 구독자 수가 0명이 되면(`sub_list.size == 0`), `self.channels.remove(channel)`을 호출해 빈 채널 껍데기 엔트리 자체를 해시맵에서 제거하여 메모리 누수를 방지합니다.

---

## 5. 보너스 과제: Redis List 명령어 구현 (`lpush`, `lpop`, `lrange`)

`mini_redis.py`의 `self.db` 해시맵 Value 자리에 단순 문자열 대신 **`DoublyLinkedList` 인스턴스를 통째로 저장**하여 덱(Deque) 구조로 동작시킵니다.

- **`lpush(key, value)`**:
  - 키가 없으면 새 `DoublyLinkedList`를 만들어 헤드에 노드를 추가하고 DB에 등록.
  - 이미 키가 있다면 `isinstance(lst, DoublyLinkedList)`로 검증 후 `insert_front(key, value)` 수행.
  - 만약 일반 String 키에 `LPUSH`를 시도하면 Redis 표준 에러인 `WRONGTYPE Operation against a key holding the wrong kind of value` 예외를 발생시킴.
- **`lpop(key)`**:
  - 연결 리스트의 맨 앞 노드를 `remove_front()`로 꺼내 반환.
  - **빈 키 자동 청소**: 마지막 원소를 꺼내 리스트가 완전히 비게 되면(`lst.size == 0`), `self.delete(key)`를 호출해 껍데기 키를 DB에서 자동 소멸시킴.
- **`lrange(key, start, stop)`**:
  - `lst.get_range(start, stop)`를 호출하여 음수 인덱스(`-1` 등)를 지원하는 구간 슬라이싱 리스트 반환.

---

## 6. CLI 인터페이스 및 Redis 프로토콜 파서

### 1) 대화형 REPL과 `shlex` 파서 (`main.py`)
- 일반 `.split()`을 쓰면 `SET user:1 "Hello World" EX 10` 입력 시 큰따옴표 안의 공백까지 쪼개져 6개 토큰으로 잘못 잘립니다.
- 파이썬 표준 라이브러리인 **`shlex.split()`**을 도입하여 큰따옴표 안의 문자열을 하나의 묶음으로 온전히 보존합니다.
- 사용자가 닫는 따옴표를 빼먹었을 때 발생하는 `ValueError`를 캐치하여 프로세스 다운 없이 `(error) ERR syntax error or unclosed quote`를 띄웁니다.
- **무중단 예외 처리**: 어떤 런타임 오류가 발생해도 `try-except`로 감싸 REPL 세션이 종료되지 않으며, `Ctrl+C`(`KeyboardInterrupt`) 입력 시에만 정상 종료(Graceful Shutdown)합니다.

---

### 2) 동적 디스패치와 Redis 6대 표준 응답 (`command_executor.py`)

`getattr(self, f"do_{cmd_name}", None)`을 활용하여 명령어 이름에 따라 적절한 핸들러 메서드로 자동 라우팅합니다 (OCP 개방-폐쇄 원칙 준수).

#### [Redis 6대 핵심 표준 응답 포맷]

| 상태 및 반환 유형 | 내부 반환값 예시 | Redis 표준 출력 규격 포맷 |
| :--- | :--- | :--- |
| **단순 성공 문자열** | `"OK"` | `OK` |
| **널 데이터 / 미존재** | `None` | `(nil)` |
| **정수 반환 (카운트/불리언)** | `1`, `0` | `(integer) 1`, `(integer) 0` |
| **문자열 반환** | `"Alice"` | `"Alice"` (큰따옴표로 감싸서 반환) |
| **배열/목록 반환** | `["first", "second"]` | `1) "first"`<br>`2) "second"` |
| **빈 배열** | `[]` | `(empty array)` |

#### [표준 에러 포맷팅 규칙]
- 알 수 없는 명령: `(error) ERR unknown command '<cmd>'`
- 인자 개수 오류: `(error) ERR wrong number of arguments for '<cmd>' command`
- 정수 파싱 실패: `(error) ERR value is not an integer or out of range`
- 메모리 한도 초과: `(error) OOM command not allowed when used_memory > '<maxmemory>'`
- 자료형 불일치: `(error) WRONGTYPE Operation against a key holding the wrong kind of value`

