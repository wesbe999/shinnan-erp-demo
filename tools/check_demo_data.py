import json
from pathlib import Path

from app.services.demo_data import generate_all_demo_data

data = generate_all_demo_data()

out = Path(r"D:\Shinnan ERP\data\demo_data_snapshot.json")
out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

print("demo_data_generated")
print("areas:", len(data["areas"]))
print("buildings:", len(data["buildings"]))
print("customers:", len(data["customers"]))
print("billing_records:", len(data["billing_records"]))
print("dispatch_tickets:", len(data["dispatch_tickets"]))

print("sample_building:", data["buildings"][0])
print("sample_customer:", data["customers"][0])
print("sample_billing:", data["billing_records"][0])
print("sample_ticket:", data["dispatch_tickets"][0])
print("snapshot:", out)
