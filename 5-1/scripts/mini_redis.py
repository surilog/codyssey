import time
from doubly_linked_list import DoublyLinkedList
from hash_map import HashMap
from min_heap import MinHeap
from pubsub import PubSubBroker
from binary_search_tree import BinarySearchTree

class MiniRedis:
    def __init__(self, maxmemory: int = 0):
        self.key_ttl = {}
        self.maxmemory = maxmemory # 0은 무제한
        self.used_memory = 0 # 현재 사용중인 바이트 수
        self.evicted_keys = 0 # LRU로 제거된 키 개수

        self.db = HashMap()
        self.lru_list = DoublyLinkedList()
        self.ttl_heap = MinHeap()
        self.pubsub = PubSubBroker()
        self.zsets = HashMap()

    def zadd(self, key:str, score: float,member:str) -> int:
        self._clean_expired()
        bst = self.zsets.get(key)
        if bst is None:
            bst = BinarySearchTree()
            self.zsets.put(key, bst)

        bst.insert((score, member))
        return 1

    def zrange(self, key: str)-> list:
        self._clean_expired()
        bst = self.zsets.get(key)
        if bst is None:
            return []
        return bst.inorder_sort()

    
    def subscribe(self, client_id: str, channel: str) -> int:
        return self.pubsub.subscribe(client_id,channel)
    def unsubscribe(self, client_id:str, channel:str)->int:
        return self.pubsub.unsubscribe(client_id,channel)
    def publish(self,channel:str, message:str)->int:
        return self.pubsub.publish(channel,message)
    def pubsub_channels(self) -> list:
        return self.pubsub.get_active_channels()
    

    def _get_bytes(self, key:str,value:str) -> int:
        #UTF-8 바이트 크기 계산 (공식 : len(utf8(key)) + len(utf8(value)))
        # 실제 메모리를 몇 바이트 점유하는지 정확하게 알기 위해
        return len(str(key).encode('utf-8'))  + len(str(value).encode('utf-8'))
    # 만료된 키 청소 
    def _clean_expired(self) -> None:
        current_time = time.time()

        while not self.ttl_heap.is_empty():
            
           peek_item = self.ttl_heap.peek()
           if peek_item is None:
            break
           expire_at,key = peek_item
           if expire_at > current_time:
               break
           
           self.ttl_heap.pop()
           if(hasattr(self, "key_ttl")and key in self.key_ttl and self.key_ttl[key]!=expire_at): 
               #
               continue
           lru_node = self.db.get(key)
           if lru_node:
                self.used_memory -= self._get_bytes(lru_node.key, lru_node.value)
                self.lru_list.remove_node(lru_node)
                self.db.remove(key)
                print(f"[TTL 만료 삭제] 키 '{key}'가 자동으로 삭제되었습니다.")

    # redis 명령어 구현
    def set(self, key:str, value, ttl:int = None) -> str:
        self._clean_expired()
        entry_bytes = self._get_bytes(key, value)

        # 단일 엔트리 > maxmemory ==> OOM에러
        if self.maxmemory > 0 and entry_bytes > self.maxmemory:
            return(f"(error) OOM command not allowed when used_memory > '{self.maxmemory}'")

        lru_node = self.db.get(key)

        if lru_node:
            # 기존 키 존재 시 이전 바이트 차감 후 값 수정
            self.used_memory -= self._get_bytes(lru_node.key, lru_node.value)
            lru_node.value = value
            self.used_memory += entry_bytes
            self.lru_list.move_to_front(lru_node)
        else:
            self.used_memory += entry_bytes
            new_lru_node = self.lru_list.insert_front(key,value)
            self.db.put(key, new_lru_node)

        #ttl 만료 시간이 등록된 경우 최소 힙에 등록
        if ttl is not None:
            expire_at = time.time() + ttl
            self.key_ttl[key] = expire_at
            self.ttl_heap.push(expire_at,key)
        else:
