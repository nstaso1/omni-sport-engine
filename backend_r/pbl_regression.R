# Install required packages if you don't have them yet:
# install.packages("jsonlite")
# install.packages("dplyr")

library(jsonlite)
library(dplyr)

cat("Loading Mystics Analytics Database...\n")

# 1. Load the JSON exported from your dashboard
json_data <- fromJSON("MysticsAnalytics_Save.json")

# 2. Extract and combine Pickleball data from the nested lists
pbl_minor <- json_data$masterDB$minor$pbl
pbl_pro <- json_data$masterDB$proleague$pbl
pbl_df <- bind_rows(pbl_minor, pbl_pro)

cat("Running Multiple Linear Regression Model...\n")

# 3. Run the Regression Model
# Predicting 'score' based on p1 (DUPR), p2 (Drop %), and p3 (Kitchen %)
model <- lm(score ~ p1 + p2 + p3, data = pbl_df)

# 4. Print the summary statistics (p-values, R-squared, coefficients)
summary(model)
