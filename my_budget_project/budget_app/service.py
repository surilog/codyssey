import csv
import os
from typing import List, Dict, Any, Optional, Generator
from .model import Transaction
from .repository import TransactionRepository, CategoryRepository, BudgetRepository
from .exceptions import InvalidInputException, DataNotFoundException

class BudgetService:
    def __init__(self, tx_repo: TransactionRepository):
        self.tx_repo = tx_repo
        self.cat_repo = CategoryRepository()
        self.budget_repo = BudgetRepository()

    """현재 저장된 전체 카테고리 목록 반환"""
    def get_categories(self) ->List[str]:
        return self.cat_repo.get_all()
    
    """새로운 카테고리 검증 후 추가"""
    def add_category(self, name:str) ->None:
        categories= self.cat_repo.get_all()
        if name in categories:
            raise InvalidInputException(f"이미 존재하는 카테고리입니다: {name}")
        categories.append(name)
        self.cat_repo.save_all(categories)

    def remove_category(self, name:str) -> None:
        categories =self.cat_repo.get_all()
        if name not in categories:
            raise DataNotFoundException(f"존재하지 않는 카테고리입니다: {name}",
        hint="python -m budget_app category list 명령어로 등록된 카테고리를 확인해 주세요")

        #필수 요구사항! 삭제하려는 카테고리를 사용하는 내역 존재 시 삭제 차단!
        for tx in self.tx_repo.get_all_stream():# 사용하는 내역은 TransactionReapository에 존재하겠지?
            if tx.category == name:
                raise InvalidInputException(f"카테고리 '{name}'을 사용하는 거래 내역이 존재하여 삭제할 수 없습니다.",
                    hint="해당 카테고리의 거래 내역을 먼저 수정하거나 삭제해주세요!")

        categories.remove(name)
        self.cat_repo.save_all(categories)
    """목표 금액 설정(월별)"""
    def set_budget(self, month:str, amount: int) -> None:
        if amount <=0:
            raise InvalidInputException("예산 금액이 0보다 큰 양수여야 합니다")
        self.budget_repo.save_budget(month, amount)

    def export_to_csv(
            self,
            out_path:str,
            month: Optional[str]=None,
            from_date: Optional[str]=None,
            to_date:Optional[str]=None
    )->int:
        """조건에 맞는 거래 내역을 지정한 CSV파일로 내보내기"""
        #필수 조건 검증(month 또는 from/to 중 하나는 필수)
        if not month and not (from_date or to_date):
            raise InvalidInputException("export시 --month 또는 --from/--to 조건 중 하나는 필수입니다.",
                                        hint="예 --month 2024-01 또는 --from 2024-01-01 --to 2024-01-31")

        export_count = 0

        #저장 대상 디렉터리가 없으면 자동으로 생성
        out_dir = os.path.dirname(out_path)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
        with open(out_path,"w",encoding="utf-8", newline="") as f:
            writer=csv.writer(f) # 파일 객체 f에 리스트 데이터를 CSV형식(쉼표로 구분된 텍스트)로 자동으로 바꾸어주는 도구를 생성
            #csv표준헤더 작성 , 전달받은 리스트를 csv파일의 한 줄로 써줌
            writer.writerow(["date", "type", "category", "amount", "memo", "tags"])

            #제러레이터 스트리밍으로 데이터를 하나씩 가져와 조건 검사 후 쓰기
            for tx in self.tx_repo.get_all_stream():
                if month and not tx.date.startswith(month):
                    continue
                if from_date and tx.date < from_date:
                    continue
                if to_date and tx.date >to_date:
                    continue

                # tags 리스트를 쉼표 구분 문자열로 변환 (예: ['meal', 'food'] -> 'meal,food')
                tags_str=",".join(tx.tags) if tx.tags else ""
                writer.writerow([tx.date, tx.type, tx.category, tx.amount,tx.memo or "",tags_str])
                export_count+=1

        return export_count 

    
    def import_from_csv(self, file_path:str) -> Dict[str,int]:
        """csv 파일에서 거래내역을 일괄 읽어와 등록하기(일부 깨진 행 예외 처리 포함)"""
        if not os.path.exists(file_path):
            raise DataNotFoundException(
                f"가져올 csv파일 '{file_path}'을(를) 찾을 수 없습니다.",
                hint="올바른 파일 경로를 입력했는지 확인해주세요."
            )
        imported_count =0
        skipped_count =0

        # UTF-8 BOM 대응을 위해 utf-8-sig사용
        # 이유 : 한글 윈도우 환경의 엑셀에서 csv파일 만들면 맨 얖에 Bom 문자가 삽입되어 첫 번째 칼럼명인 (date)가 깨질 수 있음
        with open(file_path,"r",encoding="utf-8-sig")as f:
            reader =csv.DictReader(f)# csv파일의 데이터를 딕셔너리 형태로 편리하게 읽어와줌
            for row in reader:
                try:
                    date= row.get("date","").strip()
                    tx_type = row.get("type","").strip()
                    category=row.get("category","").strip()
                    amount_str = row.get("amount","").strip()
                    memo=row.get("memo","").strip()
                    tags_raw=row.get("tags","").strip()

                    #필수 입력값 기본검증
                    if not date or not tx_type or not category or not amount_str:
                        skipped_count +=1
                        continue

                    amount = int(amount_str)
                    tags = [t.strip() for t in tags_raw.split(",") if t.strip()] if tags_raw else []

                    #비즈니스 검증 및 거래 등록 호출
                    
                    self.add_transaction(
                        tx_type = tx_type,
                        date=date,
                        amount=amount,
                        category=category,
                        memo=memo,
                        tags=tags
                    )
                    imported_count +=1
                except Exception:
                    #유호하지 않은 데이터행이 섞인 경우 프로그램이 멈추지 않고 건너뜀(skipped누적)
                    skipped_count +=1
        return {"imported": imported_count, "skipped":skipped_count}


    def add_transaction(
            self,
            tx_type:str,
            date:str,
            amount:int,
            category:str,
            memo: str="",
            tags: Optional[List[str]] = None # 하나의 지출에 ['식비','외식','친구'처럼 여러 태그가 올 수 있음]
            #Optional[list[str]=None : tags변수가 List일수도 있고 None일수도 있음
    )->Transaction:
        """검증 후 거래 내역 저장"""
        if amount <=0:
            raise InvalidInputException("금액은 0보다 큰 양수여야 합니다.",hint="예 : 15000")

        if tx_type not in ["income","expense"]:
            raise InvalidInputException("타입은 'income' 또는 'expense'이어야 합니다.")

        existing_count = sum(1 for _ in self.tx_repo.get_all_stream())#기존 거래를 하나씩 꺼내면서 1을 더해 , 총 거래 개수 세는 코드
        tx_id=f"TX-{existing_count + 1:06d}"#정수 숫자를 6자로 맞추되 , 앞의 빈자리는 0으로 채움
        #ex)12번째 거래라면 existing_count +1은 13이되고 06:d에 의해 TX-000013이라는 id로 생성됨
        #id를 쓰는 이유는 모든 거래 내역을 구분할 수 있는 유일한 식별자이기 때문!

        new_tx = Transaction(
            id=tx_id,
            type=tx_type,
            date=date,
            amount=amount,
            category=category,
            memo=memo,
            tags=tags or []
        )
        self.tx_repo.add(new_tx)
        return new_tx


    def delete_transaction(self,tx_id:str)->None:
        """ID기반 거래 내역 삭제 및 원자적 영구 저장"""
        success = self.tx_repo.delete_transaction(tx_id)
        if not success:
            raise DataNotFoundException(
                f"ID '{tx_id}에 해당하는 거래 내역이 존재하지 않습니다.",
                hint="python -m budget_app list 명령어로 올바른 ID를 확인해 주세요."
            )

        

    def update_transaction(
            self,
            tx_id:str,
            date: Optional[str] = None,
            tx_type: Optional[str] = None,
            category: Optional[str] = None,
            amount: Optional[int] = None,
            memo:Optional[str]=None
    ) ->Transaction:
        """ID기반 거래 내역 수정 및 영구 저장"""
        updated_transactions =[]
        target_tx =None

        for tx in self.tx_repo.get_all_stream():
            if tx.id==tx_id:
                #변경된 인자가 전달된 항목만 갱신(None이 아닌 경우)
                if date:
                    tx.date = date
                if tx_type:
                    if tx_type not in ["income", "expense"]:
                        raise InvalidInputException("타입은 'income' 또는 'expense'여야 합니다")
                    tx.type=tx_type

                if category:
                    tx.category=category
                if amount is not None:
                    if amount<=0:
                        raise InvalidInputException("금액은 0보다 큰 양수여야 합니다")
                    tx.amount = amount
                if memo is not None:
                    tx.memo=memo

                target_tx = tx

            updated_transactions.append(tx)
        if not target_tx:
            raise DataNotFoundException(
                f"ID '{tx_id}'에 해당하는 거래 내역이 존재하지 않습니다 .",
                hint="python -m budget_app list 명령어로 올바른 ID를 확인해 주세요."
            )

        self.tx_repo.save_all_atomic(updated_transactions)
        return target_tx

    """조건별 검색 로직 (제너레이터 스트리밍 유지)"""
    def search_transactions( #과제 요구사항의 기간, 카테고리,타입, 검색어,태그
            self,
            from_date: Optional[str] =None,
            to_date: Optional[str] =None,
            category: Optional[str]=None,
            tx_type: Optional[str]=None,
            query:Optional[str]=None, 
            tag:Optional[str]=None #Optional[str]: 검색 시 사용자가 날짜가 검색할 수도 있고, 카테고리만 검색할 수도 있음
    )->Generator[Transaction,None,None]:
        for tx in self.tx_repo.get_all_stream(): 
            """repository의 get_all_stream()에서 건네받은 데이터 스트림을 끊지 않고 , 조건 필터링(if)후 다시 yield로 전달
               즉, 데이터 검색 시에도 전체 목록을 배열에 다 담는 것 X / 조건에 맞는 데이터만 그때그때 뽑아 메모리 효율성 유지!

               [주의!] get_all_stream()은 파일의 전체 내역을 읽어오는 줄기
               search_transactions()이 Generator를 활용해서 전체 내역 중 검색 조건에 맞는 내용만 골라낸 줄기!
               """
            if from_date and tx.date < from_date:#시작 날짜가 설정됬지만 이 내역의 날짜보다 더 뒤라면 범위 밖이니 건너뜀
                continue
            if to_date and tx.date > to_date: #종료 날짜가 있지만 이 내역의 날짜가 그 후면 범위 밖 => 건너뜀
                continue
            if category and tx.category!= category:# 카테고리를 지정했지만 이 내역의 카테고리와 다르면 =>건너뜀 
                continue
            if tx_type and tx.type != tx_type:#수입/지출 타입이 지정되었지만 이 내역의 타입과 다르면 =>건너뜀
                continue
            if query and (query not in tx.memo and query not in tx.category):#검색어가 있지만 메모에도 없고 카테고리에도 없으면=> 건너뜀
                continue
            if tag and (tag not in tx.tags):
                continue
            yield tx

    def get_summary(
            self,
            month:str,
            budget_amount: Optional[int] = None,
            top_n : int =3
    )->Dict[str,Any]: #Any타입: 어떤 데이터 타입든지 올 수 있음
        """월별 지출/수입 요약, 카테고리별 TOP N 지출, 예산 사용률 계산"""
        total_income = 0
        total_expense=0
        category_expenses: Dict[str, int]={} #{"food":10000,"studyitem":20000}각 카테고리별 지출금액

        """지정된 월의 데이터 집계"""
        for tx in self.tx_repo.get_all_stream():
            if tx.date.startswith(month): #startswith(month): 문자열이 month로 시작하면 참 아니면 거짓
                #ex)tx.date가 2024-01-15일때 startswith("2024-01")실행하면 ,해당 거래가 2024년 1월 거래가 맞는지 판별
                if tx.type =="income":
                    total_income += tx.amount
                elif tx.type == "expense":
                    total_expense +=tx.amount
                    category_expenses[tx.category]=(category_expenses.get(tx.category,0)+tx.amount)
                    #각 카테고리별 누적 합계 계산
        balance = total_income - total_expense
        budgets = self.budget_repo.get_all()
        budget_amount =budgets.get(month,None)

        """지출 카테고리 TOP N 정렬"""
        sorted_categories = sorted(
            category_expenses.items(), key=lambda x: x[1],reverse=True
        )[:top_n]
# 1. `category_expenses.items()`: 딕셔너리를 `[('food', 45000), ('transport', 20000)]` 같은 튜플 리스트 형태로 변환
# 2. `key=lambda x: x`[1]: 튜플의 1번째 요소인 금액(`x`[1])을 기준으로 정렬하라는 기준을 정함
# 3. `reverse=True`: 금액이 큰 순서대로(내림차순) 정렬
# 4. `[:top_n]`: 정렬된 결과 중 상위 `top_n`개(예: TOP 3)만 자름

        """요약 결과 구성"""
        summary_result={
            "month":month,
            "total_income": total_income,
            "total_expense":total_expense,
            "balance":balance,
            "top_categories":sorted_categories,
            "budget_amount":budget_amount,
            "usage_pct":None,
            "is_expected":False
            
        }

        """예산 계산 및 경고 로직"""
        if budget_amount is not None and budget_amount >0: # 예산이 있고 0보다 크면
            usage_pct = (total_expense / budget_amount) *100
            summary_result["usage_pct"] = round(usage_pct, 1)#round: 소수점 첫째자리까지 반올림
            summary_result["is_expected"]= total_expense > budget_amount

        return summary_result