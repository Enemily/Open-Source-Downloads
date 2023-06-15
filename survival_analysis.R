library(dplyr)
library(knitr)
library(DBI)
library(zoo)
library(broom)
library(survival)
library(survminer)
library(car)

coxData= read.csv("/data3/emilyngu/final_subset_peaked_early.csv")

### TRY DIFFERENT OPERATIONALIZATIONS FOR repositoryIsSmall VARIABLE
coxData$isSmall50k = coxData$size < 50
coxData$isSmall100k = coxData$size < 100
coxData$isSmall150k = coxData$size < 150
coxData$isSmallFirstQuartile = coxData$size < 19.2
coxData$isSmallLower10Percent = coxData$size < 10.991

### REMOVE PROJECTS THAT PEAKED EARLY
coxDataPeakLater = coxData[coxData$peakedEarly==F,]
coxDataPeakLater = coxDataPeakLater %>% mutate(tstart = period-1)
coxDataPeakLater <- coxDataPeakLater %>% mutate(tstop = period)


### MULTIPLE LOGISTIC REGRESSion
logit = glm(peaked ~ 
              log(numDownloads+1) +
              log(numCommitsWithDups+1) +
              log(as.numeric(numIssuesOpened)+1) +
              log(as.numeric(numIssuesClosed) + 1) +
              log(numContributors+1) +
              isSmall150K:archived
              ,data=coxDataPeakLater)
summary(logit)


cox = coxph(Surv(tstart, tstop, peaked) ~
                 log(numDownloads+1) +
                 log(numCommitsWithDups+1) +
                 log(as.numeric(numIssuesOpened)+1) +
                 log(as.numeric(numIssuesClosed) + 1) +
                 log(numContributors+1) +
                 isSmall150K:archived,
                 data=coxDataPeakLater)
summary(cox)

### DIAGNOSTICS for Cox Proportional Hazards Model
# Variance inflation factor
vif(logit)
vif(cox)

cox.zph.cox = cox.zph(cox)
cox.zph.cox 

# Schoenfeld residuals
plot(cox.zph.coxRes)

# anova effect size
anova(cox)
