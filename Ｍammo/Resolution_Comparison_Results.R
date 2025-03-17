# Load libraries
library(readr)
library(dplyr)
library(tidyr)
library(ggplot2)
library(purrr)

# Load the data (filtered version)
data <- read.csv("Model_Overall_Summary.csv")
colnames(data) <- c("Dataset", "Model", "ImageSize", "Manufacturer", "ExperimentType", 
                    "Class", "Precision", "Recall", "Specificity", "F1", "Support")

filtered_data <- data %>%
  filter(Dataset == "Mammo", Manufacturer == "All", ExperimentType == "Tissue-Only") %>%
  arrange(Class, Model, factor(ImageSize, levels = c("256x256", "512x512", "768x768", "1024x1024")))

# Z-test function (proportion test)
compare_proportions <- function(x1, n1, x2, n2, alpha = 0.05, pooled = TRUE) {
  p1 <- x1 / n1
  p2 <- x2 / n2
  
  if (pooled) {
    p_pooled <- (x1 + x2) / (n1 + n2)
    z <- (p1 - p2) / sqrt(p_pooled * (1 - p_pooled) * (1/n1 + 1/n2))
  } else {
    z <- (p1 - p2) / sqrt((p1 * (1 - p1) / n1) + (p2 * (1 - p2) / n2))
  }
  
  p_value <- 2 * (1 - pnorm(abs(z)))
  conclusion <- ifelse(p_value < alpha, "Significant Improvement", "No Significant Improvement")
  
  return(list(z = z, p = p_value, conclusion = conclusion))
}

# Confidence interval function
compute_confidence_interval <- function(p, n, confidence = 0.95) {
  z <- qnorm((1 + confidence) / 2)
  margin_of_error <- z * sqrt(p * (1 - p) / n)
  return(c(lower = p - margin_of_error, upper = p + margin_of_error))
}

# Add confidence intervals to data
ci_data <- filtered_data %>%
  mutate(
    Sensitivity_CI = map2(Recall, Support, compute_confidence_interval),
    Specificity_CI = map2(Specificity, Support, compute_confidence_interval)
  ) %>%
  unnest_wider(Sensitivity_CI, names_sep = "_") %>%
  unnest_wider(Specificity_CI, names_sep = "_")

# Compare adjacent resolutions - Z-tests and CI overlap check
results <- data.frame()
image_sizes <- c("256x256", "512x512", "768x768", "1024x1024")

for (cls in unique(ci_data$Class)) {
  for (mdl in unique(ci_data$Model)) {
    class_model_data <- ci_data %>%
      filter(Class == cls, Model == mdl) %>%
      arrange(factor(ImageSize, levels = image_sizes))
    
    for (i in 1:(nrow(class_model_data) - 1)) {
      row1 <- class_model_data[i, ]
      row2 <- class_model_data[i + 1, ]
      
      sens_ztest <- compare_proportions(
        round(row1$Recall * row1$Support),
        row1$Support,
        round(row2$Recall * row2$Support),
        row2$Support
      )
      
      spec_ztest <- compare_proportions(
        round(row1$Specificity * row1$Support),
        row1$Support,
        round(row2$Specificity * row2$Support),
        row2$Support
      )
      
      sens_ci_significant <- row2$Recall > row1$Sensitivity_CI_upper + 0.01 | 
        row2$Recall < row1$Sensitivity_CI_lower - 0.01
      spec_ci_significant <- !(row2$Specificity > row1$Specificity_CI_lower & row2$Specificity < row1$Specificity_CI_upper)
      
      results <- rbind(results, data.frame(
        Class = cls,
        Model = mdl,
        Compare_ImageSize = paste(row1$ImageSize, "vs", row2$ImageSize),
        Sensitivity_Z = sens_ztest$z,
        Sensitivity_p = sens_ztest$p,
        Sensitivity_Conclusion = sens_ztest$conclusion,
        Sensitivity_CI_Conclusion = ifelse(sens_ci_significant, "CI Suggests Improvement", "CI Overlaps - No Clear Improvement"),
        Specificity_Z = spec_ztest$z,
        Specificity_p = spec_ztest$p,
        Specificity_Conclusion = spec_ztest$conclusion,
        Specificity_CI_Conclusion = ifelse(spec_ci_significant, "CI Suggests Improvement", "CI Overlaps - No Clear Improvement")
      ))
    }
  }
}

