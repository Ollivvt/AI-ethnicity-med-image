import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load the CSV files
class_summary_path = r"U:\GitHub\AI-ethnicity-med-image\data\Mammo\Class_Summary.csv"
model_summary_path = r"U:\GitHub\AI-ethnicity-med-image\data\Mammo\Model_Overall_Summary.csv"

df_class = pd.read_csv(class_summary_path)
df_model = pd.read_csv(model_summary_path)

# Filter Model_Overall_Summary.csv based on given conditions
filtered_df_model = df_model[
    (df_model["Dataset"] == "BDen") &
    (df_model["Model"] == "EfficientNetB3") &
    (df_model["Manufacturer"] == "All") &
    # (df_model["Experiment Type"] == "Tissue-Only") &
    # (df_model["ImageSize"].isin(["256x256", "512x512", "768x768", "1024x1024"])
    (df_model["ImageSize"] == "512x512") &
    (df_model["Experiment Type"].isin(["Original Data", "Random Patching", "Tissue-Only", "Segmentation Map"]))
]

# Extract necessary columns for overlaying data
df_f1_overlay = filtered_df_model[["Class", "Experiment Type", "F1-score"]]

# Expand the data for a proper boxplot using simulated F1-score distribution
num_samples = 100  # Generate synthetic samples for a smooth boxplot
# Expand data using normal distribution approximation
expanded_data = []
for _, row in df_class.iterrows():
    samples = np.random.normal(row["Mean_F1_Score"], row["SD_F1_Score"], num_samples)
    samples = np.clip(samples, 0, 1)  # Ensure values are within valid F1-score range
    for sample in samples:
        expanded_data.append({"Class": row["Class"], "F1-score": sample})

df_box_f1 = pd.DataFrame(expanded_data)

# Create the proper boxplot
plt.figure(figsize=(8, 8))

# Boxplot using full F1-score distribution
sns.boxplot(x="Class", y="F1-score", data=df_box_f1, palette="muted", dodge=False, zorder=1)

# Overlay the F1-score values from the model dataset
sns.scatterplot(x="Class", y="F1-score",
                hue="Experiment Type", data=df_f1_overlay, palette="coolwarm",
                marker='o', s=100, edgecolor="black", zorder=2)

plt.xticks(rotation=30, ha="right")
plt.legend(title="Experiment Type")
plt.title("BDen - Comparison of Experiment Type F1-score")
plt.ylabel("F1-score")
plt.xlabel("Class")
plt.show()