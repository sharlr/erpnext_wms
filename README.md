# ERPNext WMS - Warehouse Management System

Warehouse Management System app for ERPNext v16+.

## Modules

| Module | Doctypes |
| --- | --- |
| File Creation | File Creation, Import File, Import Item, Export File, Export Item, Shipping Line |
| WMS Warehouse | Warehouse Layout, Warehouse Location |
| WMS Finance | WMS Invoice, Invoice Item, Invoice Payment Item, Payment Voucher |
| WMS Inventory | Stock Adjustment, Adjustment Item |

## Features

- **Import / Export file management** — track goods from port to warehouse and back out
- **Stock Adjustments** — physical counts posted to the stock ledger as an ERPNext
  Stock Reconciliation, reversed automatically on cancel
- **WMS Invoicing** — aggregates submitted Payment Vouchers for a file, posts a
  Journal Entry against the customer receivable on submit
- **Payment Vouchers** — per-file vendor payment tracking
- **3D warehouse visualisation** — bin occupancy viewer at
  `/assets/erpnext_wms/warehouse-visualization.html`

## Installation

```bash
cd /home/frappe/frappe-bench
bench get-app https://github.com/sharlr/erpnext_wms.git
bench --site <your-site> install-app erpnext_wms
bench build --app erpnext_wms
```

`bench get-app` is required rather than a bare `git clone` into `apps/` — it
registers the app in `sites/apps.txt` and installs the Python package.

Installation creates three roles: **WMS User**, **WMS Finance**, **WMS Manager**.

## Requirements

- Frappe Framework v16.0.0+
- ERPNext v16.0.0+ (hard dependency — declared via `required_apps`; the app links
  to Item, Warehouse, Customer, Supplier, Company, Account and Journal Entry)
- Python 3.10+

## Not implemented yet

- Storage-charge rating. `erpnext_wms.tasks.generate_storage_charges` is wired to
  the daily scheduler but is currently a no-op.
- Workflows / approval routing.
- Serial and batch numbers in Stock Adjustment.
- three.js is loaded from a CDN by the visualisation page, so that page does not
  work on an air-gapped install.

## License

MIT
