# PyShop
# Simple terminal shop developed in Python.
# Features:
# - User registration and login
# - Product browsing with search and category filters
# - Shopping cart and checkout with balance management
# - Admin panel for product management

import time
import random
import sys

# ────────────────────────────────────────────────
#  DATA (all in memory)
# ────────────────────────────────────────────────

products = [
    # Laptops
    {"id": 1,  "name": "MacBook Air M2",        "price": int(109900 * 0.8), "stock": 8,  "category": "Laptops"},
    {"id": 2,  "name": "Dell XPS 13",           "price": int(129900 * 0.8), "stock": 5,  "category": "Laptops"},
    {"id": 3,  "name": "ThinkPad X1 Carbon",     "price": int(149900 * 0.8), "stock": 6,  "category": "Laptops"},
    {"id": 4,  "name": "ROG Zephyrus G14",       "price": int(159900 * 0.8), "stock": 4,  "category": "Laptops"},

    # Smartphones
    {"id": 5,  "name": "iPhone 16 Pro",          "price": int(99900 * 0.8),  "stock": 12, "category": "Smartphones"},
    {"id": 6,  "name": "Galaxy S25 Ultra",       "price": int(129900 * 0.8), "stock": 9,  "category": "Smartphones"},
    {"id": 7,  "name": "Pixel 9 Pro",            "price": int(89900 * 0.8),  "stock": 11, "category": "Smartphones"},
    {"id": 8,  "name": "Nothing Phone 3",        "price": int(69900 * 0.8),  "stock": 15, "category": "Smartphones"},

    # Tablets & E-readers
    {"id": 9,  "name": "iPad Air M2",            "price": int(59900 * 0.8),  "stock": 10, "category": "Tablets"},
    {"id": 10, "name": "Galaxy Tab S10+",        "price": int(84900 * 0.8),  "stock": 7,  "category": "Tablets"},
    {"id": 11, "name": "Kindle Paperwhite",      "price": int(15900 * 0.8),  "stock": 22, "category": "E-readers"},

    # Accessories & Peripherals
    {"id": 12, "name": "AirPods Pro 2",          "price": int(24900 * 0.8),  "stock": 18, "category": "Audio"},
    {"id": 13, "name": "Sony WH-1000XM5",        "price": int(34900 * 0.8),  "stock": 9,  "category": "Audio"},
    {"id": 14, "name": "MX Master 3S Mouse",     "price": int(9900 * 0.8),   "stock": 25, "category": "Peripherals"},
    {"id": 15, "name": "Keychron Q1 Pro",        "price": int(19900 * 0.8),  "stock": 13, "category": "Peripherals"},
    {"id": 16, "name": "Anker 737 Power Bank",   "price": int(12900 * 0.8),  "stock": 20, "category": "Charging"},

    # Monitors & Storage
    {"id": 17, "name": "LG 27GP950-B 4K",        "price": int(42900 * 0.8),  "stock": 6,  "category": "Monitors"},
    {"id": 18, "name": "Odyssey G7 32\" 4K",     "price": int(69900 * 0.8),  "stock": 5,  "category": "Monitors"},
    {"id": 19, "name": "Samsung T9 SSD 2TB",     "price": int(22900 * 0.8),  "stock": 14, "category": "Storage"},
    {"id": 20, "name": "WD SN850X 2TB NVMe",     "price": int(18900 * 0.8),  "stock": 17, "category": "Storage"},
]

users = {
    "admin": {"password": "admin123", "role": "admin", "balance": 999900, "history": []},
    "gemechis": {"password": "Gemechis123", "role": "customer", "balance": 50000, "history": []},
}

# Current session
current_user = None
cart = []                   # [{"product": dict, "qty": int}]
browse_search = ""          # persistent during shop session
browse_category = None      # persistent during shop session

# ────────────────────────────────────────────────
#  HELPERS
# ────────────────────────────────────────────────

def clear():
    print("\033[2J\033[H", end="")     # better ANSI clear

