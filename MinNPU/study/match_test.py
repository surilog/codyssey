import re

pattern_key = "size_25_test_sample"
match = re.match(r"^size_(\d+)_", pattern_key)

if match:
    print(match.group(0))  # 출력: 'size_25_' (매칭된 전체 글자)
    print(match.group(1))  # 출력: '25'       (1번 괄호 안의 글자, str 타입)
    
    n = int(match.group(1))
    print(n, type(n))      # 출력: 25 <class 'int'> (숫자로 변환 완료!)

    