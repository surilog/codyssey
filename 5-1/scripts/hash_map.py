from doubly_linked_list import DoublyLinkedList, Node
from dynamic_array import DynamicArray
class HashMap:
    def __init__(self, initial_capacity: int = 16):
        self.capacity = initial_capacity 
        self.size_val = 0 # 해시맵에 실제 저장된 데이터 개수
        self.buckets = DynamicArray(initial_capacity=self.capacity) # 크기가 16인 동적 배열 생성
        for _ in range(self.capacity):
            self.buckets.append(DoublyLinkedList()) #배열의 16개 칸 마다 각각 빈 이중 연결 리스트를 하나씩 배치


    #책 제목(Key, 예: "user:1")을 숫자 방 번호(0~15번 버킷)로 바꿔주는 사서의 계산 규칙
    #즉, 임의의 문자열 키를 정수로 바꿈
    def _hash(self, key: str) -> int :

        return hash(str(key)) % self.capacity 
    #모듈러 연산 수행 => 숫자가 커져도 capacity(16)로 나눠 0~15사이의 범위 안으로 떨어지게함

    def _find_node(self, key:str) -> Node:
        index = self._hash(key)
        bucket = self.buckets[index]

        curr = bucket.dummy_head.next
        while curr != bucket.dummy_tail:
            if curr.key == key:
                return curr
            curr = curr.next

        return None

    def put(self, key: str, value):
        existing_node = self._find_node(key)

        if existing_node:
            existing_node.value = value
            return
        index = self._hash(key)
        bucket = self.buckets[index]
        bucket.insert_front(key, value)
        self.size_val += 1

        if self.size_val / self.capacity > 0.75:
            self._resize()

    def get(self, key: str):
        node = self._find_node(key)
        return node.value if node else None

    def contains(self, key: str) -> bool: #키가 존재하는지 T/F
        return self._find_node(key) is not None

    def remove(self, key:str) -> bool:
        node = self._find_node(key)

        if node:
            
            index = self._hash(key)
            self.buckets[index].remove_node(node)
            self.size_val -= 1
            return True
        return False

    def _resize(self):
        old_buckets =self.buckets
        self.capacity *=2
        self.size_val =0

        self.buckets = DynamicArray(initial_capacity=self.capacity)
        for _ in range(self.capacity):
            self.buckets.append(DoublyLinkedList())

        for bucket in old_buckets:
            curr = bucket.dummy_head.next
            while curr != bucket.dummy_tail:
                self.put(curr.key, curr.value)

                curr = curr.next
    # 현재 보관된 데이터 총 개수
    def size(self) -> int:
        return self.size_val
    # 모든 버킷의 모든 키를 반환
    def keys(self) -> list:
        all_keys = []
        for i in range(len(self.buckets)):
            bucket=self.buckets[i]
            curr= bucket.dummy_head.next
            while curr != bucket.dummy_tail:
                all_keys.append(curr.key)
                curr= curr.next
        return all_keys
    