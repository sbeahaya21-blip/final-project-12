"""Script to create sample invoices for testing."""
import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000/api"

def create_invoice(invoice_data):
    """Create an invoice via API."""
    try:
        response = requests.post(f"{BASE_URL}/invoices/create", json=invoice_data)
        response.raise_for_status()
        invoice = response.json()
        print(f"✓ Created invoice: {invoice['parsed_data']['invoice_number']} - ${invoice['parsed_data']['total_amount']:.2f}")
        return invoice
    except Exception as e:
        print(f"✗ Error creating invoice: {e}")
        return None

def analyze_invoice(invoice_id):
    """Analyze an invoice for anomalies."""
    try:
        response = requests.post(f"{BASE_URL}/invoices/{invoice_id}/analyze")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"✗ Error analyzing invoice: {e}")
        return None

def main():
    """Create sample invoices."""
    print("=" * 60)
    print("Creating Sample Invoices for Testing")
    print("=" * 60)
    print()
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL.replace('/api', '')}/health", timeout=2)
        if response.status_code != 200:
            print("⚠️  Backend server is not running!")
            print("Please start the server first: python run.py")
            return
    except:
        print("⚠️  Backend server is not running!")
        print("Please start the server first: python run.py")
        return
    
    vendor_name = "ABC Supplies Co."
    base_date = datetime.now() - timedelta(days=30)
    
    # Normal invoices (5 invoices with similar but slightly different details)
    print("\n📄 Creating 5 Normal Invoices (Same Supplier)...")
    print("-" * 60)
    
    normal_invoices = []
    
    # Invoice 1 - Normal
    invoice1 = create_invoice({
        "vendor_name": vendor_name,
        "invoice_number": "INV-2024-001",
        "invoice_date": (base_date + timedelta(days=1)).isoformat(),
        "total_amount": 1250.00,
        "items": [
            {"name": "Office Chairs", "quantity": 5.0, "unit_price": 150.0, "total_price": 750.0},
            {"name": "Desk Lamps", "quantity": 10.0, "unit_price": 50.0, "total_price": 500.0}
        ],
        "currency": "USD"
    })
    if invoice1:
        normal_invoices.append(invoice1)
    
    # Invoice 2 - Normal (slightly different quantities)
    invoice2 = create_invoice({
        "vendor_name": vendor_name,
        "invoice_number": "INV-2024-002",
        "invoice_date": (base_date + timedelta(days=5)).isoformat(),
        "total_amount": 1300.00,
        "items": [
            {"name": "Office Chairs", "quantity": 6.0, "unit_price": 150.0, "total_price": 900.0},
            {"name": "Desk Lamps", "quantity": 8.0, "unit_price": 50.0, "total_price": 400.0}
        ],
        "currency": "USD"
    })
    if invoice2:
        normal_invoices.append(invoice2)
    
    # Invoice 3 - Normal
    invoice3 = create_invoice({
        "vendor_name": vendor_name,
        "invoice_number": "INV-2024-003",
        "invoice_date": (base_date + timedelta(days=10)).isoformat(),
        "total_amount": 1200.00,
        "items": [
            {"name": "Office Chairs", "quantity": 4.0, "unit_price": 150.0, "total_price": 600.0},
            {"name": "Desk Lamps", "quantity": 12.0, "unit_price": 50.0, "total_price": 600.0}
        ],
        "currency": "USD"
    })
    if invoice3:
        normal_invoices.append(invoice3)
    
    # Invoice 4 - Normal
    invoice4 = create_invoice({
        "vendor_name": vendor_name,
        "invoice_number": "INV-2024-004",
        "invoice_date": (base_date + timedelta(days=15)).isoformat(),
        "total_amount": 1275.00,
        "items": [
            {"name": "Office Chairs", "quantity": 5.0, "unit_price": 150.0, "total_price": 750.0},
            {"name": "Desk Lamps", "quantity": 10.5, "unit_price": 50.0, "total_price": 525.0}
        ],
        "currency": "USD"
    })
    if invoice4:
        normal_invoices.append(invoice4)
    
    # Invoice 5 - Normal
    invoice5 = create_invoice({
        "vendor_name": vendor_name,
        "invoice_number": "INV-2024-005",
        "invoice_date": (base_date + timedelta(days=20)).isoformat(),
        "total_amount": 1280.00,
        "items": [
            {"name": "Office Chairs", "quantity": 5.0, "unit_price": 150.0, "total_price": 750.0},
            {"name": "Desk Lamps", "quantity": 10.6, "unit_price": 50.0, "total_price": 530.0}
        ],
        "currency": "USD"
    })
    if invoice5:
        normal_invoices.append(invoice5)
    
    print(f"\n✓ Created {len(normal_invoices)} normal invoices")
    
    # Anomalous Invoice (6th invoice with multiple anomalies)
    print("\n⚠️  Creating Anomalous Invoice (Should Trigger Alerts)...")
    print("-" * 60)
    
    anomalous_invoice = create_invoice({
        "vendor_name": vendor_name,
        "invoice_number": "INV-2024-006",
        "invoice_date": datetime.now().isoformat(),
        "total_amount": 3500.00,  # Much higher than normal (~1250)
        "items": [
            {"name": "Office Chairs", "quantity": 5.0, "unit_price": 250.0, "total_price": 1250.0},  # Price increased from 150 to 250 (67% increase)
            {"name": "Desk Lamps", "quantity": 25.0, "unit_price": 50.0, "total_price": 1250.0},  # Quantity much higher (normal is ~10)
            {"name": "Premium Monitor Stand", "quantity": 5.0, "unit_price": 200.0, "total_price": 1000.0}  # New item never seen before
        ],
        "currency": "USD"
    })
    
    if anomalous_invoice:
        print("\n🔍 Analyzing Anomalous Invoice...")
        analysis = analyze_invoice(anomalous_invoice['id'])
        
        if analysis:
            print(f"\n📊 Analysis Results:")
            print(f"   Risk Score: {analysis['risk_score']}/100")
            print(f"   Suspicious: {'⚠️ YES' if analysis['is_suspicious'] else '✓ NO'}")
            print(f"   Anomalies Detected: {len(analysis['anomalies'])}")
            print(f"\n   Explanation:")
            for line in analysis['explanation'].split('\n'):
                print(f"   {line}")
            
            if analysis['anomalies']:
                print(f"\n   Detected Anomalies:")
                for i, anomaly in enumerate(analysis['anomalies'], 1):
                    print(f"   {i}. {anomaly['type'].replace('_', ' ').title()}")
                    if anomaly.get('item_name'):
                        print(f"      Item: {anomaly['item_name']}")
                    print(f"      {anomaly['description']}")
    
    print("\n" + "=" * 60)
    print("✅ Sample invoices created successfully!")
    print("=" * 60)
    print("\nYou can now:")
    print("1. View invoices at: http://localhost:8000/invoices")
    print("2. Upload more invoices via the UI")
    print("3. Test the anomaly detection system")

if __name__ == "__main__":
    main()
