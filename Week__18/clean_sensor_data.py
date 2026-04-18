
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import os

# ─────────────────────────────────────────────
# STEP 1: LOAD DATA
# ─────────────────────────────────────────────
print("=" * 55)
print("  STEP 1: Loading Data")
print("=" * 55)

df = pd.read_csv("data/proximity_sensor_data.csv", parse_dates=["timestamp"])
print(f"✅ Loaded {df.shape[0]} rows × {df.shape[1]} columns\n")
print(df.head(10).to_string())

# ─────────────────────────────────────────────
# STEP 2: EXPLORE & PROFILE
# ─────────────────────────────────────────────
print("\n" + "=" * 55)
print("  STEP 2: Data Profiling")
print("=" * 55)

print("\n📋 Data Types:")
print(df.dtypes)

print("\n📊 Basic Statistics:")
print(df.describe())

print("\n❓ Missing Values:")
missing = df.isnull().sum()
missing_pct = (missing / len(df) * 100).round(2)
missing_report = pd.DataFrame({"Missing Count": missing, "Missing %": missing_pct})
print(missing_report[missing_report["Missing Count"] > 0])

print(f"\n🔁 Duplicate Rows: {df.duplicated().sum()}")

# ─────────────────────────────────────────────
# STEP 3: HANDLE MISSING VALUES
# ─────────────────────────────────────────────
print("\n" + "=" * 55)
print("  STEP 3: Handling Missing Values")
print("=" * 55)

df_clean = df.copy()

# Drop rows where both sensor_id AND location are missing (unusable records)
critical_missing = df_clean["sensor_id"].isnull() & df_clean["location"].isnull()
dropped = critical_missing.sum()
df_clean = df_clean[~critical_missing].reset_index(drop=True)
print(f"🗑️  Dropped {dropped} rows with missing sensor_id AND location")

# Fill distance_cm with per-sensor median (robust against remaining outliers)
df_clean["distance_cm"] = df_clean.groupby("sensor_id")["distance_cm"].transform(
    lambda x: x.fillna(x.median())
)
print("✅ Filled distance_cm missing values using per-sensor median")

# Fill temperature_c with forward-fill then backward-fill per sensor
df_clean["temperature_c"] = df_clean.groupby("sensor_id")["temperature_c"].transform(
    lambda x: x.ffill().bfill()
)
print("✅ Filled temperature_c using forward/backward fill per sensor")

# Fill humidity_pct with overall column median
humidity_median = df_clean["humidity_pct"].median()
df_clean["humidity_pct"] = df_clean["humidity_pct"].fillna(humidity_median)
print(f"✅ Filled humidity_pct missing values with median: {humidity_median:.1f}%")

print(f"\n✅ Remaining missing values: {df_clean.isnull().sum().sum()}")

# ─────────────────────────────────────────────
# STEP 4: DETECT & HANDLE OUTLIERS
# ─────────────────────────────────────────────
print("\n" + "=" * 55)
print("  STEP 4: Detecting & Handling Outliers")
print("=" * 55)

# Sensor valid range: proximity sensors typically read 2–400 cm
SENSOR_MIN = 2.0
SENSOR_MAX = 400.0

outliers_mask = (df_clean["distance_cm"] < SENSOR_MIN) | (df_clean["distance_cm"] > SENSOR_MAX)
outlier_count = outliers_mask.sum()
print(f"⚠️  Found {outlier_count} out-of-range distance readings")
print(f"    Valid range: {SENSOR_MIN}–{SENSOR_MAX} cm")
print(df_clean[outliers_mask][["timestamp", "sensor_id", "distance_cm"]].to_string())

# Save sensor_id before groupby (groupby drops the key column)
sensor_ids = df_clean["sensor_id"].copy()

def replace_outliers_with_median(group):
    valid_mask = (group["distance_cm"] >= SENSOR_MIN) & (group["distance_cm"] <= SENSOR_MAX)
    valid_median = group.loc[valid_mask, "distance_cm"].median()
    group = group.copy()
    group.loc[~valid_mask, "distance_cm"] = valid_median
    return group

df_clean = df_clean.groupby("sensor_id", group_keys=False).apply(replace_outliers_with_median)
df_clean["sensor_id"] = sensor_ids.values  # restore sensor_id
print(f"\n✅ Replaced {outlier_count} outliers with per-sensor median of valid readings")

