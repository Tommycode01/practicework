num1 = int(input("Enter first number: "))
operator = input("operator: ")
num2 = int(input("Enter second number: "))

def safe_calculator(num1, operator, num2):
    if operator == "+":
        return (num1 + num2)
    elif operator == "-":
        return (num1 - num2)
    elif operator == "*":
        return (num1 * num2)
    elif operator == "**":
        return (num1 ** num2)
    elif operator == "%":
        if num2 == 0:
            return "Cannot divide by zero"
        else:
            return (num1 % num2)
    elif operator == "/":
        if num2 == 0:
            return "Cannot divide by zero"
        else:
            return round(num1 / num2, 2)
    else:
        return "Invalid operator"

result = safe_calculator(num1, operator, num2)
print(result)




# print(safe_calculator(10, "+", 5))
# print(safe_calculator(10, ";", 5))
# print(safe_calculator(10, "*", 5))
# print(safe_calculator(10, "/", 0))
# print(safe_calculator(10, "%", 0))
# print(safe_calculator(2, "**", 3))