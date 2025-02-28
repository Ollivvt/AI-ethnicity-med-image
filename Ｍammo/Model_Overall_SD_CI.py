import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

# Load CSV file
file_path = "U:/GitHub/AI-ethnicity-med-image/Ｍammo/Model_Overall_Summary.csv"
df = pd.read_csv(file_path)

# Compute per-class statistics including t-based Confidence Intervals
class_summary = df.groupby('Class').apply(
    lambda x: pd.Series({
        'n': len(x),
        'Mean_Precision': x['Precision'].mean(),
        'SD_Precision': x['Precision'].std(),
        't_value': stats.t.ppf(0.975, len(x) - 1),  # Compute t-critical value
        'CI_Precision_Lower': x['Precision'].mean() - stats.t.ppf(0.975, len(x) - 1) * (x['Precision'].std() / np.sqrt(len(x))),
        'CI_Precision_Upper': x['Precision'].mean() + stats.t.ppf(0.975, len(x) - 1) * (x['Precision'].std() / np.sqrt(len(x))),
        
        'Mean_Recall': x['Recall (Sensitivity)'].mean(),
        'SD_Recall': x['Recall (Sensitivity)'].std(),
        'CI_Recall_Lower': x['Recall (Sensitivity)'].mean() - stats.t.ppf(0.975, len(x) - 1) * (x['Recall (Sensitivity)'].std() / np.sqrt(len(x))),
        'CI_Recall_Upper': x['Recall (Sensitivity)'].mean() + stats.t.ppf(0.975, len(x) - 1) * (x['Recall (Sensitivity)'].std() / np.sqrt(len(x))),
        
        'Mean_Specificity': x['Specificity'].mean(),
        'SD_Specificity': x['Specificity'].std(),
        'CI_Specificity_Lower': x['Specificity'].mean() - stats.t.ppf(0.975, len(x) - 1) * (x['Specificity'].std() / np.sqrt(len(x))),
        'CI_Specificity_Upper': x['Specificity'].mean() + stats.t.ppf(0.975, len(x) - 1) * (x['Specificity'].std() / np.sqrt(len(x))),
        
        'Mean_F1_Score': x['F1-score'].mean(),
        'SD_F1_Score': x['F1-score'].std(),
        'CI_F1_Lower': x['F1-score'].mean() - stats.t.ppf(0.975, len(x) - 1) * (x['F1-score'].std() / np.sqrt(len(x))),
        'CI_F1_Upper': x['F1-score'].mean() + stats.t.ppf(0.975, len(x) - 1) * (x['F1-score'].std() / np.sqrt(len(x)))
    })
).reset_index()

# Remove t_value column
class_summary = class_summary.drop('t_value', axis=1)

print(class_summary)

# Create box plots for the metrics
# Reshape the data for plotting
df_long = pd.melt(
    df, 
    id_vars=['Class'], 
    value_vars=['Precision', 'Recall (Sensitivity)', 'Specificity', 'F1-score'],
    var_name='Metric', 
    value_name='Value'
)

# Create subplots - 2x2 grid for the 4 metrics
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
metrics = ['Precision', 'Recall (Sensitivity)', 'Specificity', 'F1-score']

for i, metric in enumerate(metrics):
    row, col = i // 2, i % 2
    subset = df_long[df_long['Metric'] == metric]
    
    # Set plot style with grid
    axes[row, col].set_facecolor('#f0f0f0')  # Light gray background
    axes[row, col].grid(True, linestyle='--', alpha=0.7)
    
    # Create boxplot
    sns.boxplot(x='Class', y='Value', data=subset, ax=axes[row, col])
    
    # Customize plot
    axes[row, col].set_title(f'{metric} by Class', fontsize=14, fontweight='bold')
    axes[row, col].set_xlabel('Class', fontsize=12)
    axes[row, col].set_ylabel('Value', fontsize=12)
    axes[row, col].tick_params(axis='x', rotation=45)
    
    # Add horizontal gridlines to improve readability of values
    axes[row, col].yaxis.grid(True, linestyle='-', alpha=0.3)
    
    # Set y-axis limits for better visualization if needed
    if metric in ['Precision', 'Recall (Sensitivity)', 'Specificity', 'F1-score']:
        axes[row, col].set_ylim(0, 1.05)  # Assuming metrics are between 0 and 1

# Adjust layout
plt.tight_layout()
plt.show()