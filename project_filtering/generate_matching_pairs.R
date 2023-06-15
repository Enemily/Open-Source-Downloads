library(ggplot2)
library(ggpubr)
library(RMySQL)
mydb = dbConnect(MySQL(), user = "", password = "", dbname = "", host = "")

coxData = read.csv("final_subset_peaked_early.csv")


uniqueSlugs = data.frame(unique(coxData$slug))
colnames(uniqueSlugs) = c("slug")

slug_counts <- table(coxData$slug)

filtered_slugs <- data.frame(uniqueSlugs[uniqueSlugs$slug %in% names(slug_counts) & slug_counts < 7,])
colnames(filtered_slugs) = c("slug")


peakedEarly = coxData[coxData$slug %in% filtered_slugs$slug,]
peakedLater = coxData[coxData$slug %in% filtered_slugs$slug == F,]

### GET MATCHING SETS FOR PEAKED PROJECTS
uniqueSlugs <- aggregate(peakDate ~ slug, data = peakedEarly, FUN = function(x) x[1])
uniqueSlugs$downloadsAtPeak = NA

for(i in 1:nrow(uniqueSlugs)) {
  s = shQuote(uniqueSlugs$slug[i])
  str = paste("select numDownloads, yearMonth from [db_name] where slug =", s)
  historicalData <- dbGetQuery(mydb, str)
  uniqueSlugs$downloadsAtPeak[i] = historicalData$numDownloads[which(historicalData$yearMonth==uniqueSlugs$peakDate[i])]
}

uniqueSlugs$yearMonth = uniqueSlugs$peakDate
uniqueSlugs$numDownloads = uniqueSlugs$downloadsAtPeak


dataNoPeaked = dbGetQuery(mydb, "select * from [db_name] where peaked = 0;")
extracted_slug <- unique(dataNoPeaked$slug[dataNoPeaked$yearMonth %in% uniqueSlugs$yearMonth &
                                             dataNoPeaked$numDownloads <= 1.25 * uniqueSlugs$numDownloads[match(dataNoPeaked$yearMonth, uniqueSlugs$yearMonth)] &
                                             dataNoPeaked$numDownloads >=.75 * uniqueSlugs$numDownloads[match(dataNoPeaked$yearMonth, uniqueSlugs$yearMonth)] ])
df = data.frame(extracted_slug)

big = dbGetQuery(mydb, "select * from [db_name];")

limit = nrow(uniqueSlugs)
df = df[1:limit,]
colnames(df) = c("slug")

uniqueSlugs$peakDate = NULL
uniqueSlugs$yearMonth = NULL
uniqueSlugs$numDownloads = NULL
uniqueSlugs$downloadsAtPeak = NULL

df$peakDate = NULL
df$yearMonth = NULL
df$numDownloads = NULL
df$downloadsAtPeak = NULL


uniqueBig = rbind(uniqueSlugs, df)

big <- big[big$slug %in% uniqueBig$slug, ]
peakedEarly = big
peakedEarly$peakedEarly = T

peakedEarly$period <- ave(peakedEarly$slug, peakedEarly$slug, FUN = function(x) seq_along(x))
peakedEarly[is.na(peakedEarly$peakDate),]$peakDate = "2020-12"
peakedEarly$period_number <- peakedEarly$period[match(peakedEarly$peakDate, peakedEarly$yearMonth)]
peakedEarly <- peakedEarly[peakedEarly$period <= peakedEarly$period_number, ]

### GET MATCHING SETS FOR NON-PEAKED PROJECTS

uniqueSlugs = data.frame(unique(peakedLater$slug))
colnames(uniqueSlugs) = c("slug")
uniqueSlugs <- aggregate(peakDate ~ slug, data = peakedLater, FUN = function(x) x[1])
uniqueSlugs$downloadsAtPeak = NA

for(i in 1:nrow(uniqueSlugs)) {
  s = shQuote(uniqueSlugs$slug[i])
  str = paste("select numDownloads, yearMonth from [db_name] where slug =", s)
  historicalData <- dbGetQuery(mydb, str)
  uniqueSlugs$downloadsAtPeak[i] = historicalData$numDownloads[length(historicalData$numDownloads)]
}

uniqueSlugs$yearMonth = uniqueSlugs$peakDate
uniqueSlugs$numDownloads = uniqueSlugs$downloadsAtPeak


dataNoPeaked = dbGetQuery(mydb, "select * from [db_name] where peaked = 0;")
extracted_slug <- unique(dataNoPeaked$slug[dataNoPeaked$yearMonth %in% uniqueSlugs$yearMonth &
                                             dataNoPeaked$numDownloads <= 1.25 * uniqueSlugs$numDownloads[match(dataNoPeaked$yearMonth, uniqueSlugs$yearMonth)] &
                                             dataNoPeaked$numDownloads >=.75 * uniqueSlugs$numDownloads[match(dataNoPeaked$yearMonth, uniqueSlugs$yearMonth)] ])
df = data.frame(extracted_slug)
big = dbGetQuery(mydb, "select * from [db_name];")

limit = nrow(uniqueSlugs)
df = df[1:limit,]
colnames(df) = c("slug")

uniqueSlugs$peakDate = NULL
uniqueSlugs$yearMonth = NULL
uniqueSlugs$numDownloads = NULL
uniqueSlugs$downloadsAtPeak = NULL

df$peakDate = NULL
df$yearMonth = NULL
df$numDownloads = NULL
df$downloadsAtPeak = NULL


uniqueBig = rbind(uniqueSlugs, df)
big <- big[big$slug %in% uniqueBig$slug, ]
peakedLater = big
peakedLater$peakedEarly = F

peakedLater$period <- ave(peakedLater$slug, peakedLater$slug, FUN = function(x) seq_along(x))
peakedLater[is.na(peakedLater$peakDate),]$peakDate = "2020-12"
peakedLater$period_number <- peakedLater$period[match(peakedLater$peakDate, peakedLater$yearMonth)]
peakedLater <- peakedLater[peakedLater$period <= peakedLater$period_number, ]

finalCoxData = rbind(peakedEarly, peakedLater)
write.csv(finalCoxData, "final_subset_peaked_early.csv")
