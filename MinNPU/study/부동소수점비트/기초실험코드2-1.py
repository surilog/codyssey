# 입력 데이터가 binary float(2진수)로 정확한지 확인
#실험 1. "내가 넣은 숫자가 깨끗한 숫자였나?"
#확인하려 한 것: 소수점 연산에서 정보가 이미 새어나갔는지 확인


#실험 2. "sum()과 for 루프는 저울이 다른가?"
#확인하려 한 것: 파이썬의 sum()과 일반 for total += ... 문이 내부적으로 다르게 계산되는지 확인.
#sum() (C-level 레지스터) vs for 루프 (Python Object) 차이 관찰



#실험 3. "잘라내는 규칙 때문에 똑같아진 게 맞나?"
#확인하려 한 것: 순서가 다른 두 계산(Cross vs X)이 마지막 자릿수 절삭 규칙(Round to Even) 때문에 비트가 똑같아지는 현상 확인.


"""
결론: 1. 데이터의 대칭성과 비 대칭성 차이!

    2. sum() 함수와 일반 loop문의 차이!
"""

import struct

def get_hex(num):
    return num.hex()

# 1. 2진수로 딱 떨어지지 않는 소수점 데이터 (실제 MAC 연산과 유사한 데이터)
# 0.1, 0.2 등은 2진수로 무한소수이므로 무조건 52비트 경계에서 잘립니다.
cross_data = [0.1, 0.2, 0.3, 0.4, 0.1, 0.2, 0.3, 0.4] * 100
x_data     = [0.4, 0.3, 0.2, 0.1, 0.4, 0.3, 0.2, 0.1] * 100

# 2. C-level sum() 연산
cross_sum = sum(cross_data)
x_sum     = sum(x_data)

# 3. 명시적 루프(loop) 연산
cross_loop = 0.0
for val in cross_data:
    cross_loop += val

print("=== 1. sum()을 썼을 때 Cross vs X 비교 ===")
print(f"Cross sum Hex : {get_hex(cross_sum)}")
print(f"X sum Hex     : {get_hex(x_sum)}")
print(f"비트 동일 여부: {get_hex(cross_sum) == get_hex(x_sum)}")

print("\n=== 2. 같은 Cross 데이터에서 sum() vs loop() 비교 ===")
print(f"sum() 결과  Hex : {get_hex(cross_sum)}")
print(f"loop() 결과 Hex : {get_hex(cross_loop)}")
print(f"두 결과가 같은가? : {get_hex(cross_sum) == get_hex(cross_loop)}")

# 1. 2^53 (약 90조, 53비트 가수부가 꽉 찬 상태)
big_num = float(2**53)

# 2. 아주 작은 미세 수들 (1.0)
small_nums = [1.0] * 5

# --- [방식 A] 큰 수를 먼저 더하기 ---
# big_num에 1.0을 더할 때마다 52비트 경계선 밖으로 밀려나서 1.0이 싹 잘려 나갑니다.
sum_A = big_num
for s in small_nums:
    sum_A += s

# --- [방식 B] 작은 수들을 먼저 다 더하고, 나중에 큰 수 더하기 ---
# 1.0 5개가 먼저 더해져 5.0이 된 후 big_num과 합쳐지므로 비트가 살아남습니다.
small_total = 0.0
for s in small_nums:
    small_total += s
sum_B = small_total + big_num

print("=== 100% 비트 차이 검증 ===")
print(f"방식 A (큰 수 먼저) Hex : {sum_A.hex()}")
print(f"방식 B (작은 수 먼저) Hex : {sum_B.hex()}")
print(f"10진수 표기 - 방식 A: {sum_A} | 방식 B: {sum_B}")
print(f"두 결과가 완벽히 같은가? : {sum_A.hex() == sum_B.hex()}")