
# 데이터 (디셔너리로 관리)
user = {"name": "김철수", "point": 10, "score": 0}

# 기능 (데이터를 직접 매개변수로 받아서 수정 후 반환)
def use_hint(user_data):
    if user_data["point"] >= 1:
        user_data["point"] -= 1
        print(f"힌트 사용! 남은 포인트: {user_data['point']}pt")
    else:
        print("포인트가 부족합니다.")

def solve_correct(user_data):
    user_data["score"] += 1
    user_data["point"] += 1
    print(f"정답! 현재 점수: {user_data['score']}점, 포인트: {user_data['point']}pt")

# 실행
use_hint(user)      # 힌트 사용! 남은 포인트: 9pt
solve_correct(user) # 정답! 현재 점수: 1점, 포인트: 10pt

class User:
    def __init__(self, name, point=10):
        # 데이터(상태)를 객체 내부에 저장
        self.name = name
        self.point = point
        self.score = 0

    # 객체 내부 상태를 다루는 기능(메서드)
    def use_hint(self):
        if self.point >= 1:
            self.point -= 1
            print(f"힌트 사용! 남은 포인트: {self.point}pt")
        else:
            print("포인트가 부족합니다.")

    def solve_correct(self):
        self.score += 1
        self.point += 1
        print(f"정답! 현재 점수: {self.score}점, 포인트: {self.point}pt")

# 실행
user1 = User("김철수")
user1.use_hint()      # 힌트 사용! 남은 포인트: 9pt
user1.solve_correct() # 정답! 현재 점수: 1점, 포인트: 10pt