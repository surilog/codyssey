import json
import time


EPSILON = 1e-9

class Matrix_1D:
    def __init__(self, size: int, data_input=None):
        self.n = size
        
        # 1. 전달받은 입력이 Matrix 객체인지, 일반 리스트인지 판별
        if isinstance(data_input, Matrix): #isinstance: 객체가 특정 클래스의 인스턴스인지 확인하는 함수 맞으면 True, 아니면 False => 순환오류때문에 사용
            # Matrix 객체라면 그 내부의 .data (2차원 리스트)를 추출
            source_data = data_input.data
        elif isinstance(data_input, list):
            source_data = data_input
        else:
            source_data = None

        # 2. 1차원 배열로 변환
        if source_data:
            self.data_1d = [val for row in source_data for val in row]
        else:
            self.data_1d = [1.0] * (size * size)

    def mac_1d(self, pattern: "Matrix_1D", num_runs: int =10000) -> tuple[float,float]:
        size_N = self.n*self.n
        d1= self.data_1d
        d2= pattern.data_1d 

        total_sum = sum(d1[i] * d2[i] for i in range(size_N))

        start_time = time.perf_counter()
        for _ in range(num_runs):
            _ = sum(d1[i]*d2[i] for i in range(size_N))
        end_time = time.perf_counter()
        avg_time = ((end_time - start_time) /num_runs) * 1000.0
        return total_sum, avg_time
"""mode 1에서 입력받은 값을 가져와서 Matrix1D에서 1차원으로 바꾸고 mac_1d에서  연산 후 기존 mode1에서 출력
   mode2에서 불러온 data.json에서 저장되어진 self.filters와 self.patterns의 정리된 값을 그대로 저장하되 배열만
   2->1차원을 바꾸고 다시 저장 후 그 저장된 값들을 토대로 mac_1연산 수행 후 원래 로직이었언 mode2_flow에서 코드 로직 실행!
   이러면 원래 데이터를 그대로 사용하면서 바로 비교 가능!
"""
            
class Made_pattern:
    def cross(self, n: int) -> list[list[float]]:
        matrix = [[0.0] * n for _ in range(n)]
        mid = n//2

        for r in range(n):                                                  
            for c in range(n):
                if n % 2 ==1 :
                    if r == mid or c == mid:
                        matrix[r][c] = 1.0
                else:
                    if r in (mid - 1 ,mid) or c in (mid -1, mid):
                        matrix[r][c] = 1.0
        return matrix

    def x(self,n : int) -> list[list[float]]:
        matrix =[[0.0]* n for _ in range(n)]
        for r in range(n):
            for c in range(n):
                if r == c or r+c ==n-1:
                    matrix[r][c] =1.0
        return matrix
    

def only_normal(label_raw: str) -> str:
        if not label_raw:
            return "UNKNOWN"

        clean = str(label_raw).strip().lower()

        if clean in ["+","cross"]:
            return "Cross"
        elif clean in ["x"]:
            return "X"
        else:
            return "UNKNOWN"


