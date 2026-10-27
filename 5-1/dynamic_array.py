class DynamicArray:
    def __init__(self, initial_capacity: int =4):
        self.capacity = max(1, initial_capacity)
        self.size =0
        self._array = [None] * self.capacity

    #다른 파일에서 ._size로 접근하거나 수정해도 self.size와 연동되도록 지원
    @property
    def _size(self):
        return self.size

    @_size.setter
    def _size(self, value):
        self.size= value

    def _resize(self, new_capacity: int) -> None:
        new_array = [None] * new_capacity
        for i in range(self.size):
            new_array[i] = self._array[i]

        self._array = new_array
        self.capacity = new_capacity
#평소에는 O(1) , 용량 늘릴 때만 O(N)
    def append(self, item) -> None:
        if self.size == self.capacity:
            self._resize(self.capacity * 2)

        self._array[self.size] = item
        self.size +=1

    def get(self, index: int):
        if not (0 <=index <self.size):
            raise IndexError("Array index out of range")
        return self._array[index]

    def set(self, index:int ,value) ->None:
        if not (0<=index<self.size):
            raise IndexError("Array index out of range")
        self._array[index] = value

    def pop(self):
        if self.size == 0:
            raise IndexError("Pop from empty array")

        last_item = self._array[self.size -1]
        self._array[self.size -1] = None
        self.size -=1
        return last_item

    def remove_at(self, index: int):
        if not(0 <= index < self.size):
            raise IndexError("Array index out of range")

        removed_item = self._array[index]

        for i in range(index, self.size -1):
            self._array[i] = self._array[i+1]

        self._array[self.size -1] =None
        self.size -=1
        return removed_item
# 매직 메서드로 arr[0] = value가능
    def __len__(self) -> int:
        """len(arr) 지원"""
        return self.size
    def __getitem__(self, index:int):
        """arrr[index] 대괄호 조회 문법 지원"""
        return self.get(index)
    def __setitem__(self,index:int ,value):
        """arr[index] = value"""
        self.set(index,value)
    def __iter__(self):
        """for문 순회 시 actual size범위 내의 요소만 반환"""
        for i in range(self.size):
            yield self._array[i]