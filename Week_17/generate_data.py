import pandas as pd
import numpy as np

# Generate sample warehouse data in KM and KM/HR
np.random.seed(42)
n_samples = 1000

# Distance: 0 to 0.5 km (0 to 500 meters)
distance_km = np.random.uniform(0.01, 10.0, n_samples)
# Speed: 0 to 40 km/hr
speed_kmhr = np.random.uniform(5.0, 40.0, n_samples)
# Object Detected sensor
object_detected = np.where(distance_km < 5.0, 1, np.random.choice([0, 1], n_samples, p=[0.7, 0.3]))

# Create DataFrame
df = pd.DataFrame({
    'distance_km': distance_km,
    'speed_kmhr': speed_kmhr,
    'object_detected': object_detected
})

# Save to CSV
df.to_csv('warehouse_data.csv', index=False)
print("warehouse_data.csv updated with KM and KM/HR units.")