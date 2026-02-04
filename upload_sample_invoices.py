"""Quick script to upload sample invoices from JSON files."""
import requests
import json
import os
from pathlib import Path

BASE_URL = "http://localhost:8000/api"
SAMPLE_DIR = Path("sample_invoices")

def upload_invoice_file(file_path):
    """Upload an invoice from a JSON file."""
    try:
        with open(file_path, 'r') as f:
            invoice_data = json.load(f)
        
        response = requests.post(f"{BASE_URL}/invoices/create", json=invoice_data)
        response.raise_for_status()
        invoice = response.json()
        
        print(f"✓ Uploaded: {file_path.name}")
        print(f"  Invoice #: {invoice['parsed_data']['invoice_number']}")
        print(f"  Amount: ${invoice['parsed_data']['total_amount']:.2f}")
        
        return invoice
    except Exception as e:
        print(f"✗ Error uploading {file_path.name}: {e}")
        return None

def analyze_invoice(invoice_id):
    """Analyze an invoice."""
    try:
        response = requests.post(f"{BASE_URL}/invoices/{invoice_id}/analyze")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"✗ Error analyzing: {e}")
        return None

def main():
    """Upload all sample invoices."""
    print("=" * 60)
    print("Uploading Sample Invoices")
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
    
    # Get all JSON files
    json_files = sorted(SAMPLE_DIR.glob("*.json"))
    
    if not json_files:
        print(f"⚠️  No JSON files found in {SAMPLE_DIR}")
        return
    
    print(f"Found {len(json_files)} invoice file(s)\n")
    
    invoices = []
    
    # Upload normal invoices first (1-5)
    normal_files = [f for f in json_files if "ANOMALOUS" not in f.name]
    anomalous_files = [f for f in json_files if "ANOMALOUS" in f.name]
    
    print("📄 Uploading Normal Invoices...")
    print("-" * 60)
    for file_path in sorted(normal_files):
        invoice = upload_invoice_file(file_path)
        if invoice:
            invoices.append(invoice)
        print()
    
    # Upload anomalous invoice last
    if anomalous_files:
        print("⚠️  Uploading Anomalous Invoice...")
        print("-" * 60)
        for file_path in anomalous_files:
            invoice = upload_invoice_file(file_path)
            if invoice:
                invoices.append(invoice)
                print()
                
                # Analyze the anomalous invoice
                print("🔍 Analyzing anomalous invoice...")
                analysis = analyze_invoice(invoice['id'])
                if analysis:
                    print(f"\n📊 Results:")
                    print(f"   Risk Score: {analysis['risk_score']}/100")
                    print(f"   Suspicious: {'⚠️ YES' if analysis['is_suspicious'] else '✓ NO'}")
                    print(f"   Anomalies: {len(analysis['anomalies'])}")
                    if analysis['anomalies']:
                        print(f"\n   Detected:")
                        for anomaly in analysis['anomalies']:
                            print(f"   - {anomaly['type'].replace('_', ' ').title()}: {anomaly['description']}")
                print()
    
    print("=" * 60)
    print(f"✅ Successfully uploaded {len(invoices)} invoice(s)")
    print("=" * 60)
    print("\nView invoices at: http://localhost:8000/invoices")

if __name__ == "__main__":
    main()
