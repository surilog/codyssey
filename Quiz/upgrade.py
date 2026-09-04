import tkinter as tk
from tkinter import messagebox

# (위에는 기존 작성하신 User, Quiz, QuizGame 클래스가 그대로 위치합니다)

import json
import random
from datetime import datetime

class User:
    def __init__(self, username, point = 0, best_score=0, history=None, created_at = None):
        self.username = username
        self.point = point
        self.best_score = best_score
        self.history = history if history is not None else []
        self.created_at = created_at if created_at is not None else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        #__init__의 속성으로  [] 안 넣는 이유
        # 기본값이 [] 되버리면 모든 유저 객체가 단 하나의 리스트를 공유하게 된다.
        # 조건문으로 유저마다 각각 독립된 새로운 빈 리스트를 만들어 주는 것.



    def to_dict(self):
        return {"username" : self.username, "point" : self.point, "best_score" : self.best_score, "history" : self.history, "created_at": self.created_at}
    



class Quiz:
    def __init__(self, question:str, choices: list, answer:str, hint:str = "힌트가 제공되지 않는 문제입니다."):
        self.question = question
        self.choices = choices
        self.answer = answer
        self.hint = hint

        if self.answer not in self.choices:
            raise ValueError(
                f"정답 '{self.answer}'이(가) 선지 {self.choices} 에 없습니다. "
                f"(문제: {self.question})"
            )
        self.hint = hint

    def check_answer(self, user_answer: str):
        return user_answer == self.answer

    def get_answer_number(self):
        return self.choices.index(self.answer) + 1

