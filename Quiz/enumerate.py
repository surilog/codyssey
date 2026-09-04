class QuizGame:
    def __init__(self):
        self.quizzes = ["Q1. 파이썬이란?", "Q2. 리스트란?"]

    def start_quiz_flow(self, quiz_list=None):
        print("=== 5. 파이썬 내장 기능 비교 ===")

        # 1) 삼항 연산자 (target_quizzes 할당)
        # [수정 전]
        if quiz_list is not None:
            target_quizzes_old = quiz_list
        else:
            target_quizzes_old = self.quizzes

        # [수정 후]
        target_quizzes_new = quiz_list if quiz_list is not None else self.quizzes

        print(f"선택된 퀴즈 목록 (삼항 연산자): {target_quizzes_new}")


        # 2) enumerate (선지 번호 매기기)
        choices = ["파이썬", "자바", "C++", "자바스크립트"]

        print("\n [수정 전 - i=1 수동 관리]")
        i = 1
        for choice in choices:
            print(f"{i}번 선지 : {choice}")
            i += 1

        print("\n [수정 후 - enumerate(choices, 1) 적용]")
        for idx, choice in enumerate(choices, 1):
            print(f"{idx}번 선지 : {choice}")

game = QuizGame()
game.start_quiz_flow()