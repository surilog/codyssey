scores = {"철수": 90, "영희": 85, "민수": 95}
"""items() 사용!"""
# items()를 쓰면 name(키)과 score(값)가 한 번에 변수로 들어옴!
for name, score in scores.items():
    print(f"{name} 학생의 점수는 {score}점입니다.")


"""items()미 사용!"""

scores = {"철수": 90, "영희": 85, "민수": 95}

# items()를 안 쓰면 name(키)만 꺼내온다! 값을 따로 찾아야 합니다!
for name in scores:
    score = scores[name]  # <- 굳이 이 줄을 추가해서 점수(값)를 따로 찾아와야 함!
    print(f"{name} 학생의 점수는 {score}점입니다.")