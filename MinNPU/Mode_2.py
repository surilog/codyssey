import json
from Matrix import Matrix
from Matrix_1D import Matrix_1D

EPSILON = 1e-9

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
        from main import only_normal
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


