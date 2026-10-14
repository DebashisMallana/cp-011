# 🛒 SwiftCart: Point-of-Sale Billing & Inventory System


**SwiftCart (CP-011)** is a dual-interface (Console & Web) Point-of-Sale (POS) billing and inventory management system designed for neighbourhood supermarkets. It eliminates manual billing bottlenecks at checkout counters by automating product lookups, promotional discount calculations, tax computation, receipt generation, and real-time stock synchronization.

---

## 📌 Problem Statement

A neighbourhood supermarket experiences long checkout queues because billing and stock tracking are handled manually. The store requires a fast, reliable counter system that processes customer carts rapidly while keeping product inventory accurate in real time.

---

## ✨ Features

### Core Features (Compulsory)
1. **Product Lookup & Cart Management:** Fast product lookup by unique product code (`SKU`) and addition to the active cart with customizable quantities.
2. **Dynamic Offer Engine:** Automated evaluation and application of promotional rules, including:
   - **Bundle Offers:** *Buy 2 Get 1 Free* (B2G1) on eligible items.
   - **Percentage Discounts:** Flat percentage markdowns (e.g., 10% or 20% off) on selected items.
3. **Itemized Bill Generation:** Generates a structured receipt displaying line items, unit prices, applied discounts, tax breakdown, and the final grand total.
4. **Real-Time Inventory Guardrails:** Automatically deducts sold quantities from inventory upon checkout and strictly blocks out-of-stock items or quantities exceeding available stock.
5. **End-of-Day (EOD) Sales Summary:** Displays consolidated daily metrics, including total revenue collected and the total number of bills generated.

### Stretch Features (Optional)
- **Customer Loyalty Program:** Calculates loyalty points earned per completed bill and allows customers to redeem accumulated points as a discount on subsequent purchases.
- **Low-Stock Reorder Report:** Flags and generates a report for all inventory items whose current stock has fallen below their configured minimum reorder threshold.

---

## 🏗️ System Architecture & Project Structure

SwiftCart separates its core billing and inventory business logic from the presentation layer so both the **Console Interface (CLI)** and **Web Interface** share the same single source of truth.

```text
swiftcart-pos/
├── core/
│   ├── inventory.py        # Stock lookup, validation, deduction, and low-stock reporting
│   ├── cart.py             # Cart state management and line-item aggregation
│   ├── offers.py           # Discount rules engine (B2G1, percentage discounts)
│   ├── billing.py          # Tax calculation, receipt formatting, and EOD ledger
│   └── loyalty.py          # Customer point accrual and redemption logic (Stretch)
├── cli/
│   └── main_cli.py         # Interactive terminal-based counter interface
├── web/
│   ├── app.py              # Web server & API routes
│   ├── static/             # CSS styles and client-side POS scripts
│   └── templates/          # Cashier dashboard, cart view, and EOD report UI
├── data/
│   ├── products.json       # Seed product catalog with initial stock & reorder levels
│   └── sales_ledger.json   # Persistent store for completed bills and EOD metrics
├── tests/
│   └── test_pos.py         # Unit tests for cart, offers, and inventory sync
├── requirements.txt        # Project dependencies
└── README.md               # Project documentation
```

---

## 📦 Sample Product Catalog

| Code | Product Name | Unit Price | Initial Stock | Reorder Level | Active Offer |
| :--- | :--- | :---: | :---: | :---: | :--- |
| `P101` | Whole Wheat Bread (400g) | ₹45.00 | 30 | 10 | None |
| `P102` | Arabica Coffee Jar (100g) | ₹250.00 | 15 | 5 | `15% OFF` |
| `P103` | Oat Milk Carton (1L) | ₹180.00 | 24 | 8 | `BUY_2_GET_1` |
| `P104` | Organic Honey (500g) | ₹320.00 | 12 | 4 | `10% OFF` |
| `P105` | Dark Chocolate Bar (80g) | ₹90.00 | 40 | 10 | `BUY_2_GET_1` |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.9+ (or Node.js 18+ depending on your runtime implementation)
- Modern web browser (for the Web POS interface)