class Matrix:
    def __init__(self, size : int, data:list=None):
        self.n=size
        self.data = data if data is not None else []
          # 이중 for문(리스트 컴프리헨션)을 이용한 N * N 배열 초기화a
        """ self.matrix = []
        for _ in range(n):
            row = []
            for _ in range(n):
                row.append(0)
            self.matrix.append(row)    
        print(self.matrix)
        
        print(self.n)"""

        # 연산 함수 호출하고 연산 수행 시 동시에 { start_time = time.time() 시간 측정시작! 하고 연산 끝나면 
        #  end_time = time.time()후} result_time =end_time - start_time 
        # 근데 sum_time+=reuslt_time / average_time= sum_time/10

        """크기별 MAC 연산 시간을 ms 단위로 측정해야 한다.
        최소 기준: 각 크기별로 MAC 연산을 10회 반복 측정 후 평균 시간을 출력한다.
        시간 측정은 I/O(입력/출력/파일 읽기) 시간을 제외하고 “연산 함수 호출 구간” 중심으로 수행하는 것을 권장한다.
        """
    def mac(self, pathern: 'Matrix') -> tuple[float,float]  | None:  
            #튜플 사용 이유 새롭게 알게 된 점: 한 번 생성되면 내부 값을 변경할 수 없다! => 즉 고정데이터로 활용 가능
            if self.n != pathern.n:
                print(f" 오류 : 행렬 크기가 맞지 않습니다. ({self.n}*{self.n}) VS ({pathern.n}*{pathern.n})")
                return None
            if not self.data or not pathern.data:
                print("오류 : 행렬 데이터가 없습니다. ")
                return None
    

            num_runs = 10
            
            full_time = 0.0
            total_sum=0.0
            #제너레이터를 쓰면 0부터 더해서 초기화 필요 X
            for __ in range(num_runs):
                start_time = time.perf_counter() # time.time()대신 사용 이유: 마이크로처 단위의 매우 높은 정밀도
                total_sum = 0
                for r in range(self.n):
                        for c in range(self.n):
                            total_sum += self.data[r][c] * pathern.data[r][c]
                

                end_time = time.perf_counter()
                full_time += end_time - start_time
            avg_time = (full_time / num_runs) * 1000.0 #밀리 초는 1초의 1천분의 1
            # 임시 진단 코드

            """기존 소수점 차이 X 코드 
            
            
            """
           

            return total_sum, avg_time

    """  
    def get_val(self, r: int, c: int) -> float:
        return self.data[r][c] #(r,c) 위치 반환

    def set_val(self, r:int, c:int, val : float):
        self.data[r][c] = val# (r,c)위치에 값 저장
    """

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
                except EOFError: #input 에러 처리의 하나로 사용 가능 , ctrl D 
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
                    break
                     # 이러한 에러 발생 시 다시 재입력 가능하게 while 문 안에 while 문을 넣은 것!
                if not all(x in ("0", "1") for x in row):
                    print(f"\n오류 : {i}번째 줄에 '0' 또는 '1'이 아닌 값이 포함되어 있습니다." )
                    valied =False
                    break

                
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
            print(f"필터 (Cross)와의 Mac 점수 : {score_a}")
            print(f"필터 (X)와의 Mac 점수 : {score_b}")
            print(f"연산 시간(평균/10회): {avg_time:.6f}ms")
            print(f"판정: {win_score}")
            print("=" * 40 + "\n")

            print("\n [4] 최적화 비교")
            print("\n ---------------------------------------")
            print("\n" + "="*40)
            print(f"최적화 필터 (Cross)와의 Mac 점수 : {score_1a}")
            print(f"최적화 필터 (X)와의 Mac 점수 : {score_1b}")
            print(f"최적화 연산 시간(평균/10회): {avg_1time:.6f}ms")
            print(f"판정: {win_1score}")
            print("=" * 40 + "\n")

        except ValueError:
            print("올바른 정수를 입력하세요.")


        
