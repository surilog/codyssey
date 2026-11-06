# MiniRedis 전체 명령어 테스트 매뉴얼 & 검증 시나리오

이 문서는 밑바닥부터 직접 구현한 **MiniRedis의 11개 핵심 모듈과 런타임 CLI 명령어**가 과제 요구사항 및 엣지 케이스를 모두 만족하는지 직접 검증할 수 있도록 구성된 종합 테스트 매뉴얼입니다.

---

## 1. 사전 준비 및 터미널 실행

테스트를 진행하기 전, 터미널(Command Prompt 또는 PowerShell)에서 프로젝트 디렉터리로 이동한 뒤 REPL CLI를 실행합니다.

```bash
python main.py
```

프롬프트가 아래와 같이 나타나면 정상적으로 대기 상태에 들어간 것입니다:
```text
mini-redis> 
```

---

## 2. 기본 String 및 CRUD 명령어 검증 (6개)

해시맵(Chaining HashMap)을 기반으로 한 문자열 데이터의 삽입, 조회, 존재 여부 확인, 전체 키 조회, 키 개수 확인 및 삭제 연산을 검증합니다.

```text

```

### 핵심 체크포인트
* 존재하지 않거나 이미 삭제된 키를 `GET`으로 조회했을 때 `(nil)`이 반환되는가?
* 이미 삭제된 키를 다시 `DEL` 했을 때 `(integer) 0`이 반환되는가?

---

## 3. List 타입 데이터 조작 검증 (`DoublyLinkedList` 기반)

이중 연결 리스트를 내부 저장소로 활용하여 양방향 덱(Deque) 방식으로 동작하는 `LPUSH`, `LPOP`, `LRANGE` 명령어를 검증합니다.

```text
# 1. 왼쪽(앞)으로 연속 삽입
mini-redis> LPUSH mylist "world"
(integer) 1

mini-redis> LPUSH mylist "hello"
(integer) 2

# 2. 전체 범위 조회 (0부터 -1까지)
mini-redis> LRANGE mylist 0 -1
1) "hello"
2) "world"

# 3. 왼쪽 원소 꺼내기 (LPOP)
mini-redis> LPOP mylist
"hello"

mini-redis> LRANGE mylist 0 -1
1) "world"

# 4. 마지막 남은 원소 꺼내기 -> 빈 리스트가 되면 DB에서 키 자동 삭제
mini-redis> LPOP mylist
"world"

mini-redis> LPOP mylist
(nil)

mini-redis> EXISTS mylist
(integer) 0
```

### 핵심 체크포인트
* `LPUSH`로 `world` 다음 `hello`를 넣었을 때 `LRANGE` 조회 시 `hello`가 1번 인덱스로 역순 정렬되는가?
* 리스트가 비어있을 때 `LPOP` 시 `(nil)`을 반환하고 해시맵에서도 키가 자동 소멸하는가?

---

## 4. TTL 만료 관리 & 최소 힙(Min-Heap) 검증

최소 힙 기반의 최단 만료 감시, 수동 만료 부여(`EXPIRE`), 남은 만료 시간 조회(`TTL`), 그리고 **기존 키 덮어쓰기 시 만료 초기화** 규칙을 검증합니다.

```text
# 1. SET 시 EX 옵션으로 5초 만료 시간 부여
mini-redis> SET temp "secret" EX 5
OK

mini-redis> TTL temp
(integer) 5

mini-redis> GET temp
"secret"

# (5초 대기 후 실행)
mini-redis> TTL temp
(integer) -2

mini-redis> GET temp
(nil)

# 2. 만료 시간이 없는 일반 영구 키 확인
mini-redis> SET perm "forever"
OK

mini-redis> TTL perm
(integer) -1

# 3. 기존 키에 EXPIRE 명령으로 만료 시간(10초) 부여
mini-redis> EXPIRE perm 10
(integer) 1

mini-redis> TTL perm
(integer) 9

mini-redis> EXPIRE nokey 10
(integer) 0

# 4. [중요 엣지케이스] SET으로 덮어쓸 때 기존 만료 시간(TTL) 초기화 검증
mini-redis> SET temp2 "v1" EX 100
OK

mini-redis> SET temp2 "v2"
OK

mini-redis> TTL temp2
(integer) -1
```

### 핵심 체크포인트
* 만료된 키는 `TTL` 호출 시 `(integer) -2`, `GET` 호출 시 `(nil)`을 반환하는가?
* 만료 설정이 없는 키는 `TTL` 호출 시 `(integer) -1`을 반환하는가?
* `EXPIRE`로 사후에 만료 시간을 설정했을 때 `TTL`이 정상적으로 카운트다운되는가?
* `SET`으로 기존 키를 덮어썼을 때 이전의 100초 만료 스케줄이 초기화되어 `-1`이 되는가?

