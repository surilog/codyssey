from doubly_linked_list import DoublyLinkedList

#이중 연결 리스트 기반 스택,큐,덱 모듈
class Stack:
    def __init__(self):
        self._list = DoublyLinkedList()

    def push(self, item):
        self._list.insert_front(item,None)

    def pop(self):
        if self.is_empty():
            raise IndexError("pop from empty stack")
        node = self._list.remove_front()
        return node.key if node else None

    def peek(self):
        if self.is_empty():
            return None
        return self._list.dummy_head.next.key
        
    def is_empty(self) -> bool:
        return self._list.size == 0
    
    def size(self) -> int:
        return self._list.size

    def __len__(self) -> int:
        return self.size()

class Queue:
    def __init__(self):
        self._list = DoublyLinkedList()

    def enqueue(self, item) -> None:
        self._list.insert_back(item,None)

    def dequeue(self):
        if self.is_empty():
            raise IndexError("dequeue from empty queue")
        node = self._list.remove_front()
        return node.key if node else None

    def peek(self):
        if self.is_empty():
            return None
        return self._list.dummy_head.next.key

    def is_empty(self) -> bool:
        return self._list.size == 0

    def size(self) -> int:
        return self._list.size

    def __len__(self) -> int:
        return self.size()

class Deque:
    def __init__(self):
        self._list = DoublyLinkedList()

    def append_front(self, item) -> None :
        self._list.insert_front(item,None)
    def append_back(self,item) -> None :
        self._list.insert_back(item,None)
    def pop_front(self):
        if self.is_empty():
            raise IndexError("pop from empty deque")
        node = self._list.remove_front()
        return node.key if node else None

    def pop_back(self):
        if self.is_empty():
            raise IndexError("pop from empty deque")
        node = self._list.remove_back()
        return node.key if node else None
    
    def peek_front(self):
        if self.is_empty():
            return None
        return self._list.dummy_head.next.key
    def peek_back(self):
        if self.is_empty():
            return None
        return self._list.dummy_tail.prev.key

    def is_empty(self) -> bool:
        return self._list.size == 0

    def size(self) -> int:
        return self._list.size

    def __len__(self) -> int:
        return self.size()


if __name__ =="__main__":
    print("===1. stack 테스트")
    s= Stack()
    for x in ["첫번째","두번째","세번째"]:
        s.push(x)
        print(f"push: {x}")

    print(f"현재 top요소 (peek) : {s.peek()}")
    while not s.is_empty():
        print(f"pop: {s.pop()}")

    print("===2. Queue 테스트")
    q= Queue()
    for msg in ['메시지A', "메시지B","메시지C"]:
        q.enqueue(msg)
        print(f"enqueue: {msg}")

    print(f"현재 맨 앞 요소 (peek) : {q.peek()}")
    while not q.is_empty():
        print(f"dequeue: {q.dequeue()}")

    print("===3. Deque 테스트")
    dq = Deque()
    dq.append_back("중간")
    dq.append_front("앞1")
    dq.append_back("뒤1")
    print(f"pop_front: {dq.pop_front()}")
    print(f"pop_back: {dq.pop_back()}")
    print(f"남은요소 (peek_front) : {dq.peek_front()}")