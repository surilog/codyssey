import argparse #터미널 명령어와 옵션(--Limit 5)을 복잡하게 문자열로 자르는 것이 아니라 자동으로 깔끔하게 분석해주는 도구!
import sys #파이썬 실행환경을 제어/ 사용자가 터미널에 입력한 전체 명령행 인자를 읽어오거나(sys.argv), 프로그램 종료 코드(sys.exit())를 처리할 때 사용
from typing import List #타입 힌트용 클래스들(List,Dict,Optional)등을 가져옴
from .service import BudgetService
from .decorators import handle_errors, log_execution_time

class CLIHandler:
    def __init__(self, service: BudgetService): #의존성 주입
        self.service=service

    @handle_errors
    def handle_category(self, args:argparse.Namespace)->None:
        """category명령어 정리(add,list,remove)"""
        action = getattr(args, "cat_action",None) # arags객체에 "cat_action" 속성이 있으면 가져오고 없으면 에러없이 None
        if action == "add":
            print("===카테고리 추가===")
            name=input("카테고리명: ").strip()
            if name:
                self.service.add_category(name)
                print(f"[저장 완료] category={name}")
        elif action =="list":
            print("===카테고리 목록===")
            categories = self.service.get_categories()
            for cat in categories:
                print(f"*{cat}")
        elif action =="remove":
            name=getattr(args,"name",None)
            if not name:
                name=input("삭제할 카테고리명: ").strip()
            self.service.remove_category(name)
            print("[삭제 완료] category={name}")
        else:
            print("올바른 category하위 명령어를 입력하세요! (add,list,remove)")

    @handle_errors
    def handle_budget(self,args:argparse.Namespace)->None:
        """budget명령어 정리(set)"""
        action = getattr(args, "budget_action",None)
        if action=="set":
            self.service.set_budget(month=args.month,amount=args.amount)
            print(f"[저장 완료] {args.month} 예산 {args.amount:,}원")
        else:
            print("올바른 budget하위 명령어를 입력하세요(set)")


    @handle_errors
    def handle_search(self, args:argparse.Namespace)->None:
        """search명령어 정리"""
        results = self.service.search_transactions(
            from_date=args.from_date,
            to_date=args.to_date,
            category=args.category,
            tx_type=args.type,
            query=args.query,
            tag=args.tag
        )
        print("\n=== 거래 내역 검색 결과===")
        count =0
        for tx in results:
            memo_str = f" | 메모: {tx.memo}" if tx.memo else ""
            print(f"[{tx.id}] {tx.date} | {tx.type:<7} | {tx.category:<10} | {tx.amount:>8,}원{memo_str}")
            count+=1
        if count ==0:
            print("검색 조건에 맞는 거래 내역이 없습니다.")


    @handle_errors
    def handle_export(self, args: argparse.Namespace) ->None:
        """export 명령어 정리"""
        count = self.service.export_to_csv(
            out_path=args.out,
            month=args.month,
            from_date=args.from_date,
            to_date=args.to_date
        )
        print(f"[완료] {args.out} ({count} records)")

    @handle_errors
    def handle_import(self,args:argparse.Namespace)->None:
        """import 명령어 정리"""
        result = self.service.import_from_csv(file_path=args.from_file)
        print(f"[완료] imported={result['imported']},skipped={result['skipped']}")

    @handle_errors # 에러 처리 데코레이터 활용
    def handle_add(self, args: argparse.Namespace)->None:
        #args: argparse.Namespace => argparse라이브러리가 터미널 명령어를 파싱하고 난 후 그 결과물을 Namespace라는 특별한 객체로 묶어 반환
        #즉, args 매개변수 안에 args.month, args.limit처럼 파싱된 옵션 값들이 들어있는 객체가 전달됨
        """add명령어 : 대화형 input()방식으로 수입/지출 내역 입력"""
        print("=== 새로운 용돈기입장 내역 추가 ===")
        date=input("날짜 (YYYY-MM-DD): ").strip()
        tx_type=input("타입 (income/expense): ").strip()
        category = input("카테고리 (예:food, transport): ").strip()

        amount_str = input("금액 (양수 정수): ").strip()
        amount = int(amount_str) if amount_str.isdigit() else 0

        memo = input("메모 (선택, 엔터 시 건너뜀): ").strip()
        tags_str = input("태그( 쉼표 구분, 선택): ").strip()

        tags = [t.strip() for t in tags_str.split(",") if t.strip()] if tags_str else []

        """서비스 계층 호출하여 거래 내역 저장"""
        tx= self.service.add_transaction(
            tx_type =tx_type,
            date=date,
            amount=amount,
            category=category,
            memo=memo,
            tags=tags
        )
        print(f"[저장완료] id={tx.id}")
    """input => service의 add_transaction()에서 검증 후 model의 Translaction()에서 객체 생성 =>registory의 add()호출  맨 끝에 저장하기 위해
        =>model의 to_jsonal()실행해서 한 줄의 json문자열로 변환 후 저장"""

    @handle_errors
    def handle_delete(self, args: argparse.Namespace) -> None:
        self.service.delete_transaction(tx_id=args.id)
        print(f"[삭제 완료] id={args.id} 내역이 성공적으로 삭제되었습니다.")

    @handle_errors
    def handle_update(self, args: argparse.Namespace) -> None:
        updated_tx = self.service.update_transaction(tx_id=args.id,
        date=args.date,
        tx_type=args.type,
        category=args.category,
        amount=args.amount,
        memo=args.memo)
        print(f"[수정완료] id={updated_tx.id} 내역이 변경되었습니다.")

    @handle_errors
    @log_execution_time
    def handle_list(self, args: argparse.Namespace) -> None:
        #args: argparse.Namespace`: `list --limit 5` 명령어를 입력했을 때, 파싱된 `--limit` 값(`args.limit = 5`)을 들고 있는 객체 타입
        """List 명령어: 거래 목록 조회(스트리밍 및 limit적용)"""
        limit=args.limit
        count = 0
        print("\n=== 거래 내역 목록 ===")

        for tx in self.service.tx_repo.get_all_stream():
            if limit and count >= limit: 
                break
            memo_str = f" | 메모:{tx.memo}" if tx.memo else ""
            print(f"[{tx.id}][{tx.date}] | {tx.type:<7} | {tx.category:<10} | {tx.amount:>8,}원{memo_str}")
            count+=1

        if count ==0:
            print("등록된 거래 내역이 없습니다.")

    @handle_errors
    def handle_summary(self, args:argparse.Namespace) -> None:
