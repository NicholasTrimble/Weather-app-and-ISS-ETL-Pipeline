import csv
import json

input_csv = "data/worldcities.csv"  
output_json = "static/cities.json"  

cities = []

# Load CSV
with open(input_csv, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        
        try:
            population = int(float(row.get("population") or 0))
        except:
            population = 0

        if population > 100000 or row.get("capital") in ["primary", "admin"]:  
           
            cities.append({
                "name": row["city"],
                "lat": float(row["lat"]),
                "lon": float(row["lng"]),
                "country": row["country"]
            })


cities.sort(key=lambda x: -x.get("population", 0))

# Limit to 1000 cities
cities = cities[:1000]

# Save
with open(output_json, "w", encoding="utf-8") as f:
    json.dump(cities, f, indent=2)

print(f"Saved {len(cities)} cities to {output_json}")

