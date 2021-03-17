# https://www.nerdwallet.com/blog/taxes/federal-income-tax-brackets/

def convert(brackets):
    new_brackets = []
    tax = 0
    x_pre, r_pre = 0, 0
    for i in range(len(brackets)):
        x, r = brackets[i]
        tax += (x - x_pre) * r_pre
        new_brackets.append((x, tax, r))
        x_pre, r_pre = x, r
    return new_brackets

def print_list(lst):
    print("[")
    for x in lst:
        print(x)
    print("]")

def calc(brackets, income):
    #assume income > 0
    i = 0
    while i<len(brackets) and brackets[i][0] < income:
        i += 1
    i -= 1
    base, tax, rate = brackets[i]

    return tax + (income-base) * rate
brackets = convert([
        (0, 0.10),
        (19400, 0.12),
        (78950, 0.22),
        (168400, 0.24),
        (321450, 0.32),
        (408200, 0.35),
        (612350, 0.37)
        ])

print_list(brackets)

for income in [100000, 300000, 5000]:
    tax = calc(brackets, income)
    rate = tax / income
    print(income, tax, rate)
