library(dplyr)
library(readr)
library(ggplot2)
library(tidyr)

# Load CSV file
file_path <- "U:/GitHub/AI-ethnicity-med-image/Ｍammo/Model_Overall_Summary.csv"
df <- read_csv(file_path)

# Compute per-class statistics including t-based Confidence Intervals
class_summary <- df %>%
  group_by(Class) %>%
  summarise(
    n = n(),  # Count number of samples per class
    Mean_Precision = mean(Precision, na.rm = TRUE),
    SD_Precision = sd(Precision, na.rm = TRUE),
    t_value = qt(0.975, df = n - 1),  # Compute t-critical value
    CI_Precision_Lower = Mean_Precision - t_value * (SD_Precision / sqrt(n)),
    CI_Precision_Upper = Mean_Precision + t_value * (SD_Precision / sqrt(n)),
    
    Mean_Recall = mean(`Recall (Sensitivity)`, na.rm = TRUE),
    SD_Recall = sd(`Recall (Sensitivity)`, na.rm = TRUE),
    CI_Recall_Lower = Mean_Recall - t_value * (SD_Recall / sqrt(n)),
    CI_Recall_Upper = Mean_Recall + t_value * (SD_Recall / sqrt(n)),
    
    Mean_Specificity = mean(Specificity, na.rm = TRUE),
    SD_Specificity = sd(Specificity, na.rm = TRUE),
    CI_Specificity_Lower = Mean_Specificity - t_value * (SD_Specificity / sqrt(n)),
    CI_Specificity_Upper = Mean_Specificity + t_value * (SD_Specificity / sqrt(n)),
    
    Mean_F1_Score = mean(`F1-score`, na.rm = TRUE),
    SD_F1_Score = sd(`F1-score`, na.rm = TRUE),
    CI_F1_Lower = Mean_F1_Score - t_value * (SD_F1_Score / sqrt(n)),
    CI_F1_Upper = Mean_F1_Score + t_value * (SD_F1_Score / sqrt(n))
  ) %>%
  select(-t_value)  # Remove t-value column


print(class_summary)

# write_csv(class_summary, "Class_Summary.csv")

# Reshape the original data for box plotting
df_long <- df %>%
  pivot_longer(
    cols = c(Precision, `Recall (Sensitivity)`, Specificity, `F1-score`),
    names_to = "Metric",
    values_to = "Value"
  )

# Create box plots
ggplot(df_long, aes(x = Class, y = Value, fill = Class)) +
  geom_boxplot() +
  facet_wrap(~ Metric, scales = "free_y") +
  theme_bw() +
  labs(
    title = "Performance Metrics by Class",
    y = "Value",
    x = "Class"
  ) +
  theme(axis.text.x = element_text(angle = 45, hjust = 1))