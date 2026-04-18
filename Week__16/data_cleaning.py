import pandas as pd

# Load dataset
df = pd.read_csv("data/raw/iot_telemetry_data.csv")

print("Original Shape:", df.shape)

# Convert timestamp
df['ts'] = pd.to_numeric(df['ts'], errors='coerce')
df['ts'] = pd.to_datetime(df['ts'], unit='s')

# Convert motion column
df['motion'] = df['motion'].astype(str).map({'true':1, 'false':0})

# Convert numeric columns
cols = ['co','humidity','lpg','smoke','temp']

for col in cols:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# Remove duplicates
df = df.drop_duplicates()

# Handle missing values
df = df.fillna(df.mean(numeric_only=True))

# Save cleaned dataset
df.to_csv("data/processed/cleaned_iot_data.csv", index=False)

print("Cleaned Shape:", df.shape)
print("Data cleaning completed.")