def cprint(text, color="white"):
    colors = {"green": "\033[92m", "red": "\033[91m", "cyan": "\033[96m", "yellow": "\033[93m", "magenta": "\033[95m", "reset": "\033[0m"}
    print(f"{colors.get(color, '')}{text}{colors['reset']}")

def pause(t=0.7):
    time.sleep(t)

def header(title):
    clear()
    print("═" * 70)
    print(f"  {title.center(66)}  ")
    print("═" * 70)
    print()

def press_enter():
    input("\nPress ENTER to continue... ")

def invalid():
    cprint("\nInvalid choice.", "red")
    pause(1.1)

def get_float(prompt):
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            cprint("Please enter a valid number.", "red")

def get_int(prompt, min_val=None, max_val=None):
    while True:
        try:
            v = int(input(prompt))
            if min_val is not None and v < min_val:
                cprint(f"Must be at least {min_val}.", "red")
                continue
            if max_val is not None and v > max_val:
                cprint(f"Cannot be more than {max_val}.", "red")
                continue
            return v
        except ValueError:
            cprint("Please enter a whole number.", "red")

def get_yes_no(prompt):
    while True:
        ans = input(prompt).strip().lower()
        if ans in ("y", "yes"):
            return True
        if ans in ("n", "no"):
            return False
        cprint("Please type yes or no.", "red")

def etb(amount):
    return f"{amount:.0f}ETB"

# ────────────────────────────────────────────────
#  PRODUCT DISPLAY
# ────────────────────────────────────────────────

def get_categories():
    cats = {p["category"] for p in products}
    return sorted(cats)

def get_filtered_products():
    filtered = products
    if browse_search:
        s = browse_search.lower()
        filtered = [p for p in filtered if s in p["name"].lower()]
    if browse_category:
        filtered = [p for p in filtered if p["category"] == browse_category]
    return filtered

def show_product(p, show_stock_warning=True):
    warn = " ⚠ LOW STOCK" if p["stock"] <= 3 and show_stock_warning else ""
    print(f"  {p['id']:3d} │ {p['name']:<26} │ {etb(p['price']):>9} │ "
          f"stock: {p['stock']:3d}{warn} │ {p['category']}")

def display_products(prods, title="Products", page=1, page_size=None):
    if not prods:
        cprint("  No products match your criteria.", "cyan")
        return 1, 1

    if page_size and page_size > 0:
        total_pages = (len(prods) + page_size - 1) // page_size
        page = max(1, min(page, total_pages))
        start = (page - 1) * page_size
        visible = prods[start:start + page_size]
        print(f"  {title} ({len(visible)} shown • page {page}/{total_pages} • {len(prods)} matched / {len(products)} total)\n")
    else:
        total_pages = 1
        page = 1
        visible = prods
        print(f"  {title} ({len(visible)} shown / {len(products)} total)\n")

    for p in visible:
        show_product(p)
    print()
    return total_pages, page

def show_cart():
    if not cart:
        cprint("  Your cart is empty.", "cyan")
        return 0.0

    total = 0.0
    print("  Cart contents:\n")
    for i, item in enumerate(cart, 1):
        p = item["product"]
        subtotal = p["price"] * item["qty"]
        total += subtotal
        print(f"  {i:2d} │ {p['name']:<26} × {item['qty']:2d} │ {etb(subtotal):>9}")
    print(f"\n  Subtotal: {etb(total)}")
    return total

# ────────────────────────────────────────────────
#  AUTH & ACCOUNT
# ────────────────────────────────────────────────

def register():
    global current_user
    header("Create Account")
    while True:
        username = input("  Username: ").strip().lower()
        if not username:
            cprint("Username required.", "red")
            continue
        if username in users:
            cprint("Username already taken.", "red")
            continue
        break

    password = input("  Password: ").strip()
    if len(password) < 4:
        cprint("Password must be at least 4 characters.", "red")
        press_enter()
        return False

    balance = random.randint(2000, 22000)
    users[username] = {
        "password": password,
        "role": "customer",
        "balance": balance,
        "history": []
    }
    current_user = username
    cprint(f"\nWelcome, {username}! Starter balance: {etb(balance)}", "green")
    pause(2.0)
    return True

