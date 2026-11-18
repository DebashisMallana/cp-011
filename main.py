"""
CP-011 — SwiftCart: Point-of-Sale Billing and Inventory System
Domain: E-Commerce and Retail | Level: Foundation
Run command: python main.py

A console-based Point-of-Sale (POS) system built using only the Python 3
standard library. Supports product lookup, automated promotional offers
(Buy-2-Get-1-Free and Percentage Discounts), itemized tax billing, real-time
stock deduction, customer loyalty points, end-of-day reporting, and low-stock
alerts.
"""

# ============================================================================
# GLOBAL CONFIGURATION CONSTANTS
# ============================================================================
TAX_RATE = 0.05          # 5% GST / Sales Tax applied to the post-offer subtotal
REORDER_LEVEL = 5        # Products with stock <= 5 appear in the low-stock report
DEFAULT_CUSTOMER = "walk-in"


# ============================================================================
# INITIAL IN-MEMORY DATA STORE
# ============================================================================
def create_initial_inventory():
    """
    Returns a dictionary of pre-loaded supermarket products.
    Each key is a unique uppercase product code, and each value is a dict
    holding product metadata, current stock, and at most one offer rule.

    Offer types supported:
      - "B2G1": Buy 2 Get 1 Free (every 3rd unit of that item is free)
      - "PCT" : Flat percentage discount off the line's gross amount
      - "NONE": No promotional offer
    """
    return {
        "P101": {
            "name": "Aashirvaad Whole Wheat Atta (5kg)",
            "price": 240.00,
            "stock": 15,
            "offer_type": "PCT",
            "offer_value": 10.0,  # 10% off line gross
        },
        "P102": {
            "name": "Britannia Marie Gold Biscuits",
            "price": 35.00,
            "stock": 20,
            "offer_type": "B2G1",
            "offer_value": 0.0,   # Buy 2 Get 1 Free (every set of 3 gets 1 free)
        },
        "P103": {
            "name": "Tata Tea Gold (500g)",
            "price": 180.00,
            "stock": 5,           # Exactly at REORDER_LEVEL (5) for immediate demo
            "offer_type": "PCT",
            "offer_value": 15.0,  # 15% off line gross
        },
        "P104": {
            "name": "Amul Pasteurised Butter (500g)",
            "price": 275.00,
            "stock": 3,           # Below REORDER_LEVEL (5) for immediate demo
            "offer_type": "NONE",
            "offer_value": 0.0,
        },
        "P105": {
            "name": "Maggi Masala Noodles (4-Pack)",
            "price": 60.00,
            "stock": 12,
            "offer_type": "B2G1",
            "offer_value": 0.0,   # Buy 2 Get 1 Free
        },
        "P106": {
            "name": "Fortune Sunlite Refined Oil (1L)",
            "price": 145.00,
            "stock": 4,           # Below REORDER_LEVEL (5) for immediate demo
            "offer_type": "PCT",
            "offer_value": 5.0,   # 5% off line gross
        },
    }


# ============================================================================
# HELPER & FORMATTING FUNCTIONS
# ============================================================================
def format_offer_label(product):
    """
    Converts a product's internal offer fields into a human-readable badge
    for catalog tables and cart summaries.
    """
    offer_type = product["offer_type"]
    if offer_type == "B2G1":
        return "Buy 2 Get 1 Free"
    elif offer_type == "PCT":
        return f"{product['offer_value']:.0f}% Off"
    return "No Offer"


def display_catalog(inventory):
    """
    Prints a formatted table of all products in inventory so the cashier
    can see product codes, prices, current stock, and active offers.
    """
    print("\n" + "-" * 78)
    print(f"{'CODE':<6} | {'PRODUCT NAME':<34} | {'PRICE (₹)':>10} | {'STOCK':>5} | {'OFFER'}")
    print("-" * 78)
    for code, item in inventory.items():
        offer_str = format_offer_label(item)
        print(
            f"{code:<6} | {item['name']:<34} | "
            f"{item['price']:>10.2f} | {item['stock']:>5} | {offer_str}"
        )
    print("-" * 78)


