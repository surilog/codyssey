import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "scripts"))
from mini_redis import MiniRedis
from command_executor import RedisCommandExecutor
import shlex 
import traceback
# 라이브러리 사용해도 되나?
def parse_input(user_input: str) -> list:
    try:
        return shlex.split(user_input)
    except ValueError:
        return None

def run_cli():
    redis_engine = MiniRedis()
    executor = RedisCommandExecutor(redis_engine)

    print("=" * 50)
    print(" welcome to Mini Redis CLI!")
    print(" 종료하려면 'exit' 또는 'quit'를 입력하세요.")
    print("=" * 50)

    while True:
        try:
            user_input = input("mini-redis> ").strip()
 
            if not user_input:
                continue

            if user_input.lower() in ["exit", "quit"]:
                print("Mini Redis를 종료합니다.")
                break

            cmd_tokens = parse_input(user_input)
            if cmd_tokens is None:
                print("(error) ERR syntax error or unclosed quote")
                continue

            result = executor.execute(cmd_tokens)
            if result:
                print(result)

        except KeyboardInterrupt:
            print("\nMini Redis를 종료합니다.")
            break
        except Exception as e:
            traceback.print_exc() #에러가 난 파일명과 위치 알기 위해 추가
            print(f"(error) ERR {str(e)}")


if __name__ == "__main__":
   run_cli()