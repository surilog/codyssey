# cli.py
import argparse
import sys
from typing import List
from .service import BudgetService
from .decorators import handle_errors, log_execution_time

class CLIHandler:
    def __init__(self, service: BudgetService):
        self.service = service

    def handle_category(self, args: argparse.Namespace) -> None:
        action = getattr(args, "cat_action", None)
        if action == "add":
            print("===카테고리 추가===")
            name = input("카테고리명: ").strip()
            if name:
                self.service.add_category(name)
                print(f"[저장 완료] category={name}")
        elif action == "list":
            print("===카테고리 목록===")
            categories = self.service.get_categories()
            for cat in categories:
                print(f"* {cat}")
        elif action == "remove":
            name = getattr(args, "name", None)
            if not name:
                name = input("삭제할 카테고리명: ").strip()
            self.service.remove_category(name)
            print(f"[삭제 완료] category={name}")
        else:
            print("올바른 category 하위 명령어를 입력하세요! (add, list, remove)")

    def handle_budget(self, args: argparse.Namespace) -> None:
        action = getattr(args, "budget_action", None)
        if action == "set":
            self.service.set_budget(month=args.month, amount=args.amount)
            print(f"[저장 완료] {args.month} 예산 {args.amount:,}원")
        else:
            print("올바른 budget 하위 명령어를 입력하세요(set)")

    def handle_search(self, args: argparse.Namespace) -> None:
        results = self.service.search_transactions(
            from_date=args.from_date,
            to_date=args.to_date,
            category=args.category,
            tx_type=args.type,
            query=args.query,
            tag=args.tag
        )
        print("\n=== 거래 내역 검색 결과 ===")
        count = 0
        for tx in results:
            memo_str = f" | 메모: {tx.memo}" if tx.memo else ""
            print(f"[{tx.id}] {tx.date} | {tx.type:<7} | {tx.category:<10} | {tx.amount:>8,}원{memo_str}")
            count += 1
        if count == 0:
            print("검색 조건에 맞는 거래 내역이 없습니다.")

    def handle_export(self, args: argparse.Namespace) -> None:
        count = self.service.export_to_csv(
            out_path=args.out,
            month=args.month,
            from_date=args.from_date,
            to_date=args.to_date
        )
        print(f"[완료] {args.out} ({count} records)")

    def handle_import(self, args: argparse.Namespace) -> None:
        result = self.service.import_from_csv(file_path=args.from_file)
        print(f"[완료] imported={result['imported']}, skipped={result['skipped']}")

    def handle_add(self, args: argparse.Namespace) -> None:
        print("=== 새로운 용돈기입장 내역 추가 ===")
        date = input("날짜 (YYYY-MM-DD): ").strip()
        tx_type = input("타입 (income/expense): ").strip()
        category = input("카테고리 (예: food, transport): ").strip()

        amount_str = input("금액 (양수 정수): ").strip()
        amount = int(amount_str) if amount_str.isdigit() else 0

        memo = input("메모 (선택, 엔터 시 건너뜀): ").strip()
        tags_str = input("태그 (쉼표 구분, 선택): ").strip()

        tags = [t.strip() for t in tags_str.split(",") if t.strip()] if tags_str else []

        tx = self.service.add_transaction(
            tx_type=tx_type,
            date=date,
            amount=amount,
            category=category,
            memo=memo,
            tags=tags
        )
        print(f"[저장 완료] id={tx.id}")

    def handle_delete(self, args: argparse.Namespace) -> None:
        self.service.delete_transaction(tx_id=args.id)
        print(f"[삭제 완료] id={args.id} 내역이 성공적으로 삭제되었습니다.")

    def handle_update(self, args: argparse.Namespace) -> None:
        updated_tx = self.service.update_transaction(
            tx_id=args.id,
            date=args.date,
            tx_type=args.type,
            category=args.category,
            amount=args.amount,
            memo=args.memo
        )
        print(f"[수정 완료] id={updated_tx.id} 내역이 변경되었습니다.")

    @log_execution_time
    def handle_list(self, args: argparse.Namespace) -> None:
        limit = args.limit
        count = 0
        print("\n=== 거래 내역 목록 ===")

        for tx in self.service.tx_repo.get_all_stream():
            if limit and count >= limit:
                break
            memo_str = f" | 메모: {tx.memo}" if tx.memo else ""
            print(f"[{tx.id}][{tx.date}] | {tx.type:<7} | {tx.category:<10} | {tx.amount:>8,}원{memo_str}")
            count += 1

        if count == 0:
            print("등록된 거래 내역이 없습니다.")

    def handle_summary(self, args: argparse.Namespace) -> None:
        summary = self.service.get_summary(month=args.month, top_n=args.top)
        
        print(f"\n=== {summary['month']}월별 요약 리포트 ===")
        print(f"총 수입: {summary['total_income']:,}원")
        print(f"총 지출: {summary['total_expense']:,}원")
        print(f"잔   액: {summary['balance']:,}원")

        if summary.get("budget_amount"):
            print(f"예   산: {summary['budget_amount']:,}원 (사용률 {summary['usage_pct']}% )")
            if summary.get("is_expected"):
                print("[경고] 월 목표 예산을 초과했습니다!")

        if summary['top_categories']:
            print(f"\n지출 TOP {len(summary['top_categories'])}")
            for idx, (cat, amt) in enumerate(summary['top_categories'], 1):
                print(f"{idx}. {cat:<10} {amt:,}원")

    @handle_errors  # CLI 실행 및 파싱 단계 전체의 에러를 상위에서 포착해 깔끔하게 출력
    def run(self, sys_args: List[str] = None) -> None:
        parser = argparse.ArgumentParser(description="나만의 용돈기입장 콘솔 명령 프로그램")
        subparsers = parser.add_subparsers(dest="command", help="실행할 명령어")

        # category 명령어
        parser_category = subparsers.add_parser("category", help="카테고리 관리")
        cat_subparsers = parser_category.add_subparsers(dest="cat_action", help="카테고리 세부기능")
        cat_subparsers.add_parser("add", help="카테고리 추가")
        cat_subparsers.add_parser("list", help="카테고리 목록 조회")
        cat_remove = cat_subparsers.add_parser("remove", help="카테고리 삭제")
        cat_remove.add_argument("name", nargs="?", default=None, help="삭제할 카테고리명")

        # budget 명령어
        parser_budget = subparsers.add_parser("budget", help="예산 설정")
        budget_subparsers = parser_budget.add_subparsers(dest="budget_action", help="예산 세부 기능")
        budget_set = budget_subparsers.add_parser("set", help="예산 설정")
        budget_set.add_argument("--month", required=True, help="예산 월(YYYY-MM)")
        budget_set.add_argument("--amount", type=int, required=True, help="예산 금액")

        # search 명령어
        parser_search = subparsers.add_parser("search", help="거래 내역 검색")
        parser_search.add_argument("--from", dest="from_date", help="시작 날짜(YYYY-MM-DD)")
        parser_search.add_argument("--to", dest="to_date", help="종료 날짜(YYYY-MM-DD)")
        parser_search.add_argument("--category", help="카테고리")
        parser_search.add_argument("--type", help="타입 (income/expense)")
        parser_search.add_argument("--q", dest="query", help="메모 키워드")
        parser_search.add_argument("--tag", help="태그")

        # export 명령어
        parser_export = subparsers.add_parser("export", help="CSV 데이터 내보내기")
        parser_export.add_argument("--out", required=True, help="내보낼 CSV 파일 경로")
        parser_export.add_argument("--month", help="월 조건(YYYY-MM)")
        parser_export.add_argument("--from", dest="from_date", help="시작 날짜(YYYY-MM-DD)")
        parser_export.add_argument("--to", dest="to_date", help="종료 날짜(YYYY-MM-DD)")

        # import 명령어
        parser_import = subparsers.add_parser("import", help="CSV 데이터 가져오기")
        parser_import.add_argument("--from", dest="from_file", required=True, help="가져올 CSV 파일 경로")

        # add 명령어
        subparsers.add_parser("add", help="거래 내역 추가(대화형 입력)")

        # delete 명령어
        parser_delete = subparsers.add_parser("delete", help="거래 내역 삭제")
        parser_delete.add_argument("--id", required=True, help="삭제할 거래 ID")

        # update 명령어
        parser_update = subparsers.add_parser("update", help="거래 내역 수정")
        parser_update.add_argument("--id", required=True, help="수정할 거래 ID")
        parser_update.add_argument("--date", help="변경할 날짜(YYYY-MM-DD)")
        parser_update.add_argument("--type", choices=["income", "expense"], help="변경할 타입")
        parser_update.add_argument("--category", help="변경할 카테고리")
        parser_update.add_argument("--amount", type=int, help="변경할 금액")
        parser_update.add_argument("--memo", help="변경할 메모")

        # list 명령어
        parser_list = subparsers.add_parser("list", help="거래 목록 조회")
        parser_list.add_argument("--limit", type=int, default=None, help="출력 건수 제한")

        # summary 명령어
        parser_summary = subparsers.add_parser("summary", help="월별 요약 출력")
        parser_summary.add_argument("--month", required=True, help="조회할 월 (YYYY-MM)")
        parser_summary.add_argument("--top", type=int, default=3, help="상위 지출 카테고리 개수")

        args = parser.parse_args(sys_args)

        # 핸들러 매핑
        command_map = {
            "add": self.handle_add,
            "delete": self.handle_delete,
            "update": self.handle_update,
            "list": self.handle_list,
            "summary": self.handle_summary,
            "export": self.handle_export,
            "import": self.handle_import,
            "category": self.handle_category,
            "budget": self.handle_budget,
            "search": self.handle_search,
        }

        handler = command_map.get(args.command)
        if handler:
            handler(args)
        else:
            parser.print_help()