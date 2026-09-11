
def outstanding_payment_list():
    total_unpaid_transaction = 0
    total_unpaid_amount = 0

    file = open(r"C:\Users\kirel\OneDrive\Documents\Python\payments.txt","r")
    print("\n===== OUTSTANDING PAYMENT LIST =====\n")
    found = False
    for line in file:
        payment_id, customer, service, amount, status, booking_id, payment_date = line.strip().split("|")
        status = status.strip()
        if status == "UNPAID":
            found = True
            amount_value = float(amount.replace("RM", "").strip())

            total_unpaid_transaction += 1
            total_unpaid_amount += amount_value
            print(f"Payment ID : {payment_id.strip()}")
            print(f"Customer : {customer.strip()}")
            print(f"Service : {service.strip()}")
            print(f"Amount : {amount.strip()}")
            print(f"Booking ID : {booking_id.strip()}")
            print("-" * 35)
    if not found:
        print("No Outstanding Payments.")
    print()
    print(f"Total Outstanding Transactions : {total_unpaid_transaction}")
    print(f"Total Outstanding Amount : RM{total_unpaid_amount:.2f}")
    file.close()
    return total_unpaid_transaction, total_unpaid_amount

    