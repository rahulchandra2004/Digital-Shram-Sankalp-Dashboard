import pandas as pd
import numpy as np
import random
import os
from datetime import datetime, timedelta
import os

def generate_mock_data(num_records=10000):
    np.random.seed(42)
    random.seed(42)

    # Base data definitions
    states = ["Andhra Pradesh", "Bihar", "Jharkhand", "Maharashtra", "Uttar Pradesh", "Tamil Nadu", "Gujarat", "Karnataka", "West Bengal", "Odisha"]
    sectors = ["Construction", "Gig Worker", "Agriculture", "Manufacturing", "Domestic Worker"]
    skills = ["Unskilled", "Semi-skilled", "Skilled", "Highly-skilled"]
    schemes = ["PM-SYM", "eShram", "Ayushman Bharat", "None", "PM-Kisan"]
    
    # Temporal base setup (last 24 months)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=730)
    
    data = []
    
    for i in range(num_records):
        # MOCK-UAN-XXXX-1234
        uan_part1 = f"{random.randint(1000, 9999)}"
        uan_part2 = f"{random.randint(1000, 9999)}"
        uan = f"MOCK-UAN-{uan_part1}-{uan_part2}"
        age = random.randint(18, 65)
        state_origin = random.choice(states)
        
        # 60% chance to migrate
        if random.random() < 0.6:
            state_current = random.choice([s for s in states if s != state_origin])
        else:
            state_current = state_origin
            
        sector = random.choice(sectors)
        skill = random.choice(skills)
        scheme = random.choice(schemes)
        
        # Base daily wage based on skill and sector
        base_wage = 300
        if skill == "Semi-skilled": base_wage += 150
        elif skill == "Skilled": base_wage += 300
        elif skill == "Highly-skilled": base_wage += 600
        
        if sector == "Gig Worker": base_wage += 100
        elif sector == "Construction": base_wage += 50
        
        # Temporal Registration Date (Add seasonal spikes in April-June)
        random_days = random.randint(0, 730)
        reg_date = start_date + timedelta(days=random_days)
        # 20% chance to artificially force date into harvest/summer migration months (April, May, June)
        if random.random() < 0.2:
            year = random.choice([end_date.year, end_date.year - 1])
            month = random.choice([4, 5, 6])
            day = random.randint(1, 28)
            reg_date = datetime(year, month, day)
        
        # Add some noise
        wage = max(100, int(np.random.normal(base_wage, 50)))
        
        data.append([uan, age, state_origin, state_current, sector, wage, skill, scheme, reg_date.strftime('%Y-%m-%d')])

    df = pd.DataFrame(data, columns=[
        "UAN", "Age", "State_Origin", "State_Current", "Occupation_Sector", "Daily_Wage", "Skill_Level", "Scheme_Enrolled", "Registration_Date"
    ])
    
    # ---------------------------------------------------------
    # INJECT ANOMALIES (approx 5% of data)
    # ---------------------------------------------------------
    num_anomalies = int(num_records * 0.05)
    anomaly_indices = random.sample(range(num_records), num_anomalies)
    
    for idx in anomaly_indices:
        anomaly_type = random.choice(["extreme_wage", "impossible_age_skill", "negative_age"])
        
        if anomaly_type == "extreme_wage":
            # Very high or very low wage
            if random.random() > 0.5:
                df.at[idx, "Daily_Wage"] = random.randint(5000, 20000) # Unlikely high
            else:
                df.at[idx, "Daily_Wage"] = random.randint(1, 10) # Unlikely low
                
        elif anomaly_type == "impossible_age_skill":
            # Highly skilled but very young
            df.at[idx, "Age"] = random.randint(14, 18)
            df.at[idx, "Skill_Level"] = "Highly-skilled"
            df.at[idx, "Daily_Wage"] = 2500
            
        elif anomaly_type == "negative_age":
            # Negative age (data entry error)
            df.at[idx, "Age"] = -random.randint(1, 5)

    return df

if __name__ == "__main__":
    output_path = "workers_data.csv"
    print("Generating 10,000 records of synthetic worker data...")
    df = generate_mock_data(10000)
    df.to_csv(output_path, index=False)
    print(f"Data successfully saved to {output_path}")
