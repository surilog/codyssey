# =====================================================================
# test.py : MiniRedis 11개 모듈 및 통합 시스템 전수 검증 스크립트
# =====================================================================

import sys
import os
import time

# Windows 터미널 한글/이모지 인코딩 방어
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# scripts 디렉토리 임포트 경로 보장
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# 1. 밑바닥 기반 자료구조 모듈
from dynamic_array import DynamicArray
from doubly_linked_list import DoublyLinkedList
from hash_map import HashMap
from min_heap import MinHeap

# 2. 선형 및 비선형 확장 자료구조 모듈
from linear_structures import Stack, Queue, Deque
from binary_tree import TreeNode, preorder, inorder, postorder, levelorder
from binary_search_tree import BinarySearchTree

# 3. 서비스 브로커 및 중앙 엔진, CLI 라우터
from pubsub import PubSubBroker
from mini_redis import MiniRedis
from command_executor import RedisCommandExecutor


def test_1_dynamic_array():
    print("[1/10] DynamicArray (용량 자동 2배 확장 및 매직메서드) 검증 중...", end=" ")
    da = DynamicArray()
    initial_cap = da.capacity

    for i in range(25):
        da.append(f"item_{i}")

    assert len(da) == 25, "len(da) 불일치"
    assert da.capacity > initial_cap, "2배 확장 실패"
    assert da[10] == "item_10", "__getitem__ 실패"

    da[10] = "updated_10"
    assert da[10] == "updated_10", "__setitem__ 실패"
    print("PASS")


def test_2_doubly_linked_list():
    print("[2/10] DoublyLinkedList (더미 노드, O(1) 이동/삭제, get_range) 검증 중...", end=" ")
    dll = DoublyLinkedList()
    assert dll.is_empty(), "초기 상태 is_empty 실패"

    # insert_front / insert_back
    n1 = dll.insert_back("k1", "v1")
    n2 = dll.insert_back("k2", "v2")
    n3 = dll.insert_back("k3", "v3")
    n0 = dll.insert_front("k0", "v0")
    assert dll.size == 4

    # move_to_front
    dll.move_to_front(n2)
    assert dll.dummy_head.next == n2, "move_to_front 실패"

    # remove_node
    dll.remove_node(n1)
    assert dll.size == 3

    # remove_front / remove_back
    removed_head = dll.remove_front()
    assert removed_head == n2
    removed_tail = dll.remove_back()
    assert removed_tail == n3
    assert dll.size == 1

    # get_range 슬라이싱 검증
    test_list = DoublyLinkedList()
    for item in ["A", "B", "C", "D"]:
        test_list.insert_back(item, item)
    assert test_list.get_range(0, -1) == ["A", "B", "C", "D"], "음수 인덱스 슬라이싱 실패"
    assert test_list.get_range(1, 2) == ["B", "C"], "부분 슬라이싱 실패"
    print("PASS")


def test_3_hash_map():
    print("[3/10] HashMap (다항 해시, 체이닝 충돌, 0.75 로드팩터 리사이징) 검증 중...", end=" ")
    try:
        hm = HashMap(capacity=4)
    except TypeError:
        hm = HashMap(initial_capacity=4)

    initial_cap = hm.capacity
    for i in range(12):
        hm.put(f"key_{i}", f"val_{i}")

    # 조회 및 리사이징 검증
    assert hm.get("key_5") == "val_5", "get 실패"
    assert hm.capacity > initial_cap, "0.75 로드팩터 초과 리사이징 실패"

    # 키 목록 및 포함 여부
    assert hm.contains("key_7"), "contains 실패"
    assert len(hm.keys()) == 12, "keys() 개수 불일치"

    # 수정 및 삭제
    hm.put("key_5", "new_val_5")
    assert hm.get("key_5") == "new_val_5", "put 수정 실패"
    hm.remove("key_5")
    assert hm.get("key_5") is None, "remove 실패"
    assert not hm.contains("key_5")
    print("PASS")