class QuizGame:
    def __init__(self, data_file: str ="state.json", HINT_COST =1):
        self.data_file = data_file
        self.quizzes = []
        self.users = []
        self.highest_score_overall = 0
        self.quizzes, self.users = self.load_data()
        self.HINT_COST = HINT_COST
        #덮어쓰기(save_data)를 해서 기존 파일을 백지로 만들기 전에, 
        # 옛날 내용을 파이썬 머릿속으로 먼저 옮겨 담는 작업(load_data)이 반드시 필요!
        #위치: __init__은 프로그램 시작 시 단 한 번 실행되는 초기화 장소
        #즉, 바로 데이터를 메모리에 저장하기 위해서
        
        #a모드로 파일 여는 방법 안되는 이유:
        #"a" 모드는 파일 끝에 글자를 그냥 덧붙이는 기능이다.
        #JSON은 문법 구조([...])가 엄격해서 그냥 덧붙이면 파일이 깨진다.
    def update_highest_score(self):
    
        if not self.users:
            self.highest_score_overall = 0
        else:
            self.highest_score_overall = max(
                user.best_score for user in self.users
            )



    def load_data(self):
        default_quiz_data = [
                    {
                        "question": "다음 중 상대경로의 설명으로 적절한 것은?",
                        "choices": [
                            "현재 디렉토리에서 파일을 찾는 경로",
                            "루트 디렉토리에서 파일을 찾는 경로",
                            "절대 경로",
                            "고정된 경로"
                        ],
                        "answer": "현재 디렉토리에서 파일을 찾는 경로",
                        "hint" : "자유롭다..."
                    },
                    {
                        "question": "바인드 마운트에 대한 설명으로 적절한 것은?",
                        "choices": [
                            "호스트의 디렉토리를 컨테이너에 연결하는 방식",
                            "정해진 위치에서만 데이터를 읽고 쓸 수 있는 방식",
                            "영속성이 없는 임시 저장 방식",
                            "컨테이너 내부에서만 데이터를 저장하는 방식"
                        ],
                        "answer": "호스트의 디렉토리를 컨테이너에 연결하는 방식",
                        "hint" : "실시간 전송!"
                    },
                    {
                        "question": "다음 docker-compose.yml 파일에서의 depends_on 옵션의 역할은 무엇인가?\n\nversion: '3.8'\nservices:\n  web:\n    image: nginx:latest\n    depends_on:\n      - cache-redis\n      - db-postgres\n...",
                        "choices": [
                            "WEB 서비스가 시작되기 전에 cache-redis와 db-postgres 서비스가 먼저 시작되도록 보장한다.",
                            "WEB 서비스가 시작되기 전에 cache-redis와 db-postgres 서비스가 먼저 종료되도록 보장한다.",
                            "cache-redis와 db-postgres 서비스가 시작되기 전에 WEB 서비스가 먼저 시작되도록 보장한다.",
                            "WEB 서비스가 시작되기 전에 cache-redis와 db-postgres 서비스가 먼저 삭제되도록 보장한다."
                        ],
                        "answer": "WEB 서비스가 시작되기 전에 cache-redis와 db-postgres 서비스가 먼저 시작되도록 보장한다.",
                        "hint" : "의존...은 후순위?"
                    },
                    {
                        "question": "다음 중 다운로드된 도커 이미지를 확인하는 명령어는?",
                        "choices": [
                            "docker image",
                            "docker ps",
                            "docker ps -a",
                            "docker images"
                        ],
                        "answer": "docker images",
                        
                    },
                    {
                        "question": "다음 프로그램의 결과로 알맞은 것은? \n\nclass Animal: def __init__(self, name, age): self.name = name\n       self.age = age\n      def say(self):\n        print(f\"안녕하세요. 제 이름은 {self.name}이고, 나이는 {self.age}살 입니다.\")\n\nclass Dog(Animal):\n        def __init__(self, name, age, breed):\n          super().__init__(name, age)\n          self.breed = breed\n        def say(self):\n          print(f\"안녕. 내 이름은 {self.name}이고, 나이는 {self.age}살!. 나는 {self.breed}!.\")\nwolf = Dog(\"늑대\", 3, \"허스키\")\nwolf.say()",
                        "choices": [
                            "안녕하세요. 제 이름은 늑대이고, 나이는 3살 입니다. 저는 허스키입니다.",
                            "안녕. 내 이름은 늑대이고, 나이는 3살!. 나는 허스키!.",
                            "안녕하세요. 제 이름은 늑대이고, 나이는 3살 입니다. 나는 허스키!.",
                            "안녕. 내 이름은 늑대이고, 나이는 3살!. 저는 허스키입니다."
                        ],
                        "answer": "안녕. 내 이름은 늑대이고, 나이는 3살!. 나는 허스키!.",
                        "hint" : "상속"
                    },
                     {
                        "question" : "다음 설명 중 틀린 것은?", 
                        "choices" : ["shell은 사용자의 명령을 입력받아 커널이 이해할 수 있도록 번역해준다.",
                                    "shell은 커널이 직접적인 위협으로부터 감싸주는 인터페이스다.",
                                    "커널은 하드웨어(CPU,메모리)등을 직접 제어하고 관리하는 가장 핵심적인 제어 프로그램이다",
                                    "허가받지 않은 사용자가 shell의 모든 기능을 사용 할 수 있게 하는 것은 바람직하다."
                                     ],
                        "answer" : "허가받지 않은 사용자가 shell의 모든 기능을 사용 할 수 있게 하는 것은 바람직하다.",
                        "hint" : "쉘은 복숭아 씨 입니다. 커널이 복숭아 씨 안의 말랑한 부분이면 쉘은 그 위를 감싸는 복숭아 씨와 같습니다."
                    },
                    {
                        "question" : "다음 중 터미널에 대해서 알맞지 않은 것은?" ,
                        "choices" : ["terminal이란 '끝' 이라는 의미로 사람의 명령이 입력되고 결과가 출력되는 최전선의 접점이라는 의미를 가지고 있다.",
                                     "터미널이란 초창기에 글자만 입력하고 출력받을 수 있는 키보드와 모니터로 구성된 단말기를 의미했다",
                                     "사용자가 입력한 명령어 문자열을 해석하여 커널이 이해할 수 있도록 해주는 역할을 한다.",
                                     "사용자가 텍스트를 입력하고 컴퓨터의 실행결과를 돌려받는 입출력 통로 역할을 한다."],
                        "answer" : "사용자가 입력한 명령어 문자열을 해석하여 커널이 이해할 수 있도록 해주는 역할을 한다.",
                        "hint" : "커널의 기능과 헷갈리면 안됩니다!"
                    },

                ]
        default_user_data = []
        try:
            with open(self.data_file, "r", encoding="utf-8") as file:
                state_data = json.load(file)
                quiz_data = state_data.get("quizzes",[])
                user_data = state_data.get("users",[])

                quizzes = []# json파일과 같이 리스트안 딕셔너리로 만들기 위해 리스트로 설정
                for quiz_item in quiz_data:
                    try:
                         quiz = Quiz(
                             question=quiz_item["question"],
                             choices=quiz_item["choices"],
                             answer=quiz_item["answer"],
                             hint = quiz_item.get("hint", "힌트가 없습니다.")
                         )
                         quizzes.append(quiz)
                    except KeyError as e:
                        print(f"\n 퀴즈 데이터 형식 오류: {e}. 해당 퀴즈 항목을 건너뜁니다.")

                users = []
                for user_item in user_data:
                    try:
                         user= User(
                             username=user_item["username"],
                             point=user_item["point"],
                             best_score=user_item["best_score"],
                             history=user_item.get("history", []),
                             created_at = user_item.get("created_at","기록 없음")
                            )
                         
                         users.append(user)
                    except KeyError as e:
                        print(f"\n 유저 데이터 형식 오류: {e}. 해당 유저 항목을 건너뜁니다.")

                if not quizzes:
                    quizzes=[Quiz(**quiz) for quiz in default_quiz_data]
                return quizzes, users
        except (FileNotFoundError, json.JSONDecodeError, AttributeError, ValueError, KeyError):
    # 파일이 없거나 훼손되었으면 기본 퀴즈 데이터와 빈 유저 리스트를 반환
         quizzes = [Quiz(**quiz) for quiz in default_quiz_data]
         users = [User(**user) for user in default_user_data]
         print("\n 파일이 존재하지 않거나 손상되었습니다. 기본 퀴즈 데이터를 사용하겠습니다.")
         return quizzes, users
         
                

                    
                    

    def save_data(self):
        try:
            with open(self.data_file, "w", encoding="utf-8") as file:
                data = {
                    "quizzes" :  [
                       { "question": new_quiz.question,
                        "choices" : new_quiz.choices,
                        "answer" : new_quiz.answer,
                        "hint" : new_quiz.hint
                    }
                    for new_quiz in self.quizzes
                    ],
                    "users" : [
                        new_user.to_dict() for new_user in self.users]
                }
                json.dump(data,file,ensure_ascii=False, indent=4)
        except(PermissionError, OSError) as e:
            print(f"\n 파일 저장 중 문제가 발생했습니다 : {e}")


    def find_user(self, username: str):
        for user in self.users:
            if user.username == username:
                return user
        return None
    
    def register_user(self, username: str):
        if self.find_user(username) is not None:
            return False

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_user = User(username=username, created_at=now)
        self.users.append(new_user)
        self.save_data()
        return True

        
    def add_quiz(self, question: str, choices: list, answer: str, hint:str):
        new_quiz = Quiz(question=question, choices=choices, answer=answer, hint=hint)
        self.quizzes.append(new_quiz)
        self.save_data()


