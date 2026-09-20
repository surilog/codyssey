# __main__.py
from .repository import TransactionRepository
from .service import BudgetService
from .cli import CLIHandler

def main():
    # 1. 저장소 생성
    repo = TransactionRepository()

    # 2. 서비스 연결
    service = BudgetService(tx_repo=repo)

    # 3. CLI 핸들러 생성 및 실행 (CLI run 내부에서 handle_errors 데코레이터 작동)
    cli = CLIHandler(service=service)
    cli.run()

if __name__ == "__main__":
    main()