library(ggplot2)
library(ggpubr)
library(RMySQL)
mydb = dbConnect(MySQL(), user = "", password = "", dbname = "", host = "")

peakedAndWhen = function(downloadsRaw, downloadsFitted) {
  dateMaxDownloads = which.max(downloadsRaw)
  if (downloadsFitted[length(downloadsFitted)] < 0.8*downloadsRaw[dateMaxDownloads]) {
    return (TRUE, dateMaxDownloads)
  }
  else {
    return (FALSE, NA)
  }
}

coxData = read.csv( "final_subset_peaked_early.csv")
coxData$peaked = F
coxData$peakDate = -1

for(i in 1:nrow(coxData)) {
  s = shQuote(coxData$slug[i])
  str = paste("select slug, yearMonth, numDownloads from [db_name] where slug =", s)
  npm <- dbGetQuery(mydb, str)
  
  npm$period = NA
  for(k in 1:nrow(npm)) {
    npm$period[k] = k
  }
  fit3 <- lm(numDownloads~poly(period,3,raw=TRUE), coxData=npm)
  fit4 <- lm(numDownloads~poly(period,4,raw=TRUE), coxData=npm)
  fit5 <- lm(numDownloads~poly(period,5,raw=TRUE), coxData=npm)
  
  maxModel = fit3
  max = summary(maxModel)$adj.r.squared
  if(!is.nan(summary(fit4)$adj.r.squared) & summary(fit4)$adj.r.squared > max) {
    maxModel = fit4
    max = summary(fit4)$adj.r.squared
  }
  if(!is.nan(summary(fit5)$adj.r.squared) & summary(fit5)$adj.r.squared > max) {
    maxModel = fit5
    max = summary(fit5)$adj.r.squared
  }
  
  coxData$peaked[i] = peakedAndWhen(npm$numDownloads, predict(maxModel))[1]
  if(coxData$peaked[i]==T) {
    coxData$peakDate = peakedAndWhen(npm$numDownloads, predict(maxModel))[2]
  }
  else {
    coxData$peakDate = NA
  }
  
}

write.csv(coxData, "final_subset_peaked_early.csv")