def login():
    global current_user
    header("Login")
    username = input("  Username: ").strip().lower()
    if username not in users:
        cprint("User not found.", "red")
        pause(2.0)
        return False
    password = input("  Password: ").strip()
    if users[username]["password"] != password:
        cprint("Incorrect password. Login failed.", "red")
        pause(2.0)
        return False
    current_user = username
    cprint(f"\nWelcome back, {username}!", "green")
    pause(2.0)
    return True

def show_account():
    header(f"My Account • {current_user}")
    u = users[current_user]
    print(f"  Balance     : {etb(u['balance'])}")
    print(f"  Orders made : {len(u['history'])}")
    print("\n  1. Add funds")
    print("  2. View order history")
    print("  0. Back")
    ch = input("\n→ ").strip()
    if ch == "1":
        amt_etb = get_float("  Amount to add (ETB): ")
        if amt_etb > 0:
            amt = amt_etb
            u["balance"] += amt
            cprint(f"  Added {etb(amt)}. New balance: {etb(u['balance'])}", "green")
        else:
            cprint("  Amount must be positive.", "red")
        press_enter()
    elif ch == "2":
        header("Order History")
        if not u["history"]:
            cprint("  No orders yet.", "cyan")
        else:
            for i, order in enumerate(u["history"], 1):
                print(f"  #{i}  {order['date']}  {etb(order['total'])}")
                for item in order["items"]:
                    print(f"      • {item['qty']}× {item['name']}")
                print()
        press_enter()
    # 0 = back (implicit)

# ────────────────────────────────────────────────
#  BROWSING (search + category filter)
# ────────────────────────────────────────────────

def browse_products():
    global browse_search, browse_category
    page = 1
    page_size = 10

    while True:
        filtered = get_filtered_products()
        header("Browse Products")
        status = []
        if browse_search:
            status.append(f"Search: {browse_search}")
        if browse_category:
            status.append(f"Category: {browse_category}")
        if status:
            cprint("  Filters → " + " | ".join(status), "yellow")
        else:
            cprint("  ────────────── Showing all products ──────────────", "yellow")
        print()

        # Show trending hint
        if products:
            top = sorted(products, key=lambda p: p["stock"], reverse=True)[:3]
            cprint("  Trending: " + ", ".join(p["name"] for p in top[:2]) + (f", {top[2]['name']}" if len(top)>2 else ""), "cyan")
            print()

        total_pages, page = display_products(filtered, page=page, page_size=page_size)

        cprint("  [S] Search by name   [C] Filter category   [R] Reset filters", "magenta")
        if total_pages > 1:
            cprint("  [P] Previous page    [N] Next page", "magenta")
        cprint("  Or enter product number to view/add   [0] Back", "magenta")
        action = input("\n→ ").strip().lower()

        if action == "0":
            break
        elif action == "s":
            term = input("  Search term: ").strip()
            browse_search = term
            page = 1
            continue
        elif action == "c":
            cats = get_categories()
            if not cats:
                cprint("  No categories yet.", "cyan")
                press_enter()
                continue
            print("\n  Categories:")
            for i, cat in enumerate(cats, 1):
                print(f"  {i}. {cat}")
            idx = get_int("  Choose category number (0=cancel): ", 0)
            if idx == 0:
                continue
            if 1 <= idx <= len(cats):
                browse_category = cats[idx-1]
                page = 1
            else:
                cprint("Invalid selection.", "red")
            continue
        elif action == "r":
            browse_search = ""
            browse_category = None
            page = 1
            cprint("  Filters reset.", "green")
            pause(1.3)
            continue
        elif action == "n":
            if page < total_pages:
                page += 1
            else:
                cprint("  You are already on the last page.", "cyan")
                pause(1.3)
            continue
        elif action == "p":
            if page > 1:
                page -= 1
            else:
                cprint("  You are already on the first page.", "cyan")
                pause(1.3)
            continue
        else:
            # Assume product number
            try:
                pid = int(action)
                prod = next((p for p in products if p["id"] == pid), None)
                if not prod:
                    cprint("Product not found.", "red")
                    pause(1.3)
                    continue

                header(prod["name"])
                show_product(prod, False)
                print()
                if prod["stock"] == 0:
                    cprint("  OUT OF STOCK", "red")
                else:
                    qty = get_int("  Quantity: ", 1, prod["stock"])
                    cart.append({"product": prod, "qty": qty})
                    cprint(f"  Added {qty} × {prod['name']} to cart", "green")
                pause(1.3)
            except ValueError:
                invalid()

