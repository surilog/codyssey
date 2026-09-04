import json

# 1. JSON 데이터 로드
with open('data.json', 'r', encoding='utf-8') as f:
    json_data = json.load(f)

# 기존 5x5 필터 및 패턴 로드
cross_filter = json_data["filters"]["size_5"]["cross"]
x_filter = json_data["filters"]["size_5"]["x"]
n = 5

# Case 1: 기존 완벽 대칭 패턴 (size_5_1)
symmetric_pattern = json_data["patterns"]["size_5_1"]["input"]

# Case 2: 명확한 비대칭 패턴 생성 (한쪽 영역에만 가중치/노이즈 부여)
# (0, 0) 위치에만 0.5를 추가하여 좌우/상하 대칭성을 완전히 파괴함
asymmetric_pattern = [row[:] for row in symmetric_pattern]  # 깊은 복사
asymmetric_pattern[0][0] += 0.5 

def test_sum_pipeline(pattern_data, dataset_name):
    print(f"====================================================================================================")
    print(f"  [{dataset_name}] sum() C-level 파이프라인 연산")
    print(f"====================================================================================================")
    
    # sum() 연산 진행
    sum_cross = sum(cross_filter[r][c] * pattern_data[r][c] for r in range(n) for c in range(n))
    sum_x     = sum(x_filter[r][c] * pattern_data[r][c] for r in range(n) for c in range(n))
    
    is_exact_tie = (sum_cross.hex() == sum_x.hex())
    
    print(f" ├─ Cross 점수 : {sum_cross:<20} | Hex: {sum_cross.hex()}")
    print(f" ├─ X     점수 : {sum_x:<20} | Hex: {sum_x.hex()}")
    print(f" ├─ 비트 완벽 일치 여부 : {is_exact_tie}")
    print(f" └─ 최종 판정           : {' UNDECIDED (FAIL)' if is_exact_tie else ' 동점 해소 / 정상 분류 (PASS)'}\n")

# 1) 완벽 대칭 데이터 검증
test_sum_pipeline(symmetric_pattern, "1. 완벽 대칭 데이터셋 (size_5_1)")

# 2) 비대칭 데이터 검증
test_sum_pipeline(asymmetric_pattern, "2. 비대칭 데이터셋 (Asymmetric Input)")