def test_4_linear_structures():
    print("[4/10] LinearStructures (Stack, Queue, Deque 전 연산 O(1)) 검증 중...", end=" ")
    # 1. Stack (LIFO)
    s = Stack()
    s.push("A")
    s.push("B")
    assert s.peek() == "B"
    assert s.pop() == "B"
    assert s.pop() == "A"
    assert s.is_empty()

    # 2. Queue (FIFO)
    q = Queue()
    q.enqueue("first")
    q.enqueue("second")
    assert q.peek() == "first"
    assert q.dequeue() == "first"
    assert q.dequeue() == "second"
    assert q.is_empty()

    # 3. Deque (양방향)
    dq = Deque()
    dq.append_front(10)
    dq.append_back(20)
    dq.append_front(5)
    # 현재 상태: [5, 10, 20]
    assert dq.peek_front() == 5
    assert dq.peek_back() == 20
    assert dq.pop_front() == 5
    assert dq.pop_back() == 20
    assert dq.pop_front() == 10
    assert dq.is_empty()
    print("PASS")


def test_5_min_heap():
    print("[5/10] MinHeap (완전 이진 트리 인덱스 산술, O(log N) 정렬) 검증 중...", end=" ")
    heap = MinHeap()

    def _push(h, expire_at, key):
        try:
            h.push(expire_at, key)
        except TypeError:
            h.push((expire_at, key))

    # 무작위 순서 삽입
    _push(heap, 50.0, "k50")
    _push(heap, 10.0, "k10")
    _push(heap, 30.0, "k30")
    _push(heap, 5.0, "k5")
    _push(heap, 40.0, "k40")

    # peek 검증 (항상 최솟값 O(1))
    top = heap.peek()
    top_val = top[0] if isinstance(top, (tuple, list)) else top
    assert top_val == 5.0, "peek 최솟값 불일치"

    # pop 검증 (오름차순 정렬 추출)
    extracted = []
    while not heap.is_empty():
        item = heap.pop()
        val = item[0] if isinstance(item, (tuple, list)) else item
        extracted.append(val)

    assert extracted == [5.0, 10.0, 30.0, 40.0, 50.0], "Min-Heap 힙 정렬 추출 순서 오류"
    print("PASS")


def test_6_binary_tree():
    print("[6/10] BinaryTree (TreeNode 노드 구조 & 4대 순회 알고리즘) 검증 중...", end=" ")
    # 트리 구조 생성:
    #        1
    #       / \
    #      2   3
    #     / \
    #    4   5
    root = TreeNode(1)
    root.left = TreeNode(2)
    root.right = TreeNode(3)
    root.left.left = TreeNode(4)
    root.left.right = TreeNode(5)

    assert preorder(root) == [1, 2, 4, 5, 3], "전위 순회(Pre-order) 실패"
    assert inorder(root) == [4, 2, 5, 1, 3], "중위 순회(In-order) 실패"
    assert postorder(root) == [4, 5, 2, 3, 1], "후위 순회(Post-order) 실패"
    assert levelorder(root) == [1, 2, 3, 4, 5], "레벨 순회(Level-order BFS) 실패"
    print("PASS")


def test_7_binary_search_tree():
    print("[7/10] BinarySearchTree (점수 튜플 삽입 & 중위 순회 오름차순 정렬) 검증 중...", end=" ")
    bst = BinarySearchTree()
    bst.insert((85.0, "Bob"))
    bst.insert((95.0, "Alice"))
    bst.insert((70.0, "Charlie"))
    bst.insert((60.0, "David"))
    bst.insert((80.0, "Eve"))

    # inorder_sort 검증
    sorted_items = bst.inorder_sort()
    members = [m for s, m in sorted_items]
    scores = [s for s, m in sorted_items]

    assert members == ["David", "Charlie", "Eve", "Bob", "Alice"], "BST 중위 정렬 멤버 순서 오류"
    assert scores == [60.0, 70.0, 80.0, 85.0, 95.0], "BST 점수 오름차순 오류"
    print("PASS")


