# CP-011 SwiftCart: Point-of-Sale Billing and Inventory System


## How to run
# If using Java track:
javac Main.java
java Main

# If using Python track:
python main.py

# If using C track:
gcc main.c -o main
./main

## Features that work
### Core Features (Compulsory)
1. Look up products by code and add them to the cart with quantity
2. Apply offers such as buy 2 get 1 free and a percentage discount on selected items
3. Print a bill with item lines, discounts, tax and grand total
4. Reduce stock for every sale and refuse items that are out of stock
5. Show end-of-day sales total and the number of bills

### Stretch Features (Optional)
6. Loyalty points earned per bill and redeemable on the next bill
7. Low-stock report for items below a reorder level

## Sample run
```text
====================================================
CP-011 SwiftCart: Point-of-Sale Billing & Inventory
====================================================
1. Look up product by code & add to cart
2. View current cart & applied offers
3. Checkout & print bill
4. Show end-of-day sales total & number of bills
5. Low-stock report (Stretch)
6. Exit
----------------------------------------------------
Enter choice: 1
Enter product code: P101
Product: Milk (1L) | Price: 60.00 | Stock: 20 | Offer: Buy 2 Get 1 Free
Enter quantity to add: 3
Added 3 x Milk (1L) to cart.

Enter choice: 1
Enter product code: P102
Product: Coffee (100g) | Price: 200.00 | Stock: 5 | Offer: 10% Discount
Enter quantity to add: 6
Error: Out of stock / insufficient quantity! Available stock is 5.

Enter choice: 1
Enter product code: P102
Product: Coffee (100g) | Price: 200.00 | Stock: 5 | Offer: 10% Discount
Enter quantity to add: 1
Added 1 x Coffee (100g) to cart.

Enter choice: 3
Enter customer loyalty points to redeem (Available: 0): 0

-------------------- BILL #1 -----------------------
Code   Item            Qty    Price   Discount    Net
P101   Milk (1L)         3    60.00     -60.00  120.00
       (Offer: Buy 2 Get 1 Free)
P102   Coffee (100g)     1   200.00     -20.00  180.00
       (Offer: 10% Discount)
----------------------------------------------------
Subtotal:                                       300.00
Total Discount:                                 -80.00
Tax (5%):                                        15.00
Grand Total:                                    315.00
----------------------------------------------------
Loyalty Points Earned on this Bill: 3
Stock updated: P101 (Remaining: 17), P102 (Remaining: 4)
----------------------------------------------------

Enter choice: 4
--- END-OF-DAY SALES SUMMARY ---
Number of bills: 1
End-of-day sales total: 315.00

Enter choice: 5
--- LOW-STOCK REPORT (Below Reorder Level: 5) ---
Code: P102 | Coffee (100g) | Current Stock: 4 | Reorder Level: 5

Enter choice: 6
Exiting SwiftCart.
```