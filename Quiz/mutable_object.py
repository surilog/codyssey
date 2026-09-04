class User:
    # 매개변수 기본값으로 빈 리스트 [] 를 직접 지정
    def __init__(self, username, history=None):
        self.username = username
        self.history = history if history is not None else []
        # history가 전달되었으면 쓰고, None이면 '각 인스턴스 전용 새 리스트 []'를 생성
        """
        if history is not None:
            self.history = history
        else:
            self.history = []
        #와 같습니다!
        """
user1 = User("Alice")
user2 = User("Bob")

# Alice의 히스토리에만 기록을 추가!
user1.history.append("1번 문제 정답")

print(f"Alice 히스토리: {user1.history}")
print(f"Bob 히스토리  : {user2.history}")  # Bob은 아무것도 안 했는데...?


"""
새 객체가 만들어질 때 생성되지 않음: User("Alice")나 User("Bob")처럼 인스턴스를 만들 때마다 새로 빈 리스트를 만드는 것이 아니라, 
미리 만들어둔 그 단 하나의 메모리 리스트 주소를 공유합니다.

가변(Mutable) 특성: 리스트는 내용물이 바뀔 수 있는 객체입니다. 따라서 user1이 리스트를 수정(append)하면, 
동일한 메모리 주소를 가리키고 있던 user2의 리스트도 함께 변경된 것처럼 보이게 되기 때문에 None설정을 적용!
"""