def calculate_line_item(code, product, qty):
    """
    Computes the exact pricing breakdown for a single cart row.

    Required math rules:
      gross    = unit_price * qty
      discount = per the product's single active offer rule
      net      = gross - discount

    Returns a dictionary with all computed values for bill printing.
    """
    unit_price = product["price"]
    gross = round(unit_price * qty, 2)
    offer_type = product["offer_type"]
    offer_value = product["offer_value"]

    # Apply at most one offer per product
    if offer_type == "B2G1":
        # One free unit for every complete group of 3 units bought
        free_units = qty // 3
        discount = round(free_units * unit_price, 2)
    elif offer_type == "PCT":
        # Flat percentage discount off this line's gross amount
        discount = round(gross * (offer_value / 100.0), 2)
    else:
        discount = 0.00

    net = round(gross - discount, 2)

    return {
        "code": code,
        "name": product["name"],
        "qty": qty,
        "unit_price": unit_price,
        "offer_label": format_offer_label(product),
        "gross": gross,
        "discount": discount,
        "net": net,
    }


def calculate_cart_totals(cart, inventory):
    """
    Iterates through all items in the current cart and computes:
      - A list of itemized line dictionaries
      - subtotal: sum of all items' NET amounts
      - total_discount: sum of all items' discounts (informational only)
    """
    line_items = []
    subtotal = 0.0
    total_discount = 0.0

    for code, qty in cart.items():
        product = inventory[code]
        line = calculate_line_item(code, product, qty)
        line_items.append(line)
        subtotal += line["net"]
        total_discount += line["discount"]

    return {
        "lines": line_items,
        "subtotal": round(subtotal, 2),
        "total_discount": round(total_discount, 2),
    }


# ============================================================================
# CORE FEATURE 1: LOOK UP PRODUCT BY CODE & ADD TO CART
# ============================================================================
def look_up_and_add_to_cart(inventory, cart):
    """
    Prompts the cashier for a product code and quantity.
    Validates that:
      1. The code exists in inventory (case-insensitive, whitespace-trimmed).
      2. The product is not completely out of stock.
      3. The quantity is a valid positive integer.
      4. Adding the quantity does not push (existing_cart_qty + new_qty)
         above the available shelf stock.
    """
    display_catalog(inventory)

    raw_code = input("Enter Product Code to add (or press Enter to cancel): ").strip().upper()
    if raw_code == "":
        print("[Info] Cancelled. Returning to main menu.")
        return

    # Reject unknown product codes immediately
    if raw_code not in inventory:
        print(f"[Error] Unknown product code '{raw_code}'. Please check the catalog.")
        return

    product = inventory[raw_code]
    available_stock = product["stock"]
    already_in_cart = cart.get(raw_code, 0)
    remaining_addable = available_stock - already_in_cart

    print(
        f"\nSelected: {product['name']} | Price: ₹{product['price']:.2f} | "
        f"Offer: {format_offer_label(product)}"
    )
    print(
        f"In Stock: {available_stock} | Already in Cart: {already_in_cart} | "
        f"Max You Can Add Now: {remaining_addable}"
    )

    if remaining_addable <= 0:
        print(
            f"[Error] Cannot add more '{product['name']}'. All available stock "
            f"({available_stock} units) is already in the cart."
        )
        return

    raw_qty = input("Enter quantity to add: ").strip()

    # Validate numeric integer input without crashing
    try:
        qty = int(raw_qty)
    except ValueError:
        print(f"[Error] Invalid quantity '{raw_qty}'. Please enter a whole number.")
        return

    if qty <= 0:
        print("[Error] Quantity must be at least 1.")
        return

    if qty > remaining_addable:
        print(
            f"[Error] Insufficient stock! Requested {qty}, but only "
            f"{remaining_addable} more unit(s) can be added (Total stock: {available_stock})."
        )
        return

    # Update cart quantity (accumulating if item was added earlier in the same bill)
    cart[raw_code] = already_in_cart + qty
    line_preview = calculate_line_item(raw_code, product, cart[raw_code])
    print(
        f"[Success] Added {qty} x {product['name']} to cart. "
        f"(Cart Qty: {cart[raw_code]} | Line Net: ₹{line_preview['net']:.2f})"
    )


