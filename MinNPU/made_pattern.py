            
class Made_pattern:
    def cross(self, n: int) -> list[list[float]]:
        matrix = [[0.0] * n for _ in range(n)]
        mid = n//2

        for r in range(n):                                                  
            for c in range(n):
                if n % 2 ==1 :
                    if r == mid or c == mid:
                        matrix[r][c] = 1.0
                else:
                    if r in (mid - 1 ,mid) or c in (mid -1, mid):
                        matrix[r][c] = 1.0
        return matrix

    def x(self,n : int) -> list[list[float]]:
        matrix =[[0.0]* n for _ in range(n)]
        for r in range(n):
            for c in range(n):
                if r == c or r+c ==n-1:
                    matrix[r][c] =1.0
        return matrix
# 기존 모드 1에서 입력 받았고 출력도 그대로 하는 로직에서  1d로 바꾸는 함수 호출 후 1dmac함수를 실행하여 결과값을 받아와서 기존 로직에서 실행만 하면?