class Mode_2():
    """[모드 2] JSON 기반 데이터 일괄 검수 및 분석 실행기"""
    def __init__(self, json_path: str = "data.json"):
        self.json_path = json_path
        self.filters = {}
        self.patterns = {}

    def load_data(self) -> bool:
        try:
            with open(self.json_path,"r",encoding="utf-8") as f:
                read_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"[오류] 파일 로드 실패 : {e}")
            return False


        raw_filters = read_data.get("filters",{})
        raw_patterns = read_data.get("patterns",{})
        self.filters = {}
        self.patterns = {}

        """ 지금 2 -> 1 차원 축소 함
        이제 이 값들로 연산 수행 시작
        """
        



        for f_key, f_value in raw_filters.items():
            try:
                n_size = int(f_key.split('_')[1])
            except(IndexError,ValueError) as e:
                print("[오류]")
                n_size = None

            self.filters[f_key] = {
                "n_size" : n_size,
                "cross" : f_value.get("cross",[]),
                "x" : f_value.get("x",[])
            }
            
        for p_key, p_value in raw_patterns.items():
            try:
                n_size = int(p_key.split('_')[1])
            except(IndexError,ValueError):
                print("[오류]")
                n_size = None

            self.patterns[p_key] = {
                "n_size" : n_size,
                "input" : p_value.get("input",[]),
                "expected" : p_value.get("expected","UNKNOWN")
            }

        

        """
        기존 mode 2에서 필터와 패턴 배열만 차원 을 1차원으로 바꿔.  그리고 mac_1d에서 연산 후 기존 mode2_flow()의 출력값 + mac_1d()연산 값을 수행하는 거지
        여기서 핵심은 기존 값들을 없애면 안되. 기존 값 + 새로운 1d연산 값이 나오는 거니까
        그리고 패턴생성기는 클래스를 별도로 하나 만들어놨어.

        """

        return True
 
    def check_filter_pattern(self, p_key : str) -> tuple[bool,str]:
        p_data = self.patterns.get(p_key,{})
        n_size = p_data.get("n_size",0)
        input_data = p_data.get("input",[])

        if n_size is None or n_size <=0:
            return False, "N 크기 파싱 실패"

        f_key = f"size_{n_size}"
        f_data = self.filters.get(f_key, {})
        cross_filter = f_data.get("cross",{})
        x_filter = f_data.get("x",{})
        targets = [
            ("입력 패턴 ", input_data),
            ("Cross 필터", cross_filter),
            ("X 필터", x_filter)
        ]

        for name, input in targets:
            if len(input) != n_size or any(len(row) != n_size for row in input):
                return False, f"{name} 크기 불일치 (N={n_size})"# input, Cross, X필터 중 에러뜨면 에러 뜬 곳과 이유 반환!
        return True, "정상"
    """1. N 크기가 올바른 숫자인지 검사 (n_size > 0)
            2. input 데이터가 N개 행 & 각 행이 N개 열인지 검사
            3. Cross 필터 데이터가 N x N 인지 검사
            4. X 필터 데이터가 N x N 인지 검사
            => 하나라도 틀리면 (False, "에러 이유") 반환!"""
    
    def analyze_pattern(self, p_key: str)->dict:

        p_data = self.patterns.get(p_key, {}) 
        n_size = p_data.get("n_size",0)
        input_data = p_data.get("input",[])
        f_expected = p_data.get("expected","UNKNOWN")

        #정규화 하려면 패턴 값에 따른 필터 필요!
        f_key = f"size_{n_size}"
        f_data = self.filters.get(f_key,{})
        cross_data = f_data.get("cross",[])
        x_data = f_data.get("x",[])

        input_mat = Matrix(n_size, input_data) # 크기 정보와 데이터 묶어서 객체로 만듬.(바로 mac함수 사용)
        cross_mat = Matrix(n_size, cross_data)
        x_mat = Matrix(n_size, x_data)

        score_cross, time_cross=input_mat.mac(cross_mat)
        score_x, time_x = input_mat.mac(x_mat)

        #함수 호출을 어떻게 할건지? 과정부터 정하자!
        
        expected = only_normal(f_expected)#라벨까지 해주고 
        avg_time = (time_cross + time_x)/2.0 #각각 10회면 총 20회이니 2로 나눔

        
       # 임시 진단 코드

        """
        run() -> mode2_flow() -> load_data()호출 -> [1]필터로드 화면 출력 -> 패턴 수 만큼 반복문 실행(for p_key in self.pattern.key()) 
        -> check_filter_pattern()호출 -> analyze_pattern(p_key) 호출 ->dict형태로 반환 ->  [2]패턴 분석 결과 화면 출력
        """

        if abs(score_cross - score_x) < EPSILON:
            result =  "UNDECIDED"
            status = "FAIL"
            reason = "(동점(UNDECIDED)처리 규칙에 따른 FAIL)"
        
        elif score_cross > score_x:
            result = "Cross"
             
            if expected == "Cross" :
                status = "PASS"
                reason = "정상" 
            else:
                status = "FAIL"
                reason = f"불일치(예측: {expected} / 결과: Cross)에 따른 FAIL"
            
        else :
            result = "X"
            if expected == "X": 
                status = "PASS" 
                reason= "정상"
            else :
                status  ="FAIL"
                reason = f"불일치(예측: {expected} / 결과: X)에 따른 FAIL"

        input_mat_1d = Matrix_1D(n_size, input_mat)
        cross_mat_1d = Matrix_1D(n_size, cross_mat)
        x_mat_1d = Matrix_1D(n_size, x_mat)

        score_cross_1d , time_cross_1d = input_mat_1d.mac_1d(cross_mat_1d)
        score_x_1d, time_x_1d = input_mat_1d.mac_1d(x_mat_1d)
        avg_time_1d = (time_cross_1d + time_x_1d) / 2.0

        if abs(score_cross_1d - score_x_1d) < EPSILON:
            result_1d = "UNDECIDED"
        elif score_cross_1d > score_x_1d:
            result_1d = "Cross"
        else:
            result_1d = "X"

        return {
            "score_cross" : score_cross,
            "score_x" : score_x,
            "expected" : expected,
            "result" : result,
            "status" : status,
            "reason" : reason,
            "avg_time" : avg_time,
            "score_cross_1d" : score_cross_1d,
            "score_x_1d" : score_x_1d,
            "avg_time_1d" : avg_time_1d,
            "result_1d" : result_1d
        }



    def mode2_flow(self) -> None:
        print(f"\n -------[모드 2] {self.json_path} 자동 일괄 분석 ---------------")
        if not self.load_data():
            print("[오류] 데이터를 불러오지 못해 분석을 중단합니다.")
            return
        """
        run() -> mode2_flow() -> load_data()호출 -> [1]필터로드 화면 출력 -> 패턴 수 만큼 반복문 실행(for p_key in self.pattern.key()) 
        -> check_filter_pattern()호출 -> analyze_pattern(p_key) 호출 ->dict형태로 반환 ->  [2]패턴 분석 결과 화면 출력
        """
        print("\n#---------------------------------------")
        print("# [1] 필터 로드")
        print("#---------------------------------------")
        for f_key in self.filters.keys(): #딕셔너리의 key만 모을 수 있는 함수!
            print(f"✓ {f_key:<10} 필터 로드 완료 (Cross, X)")

        valid_result = {} #성능분석시에 사용할 패턴별 연산 결과를 담아둘 딕셔너리
        print("\n#---------------------------------------")
        print("# [2] 패턴 분석(라벨 정규화 적용)")
        print("#---------------------------------------")

        total_count= 0
        pass_count =0
        

        fail_case = []

        
        for p_key in self.patterns.keys():
            print(f"- --{p_key} ---")
            total_count +=1

            is_size_valid, size_error_reason = self.check_filter_pattern(p_key)
            if not is_size_valid:
                print(f"판정 : ERROR | FAIL ({size_error_reason})\n")
                fail_case.append((p_key,size_error_reason))
                continue

            analyze_result = self.analyze_pattern(p_key)
            valid_result[p_key] = analyze_result

            
            print(f"Cross 점수: {analyze_result['score_cross']:.17f}")
            print(f"X점수 : {analyze_result['score_x']:.17f}")
            print(f"판정: {analyze_result['result']} | expected: {analyze_result['expected']} | {analyze_result['status']} {analyze_result['reason']} ")

            if analyze_result["status"]=="PASS":
                pass_count+=1
            else:
                fail_case.append((p_key,analyze_result["reason"]))

        print("\n#---------------------------------------")
        print("# [3] 성능 분석 (평균/10회)")
        print("#---------------------------------------")
        print(f"{'크기':<12}{'평균 시간(ms)':<16}{'연산 횟수':<12}")
        print("#---------------------------------------")

        

        for p_key, p_value in valid_result.items():
            n_size= self.patterns[p_key].get("n_size",0)
            #흠..평균 시간 어떻게 불러오지? mac()함수를 또 불러오는건 로직 낭비.. 이미 불러왔던것 사용 
            # 근데 analyze_pattern()에서는 mac함수를 사용!
            size=f"{n_size}x{n_size}"
            avg_time = p_value['avg_time']
            count = n_size * n_size

            print(f"{size:<12}{avg_time:<12.4f}{count:<12}")

        print("#---------------------------------------")
        print("# [4] 결과 요약") 
        print("#---------------------------------------")

        fail_count = len(fail_case)

       
        
        print(f"총 테스트: {total_count}개")
        print(f"통과: {pass_count}개")
        print(f"실패: {fail_count}개\n")

        if  fail_case:
            print("실패 케이스")
            for p_key, reason in fail_case:
                print(f"- {p_key}: {reason}")
        print("\n")
        print("=" * 60)
        print("[수치 정밀도 검증] IEEE 754 부동소수점 오차 및 Epsilon 처리 시연")
        print("=" * 60)

        print("\n#---------------------------------------")
        print("# [5] 최적화 전/후 성능 분석 비교 (2D vs 1D)")
        print("#---------------------------------------")
        print(f"{'패턴 키':<12}{'2D 시간(ms)':<15}{'1D 시간(ms)':<15}{'개선율(%)':<12}{'판정 일치':<10}")
        print("#---------------------------------------")

        total_2d_time = 0.0
        total_1d_time = 0.0

        for p_key, p_value in valid_result.items():
            t_2d = p_value['avg_time']
            t_1d = p_value['avg_time_1d']

            total_2d_time += t_2d
            total_1d_time += t_1d

            # 속도 개선율 계산
            speedup = ((t_2d - t_1d) / t_2d * 100) if t_2d > 0 else 0.0
            
            # 2D 결과와 1D 최적화 결과가 서로 일치하는지 확인
            is_match = "일치" if p_value['result'] == p_value['result_1d'] else "불일치"

            print(f"{p_key:<12}{t_2d:<15.6f}{t_1d:<15.6f}{speedup:<12.2f}%{is_match:<10}")

        print("#---------------------------------------")
        if total_2d_time > 0:
            overall_speedup = ((total_2d_time - total_1d_time) / total_2d_time) * 100
            print(f" 기존 2D 방식 총 평균 소요시간 : {total_2d_time:.6f} ms")
            print(f" 최적화 1D 방식 총 평균 소요시간 : {total_1d_time:.6f} ms")
            print(f" 전체 속도 개선율             : {overall_speedup:.2f}% 단축")
        print("=" * 60 + "\n")