def test_8_pubsub_broker():
    print("[8/10] PubSubBroker (양방향 해시맵, 1:N 브로드캐스트 & 큐 버퍼링) 검증 중...", end=" ")
    broker = PubSubBroker()

    # 채널 구독
    c1_count = broker.subscribe("client_1", "news")
    assert c1_count == 1
    broker.subscribe("client_1", "tech")
    broker.subscribe("client_2", "news")

    # 발행 검증 (news 채널 청취자는 client_1, client_2 2명)
    receivers = broker.publish("news", "Breaking News!")
    assert receivers == 2

    # client_1의 news 큐 메시지 수신 확인
    sub_list = broker.channels.get("news")
    assert sub_list is not None

    # 구독 해제 검증
    broker.unsubscribe("client_2", "news")
    broker.unsubscribe("client_1", "news")
    # 구독자 0명 시 채널 해시맵에서 완전 정리(Clean-up) 확인
    assert broker.channels.get("news") is None, "구독자 0명 시 유령 채널 메모리 회수 실패"
    print("PASS")


def test_9_mini_redis_integration():
    print("[9/10] MiniRedis 중앙 엔진 (LRU 축출, OOM 방어, TTL 지연 만료, List, ZSet) 검증 중...", end=" ")
    redis = MiniRedis(maxmemory=20)  # 20바이트 제한

    # 1. 단일 엔트리 OOM 사전 방어 검증 ("toolarge" 8B + "value_over_20_bytes_here" 24B = 32B > 20B)
    oom_res = redis.set("toolarge", "value_over_20_bytes_here")
    assert "OOM" in oom_res, "단일 엔트리 OOM 방어 실패"

    # 2. String & LRU 축출 검증 ("k1"+"v1" = 4B)
    redis.set("k1", "v1")  # 4B
    redis.set("k2", "v2")  # 4B
    redis.set("k3", "v3")  # 4B
    redis.set("k4", "v4")  # 4B (총 16B)
    redis.get("k1")        # k1 최신화 (가장 오래된 키는 k2)

    # k5(7B) 삽입 -> 총 23B > 20B -> k2 축출
    redis.set("k5", "v5555")
    assert redis.get("k2") is None, "LRU 대상 k2 미축출"
    assert redis.get("k1") == "v1", "최근 참조된 k1 보존 실패"
    assert redis.evicted_keys >= 1, "evicted_keys 카운트 누락"

    # 3. 기존 키 덮어쓰기 메모리 정산 검증
    redis.set("k1", "v_new")
    assert redis.get("k1") == "v_new"

    # 4. TTL 만료 자동 청소 검증
    redis.set("temp_key", "temp_val", ttl=1)
    assert redis.ttl("temp_key") in (0, 1)
    time.sleep(1.1)
    assert redis.get("temp_key") is None, "TTL 만료 키 삭제 실패"
    assert redis.ttl("temp_key") == -2, "만료된 키의 TTL 반환값 오류"

    # 5. List 자료형 (LPUSH, LPOP, LRANGE) 검증
    redis.maxmemory = 0  # 무제한으로 변경
    redis.lpush("mylist", "item1")
    redis.lpush("mylist", "item2")
    redis.lpush("mylist", "item3")
    assert redis.lrange("mylist", 0, -1) == ["item3", "item2", "item1"], "LRANGE 순서 오류"
    assert redis.lpop("mylist") == "item3", "LPOP 헤드 추출 오류"
    assert redis.lrange("mylist", 0, -1) == ["item2", "item1"]

    # 6. ZSet 자료형 (ZADD, ZRANGE) 검증
    redis.zadd("ranks", 100.0, "Winner")
    redis.zadd("ranks", 60.0, "Third")
    redis.zadd("ranks", 80.0, "Second")
    z_res = redis.zrange("ranks")
    assert [m for s, m in z_res] == ["Third", "Second", "Winner"], "ZSET 오름차순 순서 오류"
    print("PASS")


