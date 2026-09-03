def income_summary():

    service_summary = {}
    total_paid_transaction = 0
    total_income = 0
    file = open(r"C:\Users\kirel\OneDrive\Documents\Python\payments.txt","r")

    for line in file:
        payment_id, customer, service, amount, status, booking_id, payment_date = line.strip().split("|")
        service = service.strip()
        status = status.strip()
        amount = float(amount.replace("RM", "").strip())

        if status == "PAID":
            total_paid_transaction += 1
            total_income += amount

            if service not in service_summary:
                service_summary[service] = {"count": 0, "income": 0}

            service_summary[service]["count"] += 1
            service_summary[service]["income"] += amount

    file.close()

    print("\n=========== INCOME SUMMARY ===========\n")
    for service in service_summary:
        print(
        f"{service:<25}"
        f"-{service_summary[service]['count']}- "
        f"RM{service_summary[service]['income']:.2f}")
        print()
    print(f"Total Paid Transaction : {total_paid_transaction}")
    print(f"Total Income : RM{total_income:.2f}")

income_summary()




