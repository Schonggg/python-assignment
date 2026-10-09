def main():
    from module.utils import(
        clear_screen,
        render_menu,
        error,
        process_due_bookings,
        warning
    )


    clear_screen()
    process_due_bookings()

    while True:
        print(render_menu(
            "MAIN MENU",
            [("1", "Login"), ("2", "Register user"), ("3", "Exit")]
        ))

        choice = input("> ").strip()
        if choice == "1":
            from module.admin.admin_menu import admin_menu
            from module.authentication import login
            from module.customer_pkg.customer_menu import customer_menu
            from module.maintenance_pkg.maintenance_menu import maintenance_menu
            from module.finance_pkg.finance_menu import finance_menu
            from module.booking_pkg.booking_menu import booking_menu
            from module.utils import clear_screen, show_startup_messages
            import time

            user = login()
            if not user:
                continue

            role = user["role"].lower()

            
            if role == "admin":
                time.sleep(2.5)
                clear_screen()
                show_startup_messages(role)
                admin_menu()

            elif role == "customer":
                time.sleep(2.5)
                clear_screen()
                customer_menu(user["username"])

            elif role == "maintenance":
                time.sleep(2.5)
                clear_screen()
                show_startup_messages(role)
                maintenance_menu(user["user_id"])

            elif role == "officer":
                time.sleep(2.5)
                clear_screen()
                show_startup_messages(role)
                booking_menu()

            elif role == "accountant":
                time.sleep(2.5)
                clear_screen()
                show_startup_messages(role)
                finance_menu()

            else:
                print(warning("This role has no menu yet."))

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