### Installation

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/your-username/swiftcart-pos.git](https://github.com/your-username/swiftcart-pos.git)
   cd swiftcart-pos
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

#### Option 1: Console Interface (CLI)
Run the interactive terminal interface for rapid keyboard-only counter billing:
```bash
python -m cli.main_cli
```

#### Option 2: Web Interface
Launch the browser-based POS dashboard:
```bash
python -m web.app
```
Open `http://localhost:5000` in your browser to access the cashier counter, inventory table, and End-of-Day dashboard.

---

## 🧾 Sample Bill Output (Console)

```text
============================================================
                 SWIFTCART SUPERMARKET POS                  
Bill No: INV-2026-0042             Date: 14-Oct-2026 11:40
============================================================
Code   Item                  Qty    Price   Discount   Total
------------------------------------------------------------
P103   Oat Milk Carton (1L)   3    180.00   -180.00   360.00
       [Offer Applied: Buy 2 Get 1 Free]
P102   Arabica Coffee (100g)  1    250.00    -37.50   212.50
       [Offer Applied: 15% Off]
P101   Whole Wheat Bread      2     45.00      0.00    90.00
------------------------------------------------------------
Subtotal (Gross):                                    ₹880.00
Total Discounts Saved:                              -₹217.50
Taxable Amount:                                      ₹662.50
GST (5%):                                             ₹33.13
Loyalty Points Redeemed:                              -₹0.00
------------------------------------------------------------
GRAND TOTAL:                                         ₹695.63
============================================================
Loyalty Points Earned on this Bill: 6 pts
Thank you for shopping at SwiftCart!
============================================================
```

---

## 💡 Architecture & Interview Talking Points

### 1. Cart Handling
- **Idempotent Item Addition:** Adding the same product code multiple times in a single session increments the existing line item's quantity rather than creating duplicate rows.
- **Pre-Check Validation:** Every cart addition or quantity update checks `(current_cart_qty + requested_qty) <= available_stock` immediately, giving the cashier instant feedback before checkout.
- **Session Isolation:** Unbilled carts hold temporary reservations or validate at checkout so cancelled transactions never corrupt actual inventory counts.

### 2. Applying Offer Rules
- **Extensible Rule Evaluation:** Promotions are decoupled from core item pricing using a rule-evaluation pipeline:
  - **Buy 2 Get 1 Free (`B2G1`):** For every group of 3 identical items (`free_units = quantity // 3`), 1 unit's price is deducted as a line-item discount. If a customer buys 6 units, 2 units are free.
  - **Percentage Discount:** Computes `discount = (unit_price * quantity) * (discount_pct / 100)` with standard two-decimal rounding.
- **Tax Calculation Order:** Discounts are deducted from the gross line-item subtotal *before* computing tax (net-price taxation), ensuring accurate compliance and transparent savings on the customer receipt.

### 3. Keeping Inventory in Sync with Sales
- **Atomic Checkout Commit:** Stock is only permanently deducted when a bill transitions to `COMPLETED`. The checkout transaction verifies stock availability across all cart items, decrements quantities, appends the bill to the daily ledger, and triggers low-stock alerts in a single atomic operation.
- **Out-of-Stock Guardrails:** Products with `stock == 0` are blocked at lookup, and attempts to purchase quantities greater than remaining stock return a clear error displaying the maximum available units.
- **Low-Stock Threshold Monitoring:** Immediately after stock deduction, any item where `current_stock <= reorder_level` is flagged in the Low-Stock Report for store restocking.

---

## 🧪 Testing Scenarios

| Test Case | Input / Action | Expected System Behaviour |
| :--- | :--- | :--- |
| **Valid Lookup & Add** | Enter code `P101`, Qty `2` | Adds 2 units of Whole Wheat Bread (`₹90.00`) to cart. |
| **B2G1 Offer Trigger** | Enter code `P103`, Qty `3` | Charges for 2 units (`₹360.00`), applies `₹180.00` discount. |
| **Out-of-Stock Refusal** | Request Qty `20` for `P104` (Stock: `12`) | Rejects addition with alert: *"Insufficient stock. Available: 12"*. |
| **Stock Deduction** | Complete checkout for `2` units of `P101` | `P101` stock decreases from `30` to `28` across both CLI and Web views. |
| **EOD Reconciliation** | Process 3 bills and open EOD summary | Displays `Total Bills: 3` and exact sum of all 3 grand totals. |

---

## 📄 License

This project is created for educational and assessment purposes under the **E-Commerce and Retail Foundation (CP-011)** curriculum.