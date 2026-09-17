# model.py: 용돈 가입장의 기본 뼈대 생성(수입 지출내역(Transaction,category,budget)라는 데이터를 다룸.)
# 이때 파일에 저장하거나 터미널 화면에 출력하기 전에, 하나의 거래 내역에은 id,날짜,금액,메모등이들어 간다는 규격과 형식을 파이썬 코드로 선언해주는 곳
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any
import json


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





