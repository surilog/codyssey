li = []
"""컴프리헨션 : 반복문과 조건문을 한 번에 설정! ==> 코드 간결화
             : 중첩 반복문 중첩 조건문 또한 가능!"""

#리스트 컴프리헨션 없이
for i in range(5):
    li.append(i)

print("리스트 컴프리헨션 없이: ",li)

# 리스트 컴프리헨션 사용
[i for i in range(5)]
print("리스트 컴프리헨션 사용: ",li)

li2 = []

#2차원 리스트 not 컴프리헨션

"""for _ in range(5):
    row = []
    for _ in range(5):
        row.append(0)
    li2.append(row)"""

# 2차원 리스트 컴프리헨션
li2 = [[0 for _ in range(5)] for _ in range(5)]
print("리스트 컴프리헨션 사용: ",li2)
# 안쪽[]가 세로 바깥쪽이 가로라고 보면 편함!

for _ in range(3):
    print("안녕")  # "안녕"이 3번 출력됩니다.
# i나 idx 대신 _를 써서 변수를 사용하지 않는다고 선언.
# 특정 크기의 리스트를 기본값으로 똑같이 채워 새로 만들 때 사용


N=3
array = [[0 for _ in range(N)]for _ in range(N)]

print(array)


