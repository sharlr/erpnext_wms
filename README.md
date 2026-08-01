# ERPNext WMS - Warehouse Management System

Complete Warehouse Management System for ERPNext v16+

## Features

- **Import File Management** - Track goods from port to warehouse
- **Export File Management** - Track goods from warehouse to customer
- **Stock Adjustments** - Handle inventory variances
- **WMS Invoicing** - Generate bills for customers
- **Payment Vouchers** - Track payments
- **Auto-numbering** - Automatic document numbering
- **Workflows** - Automated approval processes
- **Data Validation** - Real-time validation

## Installation

```bash
cd /home/frappe/frappe-bench/apps
git clone https://github.com/sharlr/erpnext_wms.git
cd ..
bench install-app erpnext_wms
bench migrate
```

## Requirements

- ERPNext v16.0.0+
- Frappe Framework v16.0.0+
- Python 3.7+

## License

MIT
