import re
import numpy as np
import pandas as pd

# 1. Chargement de la base d'origine brute
df = pd.read_csv("austlang.csv")

# 2. Définition des 8 régions principales (hors frontières multiples)
single_regions = ["QLD", "NT", "WA", "NSW", "VIC", "SA", "TAS", "TSI"]
df_main = df[df["state_territory"].isin(single_regions)].copy()

# 3. Calcul de la répartition proportionnelle pour un total de 250 enregistrements
total_target = 250
counts = df_main["state_territory"].value_counts()
total_main = len(df_main)

np.random.seed(42)  # Assure la reproductibilité de l'échantillonnage
sampled_dfs = []

for region, count in counts.items():
  prop = count / total_main
  alloc = round(prop * total_target)
  alloc = max(1, alloc)  # S'assure d'avoir au moins 1 entrée par région

  reg_df = df_main[df_main["state_territory"] == region]
  sample_size = min(alloc, len(reg_df))
  sampled_dfs.append(reg_df.sample(n=sample_size, random_state=42))

df_sampled = pd.concat(sampled_dfs).reset_index(drop=True)

# 4. Ajustement pour garantir exactement 250 lignes au total
if len(df_sampled) > total_target:
  df_sampled = df_sampled.sample(n=total_target, random_state=42).reset_index(
      drop=True
  )
elif len(df_sampled) < total_target:
  remaining = df_main.drop(df_sampled.index, errors="ignore")
  needed = total_target - len(df_sampled)
  extra = remaining.sample(n=min(needed, len(remaining)), random_state=42)
  df_sampled = pd.concat([df_sampled, extra]).reset_index(drop=True)


# 5. Fonction de nettoyage des balises HTML dans les textes
def clean_html(text):
  if pd.isna(text):
    return ""
  clean = re.compile("<.*?>")
  return re.sub(clean, "", text)


df_sampled["overview"] = df_sampled["overview"].apply(clean_html)
df_sampled["location_info"] = df_sampled["location_info"].apply(clean_html)

# 6. Sélection et renommage propre des colonnes pour l'application
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

# 7. Sauvegarde du fichier CSV final prêt pour Streamlit
df_final.to_csv("language_learning_data.csv", index=False, encoding="utf-8-sig")

print(f"Succès ! Fichier généré avec {len(df_final)} lignes.")
print(df_final["territoire"].value_counts())