# repository.py
import os
import json
import time
from typing import Generator, List, Dict, Any, Callable
from .model import Transaction

class JsonlRepository:
    """JSONL 파일 기반 영구 저장을 처리하는 공통 헬퍼 클래스"""
    def __init__(self, file_path: str):
        self.file_path = file_path
        dir_name = os.path.dirname(self.file_path)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)
            
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w", encoding="utf-8") as f:
                pass

    def read_lines(self) -> Generator[Dict[str, Any], None, None]:
        """한 줄씩 JSON 딕셔너리로 읽어오는 공통 제너레이터"""
        if not os.path.exists(self.file_path):
            return
        with open(self.file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    yield json.loads(line)

    def append_line(self, data: Dict[str, Any]) -> None:
        """한 줄 추가 (Append)"""
        with open(self.file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(data, ensure_ascii=False) + "\n")

    def save_all_atomic(self, items: List[Dict[str, Any]]) -> None:
        """원자적 저장 (Atomic Save): 임시 파일 작성 후 순간 교체"""
        temp_file_path = f"{self.file_path}.tmp"
        with open(temp_file_path, "w", encoding="utf-8") as f:
            for item in items:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")

        # Windows OneDrive 권한 잠금 방지 재시도 로직
        for _ in range(5):
            try:
                os.replace(temp_file_path, self.file_path)
                break
            except PermissionError:
                time.sleep(0.1)


class TransactionRepository:
    def __init__(self, file_path: str = "./data/transactions.jsonl"):
        self.storage = JsonlRepository(file_path)

    def add(self, transaction: Transaction) -> None:
        self.storage.append_line(transaction.to_dict())

    def get_all_stream(self) -> Generator[Transaction, None, None]:
        for data in self.storage.read_lines():
            yield Transaction.from_dict(data)

    def delete_transaction(self, tx_id: str) -> bool:
        all_txs = list(self.get_all_stream())
        if not any(tx.id == tx_id for tx in all_txs):
            return False
        remaining_txs = [tx.to_dict() for tx in all_txs if tx.id != tx_id]
        self.storage.save_all_atomic(remaining_txs)
        return True

    def save_all_atomic(self, transactions: List[Transaction]) -> None:
        raw_items = [tx.to_dict() for tx in transactions]
        self.storage.save_all_atomic(raw_items)


class CategoryRepository:
    def __init__(self, data_dir: str = "./data"):
        file_path = os.path.join(data_dir, "categories.jsonl")
        self.storage = JsonlRepository(file_path)
        
        # 파일이 비어있으면 기본 카테고리 자동 생성
        if not self.get_all():
            self.save_all(["food", "transport", "rent", "salary", "etc"])

    def get_all(self) -> List[str]:
        return [data["name"] for data in self.storage.read_lines()]

    def save_all(self, categories: List[str]) -> None:
        raw_items = [{"name": cat} for cat in categories]
        self.storage.save_all_atomic(raw_items)


class BudgetRepository:
    def __init__(self, data_dir: str = "./data"):
        file_path = os.path.join(data_dir, "budgets.jsonl")
        self.storage = JsonlRepository(file_path)

    def get_all(self) -> Dict[str, int]:
        budgets = {}
        for data in self.storage.read_lines():
            budgets[data["month"]] = data["amount"]
        return budgets

    def save_budget(self, month: str, amount: int) -> None:
        budgets = self.get_all()
        budgets[month] = amount
        raw_items = [{"month": m, "amount": amt} for m, amt in budgets.items()]
        self.storage.save_all_atomic(raw_items)