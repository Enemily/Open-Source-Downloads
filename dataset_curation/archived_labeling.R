library(dplyr)

coxData = read.csv("final_subset_peaked_early.csv")
coxData <- coxData %>%
  group_by(slug) %>%
  mutate(archived = ifelse(yearMonth < archivedAt, FALSE, TRUE))