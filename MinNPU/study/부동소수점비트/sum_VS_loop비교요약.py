import json
import time

# 1. JSON 데이터 로드
with open('data.json', 'r', encoding='utf-8') as f:
    json_data = json.load(f)

class Matrix:
    def __init__(self, n: int, data: list[list[float]]):
        self.n = n
        self.data = data

    def mac(self, pattern: 'Matrix', mode: str = 'sum') -> tuple[float, str]:
        """MAC 연산 (결과값과 16진수 Hex 반환)"""
        if mode == 'sum':
            total_sum = sum(
                self.data[r][c] * pattern.data[r][c]
                for r in range(self.n)
                for c in range(self.n)
            )
        else:
            total_sum = 0.0
            for r in range(self.n):
                for c in range(self.n):
                    total_sum += self.data[r][c] * pattern.data[r][c]

        return total_sum, total_sum.hex()


def diagnose_pattern(size_key: str, pattern_key: str):
    """
    특정 패턴 입력에 대해 Cross 필터 점수와 X 필터 점수를 각각 계산하여
    비트 단위 동점(UNDECIDED) 발생 여부를 진단합니다.
    """
    # Matrix 크기 파악 (e.g., "size_5_1" -> size_5)
    size_name = f"size_{size_key.split('_')[1]}"
    
    # 1. 데이터 가져오기
    cross_filter = Matrix(len(json_data["filters"][size_name]["cross"]), json_data["filters"][size_name]["cross"])
    x_filter     = Matrix(len(json_data["filters"][size_name]["x"]), json_data["filters"][size_name]["x"])
    
    pattern_input = Matrix(len(json_data["patterns"][pattern_key]["input"]), json_data["patterns"][pattern_key]["input"])
    expected_type = json_data["patterns"][pattern_key]["expected"]

    print(f"\n==================================================================")
    print(f"  [진단] 패턴: {pattern_key} (기대 결과: '{expected_type}')")
    print(f"==================================================================")

    # 2. sum() 방식 및 loop() 방식 각각에서 Cross vs X 점수 비교
    for mode in ['sum', 'loop']:
        cross_score, cross_hex = cross_filter.mac(pattern_input, mode=mode)
        x_score, x_hex         = x_filter.mac(pattern_input, mode=mode)

        # 비트 단위 완벽 동점 여부
        is_exact_tie = (cross_hex == x_hex)
        
        # 승자 판정 (동점이면 UNDECIDED)
        if is_exact_tie:
            winner = " UNDECIDED (동점 발생 -> FAIL)"
        elif cross_score > x_score:
            winner = "cross (+)"
        else:
            winner = "x"

        print(f"[{mode.upper():^4} 파이프라인]")
        print(f" ├─ Cross 점수 : {cross_score:<20} | Hex: {cross_hex}")
        print(f" ├─ X     점수 : {x_score:<20} | Hex: {x_hex}")
        print(f" ├─ 비트 일치(동점) : {is_exact_tie}")
        print(f" └─ 판정 결과    : {winner}\n")


# 확인해야 할 3가지 데이터 셋 실행
target_patterns = [
    ("size_5", "size_5_1"),
    ("size_13", "size_13_2"),
    ("size_25", "size_25_1")
]

for size_k, pattern_k in target_patterns:
    diagnose_pattern(size_k, pattern_k)



"""
sum()**은 C-API 연속 누적 과정에서 대칭 데이터의 미세 오차가 반올림 규칙에 의해 같은 비트로 정리되어 동점이 되고,
**loop()**는 행렬 탐색 순서에 따른 부동소수점 누적 순서 오차가 하위 비트에 살아남아 동점이 해소되는 것입니다.
"""