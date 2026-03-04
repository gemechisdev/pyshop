# PyShop - Terminal Shop (single file, no external modules, no files)

import time
import random
import sys

# ────────────────────────────────────────────────
#  DATA (lives only in memory)
# ────────────────────────────────────────────────

products = [
    {"id": 1,  "name": "Wireless Earbuds",      "price":  89.90, "stock": 14, "category": "Audio"},
    {"id": 2,  "name": "Mechanical Keyboard",    "price": 129.00, "stock":  7, "category": "Peripherals"},
    {"id": 3,  "name": "27\" 1440p Monitor",     "price": 249.99, "stock":  5, "category": "Display"},
    {"id": 4,  "name": "USB-C 100W Charger",     "price":  59.00, "stock": 22, "category": "Charging"},
    {"id": 5,  "name": "Portable SSD 1TB",       "price": 109.90, "stock": 11, "category": "Storage"},
    {"id": 6,  "name": "RGB Mouse Pad XXL",      "price":  24.99, "stock": 38, "category": "Peripherals"},
    {"id": 7,  "name": "4K Webcam",              "price":  79.50, "stock":  9, "category": "Camera"},
    {"id": 8,  "name": "Cable Management Box",   "price":  19.90, "stock": 47, "category": "Accessories"},
]

users = {
    "admin": {"password": "admin123", "role": "admin", "balance": 9999.0},
}

# Current session
current_user = None
cart = []           # list of {"product": dict, "qty": int}

# ────────────────────────────────────────────────
#  HELPERS
# ────────────────────────────────────────────────

def clear():
    print("\033[H\033[J", end="")   # ANSI clear screen (works in most terminals)

def pause(t=0.6):
    time.sleep(t)

def header(title):
    clear()
    print("═" * 60)
    print(f"  {title.center(56)}  ")
    print("═" * 60)
    print()

def press_enter_to_continue():
    input("\nPress ENTER to continue... ")

def invalid_choice():
    print("\nInvalid choice. Try again.")
    pause(1.2)

def get_float(prompt):
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("Please enter a number.")

def get_int(prompt, min_val=0, max_val=None):
    while True:
        try:
            v = int(input(prompt))
            if v < min_val:
                print(f"Value must be at least {min_val}.")
                continue
            if max_val is not None and v > max_val:
                print(f"Value cannot be more than {max_val}.")
                continue
            return v
        except ValueError:
            print("Please enter a whole number.")

# ────────────────────────────────────────────────
#  PRODUCT DISPLAY
# ────────────────────────────────────────────────

def show_product(p, show_id=True):
    print(f"  {p['id']:2d}. {p['name']:<24} ${p['price']:6.2f}  "
          f"(stock: {p['stock']:2d})  {p['category']}")

def list_products():
    if not products:
        print("  No products available right now.\n")
        return
    for p in products:
        show_product(p)

def find_product_by_id(pid):
    for p in products:
        if p["id"] == pid:
            return p
    return None

def show_cart():
    if not cart:
        print("  Your cart is empty.\n")
        return 0.0

    total = 0.0
    print("  Your cart:\n")
    for i, item in enumerate(cart, 1):
        p = item["product"]
        qty = item["qty"]
        subtotal = p["price"] * qty
        total += subtotal
        print(f"  {i:2d}. {p['name']:<24} ×{qty:2d}   ${subtotal:7.2f}")
    print(f"\n  Total: ${total:,.2f}\n")
    return total

# ────────────────────────────────────────────────
#  AUTH
# ────────────────────────────────────────────────

def register():
    global current_user
    header("Create Account")

    while True:
        username = input("  Username: ").strip().lower()
        if not username:
            print("Username cannot be empty.")
            continue
        if username in users:
            print("Username already taken.")
            continue
        break

    password = input("  Password: ").strip()
    if len(password) < 3:
        print("Password too short. Minimum 3 characters.")
        press_enter_to_continue()
        return False

    users[username] = {
        "password": password,
        "role": "customer",
        "balance": round(random.uniform(15, 180), 2)
    }
    current_user = username
    print(f"\nWelcome, {username}! You received a starter balance of ${users[username]['balance']:.2f}")
    pause(1.8)
    return True

def login():
    global current_user
    header("Login")

    username = input("  Username: ").strip().lower()
    if username not in users:
        print("User not found.")
        return False

    password = input("  Password: ").strip()
    if users[username]["password"] != password:
        print("Incorrect password.")
        return False

    current_user = username
    print(f"\nWelcome back, {username}!")
    pause(1.2)
    return True

# ────────────────────────────────────────────────
#  ADMIN
# ────────────────────────────────────────────────

def admin_menu():
    while True:
        header("ADMIN PANEL")
        print("  1. Add new product")
        print("  2. List all products")
        print("  3. Restock product")
        print("  0. Back to main menu")
        print()

        ch = input("→ ").strip()
        if ch == "0":
            break
        elif ch == "1":
            add_product()
        elif ch == "2":
            header("All Products")
            list_products()
            press_enter_to_continue()
        elif ch == "3":
            restock_product()
        else:
            invalid_choice()

def add_product():
    header("Add New Product")
    name = input("  Name              : ").strip()
    if not name:
        print("Name required.")
        return

    price = get_float("  Price ($)         : ")
    stock = get_int(  "  Initial stock     : ", min_val=0)
    cat   = input(    "  Category          : ").strip() or "General"

    new_id = max(p["id"] for p in products) + 1 if products else 1

    products.append({
        "id": new_id,
        "name": name,
        "price": round(price, 2),
        "stock": stock,
        "category": cat
    })
    print(f"\nProduct '{name}' added (ID: {new_id})")
    press_enter_to_continue()

