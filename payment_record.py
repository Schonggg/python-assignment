from datetime import datetime   

def generate_payment_id():

    file = open(r"C:\Users\kirel\OneDrive\Documents\Python\payments.txt","r")
    lines = file.readlines()
    file.close()

    if len(lines) == 0:
        return "P001"
    
    last_line = lines[-1]
    last_payment_id = last_line.split("|")[0]

    number = int(last_payment_id.replace("P", ""))
    number += 1
    return f"P{number:03d}"


def record_payment():

    booking_id_search = input("Enter Booking ID: ")
    if bool(booking_id_search):
        print("Booking ID entered")
#ID start with B001,B002,n+

    file = open(
        r"C:\Users\kirel\OneDrive\Documents\Python\bookings.txt",
        "r")
#better write the destination of file in full path to avoid errors

    

    for line in file:
        booking_id, customer, service, amount = line.strip().split("|")
    #status only show in payments.txt 

        if booking_id == booking_id_search:

            
            print("| Booking Found |")
            print("Customer:", customer)
            print("Service:", service)
            print("Amount: RM", amount)


            status = input("Enter Status (Paid/Unpaid): ")
            while status.lower() not in ["paid", "unpaid"]:
                print("Invalid status. Please enter 'Paid' or 'Unpaid'.")
                status = input("Enter Status (Paid/Unpaid): ")
            payment_id = generate_payment_id()
            payment_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            payment_file = open( r"C:\Users\kirel\OneDrive\Documents\Python\payments.txt",
            "a")

            payment_file.write(
            payment_id + "|" +
            customer + " | " +
            service + " | " +
            "RM" + amount + " | " +
            status.upper() + " | " +
            booking_id + " | " +
            payment_date + "\n"
            )

            payment_file.close()

            print("--Payment Recorded Successfully--")
            break
    else:
        print("--Booking Not Found--")
    file.close()

while True:

    record_payment()

    print("\n1. Make another payment record\n2. Exit")
    again = input("Make your choice: ")
    if again == "1":
        continue
    
    else:
        break

record_payment()