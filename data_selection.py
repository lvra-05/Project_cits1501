import re
import numpy as np
import pandas as pd

# 1. Load the raw original dataset
df = pd.read_csv("austlang.csv")

# 2. Define the 8 main regions (excluding multiple borders)
single_regions = ["QLD", "NT", "WA", "NSW", "VIC", "SA", "TAS", "TSI"]
df_main = df[df["state_territory"].isin(single_regions)].copy()

# 3. Calculate proportional distribution for a total of 250 records
total_target = 250
counts = df_main["state_territory"].value_counts()
total_main = len(df_main)

np.random.seed(42)  # Ensure sampling reproducibility
sampled_dfs = []

for region, count in counts.items():
    prop = count / total_main
    alloc = round(prop * total_target)
    alloc = max(1, alloc)  # Ensure at least 1 entry per region

    reg_df = df_main[df_main["state_territory"] == region]
    sample_size = min(alloc, len(reg_df))
    sampled_dfs.append(reg_df.sample(n=sample_size, random_state=42))

df_sampled = pd.concat(sampled_dfs).reset_index(drop=True)

# 4. Adjustment to guarantee exactly 250 rows in total
if len(df_sampled) > total_target:
    df_sampled = df_sampled.sample(n=total_target, random_state=42).reset_index(
        drop=True
    )
elif len(df_sampled) < total_target:
    remaining = df_main.drop(df_sampled.index, errors="ignore")
    needed = total_target - len(df_sampled)
    extra = remaining.sample(n=min(needed, len(remaining)), random_state=42)
    df_sampled = pd.concat([df_sampled, extra]).reset_index(drop=True)


# 5. Function to clean HTML tags from text fields
def clean_html(text):
    if pd.isna(text):
        return ""
    clean = re.compile("<.*?>")
    return re.sub(clean, "", text)


df_sampled["overview"] = df_sampled["overview"].apply(clean_html)
df_sampled["location_info"] = df_sampled["location_info"].apply(clean_html)

# 6. Select and cleanly rename columns for the application
df_final = df_sampled[[
    "primary_name",
    "austlang_code",
    "state_territory",
    "status",
    "overview",
    "location_info",
    "lat",
    "lon",
]].copy()

df_final.columns = [
    "nom_langue",
    "code",
    "territoire",
    "statut",
    "description",
    "localisation",
    "latitude",
    "longitude",
]

# 7. Save the final CSV file ready for Streamlit
df_final.to_csv("language_learning_data.csv", index=False, encoding="utf-8-sig")

print(f"Success! File generated with {len(df_final)} rows.")
print(df_final["territoire"].value_counts())