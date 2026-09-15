# model.py: 용돈 가입장의 기본 뼈대 생성(수입 지출내역(Transaction,category,budget)라는 데이터를 다룸.)
# 이때 파일에 저장하거나 터미널 화면에 출력하기 전에, 하나의 거래 내역에은 id,날짜,금액,메모등이들어 간다는 규격과 형식을 파이썬 코드로 선언해주는 곳
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any
import json


"""
class Transasction:
    def __init__(self, id:str,type:str, data:str, amount: int , category: str):
        self.id = id
        self.type = type
        self.data =data
        self.amount = amount
        self.category = category
     #print(tx) 했을 때 예쁘게 출력되게 하려면 이 메서드도 직접 구현해야 함
    def __repr__(self):
        return f"Transaction(id={self.id}, amount={self.amount})"

만약 `@dataclass`를 쓰지 않고 일반 클래스로 작성한다면, 
객체를 만들고 출력할 때마다 아래처럼 반복적인 보일러플레이트 코드를 직접 다 작성
"""
"""
반면 `@dataclass`를 사용하면, 파이썬이 `__init__`(초기화)이나 `__repr__`(문자열 출력) 같은 기본 메서드를 배후에서 자동으로 생성
"""


#클래스 3개로 나눈 이유 

"""
1.Transaction에 category와 budget들어가 있는데 굳이 나눔?

==>가계부 프로그램을 확장성 있게 설계하기 위해 ,세 데이터의 역할(책임)과 수명 주기가 다르기 때문에 분리

-Transaction: 언제, 얼마를, 어디에 썼는가?"라는 하나하나의 사건을 기록

-category: 가계부에서 사용 가능한 올바른 분류 항목들(미리 정해진 카테고리만)을 정의하고 검증 
=> 즉, 아직 거래 내역(`Transaction`)을 하나도 적지 않은 초기 상태라도, 기본 카테고리 목록(`식비`, `교통`, `주거` 등)은 미리 존재해야함

-Budget:특정 달(YYYY-MM)에 총 얼마까지 쓸 것인가?"라는 목표 기준점
=> 즉, 예산은 지출 데이터가 아니라, 한달에 한 번 설정하는 *월 단위 정책 데이터* => 지출 내역이 없어도 이미 저장되어 있어야함!
"""
@dataclass
class Transaction:
    id: str            # 유일한 식별자 (예: TX-000001)
    type: str          # 'income' 또는 'expense'
    date: str          # YYYY-MM-DD
    amount: int        # 양수 정수
    category: str      # 카테고리명
    memo: Optional[str] = ""                       # 선 택 사항 (기본값 빈 문자열)
    tags: List[str] = field(default_factory=list)  # 선택 사항 (기본값 빈 리스트)

    def to_dict(self) -> Dict[str, Any]:
        """객체를 Dictionary 형태로 변환 (asdict 활용)"""
        return asdict(self)

    @classmethod  # 새 객체를 만들어야 할 때 classmethod사용
    def from_dict(cls, data: Dict[str, Any]) -> "Transaction":
        """Dictionary 데이터를 받아 Transaction 객체로 생성"""
        return cls(**data)

    def to_jsonl(self) -> str:
        """JSONL 포맷 저장을 위해 한 줄의 JSON 문자열로 변환"""
        return json.dumps(self.to_dict(), ensure_ascii=False)

    @classmethod
    def from_jsonl(cls, json_str: str) -> "Transaction":
        """JSONL 한 줄 문자열을 파싱하여 Transaction 객체로 복원"""
        return cls.from_dict(json.loads(json_str))


@dataclass
class Category:
    name: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Category":
        return cls(**data)


@dataclass
class Budget:
    month: str         # YYYY-MM
    amount: int        # 예산 금액

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Budget":
        return cls(**data)





