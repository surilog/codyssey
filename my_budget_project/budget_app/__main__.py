import sys
from .repository import TransactionRepository
from .service import BudgetService
from .cli import CLIHandler

def main():
    # 저장소 객체 생성
    repo=TransactionRepository()

    #저장소를 서비스에 전달하며 생성(서비스가 파일 저장 할 수 있게 연결)
    service=BudgetService(tx_repo=repo)
    #서비스를 CLI 핸들러에 전달하며 생성 (CLI가 계산 로직을 쓸 수 있게 연결)
    cli=CLIHandler(service=service)
    cli.run()

if __name__== "__main__":
    main()