#args:argparse.Namespace =>summary --month 2024-01 --top 3`에서 넘겨받은 args.month("2024-01")와 args.top(3) 값이 들어있는 객체 타입
        """summary명령어: 월별 요약 리포트 및 예산 경고 출력"""
        summary =  self.service.get_summary(month =args.month, top_n=args.top)
        
        print(f"\n=== {summary['month']}월별 요약 리포트")
        print(f"\n 총 수입{summary['total_income']:,}원")
        print(f"\n 총 지출{summary['total_expense']:,}원")
        print(f"\n 잔 액{summary['balance']:,}원")

        if summary.get("budget_amount"):
            print(f"예  산: {summary['budget_amount']:,}원 (사용률 {summary['usage_pct']}% )")
            if summary.get("is_exceeded"):
                print("[경고] 월 목표 예산을 초과했습니다!")

        if summary['top_categories']:
            print(f"\n지출 TOP {len(summary['top_categories'])}")
            for idx, (cat, amt) in enumerate(summary['top_categories'],1): #cat이 카테고리 항목, amt가 금액?
                print(f"{idx}. {cat:<10} {amt:,}원")

    def run(self, sys_args: List[str]=None)->None:
        """argparse를 사용한 터미널 명령어 및 옵션 인자 파싱"""
        parser = argparse.ArgumentParser(description="나만의 용돈기입장 콘솔 명령 프로그램") #터미널 명령 규칙 선언 시작(명령객체생성)
        subparsers = parser.add_subparsers(dest="command",help="실행할 명령어") #add_subparsers()로 add,list,summary같은 서브 명령어 등록

        #add_subparsers: 가지치기(메뉴판 생성) =>새로운 하위 명령어 그룹을 만들어낼 준비
        #add_parser:가지 추가(메뉴 항목)=>그룹 안에 들어갈 실제 명령어 단어(`add`, `list`, `category` 등)를 등록
        #add_argument:열매달기(옵션/재료) =>등록된 명령어 뒤에 붙는 옵션 플래그(`--limit`, `--amount`, `--month`)를 설정
        #category명령어 등록
        parser_category = subparsers.add_parser("category", help="카테고리 관리")
        cat_subparsers=parser_category.add_subparsers(dest="cat_action",help="카테고리 세부기능") #중첩 명령어 사용 위한 서브파서 등록
        #`category`라는 큰 그룹 안에 `add`, `list`, `remove`라는 여러 하위 기능이 존재. 
