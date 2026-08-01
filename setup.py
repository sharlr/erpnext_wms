from setuptools import setup, find_packages

setup(
    name="erpnext_wms",
    version="1.0.0",
    description="ERPNext Warehouse Management System",
    author="ERPNext WMS",
    author_email="support@erpnext-wms.com",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "frappe>=16.0.0"
    ]
)