def restock_product():
    header("Restock Product")
    list_products()
    pid = get_int("  Product ID to restock: ")
    prod = find_product_by_id(pid)
    if not prod:
        print("Product not found.")
        press_enter_to_continue()
        return

    add = get_int(f"  How many to add to {prod['name']}? ", min_val=1)
    prod["stock"] += add
    print(f"\n{add} units added. New stock: {prod['stock']}")
    press_enter_to_continue()

# ────────────────────────────────────────────────
#  SHOP FLOW
# ────────────────────────────────────────────────

def shop_menu():
    global cart
    while True:
        header(f"PyShop  •  {current_user}")
        print("  1. Browse all products")
        print("  2. View cart")
        print("  3. Checkout")
        print("  4. Logout")
        print()

        ch = input("→ ").strip()

        if ch == "1":
            header("Products")
            list_products()
            while True:
                try:
                    sel = input("\nEnter product number (0 = back): ").strip()
                    if sel == "0":
                        break
                    pid = int(sel)
                    prod = find_product_by_id(pid)
                    if not prod:
                        print("Product not found.")
                        continue

                    print(f"\n  {prod['name']}")
                    print(f"  Price    : ${prod['price']:.2f}")
                    print(f"  Stock    : {prod['stock']}")
                    print(f"  Category : {prod['category']}")
                    print()

                    if prod["stock"] == 0:
                        print("  OUT OF STOCK")
                    else:
                        qty = get_int("  Quantity: ", min_val=1, max_val=prod["stock"])
                        cart.append({"product": prod, "qty": qty})
                        print(f"  → {qty} × {prod['name']} added to cart")
                    pause(1.4)
                except ValueError:
                    print("Enter a number or 0.")

        elif ch == "2":
            header("Shopping Cart")
            show_cart()
            while cart:
                rem = input("Remove item? (number or 0=back): ").strip()
                if rem == "0":
                    break
                try:
                    idx = int(rem) - 1
                    if 0 <= idx < len(cart):
                        removed = cart.pop(idx)
                        print(f"Removed: {removed['qty']} × {removed['product']['name']}")
                        pause(0.9)
                    else:
                        print("Invalid item number.")
                except ValueError:
                    print("Enter a number.")
            press_enter_to_continue()

        elif ch == "3":
            if not cart:
                print("Your cart is empty.")
                press_enter_to_continue()
                continue

            header("Checkout")
            total = show_cart()
            balance = users[current_user]["balance"]

            print(f"  Your balance : ${balance:.2f}")
            print(f"  Order total  : ${total:.2f}\n")

            if total > balance:
                print("  Insufficient funds!")
                press_enter_to_continue()
                continue

            confirm = input("Confirm purchase? (yes/no): ").strip().lower()
            if confirm not in ("y", "yes"):
                print("Purchase cancelled.")
                press_enter_to_continue()
                continue

            # process order
            users[current_user]["balance"] -= total
            for item in cart:
                item["product"]["stock"] -= item["qty"]

            print("\n" + "═"*60)
            print("  PURCHASE SUCCESSFUL!")
            print("  Thank you for shopping at PyShop!")
            print(f"  New balance: ${users[current_user]['balance']:.2f}")
            print("═"*60 + "\n")
            cart.clear()
            pause(2.5)

        elif ch == "4":
            print("Logging out...")
            pause(0.8)
            break

        else:
            invalid_choice()

# ────────────────────────────────────────────────
#  MAIN
# ────────────────────────────────────────────────

def main():
    global current_user

    while True:
        clear()
        print("""
    ██████╗ ██╗   ██╗███████╗██╗  ██╗ ██████╗ ██████╗ 
    ██╔══██╗╚██╗ ██╔╝██╔════╝██║  ██║██╔═══██╗██╔══██╗
    ██████╔╝ ╚████╔╝ ███████╗███████║██║   ██║██████╔╝
    ██╔═══╝   ╚██╔╝  ╚════██║██╔══██║██║   ██║██╔═══╝
    ██║        ██║   ███████║██║  ██║╚██████╔╝██║  
    ╚═╝        ╚═╝   ╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  
        """.center(60))
        print("                  Terminal Tech Shop                  \n")

        if current_user:
            print(f"  Logged in as: {current_user}\n")
            print("  1. Enter shop")
            if users[current_user]["role"] == "admin":
                print("  2. Admin panel")
            print("  0. Logout & exit")
        else:
            print("  1. Login")
            print("  2. Register")
            print("  0. Exit")
        print()

        choice = input("→ ").strip()

        if current_user:
            if choice == "1":
                shop_menu()
            elif choice == "2" and users[current_user]["role"] == "admin":
                admin_menu()
            elif choice == "0":
                print("\nThank you for visiting PyShop. Goodbye!\n")
                break
            else:
                invalid_choice()
        else:
            if choice == "1":
                if login():
                    shop_menu()
            elif choice == "2":
                register()
                if current_user:
                    shop_menu()
            elif choice == "0":
                print("\nGoodbye!\n")
                break
            else:
                invalid_choice()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nShop closed.\n")
    except Exception as e:
        print(f"\nSomething broke: {e}")
        print("The shop will now close.")