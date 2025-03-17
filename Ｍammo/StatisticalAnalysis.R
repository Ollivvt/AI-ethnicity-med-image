library(readr)
library(ggplot2)
library(dplyr)
library(tidyr)

# Load data
data <- read.csv("Model_Overall_Summary.csv")
colnames(data) <- c("Dataset", "Model", "ImageSize", "Manufacturer", "ExperimentType", 
                    "Class", "Precision", "Recall", "Specificity", "F1", "Support")

filtered_data <- data %>%
  filter(Dataset == "Mammo", 
         Manufacturer == "All", 
         ExperimentType == "Tissue-Only")

filtered_data$ImageSize <- factor(filtered_data$ImageSize, 
                                  levels = c("256x256", "512x512", "768x768", "1024x1024"))

# Function for comparing proportions (Z-test)
compare_proportions <- function(x1, n1, x2, n2, alpha = 0.05, pooled = TRUE) {
  p1_hat <- x1 / n1
  p2_hat <- x2 / n2
  
  if (pooled) {
    p_pooled <- (x1 + x2) / (n1 + n2)
    z <- (p1_hat - p2_hat) / sqrt(p_pooled * (1 - p_pooled) * (1/n1 + 1/n2))
  } else {
    z <- (p1_hat - p2_hat) / sqrt((p1_hat * (1 - p1_hat) / n1) + (p2_hat * (1 - p2_hat) / n2))
  }
  
  p_value <- 2 * (1 - pnorm(abs(z)))  # One-sided test (testing if resolution increase improves)
  conclusion <- ifelse(p_value < alpha, "Significant Improvement", "No Significant Improvement")
  return(list(z_statistic = z, p_value = p_value, conclusion = conclusion))
}

# === Initialize results storage ===
results <- data.frame()

# Sort for adjacent comparisons
filtered_data <- filtered_data %>%
  arrange(Class, Model, ImageSize)

# List unique image sizes
image_sizes <- levels(filtered_data$ImageSize)

# Compare adjacent image sizes within each class & model
for (cls in unique(filtered_data$Class)) {
  for (mdl in unique(filtered_data$Model)) {
    for (i in 1:(length(image_sizes) - 1)) {
      size1 <- image_sizes[i]
      size2 <- image_sizes[i + 1]
      
      row1 <- filtered_data %>%
        filter(Class == cls, Model == mdl, ImageSize == size1)
      
      row2 <- filtered_data %>%
        filter(Class == cls, Model == mdl, ImageSize == size2)
      
      if (nrow(row1) == 1 && nrow(row2) == 1) {
        # Sensitivity comparison
        n1 <- row1$Support
        n2 <- row2$Support
        
        x1_sens <- round(row1$Recall * n1)  # True positives
        x2_sens <- round(row2$Recall * n2)
        
        sens_result <- compare_proportions(x1_sens, n1, x2_sens, n2)
        
        # Specificity comparison
        x1_spec <- round(row1$Specificity * n1)  # True negatives
        x2_spec <- round(row2$Specificity * n2)
        
        spec_result <- compare_proportions(x1_spec, n1, x2_spec, n2)
        
        # Append results
        results <- rbind(results, data.frame(
          Class = cls,
          Model = mdl,
          Compare_ImageSize = paste(size1, "vs", size2),
          Sensitivity_Z = sens_result$z_statistic,
          Sensitivity_p = sens_result$p_value,
          Sensitivity_Conclusion = sens_result$conclusion,
          Specificity_Z = spec_result$z_statistic,
          Specificity_p = spec_result$p_value,
          Specificity_Conclusion = spec_result$conclusion
        ))
      }
    }
  }
}

# Save results to CSV
# write.csv(results, "Resolution_Comparison_Results.csv", row.names = FALSE)

# Print to console for quick check
print(results)

# Heatmap of Significance Conclusions
results_summary <- results %>%
  select(Class, Compare_ImageSize, Sensitivity_Conclusion, Specificity_Conclusion) %>%
  pivot_longer(cols = c("Sensitivity_Conclusion", "Specificity_Conclusion"),
               names_to = "Metric",
               values_to = "Conclusion") %>%
  mutate(Metric = ifelse(Metric == "Sensitivity_Conclusion", "Sensitivity", "Specificity"))

ggplot(results_summary, aes(x = Compare_ImageSize, y = Class, fill = Conclusion)) +
  geom_tile(color = "white") +
  facet_wrap(~Metric) +
  scale_fill_manual(values = c("Significant Improvement" = "lightgreen", 
                               "No Significant Improvement" = "lightcoral")) +
  theme_minimal() +
  labs(title = "Statistical Significance Heatmap - Sensitivity & Specificity",
       x = "Image Size Comparison",
       y = "Class") +
  theme(axis.text.x = element_text(angle = 45, hjust = 1))