# ============================================================================
# CORE FEATURE 2: VIEW CURRENT CART & APPLIED OFFERS
# ============================================================================
def view_cart(cart, inventory):
    """
    Displays all items currently in the cart along with their automatic
    offer discounts and the running subtotal before checkout.
    """
    if not cart:
        print("\n[Info] Your cart is currently empty.")
        return

    summary = calculate_cart_totals(cart, inventory)

    print("\n" + "=" * 86)
    print("                         CURRENT CART & APPLIED OFFERS")
    print("=" * 86)
    print(
        f"{'CODE':<6} | {'NAME':<28} | {'QTY':>4} | {'UNIT (₹)':>9} | "
        f"{'OFFER':<16} | {'DISC (₹)':>9} | {'NET (₹)':>9}"
    )
    print("-" * 86)

    for line in summary["lines"]:
        short_name = line["name"][:28]
        print(
            f"{line['code']:<6} | {short_name:<28} | {line['qty']:>4} | "
            f"{line['unit_price']:>9.2f} | {line['offer_label']:<16} | "
            f"{line['discount']:>9.2f} | {line['net']:>9.2f}"
        )

    print("-" * 86)
    print(f"{'Total Promotional Discount (Info Only):':>74} ₹{summary['total_discount']:>9.2f}")
    print(f"{'Current Cart Subtotal (Before Tax):':>74} ₹{summary['subtotal']:>9.2f}")
    print("=" * 86)


# ============================================================================
# STRETCH FEATURE 6 HELPER: LOYALTY IDENTIFICATION & REDEMPTION
# ============================================================================
def handle_loyalty_at_checkout(subtotal, loyalty_points):
    """
    Asks for a customer ID at checkout (defaults to 'walk-in').
    If the customer is not 'walk-in' and has existing loyalty points, lets them
    redeem up to their available balance BEFORE tax is calculated, capped so
    that the Subtotal never goes negative (1 point = ₹1 off).

    Returns a tuple: (customer_id, points_redeemed)
    """
    raw_id = input(
        f"\nEnter Customer ID / Phone (press Enter for '{DEFAULT_CUSTOMER}'): "
    ).strip()

    if raw_id == "" or raw_id.lower() == DEFAULT_CUSTOMER:
        return DEFAULT_CUSTOMER, 0

    customer_id = raw_id
    available_pts = loyalty_points.get(customer_id, 0)
    print(f"[Loyalty] Customer '{customer_id}' has {available_pts} loyalty point(s).")

    # Walk-in or 0 balance cannot redeem points
    if available_pts <= 0 or subtotal < 1.0:
        return customer_id, 0

    # Cap maximum redeemable points so Subtotal cannot go negative
    max_redeemable = min(available_pts, int(subtotal))
    choice = input(
        f"Would you like to redeem points on this bill? "
        f"(Max redeemable: {max_redeemable} pts = ₹{max_redeemable:.2f}) [y/N]: "
    ).strip().lower()

    if choice != "y":
        return customer_id, 0

    raw_pts = input(f"Enter points to redeem (0 to {max_redeemable}): ").strip()
    try:
        pts_to_redeem = int(raw_pts)
    except ValueError:
        print("[Warning] Non-numeric points entered. Proceeding with 0 points redeemed.")
        return customer_id, 0

    if pts_to_redeem < 0 or pts_to_redeem > max_redeemable:
        print(
            f"[Warning] Invalid amount ({pts_to_redeem}). Must be between 0 and "
            f"{max_redeemable}. Proceeding with 0 points redeemed."
        )
        return customer_id, 0

    return customer_id, pts_to_redeem