#ttl 인자가 주어지지 않은(else) 경우, 장부(self.key_ttl)에서 해당 키의 만료 기록을 완전히 지움(pop)
            self.key_ttl.pop(key,None)
        #메모리 제한 초과 시 lru 노드 계속 제거
        if self.maxmemory > 0:
                    while (self.used_memory > self.maxmemory and self.lru_list.size > 0):
                        oldest_node = self.lru_list.remove_back()
                        if oldest_node:
                            self.used_memory -= self._get_bytes(oldest_node.key, oldest_node.value)
                            self.db.remove(oldest_node.key)
                            self.key_ttl.pop(oldest_node.key, None)
                            self.evicted_keys += 1
        return "OK"

    #해시맵에서 O(1)로 노드 찾기
    def get(self, key: str) -> str:
        self._clean_expired()
        lru_node = self.db.get(key)
        if lru_node is None:
            return None

        self.lru_list.move_to_front(lru_node)
        return lru_node.value


    #이때 heap은 제거 X, heap은 지연삭제 (Min-heap: 루트 노드만 O(1) 다른 위치면 O(N)일 수도 있음!) TTL활용!
    def delete(self, key:str) -> int:
        self._clean_expired()
        self.key_ttl.pop(key,None)
        lru_node = self.db.get(key)
        if lru_node :
            self.used_memory -= self._get_bytes(lru_node.key, lru_node.value)
            self.lru_list.remove_node(lru_node)
            self.db.remove(key)
            return 1
        return 0

    def exists(self, key:str) -> int:
        self._clean_expired()
        lru_node = self.db.get(key)
        return 1 if lru_node is not None else 0

    def dbsize(self) -> int:
        self._clean_expired()
        return self.db.size()

    def keys(self)-> list:
        self._clean_expired()
        return self.db.keys()

    def config_set_maxmemory(self, bytes_val: int):
        self.maxmemory = max(0, bytes_val)
        return "OK"

    def info_memory(self) -> dict:
        self._clean_expired()
        return {
            "used_memory": self.used_memory,
            "maxmemory" : self.maxmemory,
            "evicted_keys": self.evicted_keys
        }


    def expire(self, key:str, seconds:int) -> int:
        self._clean_expired()
        lru_node = self.db.get(key)
        if lru_node is None:
            return 0

        if seconds <=0 :
            self.delete(key)
            return 1

        expire_at = time.time() + seconds
        self.ttl_heap.push(expire_at,key)
        return 1

    def ttl(self, key:str) -> int:
        self._clean_expired()
        lru_node = self.db.get(key)
        if lru_node is None:
            return -2

        min_expire = None
        for expire_at , k in self.ttl_heap.heap:
            if k ==key:
                if min_expire is None or expire_at < min_expire:
                    min_expire = expire_at


        if min_expire is None:
                return -1
               
        remaining = int(min_expire - time.time())
        return max(0, remaining)
        


    def lpush(self, key:str, value:str) -> int :
        self._clean_expired()
        lru_node = self.db.get(key)

        if lru_node is None:
            lst = DoublyLinkedList()
            lst.insert_front(key,value)

            new_lru_node = self.lru_list.insert_front(key,lst)
            self.db.put(key, new_lru_node)
            return 1

        else:
            lst = lru_node.value
            if isinstance(lst, DoublyLinkedList):
                lst.insert_front(key,value)
                self.lru_list.move_to_front(lru_node)
                return lst.size

            else:
                raise TypeError("WRONGTYPE Operation against a key holding the wrong kind of value")

    def lpop(self, key:str) -> str | None:
        self._clean_expired()
        lru_node = self.db.get(key)

        if lru_node is None:
            return None

        lst= lru_node.value
        if not isinstance(lst, DoublyLinkedList) or lst.size == 0:
            return None

        popped_node = lst.remove_front()
        self.lru_list.move_to_front(lru_node)

        if lst.size == 0:
            self.delete(key)

        return popped_node.value if popped_node else None

    def lrange(self, key:str, start:int,stop:int) -> list:
        """지정한 범위의 요소 목록 반환"""
        self._clean_expired()
        lru_node = self.db.get(key)

        if lru_node is None:
            return []

        lst = lru_node.value
        if isinstance(lst, DoublyLinkedList):
            self.lru_list.move_to_front(lru_node)
            return lst.get_range(start, stop)
        return []