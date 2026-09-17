# decorators.py
import time
import sys
import functools
from .exceptions import BudgetAppException

def handle_errors(func):
    """공통 예외 처리 데코레이터: 에러 발생 지점의 메시지와 힌트를 깔끔하게 출력하고 sys.exit(1)로 종료"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except BudgetAppException as e:
            print(f"[오류] {e.message}")
            if e.hint:
                print(f"[힌트] {e.hint}")
            sys.exit(1)
        except Exception as e:
            print(f"[시스템 오류] ({func.__name__} 실행 중 오류): {e}")
            sys.exit(1)
    return wrapper

def log_execution_time(func):
    """함수의 실행 시간을 측정하여 출력하는 데코레이터"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"[LOG] {func.__name__} 실행 시간 : {(end_time - start_time) * 1000:.2f}ms")
        return result
    return wrapper