class Manager:
    def __init__(self):
        #__init__ 에서 인스턴스를 만들어 이전 실행결과를 기억!
        self.mode1_run = Mode_1()
        self.mode2_run = Mode_2("data.json")
        self.generator = Made_pattern()

    def menu(self) -> None:
        print("1. 사용자 직접 입력 모드 (Mode1)")
        print("2. data.json 자동 일괄 분석 모드 (Mode2)")
        print("3. 프로그램 종료")
        print("4. 패턴생성기!")

    def run(self) -> None:
        while True:
            self.menu()
            choice = input("원하는 모드를 선택하세요 : ").strip()

            if choice == "1":
                self.mode1_run.mode1_flow()
            elif choice == "2":
                self.mode2_run.mode2_flow()
            elif choice == "3":
                print("\n프로그램을 종료합니다. 이용해 주셔서 감사합니다!")
                break
            elif choice == "4":
                n=int(input("생성할 N 크기 입력하세요!: "))
                cross_pattern = self.generator.cross(n)
                x_pattern = self.generator.x(n)
                print(f"{n}x{n} Cross 패턴 생성 완료.")
                for row in cross_pattern:
                    print(row)
                print(f"{n}*{n} X 패턴 생성 완료!")
                for row in x_pattern:
                    print(row)
            elif choice == "5":
                print("1D 메모리 최적화 성능 분석 비교!")
                n= int(input("테스트할 N 크기 선택 기본(64)  : "))
                




            else:
                print("\n 올바른 번호를 입력해 주세요 (1, 2, 3).")


if __name__ == "__main__":
    manager = Manager()
    manager.run()