---

## 5. 메모리 제한(`maxmemory`) & LRU 자동 축출 검증

설정된 `maxmemory`를 초과할 때 이중 연결 리스트의 꼬리(Tail) 노드를 기준으로 가장 오래 참조되지 않은 키가 자동 축출(Eviction)되는지 확인합니다.

```text
# 1. 메모리 한도를 15바이트로 설정
mini-redis> CONFIG SET maxmemory 15
OK

mini-redis> INFO memory
used_memory:0 maxmemory:15 evicted_keys:0

# 2. 단일 엔트리가 maxmemory를 초과할 때 OOM 방어 검증 (24바이트 > 15바이트)
mini-redis> SET huge "12345678901234567890"
(error) OOM command not allowed when used_memory > 'maxmemory'

# 3. 데이터 삽입 (a: 5B, b: 5B -> 총 10B)
mini-redis> SET a "1234"
OK

mini-redis> SET b "1234"
OK

# 4. a를 조회하여 LRU 헤드 최신 상태로 갱신 (가장 오래된 키는 b가 됨)
mini-redis> GET a
"1234"

# 5. c(7B) 삽입 -> 10 + 7 = 17B로 15B 한도 초과! (가장 오래된 b가 자동 축출)
mini-redis> SET c "123456"
OK

# 6. 축출 결과 검증
mini-redis> GET b
(nil)

mini-redis> GET a
"1234"

mini-redis> INFO memory
used_memory:12 maxmemory:15 evicted_keys:1

# 7. 테스트 후 메모리 제한 무제한(0) 복구
mini-redis> CONFIG SET maxmemory 0
OK
```

### 핵심 체크포인트
* `GET a`를 실행했으므로 메모리 초과 시 `a` 대신 `b`가 삭제되는가?
* `INFO memory`에서 `evicted_keys`가 1 증가하고 `used_memory`가 음수로 떨어지지 않는가?

---

## 6. 발행-구독 (Pub/Sub) 메시징 브로커 검증

`HashMap`과 `Queue`를 활용한 채널 기반 메시징 브로커의 동작을 검증합니다.

```text
# 1. 복수 채널 동시 구독
mini-redis> SUBSCRIBE news sports
1) "subscribe"
2) "news"
3) (integer) 1
1) "subscribe"
2) "sports"
3) (integer) 2

# 2. 활성 채널 목록 조회
mini-redis> PUBSUB CHANNELS
1) "news"
2) "sports"

# 3. 메시지 발행 (수신한 구독자 수 반환)
mini-redis> PUBLISH news "Breaking News!"
(integer) 1

# 4. 채널 구독 취소
mini-redis> UNSUBSCRIBE news
1) "unsubscribe"
2) "news"
3) (integer) 1
```

---

## 7. ZSET (이진 탐색 트리 - BST) 정렬 랭킹 검증

이진 탐색 트리(BST)에 `(score, member)` 튜플을 삽입하고 중위 순회(In-order)를 통해 점수 오름차순으로 자동 정렬되는지 확인합니다.

```text
# 1. 점수를 무작위 순서로 삽입
mini-redis> ZADD rank 85 "Bob"
(integer) 1

mini-redis> ZADD rank 95 "Alice"
(integer) 1

mini-redis> ZADD rank 70 "Charlie"
(integer) 1

# 2. 범위 조회 시 자동 오름차순 정렬 확인
mini-redis> ZRANGE rank
1) "Charlie" (Score: 70.0)
2) "Bob" (Score: 85.0)
3) "Alice" (Score: 95.0)

# 3. 비어있는 정렬 집합 조회
mini-redis> ZRANGE empty_rank
(empty list or set)
```

---

## 8. 에러 처리 표준 & CLI 종료 검증

사용자의 잘못된 입력 시 Redis 공식 에러 프로토콜에 맞추어 처리되는지 확인합니다.

```text
# 1. 알 수 없는 명령어 에러
mini-redis> UNKNOWNCMD
(error) ERR unknown command 'UNKNOWNCMD'

# 2. 인자 개수 부족 에러
mini-redis> SET mykey
(error) ERR wrong number of arguments for 'set' command

# 3. 정수 파싱 실패 에러
mini-redis> CONFIG SET maxmemory abc
(error) ERR value is not an integer or out of range

# 4. 부동소수점 점수 파싱 실패 에러
mini-redis> ZADD rank invalid_score "Dave"
(error) ERR value is not a valid float or integer

# 5. CLI 정상 종료
mini-redis> exit
```