write.csv(results, "Resolution_Comparison_Results.csv", row.names = FALSE)

# Plot 1: Z-score bar plot
results_long <- results %>%
  pivot_longer(cols = c("Sensitivity_Z", "Specificity_Z"), names_to = "Metric", values_to = "Z_Score") %>%
  mutate(Metric = ifelse(Metric == "Sensitivity_Z", "Sensitivity", "Specificity"))

if (nrow(results_long) > 0) {
  z_score_plot <- ggplot(results_long, aes(x = Compare_ImageSize, y = Z_Score, fill = Metric)) +
    geom_bar(stat = "identity", position = position_dodge()) +
    geom_hline(yintercept = 1.645, linetype = "dashed", color = "red") +
    facet_wrap(~Class, scales = "free_x") +
    theme_minimal() +
    labs(title = "Z-Scores for Sensitivity and Specificity by Image Size Comparison",
         x = "Image Size Comparison", y = "Z-Score",
         caption = "Red line = threshold for significance (Z = 1.645 for alpha = 0.05)") +
    theme(axis.text.x = element_text(angle = 45, hjust = 1))
  
  ggsave("Z_Score_Barplot.png", plot = z_score_plot, width = 10, height = 6)
} else {
  message("No valid comparisons found for Z-Score plot. Skipping plot generation.")
}

# Plot 2: Significance heatmap
results_summary <- results %>%
  select(Class, Compare_ImageSize, Sensitivity_Conclusion, Specificity_Conclusion) %>%
  pivot_longer(cols = c("Sensitivity_Conclusion", "Specificity_Conclusion"), names_to = "Metric", values_to = "Conclusion") %>%
  mutate(Metric = ifelse(Metric == "Sensitivity_Conclusion", "Sensitivity", "Specificity"))

heatmap_plot <- ggplot(results_summary, aes(x = Compare_ImageSize, y = Class, fill = Conclusion)) +
  geom_tile(color = "white") +
  facet_wrap(~Metric) +
  scale_fill_manual(values = c("Significant Improvement" = "lightgreen", "No Significant Improvement" = "lightcoral")) +
  theme_minimal() +
  labs(title = "Statistical Significance Heatmap - Sensitivity & Specificity",
       x = "Image Size Comparison", y = "Class") +
  theme(axis.text.x = element_text(angle = 45, hjust = 1))

ggsave("Significance_Heatmap.png", plot = heatmap_plot, width = 10, height = 6)

# Plot 3: Confidence interval error bar plot
ci_long <- ci_data %>%
  pivot_longer(cols = c("Recall", "Specificity"), names_to = "Metric", values_to = "Value") %>%
  pivot_longer(cols = starts_with("Sensitivity_CI") | starts_with("Specificity_CI"), names_to = "CI_Type", values_to = "CI_Value") %>%
  separate(CI_Type, into = c("Metric_Type", "CI_Bound"), sep = "_") %>%
  filter(grepl(Metric_Type, Metric)) %>%
  pivot_wider(names_from = CI_Bound, values_from = CI_Value)

ci_plot <- ggplot(ci_long, aes(x = ImageSize, y = Value, color = Metric, group = Metric)) +
  geom_line() +
  geom_point() +
  geom_errorbar(aes(ymin = lower, ymax = upper), width = 0.1) +
  facet_wrap(~Class) +
  theme_minimal() +
  labs(title = "Performance with Confidence Intervals", x = "Image Size", y = "Metric Value")

ggsave("Confidence_Interval_Plot.png", plot = ci_plot, width = 10, height = 6)

