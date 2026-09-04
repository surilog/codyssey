import time

class Matrix_1D:
    def __init__(self, size: int, data_input=None):
        self.n = size
        from Matrix import Matrix
        # 1. 전달받은 입력이 Matrix 객체인지, 일반 리스트인지 판별
        if isinstance(data_input, Matrix): #isinstance: 객체가 특정 클래스의 인스턴스인지 확인하는 함수 맞으면 True, 아니면 False
            # Matrix 객체라면 그 내부의 사이즈(n) 말고 .data (2차원 리스트)를 추출
            source_data = data_input.data 
        elif isinstance(data_input, list):
            source_data = data_input
        else:
            source_data = None

        # 2. 1차원 배열(Flatten)로 변환
        if source_data:
            self.data_1d = [val for row in source_data for val in row]

            """
            data_1d = []
            for row in source_data:
                for val in row:
                     data_1d.append(val)
            """
        else:
            self.data_1d = [1.0] * (size * size)

    def mac_1d(self, pattern: "Matrix_1D", num_runs: int =10) -> tuple[float,float]:
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
            

    