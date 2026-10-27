#  Mini-Redis: In-Memory NoSQL Key-Value 스토리지 엔진

> **파이썬의 내장 컬렉션(`dict`, `set`, `collections`)을 일절 사용하지 않고**,  
> 기본 메모리 인프라부터 해시 테이블, 이중 연결 리스트, 최소 힙, 이진 탐색 트리, Pub/Sub 브로커까지 밑바닥부터 직접 구현하여 완성한 **CLI 기반 고성능 Mini-Redis 데이터베이스 엔진**입니다.

---

##  목차 (Table of Contents)

1. [프로젝트 개요 (Overview)](#1-프로젝트-개요-overview)
2. [전체 시스템 아키텍처 (System Architecture)](#2-전체-시스템-아키텍처-system-architecture)
3. [프로젝트 모듈 구조 및 기술 명세서 (Project Structure & Technical Docs)](#3-프로젝트-모듈-구조-및-기술-명세서-project-structure--technical-docs)
4. [핵심 알고리즘 및 기술적 의사결정 (Technical Decisions)](#4-핵심-알고리즘-및-기술적-의사결정-technical-decisions)
5. [지원 명령어 명세 (Command Specifications)](#5-지원-명령어-명세-command-specifications)
   * [1) String 데이터 조작 명령어](#1-string-데이터-조작-명령어)
   * [2) List 데이터 조작 명령어 (DoublyLinkedList 기반)](#2-list-데이터-조작-명령어-doublylinkedlist-기반)
   * [3) Sorted Set (ZSet) 데이터 조작 명령어 (BST 기반)](#3-sorted-set-zset-데이터-조작-명령어-bst-기반)
   * [4) 메모리 제어 및 시스템 명령어](#4-메모리-제어-및-시스템-명령어)
   * [5) TTL(Time-To-Live) 관리 명령어](#5-ttltime-to-live-관리-명령어)
   * [6) Pub/Sub (발행/구독) 브로커 명령어](#6-pubsub-발행구독-브로커-명령어)
6. [메모리 관리 및 만료 정책 (Memory & Eviction Policy)](#6-메모리-관리-및-만료-정책-memory--eviction-policy)
7. [실행 및 사용 방법 (Getting Started)](#7-실행-및-사용-방법-getting-started)
8. [설계 원칙 및 기술적 제약 사항 (Design Principles & Technical Constraints)](#8-설계-원칙-및-기술적-제약-사항-design-principles--technical-constraints)
9. [시간 복잡도 분석표 (Time Complexity)](#9-시간-복잡도-분석표-time-complexity)

---

## 1. 프로젝트 개요 (Overview)

현대 분산 시스템의 표준 인메모리 스토리지인 **Redis(Remote Dictionary Server)**는 단순한 Key-Value 저장소를 넘어 캐싱, 실시간 세션 관리, 메시지 브로커 등으로 폭넓게 활용됩니다. Redis가 초당 수십만 건의 연산을 처리할 수 있는 본질적인 비결은 **목적에 최적화된 자료구조들의 유기적인 결합**에 있습니다.

본 프로젝트는 고수준 언어가 기본 제공하는 추상화된 자료형의 편의성을 배제하고, 컴퓨터 과학의 원초적인 자료구조들을 직접 구현함으로써 다음 기술적 목표를 달성합니다:
* **$O(1)$ LRU 캐시 메커니즘**: `HashMap`의 즉시 탐색과 `DoublyLinkedList`의 포인터 조작을 결합하여 메모리 초과 시 가장 오래 참조되지 않은 키를 $O(1)$로 축출(Eviction)합니다.
* **$O(1)$ TTL 모니터링**: `MinHeap` 우선순위 큐를 통해 데이터베이스 전체를 스캔하지 않고도 가장 먼저 만료될 데이터를 $O(1)$로 감지하고 제거합니다.
* **List 자료형 지원**: 자체 제작한 `DoublyLinkedList`를 밸류 컨테이너로 재사용하여 $O(1)$ 양방향 삽입/삭제(`LPUSH`, `LPOP`) 및 범위 탐색(`LRANGE`)을 제공합니다.
* **Sorted Set (ZSet) 정렬 집합**: `BinarySearchTree(BST)`를 활용하여 스코어 기반 $O(\log N)$ 삽입(`ZADD`)과 중위 순회 오름차순 정렬 조회(`ZRANGE`)를 지원합니다.
* **비동기 1:N 메시징 브로커**: `HashMap`, `DoublyLinkedList`, `Queue`를 결합하여 실시간 채널 기반 발행/구독(Pub/Sub) 시스템을 구축합니다.

---

## 2. 전체 시스템 아키텍처 (System Architecture)

Mini-Redis는 **REPL CLI 환경**을 시작점으로, **명령어 파서**, **비즈니스 오케스트레이션 엔진**, 그리고 **순수 자체 제작 자료구조 계층**의 4단계 파이프라인으로 구성됩니다.

```text
[ 사용자 CLI 입력 (Terminal) ] 
       │  "LPUSH mylist 'item1'" / "ZADD myzset 95.5 'Alice'"
       ▼
┌────────────────────────────────────────────────────────┐
│ 1. main.py (REPL Interface)                            │
│    - shlex.split() 기반 따옴표 보존 토큰 분리         │
│    - Ctrl+C (Graceful Shutdown) 및 예외 격리 방어 루프 │
└──────────────────────────┬─────────────────────────────┘
                           │ cmd_tokens = ['LPUSH', 'mylist', 'item1']
                           ▼
┌────────────────────────────────────────────────────────┐
│ 2. command_executor.py (Command Router)                │
│    - 대소문자 무관 커맨드 라우팅 및 인자 개수/타입 검증│
│    - Redis 표준 응답 프로토콜 직렬화 (OK, nil, int, ERR)│
└──────────────────────────┬─────────────────────────────┘
                           │ lpush(key, value) / zadd(key, score, member)
                           ▼
┌────────────────────────────────────────────────────────┐
│ 3. mini_redis.py (Core Storage & Eviction Engine)      │
│    ┌───────────────────┬───────────────────┐           │
│    │  HashMap (self.db)│ DoublyLinkedList  │           │
│    │  (String/List 저장│ (self.lru_list)   │           │
│    ├───────────────────┼───────────────────┤           │
│    │  HashMap(zsets)   │ MinHeap(ttl_heap) │           │
│    │  (BST Sorted Set) │ (만료 스케줄러)   │           │
│    └───────────────────┴───────────────────┘           │
└──────────────────────────┬─────────────────────────────┘
                           │
       ▼───────────────────┴───────────────────▼
┌────────────────────────────────────────────────────────┐
│ 4. Underlying Custom Data Structures (Zero Built-in)   │
│    - dynamic_array.py      : 동적 크기 확장 배열       │
│    - doubly_linked_list.py : LRU 및 List 자료형 척추   │
│    - hash_map.py           : 체이닝 & 리사이징 해시맵  │
│    - min_heap.py           : 배열 기반 TTL 최소 힙     │
│    - linear_structures.py  : Stack, Queue, Deque       │
│    - binary_search_tree.py : 점수/키 정렬 트리(ZSet)   │
│    - pubsub.py             : 교차 해시맵 기반 Pub/Sub  │
└────────────────────────────────────────────────────────┘
```

---

## 3. 프로젝트 모듈 구조 및 기술 명세서 (Project Structure & Technical Docs)

```text
mini-redis/
├── main.py                     # [진입점] CLI REPL 실행 루프 및 프로세스 제어
├── mini_redis.py               # [엔진] LRU/TTL 정책, String/List/ZSet을 총괄하는 메인 스토리지 엔진
├── command_executor.py         # [라우터] 명령어 파싱, 유효성 검증 및 Redis 표준 포매터
├── hash_map.py                 # [저장소] 다항 롤링 해시 & 개별 체이닝 기반 해시 테이블
├── doubly_linked_list.py       # [척추] 더미 노드 양방향 연결 리스트 (LRU 추적 & List 자료형)
├── min_heap.py                 # [우선순위] 완전 이진 트리 기반 TTL 만료 관리 최소 힙
├── dynamic_array.py            # [기반 메모리] 2배 확장(Resizing) 지원 저수준 동적 배열
├── linear_structures.py        # [선형] 컴포지션 패턴 기반 Stack, Queue, Deque
├── binary_tree.py              # [트리] 이진 트리 노드 및 4대 순회(전위/중위/후위/레벨)
├── binary_search_tree.py       # [정렬 트리] $O(\log N)$ 삽입/탐색 및 중위 순회 정렬(ZSet)
├── pubsub.py                   # [브로커] 1:N 메시지 발행/구독 및 구독자별 큐 버퍼링 엔진
├── docs/                       #  [심층 기술 및 아키텍처 명세서 디렉토리]
│   ├── Redis_엔진_메모리_및_명령어_처리.md # └─ 엔진 오케스트레이션, LRU 축출, 메모리 모델 및 CLI 규격
│   ├── 해시맵.md                # └─ 다항 해시, 체이닝/선형조사법 도해, 로드 팩터, 리사이징
│   ├── heap.md                 # └─ 완전 이진 트리 인덱스 산술, 최소 힙 및 TTL 스케줄링
│   ├── 이중연결리스트.md          # └─ 더미(Sentinel) 노드 양방향 리스트 및 O(1) 포인터 연산
│   ├── 동적배열과선형구조.md      # └─ 분할 상환 O(1) 2배 확장, Stack, Queue, Deque 어댑터
│   ├── 이진트리와_bst.md         # └─ 4대 순회(DFS/BFS) 및 BST 정렬/ZSet 랭킹 알고리즘
│   ├── pubsub.md               # └─ 양방향 해시맵 교차 매핑 및 1:N 비동기 브로드캐스팅
│   └── STACK_QUEUE_DEQUE.md    # └─ 선형 자료구조 개념 조사 및 활용 명세서
└── README.md                   # 프로젝트 종합 기술 문서
```

> **심층 기술 명세서 안내**:  
> 단순 코드 해설을 지양하고, 각 자료구조와 알고리즘의 **수학적 원리, 설계 배경, 트러블슈팅 및 성능 분석**을 체계적으로 다룬 심층 기술 문서는 **[`docs/`](docs/)** 디렉토리에 정리되어 있습니다.   

### 파일별 역할 및 핵심 기술 요약표

| 소스 코드 파일 | 핵심 역할 | 주요 알고리즘 및 기술 | 시간 복잡도 |
| :--- | :--- | :--- | :---: |
| **[`main.py`](main.py)** | 대화형 CLI 사용자 인터페이스 | `shlex.split`, 예외 격리(Crash 방지) REPL | - |
| **[`command_executor.py`](command_executor.py)**| 사용자 명령어 해석 및 디스패치 | 동적 메서드 라우팅(`do_<CMD>`), Redis 규격 응답 직렬화 | $O(1)$ |
| **[`mini_redis.py`](mini_redis.py)** | 데이터베이스 메인 오케스트레이션 | 해시맵 + 연결 리스트 + 최소 힙 + BST 통합 | $O(1)$ LRU, TTL |
| **[`hash_map.py`](hash_map.py)** | Key 기반 데이터 초고속 매핑 | 다항 롤링 해시, 개별 체이닝, 로드 팩터($0.75$) 2배 확장 | 평균 $O(1)$ |
| **[`doubly_linked_list.py`](doubly_linked_list.py)**| LRU 접근 추적 및 List 자료형 | 더미 노드(Dummy Head/Tail) Sentinel 패턴, 범위 슬라이싱 | 삽입/삭제: $O(1)$ |
| **[`min_heap.py`](min_heap.py)** | TTL 만료 예정 시각 스케줄링 | 배열 기반 완전 이진 트리, 지연 삭제(Lazy Deletion) | 조회 $O(1)$, 삽입 $O(\log N)$ |
| **[`binary_search_tree.py`](binary_search_tree.py)**| Sorted Set (ZSet) 스코어 정렬 | In-order Successor 삭제 대체, 중위 순회 오름차순 정렬 | 삽입 평균 $O(\log N)$ |
| **[`pubsub.py`](pubsub.py)** | 비동기 실시간 메시징 브로커 | 양방향 해시맵 교차 매핑, 구독자별 FIFO 큐 우편함 | 발행 $O(K)$, 구독 $O(1)$ |
| **[`dynamic_array.py`](dynamic_array.py)** | 물리적 연속 메모리 공간 관리 | 기하급수적 용량 2배 확장(Geometric Doubling) | 분할 상환 $O(1)$ |
| **[`linear_structures.py`](linear_structures.py)**| 선형 데이터 구조 지원 | 이중 연결 리스트 기반 어댑터 컴포지션(Stack, Queue, Deque) | 전체 연산 $O(1)$ |
| **[`binary_tree.py`](binary_tree.py)** | 계층형 트리 탐색 | 재귀 DFS(전위/중위/후위) + Queue 기반 BFS(레벨 순회) | $O(N)$ 전체 탐색 |

---

###  심층 기술 명세서 목록 (`docs/`)

자료구조와 알고리즘의 세부 원리, 수학적 증명, 단계별 트레이싱 및 트러블슈팅에 관한 상세 기술 문서는 **[`docs/`](docs/)** 디렉토리에 주제별로 정리되어 있습니다.

* **[Redis 엔진, 메모리 정책 및 명령어 처리 (`docs/Redis_엔진_메모리_및_명령어_처리.md`)](docs/Redis_엔진_메모리_및_명령어_처리.md)**: 중앙 제어 엔진, 바이트 단위 메모리 추적, LRU Eviction, 단일 엔트리 OOM, 기존 키 덮어쓰기 누수 방어, TTL 지연 만료, REPL CLI 규격
* **[해시맵 및 충돌 해결 기법 (`docs/해시맵.md`)](docs/해시맵.md)**: 다항 롤링 해시, 분리 체이닝, 개방 주소법 3총사(선형/이차/이중해싱) 트레이싱, 로드 팩터 성능 비교 곡선, 리사이징 버그 해결
* **[최소 힙 및 TTL 만료 관리 (`docs/heap.md`)](docs/heap.md)**: 완전 이진 트리 인덱스 산술 공식 증명, Up-Heap/Down-Heap 단계별 전이도, TTL 스케줄링 및 지연 삭제
* **[이중 연결 리스트 및 선형 구조 (`docs/이중연결리스트.md`)](docs/이중연결리스트.md)**: Dummy Sentinel 노드 패턴, 양방향 포인터 연산, 선형 자료구조 1:1 매핑
* **[동적 배열 및 선형 자료구조 (`docs/동적배열과선형구조.md`)](docs/동적배열과선형구조.md)**: 기하급수적 2배 확장 분할 상환 $O(1)$ 수학적 증명, 매직 메서드 호환, Stack/Queue/Deque 어댑터 패턴
* **[이진 트리 및 이진 탐색 트리 (`docs/이진트리와_bst.md`)](docs/이진트리와_bst.md)**: 4대 순회(DFS/BFS) 알고리즘, BST 불변식, 후계자 치환 노드 삭제 3케이스 상세 트레이싱, Redis Sorted Set(ZSet) 연계
* **[발행-구독(Pub/Sub) 브로커 (`docs/pubsub.md`)](docs/pubsub.md)**: 1:N 메시징 아키텍처, 양방향 해시맵 교차 매핑, 큐 기반 우편함 버퍼링, 유령 채널 메모리 회수(Clean-up)
* **[스택, 큐, 덱 개념 조사 (`docs/STACK_QUEUE_DEQUE.md`)](docs/STACK_QUEUE_DEQUE.md)**: LIFO, FIFO, Deque 동작 원리 및 프로젝트 활용처

---

###  심층 기술 명세서 목록 (`docs/`)

자료구조와 알고리즘의 세부 원리, 수학적 증명, 단계별 트레이싱 및 트러블슈팅에 관한 상세 기술 문서는 **[`docs/`](docs/)** 디렉토리에 주제별로 정리되어 있습니다.

* **[Redis 엔진, 메모리 정책 및 명령어 처리 (`docs/Redis_엔진_메모리_및_명령어_처리.md`)](docs/Redis_엔진_메모리_및_명령어_처리.md)**: 중앙 제어 엔진, 바이트 단위 메모리 추적, LRU Eviction, 단일 엔트리 OOM, 기존 키 덮어쓰기 누수 방어, TTL 지연 만료, REPL CLI 규격
* **[해시맵 및 충돌 해결 기법 (`docs/해시맵.md`)](docs/해시맵.md)**: 다항 롤링 해시, 분리 체이닝, 개방 주소법 3총사(선형/이차/이중해싱) 트레이싱, 로드 팩터 성능 비교 곡선, 리사이징 버그 해결
* **[최소 힙 및 TTL 만료 관리 (`docs/heap.md`)](docs/heap.md)**: 완전 이진 트리 인덱스 산술 공식 증명, Up-Heap/Down-Heap 단계별 전이도, TTL 스케줄링 및 지연 삭제
* **[이중 연결 리스트 및 선형 구조 (`docs/이중연결리스트.md`)](docs/이중연결리스트.md)**: Dummy Sentinel 노드 패턴, 양방향 포인터 연산, 선형 자료구조 1:1 매핑
* **[동적 배열 및 선형 자료구조 (`docs/동적배열과선형구조.md`)](docs/동적배열과선형구조.md)**: 기하급수적 2배 확장 분할 상환 $O(1)$ 수학적 증명, 매직 메서드 호환, Stack/Queue/Deque 어댑터 패턴
* **[이진 트리 및 이진 탐색 트리 (`docs/이진트리와_bst.md`)](docs/이진트리와_bst.md)**: 4대 순회(DFS/BFS) 알고리즘, BST 불변식, 후계자 치환 노드 삭제 3케이스 상세 트레이싱, Redis Sorted Set(ZSet) 연계
* **[발행-구독(Pub/Sub) 브로커 (`docs/pubsub.md`)](docs/pubsub.md)**: 1:N 메시징 아키텍처, 양방향 해시맵 교차 매핑, 큐 기반 우편함 버퍼링, 유령 채널 메모리 회수(Clean-up)
* **[스택, 큐, 덱 개념 조사 (`docs/STACK_QUEUE_DEQUE.md`)](docs/STACK_QUEUE_DEQUE.md)**: LIFO, FIFO, Deque 동작 원리 및 프로젝트 활용처

---

## 4. 핵심 알고리즘 및 기술적 의사결정 (Technical Decisions)

### 1) $O(1)$ LRU 캐시: 왜 해시맵과 이중 연결 리스트를 결합했는가?
* **문제 상황**:
  * 해시맵 단독: Key 검색은 $O(1)$이지만, 어떤 데이터가 가장 오래되었는지 시간 순서를 유지할 수 없음 ($O(N)$ 전수 조사 필요).
  * 배열/단일 리스트 단독: 순서는 유지할 수 있으나, 특정 키를 찾아 최신 위치로 옮기거나 삭제할 때 $O(N)$ 발생.
* **해결책**:
  * `HashMap`의 `Value`에 데이터 값 대신 **`DoublyLinkedList`의 `Node` 메모리 주소(참조)**를 저장합니다.
  * 데이터에 접근(`GET`, `SET`, `LPUSH` 등)할 때 해시맵을 통해 노드 주소를 $O(1)$로 찾고, 이중 연결 리스트의 앞뒤 포인터만 재연결하여 머리(`Head`) 쪽으로 $O(1)$만에 즉시 이동(`move_to_front`)시킵니다.
  * 메모리 제한 초과 시 가장 꼬리(`dummy_tail.prev`)에 위치한 노드를 $O(1)$로 잘라내어 축출합니다.

### 2) 더미 노드(Dummy Head & Tail) Sentinel 패턴 도입
* **배경**: 일반 연결 리스트는 리스트가 비어 있거나, 맨 앞 노드를 지우거나, 맨 뒤에 추가할 때마다 `if head is None`, `if node == tail` 같은 null 검사 분기문이 필수적이었습니다.
* **설계**: 실제 데이터를 담지 않는 `dummy_head`와 `dummy_tail`을 양 끝에 영구 고정 배치했습니다.
* **결과**: 리스트의 크기와 무관하게 모든 노드는 항상 좌우에 이웃 노드를 확보하므로, **모든 삽입/삭제/이동 로직을 조건문(if-else) 없이 단 4줄의 포인터 교환으로 일반화($O(1)$)**하여 경계 조건 버그를 원천 차단했습니다.

### 3) List 자료형: `DoublyLinkedList`를 통한 양방향 큐 구현 (`LPUSH`, `LPOP`, `LRANGE`)
* Redis의 List 자료형은 양 끝에서의 빠른 삽입과 삭제를 핵심으로 합니다.
* 본 프로젝트에서는 이미 완성도 높게 검증된 `DoublyLinkedList` 객체 자체를 `db`의 Value로 저장하는 방식을 채택했습니다.
* 헤드 삽입(`insert_front`) 및 헤드 추출(`remove_front`)을 통해 `LPUSH`와 `LPOP`을 $O(1)$로 수행하며, 음수 인덱스(예: `0 -1`) 슬라이싱을 지원하는 `get_range` 메서드로 `LRANGE`를 효율적으로 처리합니다.

### 4) Sorted Set (ZSet): `BinarySearchTree`를 활용한 랭킹 정렬 시스템 (`ZADD`, `ZRANGE`)
* Redis의 정렬 집합은 각 멤버에 실수형 점수(Score)가 부여되어 항상 정렬된 상태를 유지해야 합니다.
* `mini_redis.py`의 `self.zsets` 해시맵에 키별로 `BinarySearchTree` 인스턴스를 관리합니다.
* `ZADD` 실행 시 `(score, member)` 튜플을 BST에 삽입하여 평균 $O(\log N)$에 정렬 위치를 찾아 저장합니다.
* `ZRANGE` 실행 시 BST의 **중위 순회(In-order Traversal)**를 수행하여 추가 정렬 라이브러리 없이도 $O(N)$ 시간 안에 낮은 점수부터 오름차순으로 정렬된 멤버 목록을 즉시 추출합니다.

### 5) 최소 힙(Min-Heap)을 이용한 TTL 관리 및 지연 삭제(Lazy Deletion)
* **왜 힙인가?**: 전체 키를 1초마다 순회하며 만료 여부를 검사하면 $O(N)$의 막대한 CPU 낭비가 발생합니다. 가장 만료 시각이 임박한 데이터가 항상 루트(`index=0`)에 위치하는 최소 힙을 사용하면, 현재 시각과 힙의 루트만 비교하여 **만료 임박 키를 $O(1)$로 탐지**할 수 있습니다.
* **지연 삭제(Lazy Deletion) 전략**: 사용자가 만료 시간 이전에 `DEL`로 키를 지우거나 `SET`으로 값을 덮어쓴 경우, 힙의 중간에 위치한 노드를 찾아서 지우는 비용($O(N)$)을 피하기 위해 힙에는 옛 만료 항목을 그대로 둡니다. 추후 해당 항목이 힙의 루트로 올라왔을 때 실제 해시맵에 존재하는 키인지 대조 검증하여 자연스럽게 폐기 처리합니다.

---

## 5. 지원 명령어 명세 (Command Specifications)

Mini-Redis CLI는 실제 Redis와 동일한 문법 규격과 응답 프로토콜을 준수합니다.

### 1) String 데이터 조작 명령어

| 명령어 | 문법 | 설명 | 반환값 (Redis 표준) |
| :--- | :--- | :--- | :--- |
| **`SET`** | `SET <key> <value> [EX seconds]` | 키-값을 저장하고 LRU 순서를 최신으로 갱신합니다. `EX` 옵션 지정 시 만료 초를 설정합니다. | `OK` |
| **`GET`** | `GET <key>` | 키의 값을 조회하고 LRU 순서를 최신으로 갱신합니다. 만료된 키는 삭제 후 `(nil)`을 반환합니다. | `"value"` 또는 `(nil)` |
| **`DEL`** | `DEL <key>` | 키를 삭제하며 데이터, LRU 목록, 메모리 사용량에서 완전히 제거합니다. | `(integer) 1` (없으면 `0`) |
| **`EXISTS`**| `EXISTS <key>` | 키의 존재 여부를 확인합니다. (만료 여부 선검사) | `(integer) 1` (없으면 `0`) |
| **`DBSIZE`**| `DBSIZE` | 데이터베이스에 저장된 총 유효 키의 개수를 반환합니다. | `(integer) <count>` |
| **`KEYS`** | `KEYS` | 현재 저장된 모든 키의 목록을 인덱스와 함께 출력합니다. | `1) "key1"\n2) "key2"` |

### 2) List 데이터 조작 명령어 (DoublyLinkedList 기반)

| 명령어 | 문법 | 설명 | 반환값 (Redis 표준) |
| :--- | :--- | :--- | :--- |
| **`LPUSH`** | `LPUSH <key> <value>` | 리스트의 헤드(맨 앞)에 새로운 요소를 삽입하고 LRU를 갱신합니다. 키가 없으면 새 리스트를 생성합니다. 기존 키가 리스트가 아니면 `WRONGTYPE` 에러를 반환합니다. | `(integer) <리스트 요소 수>` |
| **`LPOP`** | `LPOP <key>` | 리스트의 헤드(맨 앞)에서 요소를 꺼내어 제거하고 반환합니다. 리스트가 비어있거나 키가 없으면 `(nil)`을 반환하며, 마지막 요소를 꺼내면 키가 자동 삭제됩니다. | `"value"` 또는 `(nil)` |
| **`LRANGE`**| `LRANGE <key> <start> <stop>` | 리스트의 `<start>`부터 `<stop>`까지의 요소 목록을 조회합니다. 0 기반 인덱스 및 음수 인덱스(예: `-1`은 맨 끝)를 완벽 지원합니다. | `1) "val1"\n2) "val2"` 또는 `(empty array)` |

### 3) Sorted Set (ZSet) 데이터 조작 명령어 (BST 기반)

| 명령어 | 문법 | 설명 | 반환값 (Redis 표준) |
| :--- | :--- | :--- | :--- |
| **`ZADD`** | `ZADD <key> <score> <member>` | 정렬 집합에 `score`(부동소수점/정수)와 `member` 쌍을 삽입합니다. 내부적으로 `BinarySearchTree`에 정렬 저장됩니다. | `(integer) 1` |
| **`ZRANGE`**| `ZRANGE <key>` | 정렬 집합의 모든 멤버를 스코어(Score) 오름차순으로 정렬하여 조회합니다. (BST 중위 순회 결과 반환) | `1) "member" (Score : 10.5)` 또는 `(empty list or set)` |

### 4) 메모리 제어 및 시스템 명령어

| 명령어 | 문법 | 설명 | 반환값 |
| :--- | :--- | :--- | :--- |
| **`CONFIG SET`** | `CONFIG SET maxmemory <bytes>` | 최대 메모리 임계치를 바이트 단위로 설정합니다. `0`은 무제한을 의미합니다. | `OK` |
| **`INFO`** | `INFO memory` | 현재 메모리 사용량, 제한치, LRU로 축출된 총 키 개수를 출력합니다. | 메모리 상세 리포트 |

### 5) TTL(Time-To-Live) 관리 명령어

| 명령어 | 문법 | 설명 | 반환값 |
| :--- | :--- | :--- | :--- |
| **`EXPIRE`** | `EXPIRE <key> <seconds>` | 기존 키에 유효기간(초)을 부여합니다. $0$ 이하 설정 시 즉시 삭제됩니다. | `(integer) 1` (키 없으면 `0`) |
| **`TTL`** | `TTL <key>` | 만료까지 남은 시간을 초 단위로 조회합니다. | 남은 초 / `-1`(무제한) / `-2`(키 없음) |

### 6) Pub/Sub (발행/구독) 브로커 명령어

| 명령어 | 문법 | 설명 | 반환값 |
| :--- | :--- | :--- | :--- |
| **`SUBSCRIBE`** | `SUBSCRIBE <channel> [ch2 ...]` | 지정한 채널(들)을 구독합니다. 구독자 전용 메시지 큐가 자동 배정됩니다. | `1) "subscribe"\n2) "<channel>"\n3) (integer) <구독수>` |
| **`UNSUBSCRIBE`**| `UNSUBSCRIBE <channel> [ch2 ...]`| 지정한 채널(들)의 구독을 해제합니다. 마지막 구독자 탈퇴 시 채널 자원을 회수합니다. | `1) "unsubscribe"\n2) "<channel>"\n3) (integer) <잔여수>` |
| **`PUBLISH`** | `PUBLISH <channel> <msg>` | 채널의 모든 구독자 우편함(Queue)에 메시지를 동시에 복사 배달합니다. | `(integer) <수신 구독자 수>` (구독 중인 CLI면 즉시 수신 알림) |
| **`PUBSUB`** | `PUBSUB CHANNELS` | 현재 1명 이상의 구독자가 활성화되어 있는 모든 활성 채널 목록을 조회합니다. | 채널 목록 배열 |

---

## 6. 메모리 관리 및 만료 정책 (Memory & Eviction Policy)

### 1) 메모리 점유율 산정 기준 (공식)
포인터나 노드 오버헤드를 제외한 순수 데이터 페이로드 크기를 추적합니다.
$$\text{used\_memory} = \sum_{\text{all keys}} \Big( \text{len}(\text{utf8}(\text{key})) + \text{len}(\text{utf8}(\text{value})) \Big)$$

### 2) LRU 축출(Eviction) 및 OOM 방어 프로세스
1. **단일 엔트리 검사**: 새로 저장하려는 단일 키-값의 바이트 크기가 `maxmemory`보다 크면, 저장을 거부하고 즉시 `(error) OOM command not allowed...` 에러를 반환합니다.
2. **반복적 캐시 축출**:
   * `SET` 연산 후 `used_memory > maxmemory`인 경우, `used_memory <= maxmemory`가 될 때까지 **`lru_list.remove_back()`**을 호출합니다.
   * 가장 오랫동안 사용되지 않은 꼬리 노드의 키를 해시맵과 연결 리스트에서 동시 제거하고 바이트를 차감하며, `evicted_keys` 카운터를 $+1$ 증가시킵니다.

### 3) 2단계 만료 청소 (Clean Expired)
* 모든 키 기반 명령어(`GET`, `SET`, `DEL`, `TTL`, `EXPIRE`, `LPUSH` 등)는 실행 직전에 내부 메서드 `_clean_expired()`를 호출합니다.
* 최소 힙의 루트(`peek()`)를 확인하여 만료 시각이 현재 시각(`time.time()`) 이전인 키들을 $O(1)$로 연속 적발하여 메모리에서 즉시 영구 삭제합니다.

---

## 7. 실행 및 사용 방법 (Getting Started)

### 요구 사양
* **Python 3.8 이상** (외부 의존성 설치 불필요, 파이썬 표준 환경에서 단독 구동)

### 1) CLI REPL 실행
```bash
# 디렉토리 이동 후 CLI 실행
python main.py
```

### 2) 종합 CLI 세션 실행 예시

```text
==================================================
 welcome to Mini Redis CLI!
 종료하려면 'exit' 또는 'quit'를 입력하세요.
==================================================
# 1. String 기본 조작 및 TTL 설정
mini-redis> SET user:1 "Alice" EX 60
OK
mini-redis> GET user:1
"Alice"
mini-redis> TTL user:1
(integer) 58

# 2. List 명령어 (LPUSH, LRANGE, LPOP)
mini-redis> LPUSH mylist "apple"
(integer) 1
mini-redis> LPUSH mylist "banana"
(integer) 2
mini-redis> LPUSH mylist "cherry"
(integer) 3
mini-redis> LRANGE mylist 0 -1
1) "cherry"
2) "banana"
3) "apple"
mini-redis> LPOP mylist
"cherry"
mini-redis> LRANGE mylist 0 -1
1) "banana"
2) "apple"

# 3. Sorted Set (ZSet) 명령어 (ZADD, ZRANGE)
mini-redis> ZADD exam 85.0 "Bob"
(integer) 1
mini-redis> ZADD exam 98.5 "Alice"
(integer) 1
mini-redis> ZADD exam 72.0 "Charlie"
(integer) 1
mini-redis> ZRANGE exam
1) "Charlie" (Score : 72.0)
2) "Bob" (Score : 85.0)
3) "Alice" (Score : 98.5)

# 4. 메모리 제한 및 LRU 자동 축출
mini-redis> CONFIG SET maxmemory 30
OK
mini-redis> SET k1 "1234567890"
OK
mini-redis> SET k2 "abcdefghij"
OK
mini-redis> INFO memory
used_memory:24
maxmemory:30
evicted_keys:1

# 5. Pub/Sub 실시간 메시징
mini-redis> SUBSCRIBE news
1) "subscribe"
2) "news"
3) (integer) 1
mini-redis> PUBLISH news "Breaking News!"
[메시지수신]
1) "message"
2 "news"
3 " Breaking News!"
(integer) 1

mini-redis> exit
Mini Redis를 종료합니다.
```

---

## 8. 설계 원칙 및 기술적 제약 사항 (Design Principles & Technical Constraints)

본 프로젝트는 고수준 내장 추상화에 의존하지 않고, 인메모리 데이터베이스 엔진의 저수준 원리와 성능 최적화를 직접 검증하기 위해 다음과 같은 설계 원칙과 제약 사항을 준수합니다.

*  **파이썬 내장 컬렉션 전면 배제 원칙**:
  * `dict`, `set`, `collections.deque`, `collections.defaultdict`, `queue.Queue` 등 고수준 컬렉션을 일절 사용하지 않았습니다.
*  **순수 자체 제작 클래스 기반 아키텍처**:
  * 해시 테이블: `hash_map.py` (`HashMap`)
  * 연결 리스트: `doubly_linked_list.py` (`DoublyLinkedList`)
  * 우선순위 큐: `min_heap.py` (`MinHeap`)
  * 동적 배열: `dynamic_array.py` (`DynamicArray`)
  * 선형 자료구조: `linear_structures.py` (`Stack`, `Queue`, `Deque`)
  * 트리 자료구조: `binary_tree.py` (`TreeNode`), `binary_search_tree.py` (`BinarySearchTree`)
*  **표준 모듈의 정당한 활용**:
  * 터미널 따옴표 보존 인자 파싱을 위해 셸 구문 분석 표준 라이브러리인 `shlex`를 사용하였습니다.
  * 시간 만료 검증을 위해 `time.time()`을 활용하였습니다.

---

## 9. 시간 복잡도 분석표 (Time Complexity)

| 기능 / 연산 | 명령어 | 구현 자료구조 | 시간 복잡도 (평균) | 시간 복잡도 (최악) | 비고 |
| :--- | :--- | :--- | :---: | :---: | :--- |
| **값 조회** | `GET` / `EXISTS` | `HashMap` + `DoublyLinkedList` | **$O(1)$** | $O(N)$ | 해시 충돌 없을 시 즉시 탐색 및 LRU 헤드 이동 |
| **값 저장** | `SET` (일반) | `HashMap` + `DoublyLinkedList` | **$O(1)$** | $O(N)$ | 노드 주소 캐싱 기반 즉시 삽입 및 헤드 이동 |
| **캐시 추출** | `SET` (LRU 추출 시) | `DoublyLinkedList` + `HashMap` | **$O(K)$** | $O(K \times N)$ | $K$ = 메모리 확보를 위해 방출해야 하는 오래된 노드 수 |
| **리스트 헤드 삽입** | `LPUSH` | `DoublyLinkedList` | **$O(1)$** | $O(1)$ | 더미 헤드 바로 뒤 4줄 포인터 교환 삽입 |
| **리스트 헤드 추출** | `LPOP` | `DoublyLinkedList` | **$O(1)$** | $O(1)$ | 더미 헤드 바로 뒤 노드 제거 및 반환 |
| **리스트 범위 조회** | `LRANGE` | `DoublyLinkedList` | **$O(K)$** | $O(N)$ | $K$ = 슬라이싱 범위($\text{stop} - \text{start}$) 내 요소 개수 |
| **정렬 집합 원소 삽입**| `ZADD` | `BinarySearchTree` | **$O(\log N)$** | $O(N)$ | 점수(Score) 기준 이진 탐색 트리 삽입 |
| **정렬 집합 오름차순 조회**| `ZRANGE` | `BinarySearchTree` | **$O(N)$** | $O(N)$ | BST 중위 순회(In-order Traversal) 기반 정렬 |
| **만료 시간 설정** | `EXPIRE` | `MinHeap` | **$O(\log M)$** | $O(\log M)$ | $M$ = TTL이 설정된 활성 키 개수 |
| **만료 키 감지** | `_clean_expired` | `MinHeap.peek()` | **$O(1)$** | $O(1)$ | 힙 루트의 최소 만료 시간만 즉시 대조 |
| **채널 구독** | `SUBSCRIBE` | `HashMap` + `DoublyLinkedList` | **$O(1)$** | $O(C)$ | 채널 해시 탐색 후 연결 리스트 끝단 $O(1)$ 삽입 |
| **메시지 발행** | `PUBLISH` | `DoublyLinkedList` + `Queue` | **$O(S)$** | $O(S)$ | $S$ = 해당 채널을 구독 중인 구독자 수 |
| **동적 배열 추가** | `append` | `DynamicArray` | **분할 상환 $O(1)$** | $O(N)$ | 2배수 용량 확장(Resizing) 발생 시에만 일시적 복사 |

---

##  Project Specification & Metadata
* **프로젝트명**: Mini-Redis Database Engine
* **시스템 분류**: In-Memory NoSQL Key-Value / Multi-Type Data Store
* **기술 스택**: Python 3 (Pure Standard Library), Zero Built-in Collections
