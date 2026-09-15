import time
import functools
from .exceptions import BudgetAppException

def handle_errors(func):#파이썬에서는 함수도 하나의 변수처럼 다른 함수의 인자(매개변수)로 전달가능

    """
    나중에 가계부 입력 함수인 `add_transaction()`에 `@handle_errors` 데코레이터를 붙이면, 
    파이썬 내부적으로 `add_transaction` 함수 전체가 `func`라는 이름의 변수로 `handle_errors` 안으로 들어오게 된다.
    """

    """공통 예외 처리 데코레이터: 지저분한 스택트레이스 대신 원인과 힌트를 출력"""
    @functools.wraps(func)# "원래 함수가 가지고 있던 이름(`__name__`)과 설명문(docstring) 등의 정체성을 잃어버리지 않도록 유지해 주는 역할
    #@functools.wraps(func)쓰지 않을 경우 CLI --help을 출력하거나 디버깅할 때 함수 이름이 모두 wrapper로 나오게 됨!

    def wrapper(*args, **kwargs): # *args, **kwargs를 가변 인자로 사용한 이유
        #=> 데코레이터가 어떤 형태의 매개변수를 가지는 함수에 적용될지 모르기 때문에, 모든 인자를 유연하게 받아 전달하기 위해서!
        # *1개는: 튜플형태로 **2개는: 딕셔너리 형태로 받음
        try:
            return func(*args, **kwargs)
        except BudgetAppException as e :
            print(f"[오류] {e.message}")
            if e.hint:
                print(f"[힌트] {e.hint}")
            return None
        except Exception as e:# 의BudgetAppException에서 잡지 못한 예외를 잡아줌!
            print(f"[시스템 오류] 예상치 못한 오류가 발생했습니다 {e}")
            return None
    return wrapper

def log_execution_time(func):
    """
    만약 파일에서 전체 거래 내역을 읽어오는 `load_all_transactions()`라는 함수 상단에 `@log_execution_time`을 붙인다면,
    그 `load_all_transactions` 함수가 `func`로 전달되어 log_execution_time 안으로 들어오게 된다!
    """
    """
    함수의 실행 시간을 굳이 알 필요 있을까?
    1.병목 구간 찾기+성능모니터링: 느리게 작동하는기능 로그로 남겨 확인 가능
    2.10만 건의 대용량 데이터를 다루더라도 읽기 시간이 단축되는지 직접 눈으로 검증할 수 있다.
      (예: "전체 로드 시 500ms vs 제너레이터 스트리밍 적용 시 5ms")
    """
    """함수의 실행 시간을 측정하여 출력하는 데코레이터"""
    def wrapper(*args, **kwars):
        start_time = time.time()
        result = func(*args,**kwars)
        end_time= time.time()
        print(f"[LOG] {func.__name__} 실행 시간 : {(end_time-start_time)*1000:.2f}ms")
        return result
    return wrapper