# ────────────────────────────────────────────────
#  ADMIN FEATURES
# ────────────────────────────────────────────────

def admin_menu():
    while True:
        header("ADMIN PANEL")
        print("  1. Add product")
        print("  2. Edit product")
        print("  3. Delete product")
        print("  4. List products")
        print("  5. View all users")
        print("  0. Back")
        ch = input("\n→ ").strip()

        if ch == "0": break
        elif ch == "1": add_product()
        elif ch == "2": edit_product()
        elif ch == "3": delete_product()
        elif ch == "4":
            header("All Products")
            display_products(products, "Full inventory")
            press_enter()
        elif ch == "5":
            header("Users")
            for uname, data in users.items():
                print(f"  {uname:12} | {data['role']:8} | {etb(data['balance']):>9} | orders: {len(data['history'])}")
            press_enter()
        else:
            invalid()

def add_product():
    header("Add Product")
    name = input("  Name: ").strip()
    if not name: 
        cprint("Name required.", "red")
        return
    price = get_float("  Price (ETB): ")
    stock = get_int(  "  Stock: ", 0)
    cat   = input(    "  Category: ").strip() or "General"

    new_id = max((p["id"] for p in products), default=0) + 1
    products.append({
        "id": new_id,
        "name": name,
        "price": round(price),
        "stock": stock,
        "category": cat
    })
    cprint(f"  Added '{name}' (ID {new_id})", "green")
    press_enter()

def edit_product():
    header("Edit Product")
    display_products(products, "Select product to edit")
    pid = get_int("  Product ID: ")
    prod = next((p for p in products if p["id"] == pid), None)
    if not prod:
        cprint("Product not found.", "red")
        press_enter()
        return

    print("\n  Current:")
    show_product(prod, False)
    print()

    name = input(f"  New name (enter to keep '{prod['name']}'): ").strip()
    if name: prod["name"] = name

    price_str = input(f"  New price (enter to keep {etb(prod['price'])}): ").strip()
    if price_str:
        try:
            prod["price"] = round(float(price_str))
        except:
            cprint("Invalid price – kept old value.", "red")

    stock = get_int(f"  New stock (current: {prod['stock']}): ", 0)
    prod["stock"] = stock

    cat = input(f"  New category (enter to keep '{prod['category']}'): ").strip()
    if cat: prod["category"] = cat

    cprint("  Product updated.", "green")
    press_enter()

def delete_product():
    header("Delete Product")
    display_products(products)
    pid = get_int("  Product ID to delete: ")
    prod = next((p for p in products if p["id"] == pid), None)
    if not prod:
        cprint("Not found.", "red")
        press_enter()
        return
    if get_yes_no(f"  Really delete '{prod['name']}'? (yes/no): "):
        products.remove(prod)
        cprint("  Product deleted.", "green")
    else:
        cprint("  Cancelled.", "cyan")
    press_enter()

# ────────────────────────────────────────────────
#  SHOP MENU
# ────────────────────────────────────────────────

