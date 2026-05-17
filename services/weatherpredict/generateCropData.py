import pandas as pd
from pathlib import Path

def generate_rice_process_csv():
    data = {
        "Stage": ["Seedbed Preparation", "Transplanting", "Tillering", "Panicle Initiation", "Ripening & Drying"],
        "Days": ["1-25", "25-30", "30-70", "70-100", "100-140"],
        "Process_Description": [
            "Soak seeds for 24h then sow in nursery",
            "Move 25-day seedlings to puddled main field",
            "Active branching and root development",
            "Reproductive phase; grain heads begin forming",
            "Grains turn golden; drain field 10 days before"
        ],
        "Water_Quantity_cm": ["Saturated Soil", "2-5cm", "5cm", "5-7cm", "0cm (Drain)"],
        "Fertilizer_Standard": [
            "5kg Organic Compost / 10sq.m",
            "1kg Urea + 500g DAP per decimal",
            "400g MOP (Potash) per decimal",
            "NPK Top Dressing",
            "None"
        ],
        "Ideal_Temp_C": [30, 28, 30, 25, 22]
    }
    
    df = pd.DataFrame(data)
    static_folder = Path(__file__).parent.parent.parent / "static"
    static_folder.mkdir(exist_ok=True)
    df.to_csv(static_folder / "rice_full_process.csv", index=False)
    print("Success: rice_full_process.csv created in static folder!")

if __name__ == "__main__":
    generate_rice_process_csv()