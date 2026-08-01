# python-assignment

[UPDATE 1st August 2026 19:37:00]
1. I have updated a new function call primary_key in utils.py

The usage is lidis:
        code = primary_key(CUSTOMER_FILE)

        with open(CUSTOMER_FILE, "a", encoding="utf-8") as handle:
            handle.write(f"{code}, {username}, {password1}, customer\n")

So the first line u should change the "CUSTOMER_FILE" to the file u wanna make changes.
Then the variable code will be changed to the primary_key that you are referring. 
For example: if the customer.txt have 2 customer, the code = C003, as this is the 3rd customer

*All you have to do is change the primary_key(PATH) to the correct PATH, the code will change accordingly.