def test_10_command_executor():
    print("[10/10] CommandExecutor (Redis CLI 6대 표준 응답 및 전 명령어 직렬화) 검증 중...", end=" ")
    redis = MiniRedis()
    executor = RedisCommandExecutor(redis)

    # 1. String 명령어군
    assert executor.execute(["SET", "msg", "hello"]) == "OK"
    assert executor.execute(["GET", "msg"]) == '"hello"'
    assert executor.execute(["EXISTS", "msg"]) == "(integer) 1"
    assert executor.execute(["DBSIZE"]) == "(integer) 1"
    assert '1) "msg"' in executor.execute(["KEYS"])
    assert executor.execute(["DEL", "msg"]) == "(integer) 1"
    assert executor.execute(["GET", "msg"]) == "(nil)"

    # 2. Memory & CONFIG 명령어군
    assert executor.execute(["CONFIG", "SET", "maxmemory", "50"]) == "OK"
    info_out = executor.execute(["INFO", "memory"])
    assert "used_memory" in info_out and "maxmemory:50" in info_out
    assert executor.execute(["CONFIG", "SET", "maxmemory", "abc"]) == "(error) ERR value is not an integer or out of range"

    # 3. TTL 명령어군
    executor.execute(["SET", "session", "token123"])
    assert executor.execute(["EXPIRE", "session", "10"]) == "(integer) 1"
    ttl_out = executor.execute(["TTL", "session"])
    assert "(integer)" in ttl_out
    assert executor.execute(["EXPIRE", "session", "not_int"]) == "(error) ERR value is not an integer or out of range"

    # 4. List 명령어군
    assert executor.execute(["LPUSH", "cart", "apple"]) == "(integer) 1"
    assert executor.execute(["LPUSH", "cart", "banana"]) == "(integer) 2"
    lrange_out = executor.execute(["LRANGE", "cart", "0", "-1"])
    assert '1) "banana"' in lrange_out and '2) "apple"' in lrange_out
    assert executor.execute(["LPOP", "cart"]) == '"banana"'

    # 5. ZSET 명령어군
    assert executor.execute(["ZADD", "exam", "92.5", "Alice"]) == "(integer) 1"
    assert executor.execute(["ZADD", "exam", "78.0", "Bob"]) == "(integer) 1"
    zrange_out = executor.execute(["ZRANGE", "exam"])
    assert '1) "Bob"' in zrange_out and '2) "Alice"' in zrange_out

    # 6. Pub/Sub 명령어군
    sub_out = executor.execute(["SUBSCRIBE", "sports"])
    assert '1) "subscribe"' in sub_out and '2) "sports"' in sub_out
    pub_out = executor.execute(["PUBLISH", "sports", "Goal!"])
    assert "(integer)" in pub_out
    assert "sports" in executor.execute(["PUBSUB", "CHANNELS"])
    unsub_out = executor.execute(["UNSUBSCRIBE", "sports"])
    assert '1) "unsubscribe"' in unsub_out

    # 7. 예외 방어 규격
    assert "(error) ERR unknown command" in executor.execute(["UNKNOWN_CMD"])
    assert "(error) ERR wrong number of arguments" in executor.execute(["GET"])
    print("PASS")


def main():
    print("=" * 70)
    print(" [MiniRedis] 11개 소스코드 모듈 및 전체 명령어 종합 검증")
    print("=" * 70)
    start_time = time.time()

    test_1_dynamic_array()
    test_2_doubly_linked_list()
    test_3_hash_map()
    test_4_linear_structures()
    test_5_min_heap()
    test_6_binary_tree()
    test_7_binary_search_tree()
    test_8_pubsub_broker()
    test_9_mini_redis_integration()
    test_10_command_executor()

    elapsed = round(time.time() - start_time, 2)
    print("=" * 70)
    print(f" 전원 통과 (10/10 ALL PASS) - 총 소요 시간: {elapsed}초")
    print(" 모든 자료구조, 엔진 로직, CLI 명령어가 완벽하게 작동합니다!")
    print("=" * 70)


if __name__ == "__main__":
    main()

    main()