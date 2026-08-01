def main():
    while True:
        print("1) Login\n2) Register user\n3) Exit")
        choice = input("> ").strip()
        if choice == "1":
            from module.admin import admin_menu
            from module.authentication import customer_menu, login

            customer = login()
            if not customer:
                continue

            if customer["role"] in ("admin", "staff"):
                admin_menu()
            else:
                customer_menu(customer["username"])
        elif choice == "2":
            from module.authentication import register_username, register_password
            new_username = register_username()
            if new_username:
                register_password(new_username)
                
        elif choice in ("3", "q", "quit", "exit"):
            break
        else:
            print("Invalid choice, try again.")

if __name__ == "__main__":
    main()