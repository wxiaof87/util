def calc_payment(principal, terms, rate):
    # discount monthly cash flow to today
    q = 1 / (1 + rate)
    return principal * (1 - q) / (1 - q ** terms) / q
    # return principal*(1-q)/(1-q**terms)


def breakdown(principal, terms, rate):
    payment = calc_payment(principal, terms, rate)
    print("annual rate: {0:.5f}".format(rate*12))
    print('\t'.join(["term", "principal", "payment", "principal_paid", "interest_paid"]))
    template = '\t'.join(["{0}", "{1:.0f}", "{2:.0f}", "{3:.0f}", "{4:.0f}"])
    for i in range(terms):
        interest_paid = principal * rate
        principal_paid = payment - interest_paid
        principal -= principal_paid
        print(template.format(i + 1, principal, payment, principal_paid, interest_paid))


principal = 1000 * 1000
terms = 30 * 12
rate = 0.02375 / 12
breakdown(principal, terms, rate)

print("\n----------------------------------")
print("\t".join(["rate", "payment", "ratio"]))
template = "\t".join(["{0:.5f}", "{1:.0f}", "{2:.3f}"])
for rr in range(2000, 4000, 125):
    r = rr / 100000
    payment = calc_payment(principal, terms, r / 12)
    ratio = payment * terms / principal
    print(template.format(r, payment, ratio))
