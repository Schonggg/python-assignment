def main():
    while True:
        print("1) Login\n2) Register user\n3) Exit")
        choice = input("> ").strip()
        if choice == "1":
            from module.admin import admin_menu
            from module.authentication import login
            from module.customer.customer_menu import customer_menu
            from module.utils import clear_screen
            import time

            user = login()
            if not user:
                continue

            if user["role"] in ("admin"):
                time.sleep(2.5)
                clear_screen()
                admin_menu()

            else:
                time.sleep(2.5)
                clear_screen()
                customer_menu(user["username"])

        elif choice == "2":
            from module.authentication import register_username, register_all
            new_username = register_username()
            if new_username:
                register_all(new_username)
                
        elif choice in ("3", "q", "quit", "exit"):
            break
        else:
            print("Invalid choice, try again.")

if __name__ == "__main__":
    main()