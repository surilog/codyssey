
class Node:
    def __init__(self, key=None, value=None):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None

    def __repr__(self):
        return f"({self.key}: {self.value})"
class DoublyLinkedList:
    """더미 노드를 활용해 head와 tail연결 => null 예외 처리 조건문 필요 X """
    def __init__(self):
        self.dummy_head = Node()
        self.dummy_tail = Node()

        self.dummy_head.next = self.dummy_tail
        self.dummy_tail.prev = self.dummy_head

        self.size = 0

    def to_list(self) -> list:
        result = []
        curr = self.dummy_head.next
        while curr != self.dummy_tail:
            result.append(curr.value)
            curr=curr.next
        return result

    def get_range(self, start: int, stop: int) -> list:
        elements = self.to_list()
        total = len(elements)
        if total == 0 :
            return []

        if start < 0:
            start = max(0, total + start)
        if stop < 0:
            stop = total + stop
        if start >= total or start > stop:
            return []

        stop = min(total -1 , stop)
        return elements[start : stop +1]

    # 삽입 시 노드 연결 해주는 함수
    def insert_front_node(self, node:Node):
        first_node = self.dummy_head.next # 처음 노드를 추가 할 때는 first_node가 dummy_tail을 가리킴

        # 새 노드의 포인터 설정
        node.prev = self.dummy_head
        node.next = first_node

        # 기존 주변 노드들의 포인터 재연결
        self.dummy_head.next = node
        first_node.prev = node

        self.size +=1

    def insert_back_node(self, node:Node):
        last_node = self.dummy_tail.prev

        node.prev = last_node
        node.next = self.dummy_tail

        last_node.next = node
        self.dummy_tail.prev = node

        self.size +=1
    # 맨 앞 노드 생성
    def insert_front(self, key, value) -> Node:
        new_node = Node(key,value)
        self.insert_front_node(new_node)
        return new_node

    def insert_back(self, key, value) -> Node:
        new_mode = Node(key,value)
        last_node = self.dummy_tail.prev

        new_mode.prev = last_node
        new_mode.next = self.dummy_tail
        last_node.next = new_mode
        self.dummy_tail.prev = new_mode

        self.size +=1

        return new_mode


    def remove_node(self, node: Node) -> Node:
        #더미 노드 삭제 X
        if node == self.dummy_head or node == self.dummy_tail:
            return None

        prev_node = node.prev
        next_node = node.next

        # 삭제할 노드 우회 하여 이전 노드와 다음 노드 연결
        prev_node.next = next_node
        next_node.prev = prev_node
        
        self.size -=1
        return node

    def remove_front(self) -> Node:
        if self.is_empty():
            return None
        return self.remove_node(self.dummy_head.next)

    def remove_back(self) -> Node:
        if self.is_empty():
            return None
        return self.remove_node(self.dummy_tail.prev)

    def is_empty(self) -> bool:
        return self.size == 0
 
    def move_to_front(self, node:Node):
        self.remove_node(node)
        self.insert_front_node(node)





