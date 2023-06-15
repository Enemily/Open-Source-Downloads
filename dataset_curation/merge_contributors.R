coxData = read.csv("final_subset_peaked_early.csv")
contributorsData = read.csv("coxData_contributors.csv")
lookup_table <- data.frame(slug = contributorsData$slug, numContributors = contributorsData$numContributors)
matching_indices <- match(coxData$slug, lookup_table$slug)
matching_slugs <- !is.na(matching_indices)
coxData$numContributors[matching_slugs] <- lookup_table$numContributors[matching_indices[matching_slugs]]