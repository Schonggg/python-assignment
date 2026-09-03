def monthly_financial_summary():
    month_check = input("Enter Month (YYYY-MM): ")
    paid_count = 0
    unpaid_count = 0
    income = 0
    outstanding = 0
    file = open(r"C:\Users\kirel\OneDrive\Documents\Python\payments.txt","r")

    for line in file:
        payment_id, customer, service, amount, status, booking_id, payment_date = line.strip().split("|")
        payment_date = payment_date.strip()
        payment_month = payment_date[:7]
        amount = float(amount.replace("RM",""))
        if payment_month == month_check:
            if status.strip() == "PAID":
                paid_count += 1
                income += amount
            elif status.strip() == "UNPAID":
                unpaid_count += 1
                outstanding += amount
    file.close()

    print("\n===== MONTHLY FINANCIAL SUMMARY =====")
    print(f"Month : {month_check}")
    print()
    print(f"Total Paid Transactions : {paid_count}")
    print(f"Total Outstanding Transactions : {unpaid_count}")
    print()
    print(f"Total Income : RM{income:.2f}")
    print(f"Outstanding Amount : RM{outstanding:.2f}")


