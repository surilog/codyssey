class BudgetAppException(Exception):
    def __init__(self,message: str , hint:str = ""):
        self.message=message
        self.hint=hint
        super().__init__(self.message)

class InvalidInputException(BudgetAppException):
    """사용자 입력 검증 실패 시 발생하는 예외 (예: 잘못된 날짜 포맷, 음수 금액)"""
    pass

class DataNotFoundException(BudgetAppException):
    """찾으려는 거래 내역이나 카테고리가 존재하지 않을 때 발생하는 예외""" 
    pass

class BudgetExceededException(BudgetAppException):
    """예산을 초과했을 때 발생하는 경고성 예외"""
    pass

