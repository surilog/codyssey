import array
import re
import json


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

    def mac(self, pathern: 'Matrix') -> float | None:
            if self.n != pathern.n:
                print(f" 오류 : 행렬 크기가 맞지 않습니다. ({self.n}*{self.n}) VS ({pathern.n}*{pathern.n})")
                return None
            if not self.data or not pathern.data:
                print("오류 : 행렬 데이터가 없습니다. ")
                return None
    
            #제너레이터를 쓰면 0부터 더해서 초기화 필요 X
            total_sum = sum(
                self.data[r][c] * pathern.data[r][c]
                for r in range(self.n)
                for c in range(self.n)
            )
            """total_sum= sum(self.data[r][c] * pathern.data[r][c]for r in range(self.n)for c in range(self.n))"""
            """
            total_sum = 0.0
            
            for r in range(self.n):
                for c in range(self.n):
                    total_sum += self.data[r][c] * pathern.data[r][c]"""
            return float(total_sum)

    """  
    def get_val(self, r: int, c: int) -> float:
        return self.data[r][c] #(r,c) 위치 반환

    def set_val(self, r:int, c:int, val : float):
        self.data[r][c] = val# (r,c)위치에 값 저장
        """

    def display(self):
        print(f"[{self.n}x{self.n}  ")
        for row in self.data:
            print(row)

class Mode_1:

    def user_input(self, name:str, n_size: int) -> Matrix:
        mat=Matrix(n_size)
        print(f"\n[{name} 입력 ({n_size}x{n_size})]")
        print(f"아래에 {n_size}줄의 데이터를 한 번에 입력(또는 붙여넣기) 후, 엔터를 한 번 더 눌러주세요:")
                
        
        while True :
            lines = []
            while True:
                try:
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
            filter_a = self.user_input("필터 A (Cross)", n_size)
            filter_b = self.user_input("필터 B (X)", n_size)
            input_pattern = self.user_input("검사할 패턴", n_size)

            score_a = input_pattern.mac(filter_a)
            score_b = input_pattern.mac(filter_b)

            print("\n" + "="*40)
            print(f"필터 A(Cross)와의 Mac 점수 : {score_a}")
            print(f"필터 B(X)와의 Mac 점수 : {score_b}")
            print("=" * 40 + "\n")

        except ValueError:
            print("올바른 정수를 입려하세요.")


        
class Mode_2():
    """[모드 2] JSON 기반 데이터 일괄 검수 및 분석 실행기"""
    def __init__(self, json_path: str = "data.json"):
        self.json_path = json_path
        self.filters = {}
        self.patterns = {}


    def N_from_patterns_key(self, pattern_key : str) -> int | None:
        """패턴 키에서 크기 N 추출"""
        match = re.match(r"^size_(\d+)_", pattern_key)
        return int(match.group(1)) if match else None


    #동작 메서드/ 데이터 검문소!
    def process_pattern(
            self, pattern_key:str, input_data:list, standard_filter: list,
            n_size: int, expected:str, filter_label: str) -> dict:
        
        filter_mat = Matrix(n_size, standard_filter)
        input_mat = Matrix(n_size, input_data)

        score = input_mat.mac(filter_mat)
        """
        내부적으로 self에는 input_mat의 데이터가, pathern에는 filter_mat의 데이터가 들어가면서 
        두 행렬의 원소끼리 곱하고 더하는 연산(MAC)이 수행
         total_sum = sum(
                        self.data[r][c] * pathern.data[r][c]
                        for r in range(self.n)
                        for c in range(self.n)
                    )
        """
        return {
            "id" : pattern_key,
            "status" : "PASS",
            "score" : score,
            "expected": expected,
            "filter_type": filter_label,
            "reason": f"정상 처리 완료 (MAC Score: {score})"
        }
    #준비 및 흐름제어 

    def select_filter(self, pattern_key:str, pattern_data:dict) -> dict:
        expected = pattern_data.get("expected", "UNKNOWN")# 0. 기본 기대 결과값 가져오기
        expected_label = only_normal(expected)

        n_size = self.N_from_patterns_key(pattern_key)# [1차 검문] 패턴 키 이름 규칙 검사 (예: 'size_3_01' -> N=3)
        if n_size is None:
            return{
                "id" : pattern_key,
                "status" : "FAIL",
                "reason" : "패턴 키 명명 규칙 위반 ('size_N_idx' 형식이 아님)",
                "expected": expected_label
            }
        #
        # [2차 검문] 매칭되는 기준 필터 존재 여부 검사
        filter_key = f"size_{n_size}"
        if filter_key not in self.filters:
            return {
                "id" : pattern_key,
                "status" : "FAIL",
                "reason" : f"대응 필터({filter_key}) 없음",
                "expected" : expected_label
            }
        
