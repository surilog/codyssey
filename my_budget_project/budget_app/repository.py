import os , json , time
from typing import Generator, List, Dict
from .model import Transaction

class TransactionRepository:
    def __init__(self, file_path:str = "./data/transactions.jsonl"):
        self.file_path=file_path
        #데이터 저장 폴더가 없으면 자동으로 생성
        dir_name=os.path.dirname(self.file_path)
        """
        os.jpath.dirnames역할: 파일 전체 경로에서 '파일명'을 제외한 '폴더(디렉터리) 경로'만 쏙 뽑아주는 기능
        ex)`self.file_path`가 `"./data/transactions.jsonl`=> dir_name=./data
        """
        if dir_name:
            """ 
            폴더가 존재하는지 검사 X / 파일 경로에 폴더명이 있는지 유무!
            """
            os.makedirs(dir_name, exist_ok=True)
            #dir_name(즉 폴더명./data)이 있으면 해당 경로의 폴더를 실제로 생성
            #exist_ok=True: ./data폴더가 이미 존재해도 에러 내지 말고 넘어가!

        #저장 파일이 없으면 빈 파일 자동으로 생성
        if not os.path.exists(self.file_path):
            with open(self.file_path,"w",encoding="utf-8")as f:
                pass

    def add(self,transaction:Transaction)->None:
        """새로운 거래 내역 1건을 파일 끝에 덧붙이기(Append)"""
        with open(self.file_path,"a",encoding="utf-8")as f:
            f.write(transaction.to_jsonl()+"\n")#파이썬 메모리 속 존재하는 transaction객체 자체는 텍스트파일(.jsonl)에 그대로 넣으 수X
            #객체의 내부 정보를 한 줄 텍스트 문자열로 바꾸는 과정 필요! 
    def delete_transaction(self, tx_id:str) ->bool:
        """특정 ID의 거래 리스트만 제외하고 다시저장"""
        all_txs = list(self.get_all_stream()) #제너레이터 스트림을 리스트로 변환
        #삭제 대상 Id가 없으면 false반환
        if not any(tx.id == tx.id for tx in all_txs):
            return False
        #삭제할 ID가 '아닌(!=)' 내역들만 남기기
        remaining_txs = [tx for tx in all_txs if tx.id != tx_id]
        #남은 내역들만 파일에 다시 저장
        self.save_all_atomic(remaining_txs)
        return True

    def get_all_stream(self) -> Generator[Transaction,None,None]:
        """Generator[뽑아낼_데이터_타입, 보낼_데이터_타입, 최종_반환_타입]
        1.Transaction:yield를 통해 밖으로 하나씩 꺼내주는 데이터가 Transaction객체
        2. 제너레이터 내부->외부 데이터 주입 없음
        3.최종 리턴값 X
        """
        """제너레이터 스트리밍: 전체 파일을 한 번에 메모리에 올리지 않고 한 줄씩 읽어오기/ 시간복잡도 O(1)이겠지 안쓰면 O(N)일 꺼고"""
        if not os.path.exists(self.file_path):
            return
        with open(self.file_path,"r",encoding="utf-8")as f:
            for line in f:
                line = line.strip()
                if line:
                    """읽어온 한 줄(Jsonl)을 Transaction객체로 생성하여 하나씩 전달"""
                    yield Transaction.from_jsonl(line)

    def save_all_atomic(self,transactions:List[Transaction])->None: #객체가 하나만 있지는 않으니 List[]로 감싸줌
        #tx1={} ,tx2={} ,tx3={} 이렇게 있을 때 남은 여러 객체들을 한 번에 파일로 덮어써야 함!
        """원자적 저장(atomic save): 임시 파일 작성 후 기존 파일과 교체"""
        temp_file_path=f"{self.file_path}.tmp"

        """1. 임시 파일에 데이터 쓰기"""
        with open(temp_file_path,"w",encoding="utf-8")as f:
            for tx in transactions:
                f.write(tx.to_jsonl()+"\n")

                
        """쓰기가 안전하게 끝나면 기존 파일과 순간 교체"""
        os.replace(temp_file_path,self.file_path)

        #운영체제(OS) 수준에서 임시 파일의 이름을 원본 파일 이름으로 '순간적(Atomic)'으로 교체
        #파일 내용을 지우고 새로 쓰는 과정이 아니라, 이미 다 작성된 파일의 이름표만 바꾸는 작업이므로 순식간에 완료!

"""카테고리 저장소: ./data/categories.jsonl 파일에서 카테고리 목록 읽어오고 추가 삭제 저장 
- 초기 실행시 카테고리 없을시 기본 카테고리 제공
"""
class CategoryRepository:
    def __init__(self, data_dir:str = "./data"):
        self.file_path = os.path.join(data_dir, "categories.jsonl")
        os.makedirs(data_dir,exist_ok=True)
        #파일이 없으면 기본 카테고리 자동 생성
        if not os.path.exists(self.file_path):
            self.save_all(["food","transport","rent","salary","etc"])
    """카테고리 읽기"""
    def get_all(self)->List[str]:
        if not os.path.exists(self.file_path):
            return []
        categories =[]
        with open(self.file_path, "r",encoding="utf-8")as f:
            for line in f:
                if line.strip():
                    data=json.loads(line)
                    categories.append(data["name"])
        return categories
    """카테고리 저장"""
    def save_all(self, categoreis: List[str])-> None:
        tmp_path = self.file_path + ".tmp"
        with open(tmp_path, "w", encoding="utf-8")as f:
            for cat in categoreis:
                f.write(json.dumps({"name":cat}, ensure_ascii=False) + "\n")

 #나 다른 프로그램이 특정 파일(`.tmp` 임시 파일 또는 원본 파일)을 열어두고 있는 동안 해당 파일을 수정하거나 
 # 이름 변경(`os.replace`)하는 것을 엄격하게 금지하기 때문에 발생하는 오류 처리
 #특히 **OneDrive 폴더(** **OneDrive\\Desktop\\...** **)** 안에서 작업 중이실 때 자주 발생하는 문제
        for _ in range(5):
            try:
                os.replace(tmp_path, self.file_path)
                break
            except PermissionError:
                time.sleep(0.1) #0.1초 대기 후 재시도

"""예산 저장소:.data/budgets.jsonl 파일에서 월별 예산 데이터를 읽고 저장 갱신"""
class BudgetRepository:
    def __init__(self, data_dir:str = "./data"):
        self.file_path = os.path.join(data_dir,"budgets.jsonl")
        os.makedirs(data_dir, exist_ok=True)

    """월별 예산 데이터 읽기"""
    def get_all(self) -> Dict[str, int]:
        if not os.path.exists(self.file_path):
            return {}
        budgets ={}

        with open(self.file_path, "r", encoding="utf-8")as f:
            for line in f:
                if line.strip():
                    data= json.loads(line)
                    budgets[data["month"]] =data["amount"] #{"2024-01": 500000}
        return budgets
    
    """특정 월의 예산을 저장하고 갱신"""
    def save_budget(self, month:str, amount:int) -> None:
        budgets = self.get_all()
        budgets[month] = amount
        tmp_path= self.file_path + ".tmp"
        with open(tmp_path, "w",encoding="utf-8")as f:
            for m, amt in budgets.items():
                f.write(json.dumps({"month":m, "amount":amt}, ensure_ascii=False) +"\n")
        os.replace(tmp_path,self.file_path) # 임시파일 로직 ! 굳