def shop_menu():
    global current_user, browse_search, browse_category, cart
    while True:
        header(f"PyShop  •  {current_user}")
        total_items = sum(p["stock"] for p in products)
        print(f"  {len(products)} products • {total_items} items in stock\n")

        print("  1. Browse products")
        print("  2. View cart & checkout")
        print("  3. My Account")
        if users[current_user]["role"] == "admin":
            print("  0. Back to main menu")
        else:
            print("  0. Logout")
        ch = input("\n→ ").strip()

        if ch == "1":
            browse_products()
        elif ch == "2":
            header("Shopping Cart")
            subtotal = show_cart()
            if not cart:
                press_enter()
                continue

            # Discount logic
            discount = 0.0
            if subtotal > 150:
                discount = subtotal * 0.05
                print(f"  → 5% discount applied (-{etb(discount)})")
                total = subtotal - discount
            else:
                total = subtotal
            print(f"  Final total: {etb(total)}")
            print(f"  Your balance: {etb(users[current_user]['balance'])}\n")

            if total > users[current_user]["balance"]:
                cprint("  Not enough funds!", "red")
                press_enter()
                continue

            if get_yes_no("  Confirm purchase? (yes/no): "):
                # Process purchase
                users[current_user]["balance"] -= total
                for item in cart:
                    item["product"]["stock"] -= item["qty"]

                # Save history
                order = {
                    "date": time.strftime("%Y-%m-%d %H:%M"),
                    "items": [{"name": i["product"]["name"], "qty": i["qty"]} for i in cart],
                    "total": total
                }
                users[current_user]["history"].append(order)

                cprint("\n" + "═"*70, "green")
                cprint("  PURCHASE SUCCESSFUL!  Thank you for shopping!", "green")
                cprint(f"  New balance: {etb(users[current_user]['balance'])}", "green")
                cprint("═"*70 + "\n", "green")
                cart.clear()
                pause(2.5)
            else:
                cprint("  Purchase cancelled.", "cyan")
                pause(2.0)

        elif ch == "3":
            show_account()
        elif ch == "0":
            if users[current_user]["role"] == "admin":
                cprint("Returning to main menu...", "cyan")
                browse_search = ""
                browse_category = None
                pause(1.0)
                break
            else:
                cprint(f"\n{current_user} logged out.\n", "cyan")
                browse_search = ""
                browse_category = None
                current_user = None
                pause(1.0)
                break
        else:
            invalid()

# ────────────────────────────────────────────────
#  MAIN LOOP
# ────────────────────────────────────────────────

def main():
    global current_user

    while True:
        if current_user and users[current_user]["role"] != "admin":
            shop_menu()
            continue

        clear()
        print("╔" + "═" * 65 + "╗")
        print("║" + " " * 65 + "║")
        print("║" + "┏━┃┃ ┃┏━┛┃ ┃┏━┃┏━┃".center(65) + "║")
        print("║" + "┏━┛━┏┛━━┃┏━┃┃ ┃┏━┛".center(65) + "║")
        print("║" + "┛   ┛ ━━┛┛ ┛━━┛┛  ".center(65) + "║")
        print("║" + " " * 65 + "║")
        print("║" + "Python Shop Store".center(65) + "║")
        print("║" + " " * 65 + "║")
        print("╚" + "═" * 65 + "╝")

        if current_user:
            print(f"  Logged in as: {current_user} ({users[current_user]['role']})")
            print("  1. Enter shop")
            if users[current_user]["role"] == "admin":
                print("  2. Admin panel")
            print("  0. Logout")
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
                cprint(f"\n{current_user} logged out.\n", "cyan")
                current_user = None
                pause(1.0)
            else:
                invalid()
        else:
            if choice == "1":
                login()
            elif choice == "2":
                register()
            elif choice == "0":
                cprint("\nGoodbye!\n", "cyan")
                break
            else:
                invalid()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nShop closed.\n")
    except Exception as e:
        print(f"\nError: {e}\nShop will close.")