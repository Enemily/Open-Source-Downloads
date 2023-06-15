library(dplyr)
library(knitr)
library(DBI)
library(zoo)
library(broom)
library(car)
library(sqldf)
library(jtools)
library(RMySQL)

mydb = dbConnect(MySQL(), user = "", password = "", dbname = "", host = "")

projects = dbGetQuery(mydb, "select * from [db_name];")

projects = projects[lengths(regmatches(projects$slug, gregexpr("/", projects$slug))) ==1,]
options(sqldf.driver = "SQLite")
projects.rowCounts = sqldf("select slug, count(*) as 'num_rows' from projects group by slug")


projects.zeroes = sqldf("select slug, count(numCommitsWithDups) as 'zero_commits' from projects where numCommitsWithDups==0 group by slug")
projects.zeroIssuesOpened = sqldf("select slug, count(numIssuesOpened) as 'zero_issuesOpened' from projects where numIssuesOpened==0 group by slug")
projects.zeroIssuesClosed = sqldf("select slug, count(numIssuesClosed) as 'zero_issuesClosed' from projects where numIssuesClosed==0 group by slug")

projects.summaries = projects.rowCounts
projects.summaries$num_zero_commits = NA
projects.summaries$num_zero_issuesOpened = NA
projects.summaries$num_zero_issuesClosed = NA

for (slug in projects.summaries$slug){
  
  # COMMITS
  if (slug %in% projects.zeroes$slug){
    projects.summaries[projects.summaries$slug == slug,]$num_zero_commits = projects.zeroes[projects.zeroes$slug == slug,]$zero_commits
  }else{
    projects.summaries[projects.summaries$slug == slug,]$num_zero_commits = 0
  }
  
  # OPENED ISSUES
  if (slug %in% projects.zeroIssuesOpened$slug){
    projects.summaries[projects.summaries$slug == slug,]$num_zero_issuesOpened = projects.zeroIssuesOpened[projects.zeroIssuesOpened$slug == slug,]$zero_issuesOpened
  }else{
    projects.summaries[projects.summaries$slug == slug,]$num_zero_issuesOpened = 0
  }
  
  # CLOSED ISSUES
  if (slug %in% projects.zeroIssuesClosed$slug){
    projects.summaries[projects.summaries$slug == slug,]$num_zero_issuesClosed = projects.zeroIssuesClosed[projects.zeroIssuesClosed$slug == slug,]$zero_issuesClosed
  }else{
    projects.summaries[projects.summaries$slug == slug,]$num_zero_issuesClosed = 0
  }
  
}
projects.summaries$ratio_zeros = projects.summaries$num_zero_commits / projects.summaries$num_rows
projects.summaries$ratio_zeroIssuesOpened = projects.summaries$num_zero_issuesOpened / projects.summaries$num_rows
projects.summaries$ratio_zeroIssuesClosed = projects.summaries$num_zero_issuesClosed / projects.summaries$num_rows


projects = projects[
  (projects$numDownloads <= quantile(projects$numDownloads, .99))  
  & (projects$numCommitsWithDups <= quantile(projects$numCommitsWithDups, .99))
  & (projects$numIssuesOpened <= quantile(projects$numIssuesOpened, .99))
  & (projects$numIssuesClosed <= quantile(projects$numIssuesClosed, .99))
  ,]


zeroStats = data.frame(
  projects.summaries[projects.summaries$ratio_zeros ==1 & projects.summaries$ratio_zeroIssuesOpened ==1 & projects.summaries$ratio_zeroIssuesClosed ==1 & projects.summaries$ratio_zeroVersions ==1,]$slug)

colnames(zeroStats) = c("slug")
firstRoundProjects <- projects[!projects$slug %in% zeroStats$slug, ]

write.csv(firstRoundProjects, "final_subset_peaked_early.csv")

