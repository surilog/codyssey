class QuizGame:
    def __init__(self):
        self.is_saved = False

    def save_data(self):
        self.is_saved = True
        print(" [save_data()] 진행 상황이 JSON 파일에 저장되었습니다.")

    # [수정 전] 예외 처리 없음
    def start_quiz_flow_before(self):
        print("\n [수정 전 흐름]")
        self.is_saved = False
        print("퀴즈 풀이 중... (강제 종료 발생")
        #raise KeyboardInterrupt() # 주석 해제 시 save_data() 도달 못하고 점수가 날아갑니다!
        self.save_data()

    # [수정 후] try-except-finally 적용
    def start_quiz_flow_after(self):
        print("\n [수정 후 흐름]")
        self.is_saved = False
        try:
            print("퀴즈 풀이 중...")
            raise KeyboardInterrupt() # 사용자가 Ctrl+C 누른 상황 시뮬레이션
        except KeyboardInterrupt:
            print("\n 사용자에 의해 프로그램이 강제 종료되었습니다.")
        finally:
            self.save_data() # 강제 종료되더라도 무조건 실행! 무조건 저장이 되기 때문에 사용 합니다!

game = QuizGame()
game.start_quiz_flow_before()
game.start_quiz_flow_after()