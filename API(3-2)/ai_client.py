import requests

def call_ai_api(prompt, api_key, model="gemini-3-flash", temperature=0.7, max_tokens=2500):
    """Codyssey REST API를 호출하여 AI 응답을 받아옵니다."""
    url = "https://copa.codyssey.kr/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    data = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": temperature,
        "max_tokens": max_tokens
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response_json = response.json()

        if response.status_code == 200:
            choice = response_json.get("choices", [{}])[0]
            if choice.get("finish_reason") == "length":
                print("[WARNING] 최대 토큰 수(max_tokens)에 도달하여 응답이 중간에 잘렸습니다. --max-tokens 옵션 값을 더 크게 지정해주세요.")
            return choice.get("message", {}).get("content", "").strip()
        elif response.status_code == 401:
            print(f"[ERROR] 인증 실패 (401 Unauthorized): AI_API_KEY를 다시 확인해주세요.")
            return None
        elif response.status_code == 429:
            print(f"[ERROR] 요청 한도 초과 (429 Too Many Requests): 잠시 후 다시 시도해주세요.")
            return None
        else:
            print(f"[ERROR] API 요청 실패 (HTTP {response.status_code}): {response_json}")
            return None

    except requests.exceptions.Timeout:
        print("[ERROR] API 요청 시간이 초과되었습니다 (30초 타임아웃). 네트워크 상태를 확인해주세요.")
        return None
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] 네트워크 연결 중 오류 발생: {e}")
        return None
    except Exception as e:
        print(f"[ERROR] 알 수 없는 오류 발생: {e}")
        return None