#self.가 없다: 이 함수 안에서만 잠깐 쓰고 버릴 데이터 (예: 입력받은 question, 방금 만든 new_quiz)

#self.가 있다: 이 프로그램이 끝날 때까지 객체가 계속 들고 다녀야 할 내 데이터나 내 기능 
#(예: 전체 퀴즈 목록 self.quizzes, 저장하는 기능 self.save_data())
    def random_quiz(self):
        if not self.quizzes:
            print("\n등록된 퀴즈가 없습니다.")
            return
        shuffled_quizzes = self.quizzes.copy()
        random.shuffle(shuffled_quizzes)
        self.start_quiz_flow(shuffled_quizzes)
  

    

    def delete_quiz(self):
        if not self.quizzes:
            print("\n삭제할 퀴즈가 없습니다.")
            return
        print("\n---[퀴즈 삭제]--- ")
        for i, quiz in enumerate(self.quizzes, 1):
            print(f"{i}번. quiz문제 {quiz.question}")

        user_input = input("삭제할 퀴즈 번호를 입력하세요 :  ").strip()
        if user_input.isdigit():
            num = int(user_input)
            if 0 < num <= len(self.quizzes):
                removed = self.quizzes.pop(num-1)
                self.save_data()
                print(f"{removed.question} 퀴즈가 삭제되었습니다. ")
            else:
                print("\n목록에 없는 번호입니다.")
        else:
            print("\n 올바른 숫자를 입력해주세요.")

    def run(self):
        
        try:
            while True:
                print("\n" + "=" * 40)
                print("1. 퀴즈 풀기\n"
                "2. 사용자 등록\n"
                "3. 사용자 목록\n"
                "4. 점수 확인\n"
                "5. 종료 화면\n"
                "6. 퀴즈 추가\n"
                "7. 퀴즈 목록\n"
                "8. 랜덤 퀴즈 풀기\n"
                "9. 퀴즈 삭제")
                print("=" * 40)
                input_menu = input("메뉴를 선택하세요: ").strip()

                if input_menu == "1":
                    self.start_quiz_flow()
                elif input_menu == "2":
                    self.register_user_flow()
                elif input_menu == "3":
                    self.show_users_flow()
                elif input_menu == "4":
                    self.check_score_flow()
                elif input_menu == "5":
                    print("\n프로그램을 종료합니다.")
                    break
                elif input_menu == "6":
                    self.add_quiz_flow()
                elif input_menu == "7":
                    self.quiz_list()
                elif input_menu == "8":
                    self.random_quiz()
                elif input_menu == "9":
                    self.delete_quiz()
                else:
                    print("\n잘못된 입력입니다. 1~9번 사이의 숫자를 입력해주세요.")
        except KeyboardInterrupt:
            print("\n사용자에 의해 프로그램이 강제 종료되었습니다.")
        except EOFError:
            print("\n입력 스트림이 종료되었습니다. 프로그램을 종료합니다.")
        finally:
            self.save_data()
            print("\n프로그램을 안전하게 정리하고 종료하겠습니다.")



    def start_quiz_flow(self, quiz_list=None):
        
        name = input ("\n퀴즈를 풀 사용자 이름을 입력해주세요 : ").strip()
        current_user = self.find_user(name)

        if not current_user:
            print(f"[{name}] 님은 등록되지 않은 사용자 입니다. 먼저 사용자 등록을 해주세요!") 
            return
        print(f"\n[{name}]님 , 퀴즈를 시작합니다!")
        
        target_quizzes = quiz_list if quiz_list is not None else self.quizzes
        #quiz_list(start_quiz_flow(random_quizzes)에서 전달됩니다.)가 있으면 ==> random   / 없으면 전체 문제 받아옵니다!  
        if not target_quizzes:
            print("\n풀 수 있는 퀴즈가 없습니다.")
            return
        
        user_select = input(f"몇 문제 풀고 싶으신가요? (현재 문제 수 : {len(target_quizzes)}문제) ").strip()
        if not user_select.isdigit():
            print("숫자만 입력해 주세요.")
            return
        
        num = int(user_select)
        if num <= 0:
            print(" 1문제 이상 선택하셔야 합니다.")
            return
        elif num > len(target_quizzes):
            print(f" 문제 수가 부족하여 전체 문제({len(target_quizzes)}개)로 진행합니다.")
            num = len(self.quizzes)

        selected_quizzes = target_quizzes[:num]

        
        try:
            score_gain = 0
            sub_score = 0
            for idx, quiz_items in enumerate(selected_quizzes, 1):
                print(f"\n문제 {idx} 번 : {quiz_items.question}")
                
                for i, choice in enumerate(quiz_items.choices, 1):
                    print(f"{i}번 선지 : {choice}")
                print(f"\n힌트가 필요하시면 5를 입력하세요! 소유 포인트{current_user.point}pt 차감 포인트{self.HINT_COST}")
                hint_used_this_quiz = False
                while True:
                    user_input = input("\n 정답을 입력하세요 : ").strip()

                    if user_input == "5":
                        if hint_used_this_quiz:
                            print("이미 이 문제의 힌트를 확인했습니다.")
                        elif current_user.point < 1 :
                            print("포인트를 1pt 이상 보유해야 힌트를 확인 할 수 있습니다.")
                        else:
                            current_user.point -=1  
                            sub_score +=1
                            print(f"\n힌트는 {quiz_items.hint} 입니다! ")
                            print(f" (1 포인트가 차감되었습니다. 남은 포인트는 {current_user.point}pt 입니다!)")
                            hint_used_this_quiz = True
                        continue
                    if user_input.isdigit() and 1<= int(user_input) <=4:
                        break
                    else:
                        print("잘못된 입력입니다. 1~4 사이의 번호나 힌트 (5)를 입력해주세요. ")


                user_choice = quiz_items.choices[int(user_input) - 1]
                if quiz_items.check_answer(user_choice):
                    print("정답입니다! +1점")
                    score_gain +=1
                    current_user.point +=1
                else:
                    print(f"틀렸습니다. 정답은 {quiz_items.get_answer_number()}번의 {quiz_items.answer}입니다.")

            if score_gain > current_user.best_score:
                current_user.best_score = score_gain

            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            record = {
                "date": now,
                "total_questions" : len(selected_quizzes),
                "score" : score_gain
            }
            current_user.history.append(record)
            self.save_data()

                 

        except KeyboardInterrupt:
            print("\n사용자에 의해 프로그램이 강제 종료되었습니다.")
        except EOFError:
            print("\n입력 스트림이 종료되었습니다. 프로그램을 종료합니다.")
        finally:
            self.save_data()
            print("\n프로그램을 안전하게 정리하고 종료하겠습니다.")
            print("=" * 40)
            print(f"현재 희득 중인 포인트: {score_gain} 점 , 깍인 포인트: {sub_score} ,최고 점수: {current_user.best_score} 점, 지금까지 희득한 포인트 : {current_user.point}pt ")
            print("=" * 40)
                
      
   
    def check_score_flow(self): 
        name = input("\n점수를 확인할 사용자를 입력해주세요: ").strip()
        user = self.find_user(name)
        if user:
            print(f"[{user.username}]님의 현재까지 쌓인 포인트 : {user.point} , 최고 점수: {user.best_score}점 입니다.")
            print(f"[게임 히스토리] {len(user.history)}회")

            if not user.history:
                print("아직 진행한 게임이 없습니다.")
            else:
                for idx, record in enumerate(user.history,1):
                    print(f" {idx}. [{record['date']}] {record['total_questions']}문제 중 {record['score']}점 희득")
        else:
            print(f"[{name}]님은 등록되지 않은 사용자입니다. 먼저 사용자 등록을 해주세요!")
            return
        
    def quiz_list(self): 
        print("\n---[ 퀴즈 목록 ]---")
        if not self.quizzes:
            print("등록된 퀴즈가 없습니다.\n")
            return
        for idx, quiz in enumerate(self.quizzes, 1):
            print(f"{idx}. 문제 {quiz.question} \n정답 : 비밀입니다!")


    def register_user_flow(self): 
           new_name = input("\n등록할 사용자 이름을 입력해주세요 : ").strip()
   
           if not new_name:
               print("이름은 빈 칸일 수 없습니다.")
               return
   
           if self.register_user(new_name) is False :
               print(f"\n[{new_name}]님은 이미 등록된 사용자입니다.")
   
           else:
               print(f"\n[{new_name}]님이 새로 등록되었습니다!")
 
    def show_users_flow(self):
        print("\n ---[사용자 목록]---")
        if not self.users:
            print("\n 등록된 사용자가 없습니다.")
            return
        for idx, user in enumerate(self.users,1):
            print(f"{idx}. {user.username} | 등록일: {user.created_at} | 보유 포인트 : {user.point}pt (최고 점수 :  {user.best_score})점")

    def add_quiz_flow(self):
        question = input("\n추가할 문제를 입력하세요 : ").strip()
        if not question:
            print("문제는 빈 칸일 수 없습니다")
            return

        choices = []
        for i in range(4):
            choice=input(f"{i+1}번 선지를 입력하세요 : ").strip()
            choices.append(choice)
        answer = input("\n정답을 입력하세요 : ").strip()
        hint = input("힌트를 입력하세요 (없으면 엔터) : ").strip()
        if not hint:
                hint = "힌트가 없습니다."
        if answer not in choices:
            print("\n정답은 반드시 선지 중 하나여야 합니다!")
            print("퀴즈 추가가 중단되었습니다.")
            return
        
        
        self.add_quiz(question, choices, answer, hint)
        print(f"\n퀴즈가 추가되었습니다! 문제: {question}, 정답: {answer}")

   

