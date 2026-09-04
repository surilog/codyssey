def user_input(self, name: str, n_size: int) -> Matrix:
    mat = Matrix(n_size)
    print(f"\n[{name} 입력 ({n_size}x{n_size})]")
    print(f"0과 1만 사용하여 {n_size}줄의 데이터를 입력(또는 붙여넣기) 후, 엔터를 한 번 더 눌러주세요:")

    while True:
        lines = []
        while True:
            try:
                line = input().strip()
                if not line:
                    break
                lines.append(line)
            except EOFError:  # Ctrl+D / Ctrl+Z 입력 처리
                break

        # 1. 전체 줄 수(N) 검사
        if len(lines) != n_size:
            print(f"\n오류: 입력된 줄 수({len(lines)})가 N({n_size})과 맞지 않습니다.")
            print("다시 입력해주세요!\n")
            continue

        final_arr = []
        is_valid = True

        for i, line in enumerate(lines, 1):
            row = line.split()

            # 2. 각 행의 원소 개수(N) 검사
            if len(row) != n_size:
                print(f"\n오류: {i}번째 줄의 숫자 개수({len(row)}개)가 N({n_size})과 맞지 않습니다.")
                is_valid = False
                break

            # 3. 모든 값이 "0" 또는 "1"인지 검사
            if not all(x in ("0", "1") for x in row):
                print(f"\n오류: {i}번째 줄에 '0' 또는 '1'이 아닌 값이 포함되어 있습니다.")
                is_valid = False
                break

            # 4. 정수로 변환하여 저장 (필요 시 float로 변경 가능)
            rows = [int(x) for x in row]
            final_arr.append(rows)

        # 5. 모든 조건 통과 시 반환
        if is_valid:
            mat.data = final_arr
            print("성공적으로 입력을 완료했습니다!")
            return mat

        print("다시 입력해주세요!\n")