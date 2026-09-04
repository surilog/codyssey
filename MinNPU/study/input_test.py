
"""
N, M = map(int, input().split())
#입력에 공백이 포함되는 경우에는 split() 함수(string타입)를 사용할 수 있다.
#이때 map(자료형, 적용할 함수)를 입력하면 int형으로 변경이 된다!
lst = [list(map(int, input().split())) for _ in range(N)]

print(lst)
"""
"""
# 1. 일반 for 문으로 풀어쓴 경우 (풀어서 생각하기)
matrix = []
for _ in range(n):                         # [바깥쪽] N번 반복 (줄 수)
    row = [int(x) for x in input().split()] # [안쪽] 한 줄 입력받아 숫자 리스트로 변환
    matrix.append(row)

"""

# 공백으로 구분 가능 + 2차원 리스트로 변환! But 아직 예외처리가 안됨(줄 마다 정확한 n개가 아니라 더 많아도 일단 받아옴!)
"""lines = []
def user_input():
    n=int(input("n 정해줘! : "))
    matrix = [[int(x) for x in input().split()]for _ in range(n)]
    # matrix = [ [안쪽 코드] for _ in range(n) ]
    # 1. 안쪽 코드를 n번 반복해서 커다란 하나의 리스트(행 생성) 생성!
    # 2. input().split() : 문자열을 공백기준으로 쪼개 정수형으로 변환후 , 한 줄 짜리 리스트 생성!
    return matrix


print(f"입력된 데이터 : {user_input()}")"""

# 예외 처리 

def user_input_except():
    n=int(input("n 정해줘! : "))
    while True:
        try:
            matrix = [[int(x) for x in input().split()]for _ in range(n)]
            if any(len(row) != n for row in matrix):
                print(f"오류! 각 줄마다 정확한 {n}개의 숫자를 입력했는지 공백을 구분했는지 확인하세요!")
                continue
            return matrix

        except ValueError:
            print("오류 : 숫자가 아닌 문자(또는 잘못된 형식)이 포함되어 있습니다. 다시 입력하세요.")

print(f"입력된 데이터 : {user_input_except()}")