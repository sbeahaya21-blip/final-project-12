"""Regenerate PDF invoices with integer quantities."""
import subprocess
import sys
from pathlib import Path

# Get the script directory
script_dir = Path(__file__).parent
script_path = script_dir / "generate_pdf_invoices.py"

print(f"Running: {script_path}")
print()

# Run the script
result = subprocess.run([sys.executable, str(script_path)], cwd=str(script_dir))

if result.returncode == 0:
    print("\n✅ PDFs regenerated successfully!")
    print(f"Check: {script_dir / 'sample_invoices' / 'pdf'}")
else:
    print("\n❌ Error regenerating PDFs")
    sys.exit(1)
