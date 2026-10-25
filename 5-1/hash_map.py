from doubly_linked_list import DoublyLinkedList, Node
from dynamic_array import DynamicArray
class HashMap:
    def __init__(self, initial_capacity: int = 16):
        self.capacity = initial_capacity # 저장공간(버킷) 배열의 기본 크f기
        self.size_val = 0
        # 각 저장공간에 이중연결 리스트 객체를 할당
        self.buckets = DynamicArray(initial_capacity=self.capacity)
        for _ in range(self.capacity):
            self.buckets.append(DoublyLinkedList())

    def _hash(self, key: str) -> int :

        return hash(str(key)) % self.capacity

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

    def contains(self, key: str) -> bool:
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
        self.size =0

        self.buckets = DynamicArray(initial_capacity=self.capacity)
        for _ in range(self.capacity):
            self.buckets.append(DoublyLinkedList())

        for bucket in old_buckets:
            curr = bucket.dummy_head.next
            while curr != bucket.dummy_tail:
                self.put(curr.key, curr.value)

                curr = curr.next
    def size(self) -> int:
        return self.size_val

    def keys(self) -> list:
        all_keys = []
        for i in range(len(self.buckets)):
            bucket=self.buckets[i]
            curr= bucket.dummy_head.next
            while curr != bucket.dummy_tail:
                all_keys.append(curr.key)
                curr= curr.next
        return all_keys
    