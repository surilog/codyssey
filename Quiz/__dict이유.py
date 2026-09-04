# [수정 전] Manager가 User의 속성을 하나하나 분해해서 저장
class OldUser:
    def __init__(self, username, point):
        self.username = username
        self.point = point

class OldQuizGame:
    def save_data(self, users):
        save_list = []
        for u in users:
            # QuizGame이 User의 내부 구조(username, point)를 직접 만짐 => 나중에 수정하려면 일일이 수정필요.
            save_list.append({"username": u.username, "point": u.point})
        return save_list


# [수정 후] User가 스스로 to_dict()를 제공하여 역할 분리
class NewUser:
    def __init__(self, username, point):
        self.username = username
        self.point = point

    def to_dict(self):
        """자기 자신의 정보 직렬화 책임을 가짐"""
        return {"username": self.username, "point": self.point}

class NewQuizGame:
    def save_data(self, users):
        # QuizGame은 to_dict()만 호출하면 됨
        return [user.to_dict() for user in users]


print("=== 4. OOP 역할 분리 비교 ===")
user = NewUser("Alice", 10)

print(" [수정 전]:", OldQuizGame().save_data([OldUser("Alice", 10)]))
print(" [수정 후]:", NewQuizGame().save_data([user]))