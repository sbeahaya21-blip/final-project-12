"""Example script demonstrating the Invoice Parser and Anomaly Detection system."""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"


def create_invoice(vendor_name, invoice_number, items, total_amount):
    """Helper function to create an invoice."""
    invoice_data = {
        "vendor_name": vendor_name,
        "invoice_number": invoice_number,
        "invoice_date": datetime.now().isoformat(),
        "total_amount": total_amount,
        "items": items,
        "currency": "USD"
    }
    
    response = requests.post(f"{BASE_URL}/api/invoices/create", json=invoice_data)
    response.raise_for_status()
    return response.json()


def analyze_invoice(invoice_id):
    """Helper function to analyze an invoice."""
    response = requests.post(f"{BASE_URL}/api/invoices/{invoice_id}/analyze")
    response.raise_for_status()
    return response.json()


def main():
    """Demonstrate the system with example invoices."""
    print("=" * 60)
    print("Invoice Parser & Anomaly Detection - Example Usage")
    print("=" * 60)
    
    # Create historical invoice (normal pricing)
    print("\n1. Creating historical invoice with normal pricing...")
    historical_invoice = create_invoice(
        vendor_name="Vendor ABC",
        invoice_number="INV-HIST-001",
        items=[
            {
                "name": "Product X",
                "quantity": 10.0,
                "unit_price": 50.0,  # $50 per unit
                "total_price": 500.0
            },
            {
                "name": "Product Y",
                "quantity": 5.0,
                "unit_price": 100.0,
                "total_price": 500.0
            }
        ],
        total_amount=1000.0
    )
    print(f"   ✓ Created invoice: {historical_invoice['id']}")
    
    # Analyze historical invoice (should be low risk - first invoice)
    analysis = analyze_invoice(historical_invoice['id'])
    print(f"   Risk Score: {analysis['risk_score']}/100")
    print(f"   Suspicious: {analysis['is_suspicious']}")
    
    # Create suspicious invoice (price increase)
    print("\n2. Creating suspicious invoice with price increase...")
    suspicious_invoice = create_invoice(
        vendor_name="Vendor ABC",  # Same vendor
        invoice_number="INV-SUSP-001",
        items=[
            {
                "name": "Product X",
                "quantity": 10.0,
                "unit_price": 100.0,  # 100% price increase!
                "total_price": 1000.0
            }
        ],
        total_amount=1000.0
    )
    print(f"   ✓ Created invoice: {suspicious_invoice['id']}")
    
    # Analyze suspicious invoice
    analysis = analyze_invoice(suspicious_invoice['id'])
    print(f"\n   ⚠️  ANALYSIS RESULTS:")
    print(f"   Risk Score: {analysis['risk_score']}/100")
    print(f"   Suspicious: {analysis['is_suspicious']}")
    print(f"\n   Explanation:")
    print(f"   {analysis['explanation']}")
    
    if analysis['anomalies']:
        print(f"\n   Detected Anomalies:")
        for i, anomaly in enumerate(analysis['anomalies'], 1):
            print(f"   {i}. {anomaly['type']}: {anomaly['description']}")
    
    # Create invoice with new item
    print("\n3. Creating invoice with new item...")
    new_item_invoice = create_invoice(
        vendor_name="Vendor ABC",
        invoice_number="INV-NEW-001",
        items=[
            {
                "name": "Product X",
                "quantity": 10.0,
                "unit_price": 50.0,
                "total_price": 500.0
            },
            {
                "name": "Product Z - NEW",  # New item never seen before
                "quantity": 10.0,
                "unit_price": 200.0,
                "total_price": 2000.0
            }
        ],
        total_amount=2500.0
    )
    print(f"   ✓ Created invoice: {new_item_invoice['id']}")
    
    analysis = analyze_invoice(new_item_invoice['id'])
    print(f"\n   ⚠️  ANALYSIS RESULTS:")
    print(f"   Risk Score: {analysis['risk_score']}/100")
    print(f"   Suspicious: {analysis['is_suspicious']}")
    print(f"\n   Explanation:")
    print(f"   {analysis['explanation']}")
    
    print("\n" + "=" * 60)
    print("Example completed!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the API.")
        print("Please make sure the server is running:")
        print("  uvicorn app.main:app --reload")
        print("  or")
        print("  python run.py")
    except Exception as e:
        print(f"Error: {e}")