# IQR check for temperature
Q1 = df_clean["temperature_c"].quantile(0.25)
Q3 = df_clean["temperature_c"].quantile(0.75)
IQR = Q3 - Q1
temp_outliers = df_clean[
    (df_clean["temperature_c"] < Q1 - 1.5 * IQR) |
    (df_clean["temperature_c"] > Q3 + 1.5 * IQR)
]
print(f"📐 IQR check on temperature: {len(temp_outliers)} outliers found")

# ─────────────────────────────────────────────
# STEP 5: FIX DATA QUALITY ISSUES
# ─────────────────────────────────────────────
print("\n" + "=" * 55)
print("  STEP 5: Fixing Data Quality Issues")
print("=" * 55)

df_clean["status"] = df_clean["status"].str.lower().str.strip()
print("✅ Normalized 'status' column to lowercase")

before = len(df_clean)
df_clean = df_clean.drop_duplicates().reset_index(drop=True)
print(f"✅ Removed {before - len(df_clean)} duplicate rows")

df_clean = df_clean.sort_values("timestamp").reset_index(drop=True)
print("✅ Sorted data by timestamp")

for col in ["distance_cm", "temperature_c", "humidity_pct"]:
    df_clean[col] = df_clean[col].round(2)
print("✅ Rounded numeric columns to 2 decimal places")

# Reorder columns nicely
df_clean = df_clean[["timestamp", "sensor_id", "distance_cm", "temperature_c", "humidity_pct", "location", "status"]]

# ─────────────────────────────────────────────
# STEP 6: EXPORT
# ─────────────────────────────────────────────
print("\n" + "=" * 55)
print("  STEP 6: Saving Cleaned Data")
print("=" * 55)

os.makedirs("output", exist_ok=True)
df_clean.to_csv("output/proximity_sensor_cleaned.csv", index=False)
print("✅ Cleaned data saved to: output/proximity_sensor_cleaned.csv")

print("\n" + "=" * 55)
print("  FINAL SUMMARY")
print("=" * 55)
print(f"  Original rows  : {len(df)}")
print(f"  Cleaned rows   : {len(df_clean)}")
print(f"  Rows removed   : {len(df) - len(df_clean)}")
print(f"\n✅ All cleaning steps completed successfully!")
print("\nCleaned Data Preview:")
print(df_clean.to_string())

# ─────────────────────────────────────────────
# BONUS: VISUALIZATIONS
# ─────────────────────────────────────────────
print("\n📊 Generating visualizations...")

fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle("IoT Proximity Sensor Data – Cleaning Report", fontsize=14, fontweight="bold")

# Plot 1: Distance over time
for sensor in df_clean["sensor_id"].dropna().unique():
    subset = df_clean[df_clean["sensor_id"] == sensor]
    axes[0, 0].plot(subset["timestamp"], subset["distance_cm"], label=sensor, marker="o", markersize=3)
axes[0, 0].set_title("Distance Readings Over Time (Cleaned)")
axes[0, 0].set_ylabel("Distance (cm)")
axes[0, 0].legend()
axes[0, 0].tick_params(axis="x", rotation=30)

# Plot 2: Missing values heatmap (original)
missing_matrix = df.isnull().astype(int)
sns.heatmap(missing_matrix, ax=axes[0, 1], cbar=False, cmap="Reds", yticklabels=False)
axes[0, 1].set_title("Missing Values – Original Data (Red = Missing)")

# Plot 3: Boxplot before/after
axes[1, 0].boxplot(
    [df["distance_cm"].dropna(), df_clean["distance_cm"]],
    labels=["Before", "After"]
)
axes[1, 0].set_title("Distance (cm) – Before vs After Outlier Removal")
axes[1, 0].set_ylabel("Distance (cm)")

# Plot 4: Records per sensor
df_clean["sensor_id"].value_counts().plot(kind="bar", ax=axes[1, 1], color=["#4C72B0","#DD8452","#55A868"])
axes[1, 1].set_title("Records per Sensor (Cleaned)")
axes[1, 1].set_ylabel("Count")
axes[1, 1].tick_params(axis="x", rotation=0)

plt.tight_layout()
plt.savefig("output/cleaning_report.png", dpi=150)
print("✅ Visualization saved to: output/cleaning_report.png")