# 검사할 데이터 2개 추출 (필터 2D 데이터, 입력 2D 데이터)
        filter_raws = self.filters[filter_key]
        #cross_filter_data = filter_raws.get("cross",[])
        #x_filter_data = filter_raws.get("x",[])
        input_raws = pattern_data.get("input", [])
        

#[3차 검문] 필터 데이터의 크기가 N x N 인지 검사
        if len(filter_raws) != n_size or any(len(row) != n_size for row in filter_raws):
            return{
                "id": pattern_key,
                "status": "FAIL",
                "reason" : f"필터 크기 불일치(기준 : {n_size}x{n_size})",
                "expected": expected_label
            }
        raw_filter_type = pattern_data.get("filter_type", "cross" if "cross" in pattern_key.lower() else "x")
        filter_label = only_normal(raw_filter_type)

        # [4차 검문] 입력 데이터의 크기가 N x N 인지 검사
        if len(input_raws) != n_size or any(len(row) != n_size for row in input_raws):
            actual_hight = len(input_raws)
            actual_width = len(input_raws[0]) if actual_hight > 0 else 0
            return {
                "id": pattern_key,
                "status" : "FAIL",
                "reason" : f"입력 크기({actual_hight}x{actual_width}) 불일치",
                "expected" : expected_label
            }
        return self.process_pattern(pattern_key, input_raws, filter_raws, n_size, expected_label, filter_label)


    def mode2_flow(self) -> None:
        print(f"\n -------[모드 2] {self.json_path} 자동 일괄 분석 ---------------")
        try:
            with open(self.json_path, "r", encoding="utf-8") as f:
                raw_data = json.load(f)
        except FileNotFoundError:
            print(f"오류 : '{self.json_path}' 파일을 찾을 수 없습니다.")
            return
        except json.JSONDecodeError:
            print(f"오류: '{self.json_path}' 파일 형식이 올바르지 않습니다.")
            return

        self.filters = raw_data.get("filters",{})
        self.patterns = raw_data.get("patterns",{})# patterns의 값을 가져옴
        print("\n#---------------------------------------")
        print("# [1] 필터 로드")
        print("#---------------------------------------")
        for f_key in self.filters.keys(): #딕셔너리의 key만 모을 수 있는 함수!
            print(f"✓ {f_key:<10} 필터 로드 완료 (Cross, X)")

        print("\n#---------------------------------------")
        print("# [2] 패턴 분석(라벨 정규화 적용)")
        print("#---------------------------------------")

        for p_key, p_data in self.patterns.items(): # ex) p_key: size_3_01 p_data: {input[]},expected
            print(f"\n- --{p_key}---")
            score_cross = p_data.get("score_cross",1.0) # p_data에는 score_cross가 없는데?

            
              
        
        print("\n"+"="*50)
        print("\n분석 결과 목록")
        for p_key, p_data in self.patterns.items():
            res = self.process_pattern_flow(p_key, p_data)
            print(f"ID: {res['id']} | 상태: {res['status']} | 결과: {res['reason']}")



class Manager:
    def __init__(self):
        #__init__ 에서 인스턴스를 만들어 이전 실행결과를 기억!
        self.mode1_run = Mode_1()
        self.mode2_run = Mode_2("data.json")

    def menu(self) -> None:
        print("1. 사용자 직접 입력 모드 (Mode1)")
        print("2. data.json 자동 일괄 분석 모드 (Mode2)")
        print("3. 프로그램 종료")

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

            else:
                print("\n 올바른 번호를 입력해 주세요 (1, 2, 3).")


if __name__ == "__main__":
    manager = Manager()
    manager.run()

   
    """ try:
        n_size = int(input("만들고 싶은 N x N 배열의 크기(N)를 입력하세요:  "))

        if n_size <= 0:
            print("크기는 1 이상의 양수여야 합니다! ")
        else:
            pattern=Matrix(n_size)
            while True:
                if pattern.user_input(name="사용자 패턴"):
                    break
                print("다시 시도해 주세요.\n")

        # 결과 확인
        pattern.display()

    except ValueError:
        print("N은 정수여야 합니다.")
         my_matrix = Matrix(n_size)
        print("--기본 생성된 배열")
        my_matrix.display()

        for i in range(n_size):
            my_matrix.set_val(i,i,1.0)
        print("\n--대각선 값을 1로 변경한 후 배열")
        my_matrix.display()

    except ValueError:
        print("올바른 정수를 입력해주세요.")"""