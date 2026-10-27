from doubly_linked_list import DoublyLinkedList
from hash_map import HashMap
from linear_structures import Queue

class Subscriber:

    def __init__(self, client_id : str):
        self.client_id = client_id
        self.message_queue = Queue()

class PubSubBroker:
    def __init__(self):
        #channels: key(채널명) -> value(구독중인 Subscriber들의 DoublyLinkedList)
        self.channels = HashMap()

        #key(client_id) -> value(구독 중인 채널명의 DoublyLinkedList)
        self.client_channels =HashMap()

    def subscribe(self, client_id : str, channel: str) -> int:
        """채널에 구독자 등록 후 , 해당 클라이언트의 총 구독 채널 수 반환"""
        #1. 채널의 구독자 목록 가져오기 (없으면 새로 생성)
        sub_list = self.channels.get(channel)
        if sub_list is None:
            sub_list = DoublyLinkedList()
            self.channels.put(channel,sub_list)

        #이미 구독중인지 중복 확인
        already_sub = False
        curr = sub_list.dummy_head.next
        while curr and curr != sub_list.dummy_tail:
            if curr.key == client_id:
                already_sub = True
                break
            curr=curr.next

        if not already_sub:
            sub_list.insert_back(client_id,Subscriber(client_id))

        # 2. 클라이언트의 구독 중 채널 목록 갱신
        chan_list = self.client_channels.get(client_id)
        if chan_list is None:
            chan_list = DoublyLinkedList()
            self.client_channels.put(client_id, chan_list)

        chan_exists =False
        c_curr = chan_list.dummy_head.next
        while c_curr and c_curr != chan_list.dummy_tail:
            if c_curr.key == channel:
                chan_exists = True
                break
            c_curr =c_curr.next

        if not chan_exists:
            chan_list.insert_back(channel, None)
       
        return chan_list.size

    def unsubscribe(self, client_id :str, channel:str) -> int:
        """채널 구독 취소 후, 남은 구독 채널 수 반환"""
        # 1. 채널 구독자 목록에서 제거

        sub_list = self.channels.get(channel)
        if sub_list:
            curr = sub_list.dummy_head.next
            while curr != sub_list.dummy_tail:
                if curr.key == client_id:
                    sub_list.remove_node(curr)
                    break
                curr= curr.next
            # 구독자가 한 명도 없으면 채널 자체를 해시맵에서 제고
            if sub_list.size == 0 :
                self.channels.remove(channel)

        chan_list = self.client_channels.get(client_id)
        if chan_list:
            c_curr = chan_list.dummy_head.next
            while c_curr and c_curr != sub_list.dummy_tail:
                if c_curr.key == channel:
                    chan_list.remove_node(c_curr)
                    break
                c_curr = c_curr.next
            return chan_list.size

        return 0
    
    def publish(self,
                 channel:str, message:str)->int:
        """메시지 발행 : 채널의 모든 구독자 Queue에 메시지 적재 (수신사 수 반환)"""
        sub_list = self.channels.get(channel)
        if sub_list is None or sub_list.size ==0:
            return 0

        receiver_count = 0
        curr = sub_list.dummy_head.next
        while curr != sub_list.dummy_tail:
            subscriber: Subscriber = curr.value
            if subscriber:
                subscriber.message_queue.enqueue((channel,message))
                receiver_count +=1
            curr =curr.next
        return receiver_count

    def get_active_channels(self) -> list:
        """현재 구독자가 존재하는 활성 채널 목록 반환"""
        active = []
        all_chans = self.channels.keys()
        for ch in all_chans:
            s_list = self.channels.get(ch)
            if s_list and s_list.size >0:
                active.append(ch)
        return active