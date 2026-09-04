import json

# 구버전 state.json 데이터 (point, history 키가 없는 버전.)
raw_json = '{"username": "Alice", "created_at": "2026-05-01"}'
user_data = json.loads(raw_json)

print("=== 2. dict.get() 하위 호환성 비교 ===")

# [수정 전] 키 직접 접근 -> KeyError 발생
print("\n [수정 전]")
try:
    username = user_data["username"]
    point = user_data["point"]  #  KeyError 발생!
    
    print(f"[{username}]님 포인트: {point}pt")
except KeyError as e:
    print(f"에러 발생!: KeyError {e} (구버전 데이터에 'point' 키가 없습니다)")

# [수정 후] dict.get() 사용 -> 기본값 지정으로 안전하게 로드
print("\n [수정 후]")
username = user_data.get("username", "익명")
point = user_data.get("point", 0)           # 키가 없으면 기본값 0
history = user_data.get("history", [])       # 키가 없으면 기본값 []

print(f"[{username}]님 포인트: {point}pt | 히스토리 개수: {len(history)}개")
print(" 구버전 데이터 파일이라도 튕기지 않고 정상적으로 불러옵니다.")