# 즉`category` 전용 파서를 먼저 만들고, 그 내부에 하위 파서 그룹(`cat_subparsers`)을 한 번 더 생성해야 파이썬이 `add`/`list`/`remove`를 구분
        cat_subparsers.add_parser("add",help="카테고리 추가")
        cat_subparsers.add_parser("list",help="카테고리 목록 조회")
        cat_remove= cat_subparsers.add_parser("remove",help="카테고리 삭제")
        cat_remove.add_argument("name",nargs="?",default=None, help ="삭제할 카테고리명")

        #budget명령어 등록

        parser_budget = subparsers.add_parser("budget",help="예산 설정")
        budget_subparsers=parser_budget.add_subparsers(dest="budget_action",help="예산 세부 기능")
        budget_set = budget_subparsers.add_parser("set", help="예산 설정")
        budget_set.add_argument("--month",required=True,help="예산 월(YYYY-MM)")
        budget_set.add_argument("--amount", type=int, required=True,help="예산 금액")

        #search 명령어 등록

        parser_search =subparsers.add_parser("search",help="거래 내역 검색")
        parser_search.add_argument("--from",dest="from_date",help="시작 날짜(YYYY-MM-DD)")
        parser_search.add_argument("--to",dest="to_date",help="종료 날짜(YYYY-MM-DD)")
        parser_search.add_argument("--category",help="카테고리")
        parser_search.add_argument("--type",help="타입 (income/expense)")
        parser_search.add_argument("--q",dest="query",help="메모 키워드")
        parser_search.add_argument("--tag",help="태그")

        
        #export명령어 설정
        parser_export = subparsers.add_parser("export",help="CSV 데이터 내보내기")
        parser_export.add_argument("--out",required=True,help="내보낼 CSV 파일 경로(예: export.csv)")
        parser_export.add_argument("--month",help="월 조건(YYYY-MM)")
        parser_export.add_argument("--from",dest="from_date",help="시작 날짜(YYYY-MM-DD)")
        parser_export.add_argument("--to",dest="to_date",help="종료 날짜(YYYY-MM-DD)")

        #import 명령어 설정
        parser_import = subparsers.add_parser("import",help="CSV데이터 가져오기")
        parser_import.add_argument("--from",dest="from_file",required=True,help="가져올 CSV 파일 경로 (예: import.csv)")

        #add 명령어 설정
        subparsers.add_parser("add",help = "거래 내역 추가(대화형 입력)",description="대화형(input) 인터페이스로 날짜, 타입, 카테고리, 금액, 메모, 태그를 순차 입력받아 저장합니다.")

        #delete명령어 설정
        parser_delete = subparsers.add_parser("delete",help="거래 내역 삭제")
        parser_delete.add_argument("--id",required=True,help="삭제할 거래 ID (예:Tx-000001)")

        #update명령어 설정
        parser_update = subparsers.add_parser("update",help="거래 내역 수정")
        parser_update.add_argument("--id",required=True, help="수정할 거래 ID")
        parser_update.add_argument("--date",help="변경할 날짜(YYYY-MM-DD)")
        parser_update.add_argument("--type",choices=["income","expense"],help="변경할 타입(income/expense)")
        parser_update.add_argument("--category",help="변경할 카테고리")
        parser_update.add_argument("--amount",type=int, help="변경할 금액")
        parser_update.add_argument("--memo",help="변경할 메모")
        parser_update.add_argument("--tags",help="태그 (쉼표 구분)")

        #List 명령어 설정
        parser_list = subparsers.add_parser("list",help="거래 목록 조회")
        parser_list.add_argument("--limit", type=int, default=None, help="출력 건수 제한 (예: --limit5)")
        #add_argument()로 --limit이나 --month --top같은 옵션 정의!
        #list명령어 뒤에 --limit이라는 옵션을 붙일 수 있게 등록, type=int 를 통해 자동으로 정수로 변환
        #default=None: 사용자가 옵션을 안 적으면 자동으로 None
        #help: --help 를 쳤을 때 나올 설명 문구란!
        #summary 명령어 설정

        parser_summary=subparsers.add_parser("summary",help="월별 요약 출력")
        parser_summary.add_argument("--month", required=True, help="조회할 월 (YYYY-MM)")
        parser_summary.add_argument("--top", type=int, default=3,help="상위 지출 카테고리 개수")

        args=parser.parse_args(sys_args) 
        """
        sys_args : 사용자가 터미널에 실제 입력한 '글자(문자열) 목록'. (예: `["summary", "--month", "2024-01"]`)
        등록해둔 규칙(parser)을 가지고 사용자가 입력한 sys_args을 분석!
        그래야 `args.command`("list"), `args.limit`(5) 같은 결과 객체(`args`)가 비로소 만들어짐
        """
        #명령어에 따른 핸들러 매핑 실행

        if args.command=="add":
            self.handle_add(args)
        elif args.command=="delete":
            self.handle_delete(args)
        elif args.command=="update":
            self.handle_update(args)
        elif args.command=="list":
            self.handle_list(args)
        elif args.command=="summary":
            self.handle_summary(args)
        elif args.command=="export":
            self.handle_export(args)
        elif args.command=="import":
            self.handle_import(args)
        elif args.command=="category":
            self.handle_category(args)
        elif args.command=="budget":
            self.handle_budget(args)
        elif args.command=="search":
            self.handle_search(args)
        else:
            parser.print_help()

