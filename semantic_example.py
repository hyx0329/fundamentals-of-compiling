from analyzer.semantic.example import ArithmeticAnalysis


if __name__ == "__main__":
    ath = ArithmeticAnalysis()
    print("Support: *,+,brackets,negative numbers")
    while True:
        string = input("Your expression(empty to quit):")
        if len(string) == 0:
            print("Exit!")
            break
        flag, result = ath.parse(string)
        if not flag:
            print("Wrong input!")
            continue
        print("3-address code:")
        for i in result:
            print(i)
        ans, _ = ath.run_code(result)
        print('Answer:', ans)
    