from Mode_1 import Mode_1
from Mode_2 import Mode_2
from made_pattern import Made_pattern

class Manager:
    def __init__(self):
        self.mode1_run = Mode_1()
        self.mode2_run = Mode_2("data.json")
        self.generator = Made_pattern()

    def menu(self) -> None:
        print("1. 사용자 직접 입력 모드 (Mode1)")
        print("2. data.json 자동 일괄 분석 모드 (Mode2)")
        print("3. 프로그램 종료")
        print("4. 패턴생성기!")

    def run(self) -> None:
        while True:
            self.menu()
            choice = input("원하는 모드를 선택하세요 : ").strip()

            if choice == "1":
                self.mode1_run.mode1_flow()
            elif choice == "2":
                self.mode2_run.mode2_flow()
            elif choice == "3":
                print("\n프로그램을 종료합니다!")
                break
            elif choice == "4":
                n = int(input("생성할 N 크기 입력하세요!: "))
                cross_pattern = self.generator.cross(n)
                x_pattern = self.generator.x(n)
                print(f"{n}x{n} Cross 패턴 생성 완료.")
                for row in cross_pattern:
                    print(row)
                print(f"{n}*{n} X 패턴 생성 완료!")
                for row in x_pattern:
                    print(row)
                print("\n 올바른 번호를 입력해 주세요 (1, 2, 3).")

def only_normal(label_raw: str) -> str:
        if not label_raw:
            return "UNKNOWN"

        clean = str(label_raw).strip().lower()

        if clean in ["+","cross"]:
            return "Cross"
        elif clean in ["x"]:
            return "X"
        else:
            return "UNKNOWN"


if __name__ == "__main__":
    manager = Manager()
    manager.run()