# ============================================================================
# CORE FEATURES 3 & 4 (+ STRETCH 6): CHECKOUT, BILL PRINTING & STOCK UPDATE
# ============================================================================
def checkout_and_print_bill(cart, inventory, eod_summary, loyalty_points):
    """
    Completes the sale by:
      1. Refusing empty carts or any item whose cart quantity exceeds stock.
      2. Handling optional customer loyalty point redemption pre-tax.
      3. Calculating exact Subtotal, Tax, and Grand Total.
      4. Reducing inventory stock by the quantity sold for each product.
      5. Awarding floor(grand_total / 100) loyalty points to registered customers.
      6. Updating the End-of-Day bill counter and revenue total.
      7. Printing the final itemized receipt and clearing the cart.
    """
    if not cart:
        print("\n[Error] Cannot checkout with an empty cart. Add items first!")
        return

    # Defensive stock verification: ensure no line would take stock negative
    for code, qty in cart.items():
        if code not in inventory:
            print(f"[Error] Product '{code}' no longer exists in inventory.")
            return
        if qty > inventory[code]["stock"]:
            print(
                f"[Error] Checkout refused! '{inventory[code]['name']}' requires "
                f"{qty} unit(s), but only {inventory[code]['stock']} in stock."
            )
            return

    # Step 1: Calculate itemized offer discounts and Subtotal (sum of line NETs)
    summary = calculate_cart_totals(cart, inventory)
    item_subtotal = summary["subtotal"]
    total_discount = summary["total_discount"]

    # Step 2: Handle loyalty customer identification & pre-tax redemption
    customer_id, points_redeemed = handle_loyalty_at_checkout(item_subtotal, loyalty_points)

    # 1 point = ₹1 off BEFORE tax, capped so subtotal never goes negative
    taxable_subtotal = round(item_subtotal - points_redeemed, 2)

    # Step 3: Calculate Tax and Grand Total
    tax_amount = round(TAX_RATE * taxable_subtotal, 2)
    grand_total = round(taxable_subtotal + tax_amount, 2)

    # Step 4: Deduct stock on completed sale (Core Feature 4)
    for code, qty in cart.items():
        inventory[code]["stock"] -= qty

    # Step 5: Update loyalty points balance (Stretch Feature 6)
    # floor(grand_total / 100) -> e.g. ₹315.00 earns 3 points
    points_earned = 0
    if customer_id != DEFAULT_CUSTOMER:
        points_earned = int(grand_total // 100)
        current_balance = loyalty_points.get(customer_id, 0)
        loyalty_points[customer_id] = current_balance - points_redeemed + points_earned

    # Step 6: Record completed bill in End-of-Day summary (Core Feature 5)
    eod_summary["total_bills"] += 1
    eod_summary["total_revenue"] = round(eod_summary["total_revenue"] + grand_total, 2)
    bill_number = eod_summary["total_bills"]

    # Step 7: Print formatted POS Receipt (Core Feature 3)
    print("\n" + "=" * 80)
    print("                        SWIFTCART SUPERMARKET — TAX INVOICE")
    print(f"  Bill No: #{bill_number:<10}                             Customer: {customer_id}")
    print("=" * 80)
    print(
        f"{'CODE':<6} | {'ITEM NAME':<28} | {'QTY':>4} | "
        f"{'UNIT (₹)':>9} | {'DISC (₹)':>9} | {'NET (₹)':>10}"
    )
    print("-" * 80)

    for line in summary["lines"]:
        short_name = line["name"][:28]
        print(
            f"{line['code']:<6} | {short_name:<28} | {line['qty']:>4} | "
            f"{line['unit_price']:>9.2f} | {line['discount']:>9.2f} | "
            f"{line['net']:>10.2f}"
        )

    print("-" * 80)
    print(f"{'Total Discount (Info Only - Already in Net):':>65} ₹{total_discount:>11.2f}")
    print(f"{'Subtotal (Sum of Item Net Amounts):':>65} ₹{item_subtotal:>11.2f}")

    if points_redeemed > 0:
        print(f"{'Less: Loyalty Points Redeemed (' + str(points_redeemed) + ' pts):':>65} -₹{points_redeemed:>10.2f}")
        print(f"{'Taxable Subtotal (After Points Redemption):':>65} ₹{taxable_subtotal:>11.2f}")

    print(f"{f'Tax ({TAX_RATE * 100:.0f}%):':>65} ₹{tax_amount:>11.2f}")
    print("=" * 80)
    print(f"{'GRAND TOTAL:':>65} ₹{grand_total:>11.2f}")
    print("=" * 80)

    if customer_id != DEFAULT_CUSTOMER:
        print(
            f"  [Loyalty Summary] Points Redeemed: {points_redeemed} | "
            f"Points Earned This Bill: {points_earned} | "
            f"New Balance: {loyalty_points[customer_id]} pts"
        )
        print("=" * 80)

    # Clear cart for the next customer in the queue
    cart.clear()
    print("[Success] Checkout complete! Inventory updated and cart cleared.")


# ============================================================================
# CORE FEATURE 5: END-OF-DAY SALES TOTAL & NUMBER OF BILLS
# ============================================================================
def show_eod_report(eod_summary, loyalty_points):
    """
    Displays the running count of completed bills and total sales revenue
    collected during the current session.
    """
    print("\n" + "=" * 54)
    print("            END-OF-DAY (EOD) SALES SUMMARY")
    print("=" * 54)
    print(f"  Total Bills Processed : {eod_summary['total_bills']}")
    print(f"  Total Sales Value     : ₹{eod_summary['total_revenue']:.2f}")
    print(f"  Registered Customers  : {len(loyalty_points)}")
    print("=" * 54)


# ============================================================================
# STRETCH FEATURE 7: LOW-STOCK REPORT
# ============================================================================
def show_low_stock_report(inventory):
    """
    Scans the entire inventory and lists every product whose current stock
    is at or below the global REORDER_LEVEL constant.
    """
    print("\n" + "=" * 72)
    print(f"          LOW-STOCK REPORT (Reorder Threshold: <= {REORDER_LEVEL} units)")
    print("=" * 72)

    low_stock_items = []
    for code, item in inventory.items():
        if item["stock"] <= REORDER_LEVEL:
            low_stock_items.append((code, item))

    if not low_stock_items:
        print("  All products are sufficiently stocked above the reorder level.")
        print("=" * 72)
        return

    print(f"{'CODE':<6} | {'PRODUCT NAME':<36} | {'STOCK':>7} | {'STATUS'}")
    print("-" * 72)
    for code, item in low_stock_items:
        status = "OUT OF STOCK!" if item["stock"] == 0 else "REORDER SOON"
        print(f"{code:<6} | {item['name']:<36} | {item['stock']:>7} | {status}")
    print("=" * 72)


# ============================================================================
# MAIN APPLICATION LOOP & MENU DISPATCHER
# ============================================================================
def print_main_menu():
    """Prints the exact POS operator menu specified by the project requirements."""
    print("\n" + "=" * 54)
    print("   SWIFTCART POS — BILLING & INVENTORY SYSTEM")
    print("=" * 54)
    print("1. Look up product by code & add to cart")
    print("2. View current cart & applied offers")
    print("3. Checkout & print bill")
    print("4. Show end-of-day sales total & number of bills")
    print("5. Low-stock report (Stretch)")
    print("6. Exit")
    print("-" * 54)


def main():
    """
    Entry point of the SwiftCart console application.
    Initializes state containers and runs an infinite menu loop that catches
    unexpected input errors so the terminal never crashes.
    """
    inventory = create_initial_inventory()
    cart = {}
    loyalty_points = {}
    eod_summary = {
        "total_bills": 0,
        "total_revenue": 0.0,
    }

    print("Welcome to SwiftCart POS! Pre-loaded 6 supermarket products.")

    while True:
        try:
            print_main_menu()
            choice = input("Select an option (1-6): ").strip()

            if choice == "1":
                look_up_and_add_to_cart(inventory, cart)
            elif choice == "2":
                view_cart(cart, inventory)
            elif choice == "3":
                checkout_and_print_bill(cart, inventory, eod_summary, loyalty_points)
            elif choice == "4":
                show_eod_report(eod_summary, loyalty_points)
            elif choice == "5":
                show_low_stock_report(inventory)
            elif choice == "6":
                print("\nClosing SwiftCart counter. Final End-of-Day snapshot:")
                show_eod_report(eod_summary, loyalty_points)
                print("Goodbye!")
                break
            else:
                print(
                    f"[Error] Invalid menu choice '{choice}'. "
                    "Please enter a number from 1 to 6."
                )

        except (EOFError, KeyboardInterrupt):
            # Gracefully handle Ctrl+C or Ctrl+D without printing a traceback
            print("\n\n[Info] Session interrupted by user. Exiting safely...")
            break


if __name__ == "__main__":
    main()