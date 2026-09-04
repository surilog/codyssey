import json
import time


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
            total_sum = sum(              
                            self.data[r][c] * pathern.data[r][c]
                            for r in range(self.n)
                            for c in range(self.n)
            #메모리에 리스트 전체를 만들어두지 않고, 필요할 때마다 원소를 하나씩 생성(연산)하여  sum에 받는 즉시 누적하여 저장
                            )
            
            """
           

            return total_sum, avg_time

    """  
    def get_val(self, r: int, c: int) -> float:
        return self.data[r][c] #(r,c) 위치 반환

    def set_val(self, r:int, c:int, val : float):
        self.data[r][c] = val# (r,c)위치에 값 저장
    """
