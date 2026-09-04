from Matrix import Matrix
from Matrix_1D import Matrix_1D
from made_pattern import Made_pattern

EPSILON = 1e-9



class Mode_1:

    def __init__(self):
        # 4번 수정: self.Made_pattern -> self.made_pattern 인스턴스화
        self.made_pattern = Made_pattern()

    def user_input(self, name:str, n_size: int) -> Matrix:
        mat=Matrix(n_size)
        print(f"\n[{name} 입력 ({n_size}x{n_size})]")
        print(f"아래에 {n_size}줄의 데이터를 한 번에 입력(또는 붙여넣기) 후, 엔터를 한 번 더 눌러주세요:")
                
        
        while True :
            lines = []
            while True:
                try:# while문 반복을 통해 원하는 N크기 만큼 받고 빈 줄 입력시 나올 수 있음!
                    line = input().strip()#공백 포함 해서 받음
                    if not line:
                        break
                    lines.append(line) #1줄 입력시 바로 lines에 저장
                except EOFError:
                    break

            if len(lines) != n_size : # 줄 수 검사!
                print(f"\n 오류 : 입력된 줄 수 ({len(lines)})가 N({n_size})과 맞지 않습니다.")
                continue

            final_arr = []
            valied = True
            for i, line in enumerate(lines,1): #각 줄의 '행'가 맞지 않으면 다시
                row = line.split()

                if len(row) != n_size:
                    print(f"\n 오류 : {i}번째 줄의 숫자 개수({len(row)}개)가 N({n_size})과 맞지 않습니다.")
                    valied =  False
                    break # 이러한 에러 발생 시 다시 재입력 가능하게 while 문 안에 while 문을 넣은 것!

                try:
                    rows = [float(x) for x in row]
                    final_arr.append(rows)

                except ValueError:
                    print(f"\n오류: {i}번째 숫자가 아닌값이 포함되어 있습니다.")
                    valied = False
                    break

            if valied:
                mat.data = final_arr
                print(" 성공적으로 입력을 완료했습니다!")
                return mat
            print("다시 입력해주세요! ")

    def mode1_flow(self) -> None:
        print("\n -----------------[모드 1] 사용자 직접 입력---------------")
        try:
            n_size = int(input("행렬 크기(N)를 입력하세요 (예: 3): "))
            if n_size<=0:
                print("크기는 1 이상의 양수여야 합니다.")
                return
            print("\n [1]필터 입력")
            print("\n ---------------------------------------")
            filter_a = self.user_input("필터 A (Cross)", n_size)
            filter_b = self.user_input("필터 B (X)", n_size)
            #여기서 각 필터 a 와 b 그리고 패턴 값들을 1차원을 변경하여 저장하는 변수 추가
            print("\n [2]패턴 설정\n ---------------------------------------")
            print("검사할 패턴 설정 방식:\n 1. 사용자 직접 입력\n 2. Cross(+) 패턴\n 3. X 패턴")
            p_choice = input("선택 (1/2/3) >> ").strip()

            input_pattern = Matrix(n_size)


            if p_choice == "2":
                print(f"자동 Cross(+) 패턴 생성 완료")
                input_pattern.data = self.made_pattern.cross(n_size)
            elif p_choice == "3":
                print(f"자동 X 패턴 생성 완료")
                input_pattern.data = self.made_pattern.x(n_size)
            else:
                input_pattern = self.user_input("검사할 패턴", n_size)

            
            filter_a_1d = Matrix_1D(n_size, filter_a)
            filter_b_1d = Matrix_1D(n_size, filter_b)
            input_pattern_1d = Matrix_1D(n_size, input_pattern)

            
            a_1mac = input_pattern_1d.mac_1d(filter_a_1d)
            b_1mac = input_pattern_1d.mac_1d(filter_b_1d)

            score_1a ,a1_time = a_1mac
            score_1b ,b1_time = b_1mac
            avg_1time = (a1_time + b1_time) / 2

            if abs(score_1b - score_1a) < EPSILON:
                win_1score="판정불가(|A-B| < 1e-9)"
            elif score_1a > score_1b:
                win_1score="A"
            else:
                win_1score="B"

            a_mac = input_pattern.mac(filter_a)
            b_mac = input_pattern.mac(filter_b)


            if not a_mac or not b_mac:
                print("연산 실패로 진행을 중단합니다.")
                return
            score_a, a_time = a_mac # 튜플 언패킹 활용!  tuple=(3, 5) "반환 값 가정 /
            # a,b = tuple 할 경우 왼쪽부터 a=3 ,b=5의 값이 들어간다!
            score_b, b_time =b_mac
            avg_time= (a_time + b_time)/2

            if abs(score_b -score_a) <EPSILON:
                win_score="판정불가 (|A-B| < 1e-9)"
            elif score_a > score_b:
                win_score="A"
            else :
                win_score="B"
            
            # mode_1 flow() 메서드 출력값으로 최적화 성능 분석도 확인 위해 mac_1()함수 로 계산한 값을 출력
            print("\n [3]MAC 결과")
            print("\n ---------------------------------------")
            print("\n" + "="*40)
            print(f"필터 A(Cross)와의 Mac 점수 : {score_a}")
            print(f"필터 B(X)와의 Mac 점수 : {score_b}")
            print(f"연산 시간(평균/10회): {avg_time:.6f}ms")
            print(f"판정: {win_score}")
            print("=" * 40 + "\n")

            print("\n [4] 최적화 비교")
            print("\n ---------------------------------------")
            print("\n" + "="*40)
            print(f"최적화 필터 A(Cross)와의 Mac 점수 : {score_1a}")
            print(f"최적화 필터 B(X)와의 Mac 점수 : {score_1b}")
            print(f"최적화 연산 시간(평균/10회): {avg_1time:.6f}ms")
            print(f"판정: {win_1score}")
            print("=" * 40 + "\n")

        except ValueError:
            print("올바른 정수를 입력하세요.")