class QuizGameGUI:

    def __init__(self, root, game_engine: QuizGame):
        self.root = root
        self.game = game_engine
        self.current_user = None
        self.current_quiz_idx = 0
        self.score_gain = 0

        # 창 기본 설정
        
        self.root.geometry("650x600")
        self.root.minsize(500, 400)
        self.root.title("Python Quiz Game")

        # 메인 프레임이 창 전체를 채우도록 설정
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # 첫 화면: 로그인/사용자 선택
        self.show_login_screen()
    def show_quiz(self):
        self.clear_frame()

        quiz = self.game.quizzes[self.current_quiz_idx]

        # 1. 문제 번호 및 질문 (wraplength를 지정하여 자동 줄바꿈)
        q_label = tk.Label(
            self.main_frame,
            text=f"Q{self.current_quiz_idx + 1}. {quiz.question}",
            font=("맑은 고딕", 13, "bold"),
            wraplength=550,  # 550픽셀이 넘어가면 자동으로 다음 줄로!
            justify="left",  # 왼쪽 정렬
        )
        q_label.pack(anchor="w", pady=(0, 20))

        # 2. 보기 선지 버튼 생성
       # 선지 선택 상태 저장용 변수 (show_quiz 시작 부분에 선언)
        self.selected_choice = tk.StringVar()

        for choice in quiz.choices:
            # indicatoron=0 으로 설정하면 기존 버튼 형태로 보입니다.
            rb = tk.Radiobutton(
                self.main_frame,
                text=choice,
                value=choice,
                variable=self.selected_choice,
                indicatoron=0,  # 👈 버튼 모양으로 변경
                font=("맑은 고딕", 11),
                anchor="w",
                justify="left",
                wraplength=450,  # 줄바꿈 기준
                command=lambda c=choice: self.check_answer(c),
            )
            rb.pack(fill="x", pady=5, ipady=8)

    def clear_frame(self):
        """화면 전환을 위해 기존 위젯들 삭제"""
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    # --- 1. 로그인 / 사용자 등록 화면 ---
    def show_login_screen(self):
        self.clear_frame()

        tk.Label(
            self.main_frame, text="🧩 퀴즈 게임에 오신 것을 환영합니다!", font=("맑은 고딕", 16, "bold")
        ).pack(pady=10)

        tk.Label(
            self.main_frame, text="사용자 이름을 입력하세요:", font=("맑은 고딕", 11)
        ).pack(pady=5)

        self.user_entry = tk.Entry(
            self.main_frame, font=("맑은 고딕", 12), width=20
        )
        self.user_entry.pack(pady=5)

        btn_frame = tk.Frame(self.main_frame)
        btn_frame.pack(pady=15)

        tk.Button(
            btn_frame,
            text="시작하기",
            font=("맑은 고딕", 10, "bold"),
            bg="#4CAF50",
            fg="white",
            width=10,
            command=self.login_user,
        ).pack(side="left", padx=5)
        tk.Button(
            btn_frame,
            text="신규 등록",
            font=("맑은 고딕", 10),
            width=10,
            command=self.register_user,
        ).pack(side="left", padx=5)

    def login_user(self):
        name = self.user_entry.get().strip()
        user = self.game.find_user(name)
        if user:
            self.current_user = user
            self.show_main_menu()
        else:
            messagebox.showwarning(
                "경고", f"[{name}] 님은 등록되지 않은 사용자입니다. 신규 등록을 해주세요."
            )

    def register_user(self):
        name = self.user_entry.get().strip()
        if not name:
            messagebox.showwarning("경고", "이름을 입력해주세요.")
            return

        if self.game.register_user(name):
            messagebox.showinfo("성공", f"[{name}] 님이 성공적으로 등록되었습니다!")
        else:
            messagebox.showinfo("알림", f"[{name}] 님은 이미 등록되어 있습니다.")

    # --- 2. 메인 메뉴 화면 ---
    def show_main_menu(self):
        self.clear_frame()

        tk.Label(
            self.main_frame,
            text=f"환영합니다, {self.current_user.username}님!",
            font=("맑은 고딕", 14, "bold"),
        ).pack(pady=10)

        info_text = f"현재 포인트: {self.current_user.point}점 | 최고 점수: {self.current_user.best_score}점\n(전체 역대 최고 점수: {self.game.highest_score_overall}점)"
        tk.Label(
            self.main_frame, text=info_text, font=("맑은 고딕", 10), fg="gray"
        ).pack(pady=5)

        tk.Button(
            self.main_frame,
            text="1. 퀴즈 풀기",
            font=("맑은 고딕", 11),
            width=25,
            height=2,
            bg="#2196F3",
            fg="white",
            command=self.start_quiz,
        ).pack(pady=10)
        tk.Button(
            self.main_frame,
            text="2. 사용자 목록 보기",
            font=("맑은 고딕", 11),
            width=25,
            command=self.show_user_list,
        ).pack(pady=5)
        tk.Button(
            self.main_frame,
            text="3. 로그아웃 / 사용자 변경",
            font=("맑은 고딕", 10),
            width=25,
            command=self.show_login_screen,
        ).pack(pady=10)

    # --- 3. 퀴즈 진행 화면 ---
    def start_quiz(self):
        if not self.game.quizzes:
            messagebox.showerror("오류", "퀴즈 데이터가 없습니다.")
            return

        self.current_quiz_idx = 0
        self.score_gain = 0
        self.display_quiz()

    def display_quiz(self):
        self.clear_frame()

        quiz = self.game.quizzes[self.current_quiz_idx]

        # 문제 번호 및 문제 내용
        tk.Label(
            self.main_frame,
            text=f"Q{self.current_quiz_idx + 1}. {quiz.question}",
            font=("맑은 고딕", 12, "bold"),
            wraplength=480,
            justify="left",
        ).pack(pady=15)

        # 4지선다 버튼 생성
        for i, choice in enumerate(quiz.choices, 1):
            btn = tk.Button(
                self.main_frame,
                text=f"{i}. {choice}",
                font=("맑은 고딕", 10),
                anchor="w",
                padx=10,
                width=50,
                command=lambda c=choice: self.check_answer(c),
            )
            btn.pack(pady=4)

    def check_answer(self, user_choice):
        quiz = self.game.quizzes[self.current_quiz_idx]

        if quiz.check_answer(user_choice):
            messagebox.showinfo("정답", "⭕ 정답입니다! (+1점)")
            self.current_user.point += 1
            self.score_gain += 1
        else:
            messagebox.showerror(
                "오답",
                f"❌ 틀렸습니다.\n정답: {quiz.get_answer_number()}번 ({quiz.answer})",
            )

        self.current_quiz_idx += 1

        # 다음 문제가 있으면 계속, 없으면 결과 화면
        if self.current_quiz_idx < len(self.game.quizzes):
            self.display_quiz()
        else:
            self.finish_quiz()

    def finish_quiz(self):
        # 1. 개인 최고 점수 갱신
        if self.score_gain > self.current_user.best_score:
            self.current_user.best_score = self.score_gain

        # 2. 전체 최고 점수 업데이트 (QuizGame 클래스에 해당 메서드가 있을 때만 안전하게 실행)
        if hasattr(self.game, "update_highest_score"):
            self.game.update_highest_score()
        else:
            # 메서드가 없으면 백엔드의 최고 점수 변수를 직접 계산해 갱신
            if hasattr(self.game, "highest_score_overall") and self.game.users:
                self.game.highest_score_overall = max(
                    u.best_score for u in self.game.users
                )

        # 3. 데이터 저장 (기존 백엔드 메서드 사용)
        if hasattr(self.game, "save_data"):
            self.game.save_data()

        # 4. 결과 메시지 표시
        messagebox.showinfo(
            "퀴즈 종료",
            f"🎉 모든 문제를 풀었습니다!\n\n이번 라운드 획득 점수: {self.score_gain}점\n총 누적 포인트: {self.current_user.point}점",
        )

        # 5. 안전하게 메인 메뉴로 이동
        self.show_main_menu()

    def show_user_list(self):
        users_info = "\n".join(
            [
                f"{u.username} (포인트: {u.point}점 | 최고점수: {u.best_score}점)"
                for u in self.game.users
            ]
        )
        messagebox.showinfo("📋 사용자 목록", users_info if users_info else "등록된 사용자가 없습니다.")


# --- 실행부 ---
if __name__ == "__main__":
    # 백엔드 엔진 객체 생성 (기존 QuizGame 클래스 사용)
    quiz_engine = QuizGame()

    # Tkinter GUI 창 생성
    root = tk.Tk()
    app = QuizGameGUI(root, quiz_engine)
    root.mainloop()