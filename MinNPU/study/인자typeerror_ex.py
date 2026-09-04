# --------------------------------------------------
# [오류 발생 코드]
# --------------------------------------------------

# 케이스 1: data만 받는 구조로 만들었을 때
class Data:

    def __init__(self, data):
        self.data = data

try:

    Data(3, [[1,0],[0,1]]) 
except TypeError:
    print("[오류!] __init__ 정의는 2개 받는데, 3개(self,3,[[1,0],[0,1]])가 전달되었습니다.")
#  TypeError: takes 2 positional arguments but 3 were given


# 케이스 2: size, data 둘 다 필수로 요구할 때
class Bothdata:
    def __init__(self, size, data):
        self.size = size
        self.data = data
try:
    Bothdata(3) 
except TypeError:
    print("[오류!] __init__ 필수 인자는 3개인데, 'data'가 빠진 2개(self,3)만 전달되었습니다.")
#  TypeError: missing 1 required positional argument: 'data'


# --------------------------------------------------
# [해결 코드] : data=None 기본값 활용!
# --------------------------------------------------
class FixedMatrix:
    def __init__(self, size: int, data: list = None):
        self.size = size
        # data가 안 넘어오면 0으로 채워진 빈 행렬 생성
        self.data = data if data is not None else [[0] * size for _ in range(size)]

# 둘 다 에러 없이 성공!
try:
    mat1 = FixedMatrix(3)   
    print("size인자 3만 전달 했지만 data의 기본 값으로 None설정을 해주어서 성공")                # 인자 1개 ok (모드 1)
    mat2 = FixedMatrix(3, [[1,0], [0,1]])   # 인자 2개 ok (모드 2)
    print("이거는 원래 되야되지.")
except TypeError:
    print("아직도 인자 에러가 있다니..")