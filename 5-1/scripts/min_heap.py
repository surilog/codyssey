from dynamic_array import DynamicArray
class MinHeap:
    def __init__(self):
        self.heap =  DynamicArray()

    def _parent(self, i : int) -> int:
        return (i -1) // 2

    def _left_child(self, i : int) -> int:
        return 2*i + 1

    def _right_child(self, i : int) -> int:
        return 2*i +2

    def _swap(self, i: int, j: int):
        self.heap[i], self.heap[j] = self.heap[j], self.heap[i]


    def _heapify_up(self, index : int):
        while index > 0: #루트 노드에 도달할 때까지 반복 , 시간 복잡도 : 트리의 높이만큼 위로 올라가니 O(logN)
            parent_idx = self._parent(index)
            if self.heap[index][0] < self.heap[parent_idx][0]:
                self._swap(index, parent_idx)
                index = parent_idx
            else :
                break

    def push(self, expire_at : float, key: str):
        self.heap.append((expire_at, key))
        self._heapify_up(len(self.heap)-1)


    def _heapify_down(self, index:int):
        size = len(self.heap)
        while True:
            left = self._left_child(index)
            right = self._right_child(index)
            smallest = index

            if left < size and self.heap[left][0] < self.heap[smallest][0]:
                smallest = left
            if right < size and self.heap[right][0] < self.heap[smallest][0]:
                smallest = right

            if smallest != index:
                self._swap(index, smallest)
                index = smallest
            else:
                break # 시간 복잡도: 트리의 높이만큼만 하강하므로 O(log N)

    def pop(self):
        if self.is_empty():
            return None
        if len(self.heap) == 1:
            return self.heap.pop()

        root = self.heap[0]
        self.heap[0] = self.heap.pop() #맨 마지막 노드를 떼어내서 루트(0번) 자리에 덮어씀
        self._heapify_down(0)
        return root

    def peek(self):
        return self.heap[0] if not self.is_empty() else None

    def is_empty(self) -> bool :
        return len(self.heap) == 0
