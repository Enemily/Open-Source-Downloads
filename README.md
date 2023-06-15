# Open-Source-Downloads
This artifact consists of:

1. Data collection scripts
Code was implemented in R and Python 3. The scripts can be used to curate our dataset, first selecting the GitHub projects then gathering data such as downloads, commits, opened and closed issues, contributors, repository size, and whether the project was archived in each month of our observation window. 

    The final output of the scripts is a csv file, where each row is a data point in our survival analysis. Each row represents data per project and per month in our observation window of 2015-01 to 2020-12. Because some of our projects experience the dependent outcome variable (i.e. peaked download counts) before 2020-12, each project takes occupies a different number of rows in our csv file. Required dependencies include pandas, numpy, sqldf, and RMysql. 

2. Survival analysis.
Code was implemented in R. The script ```survival_analysis.R``` builds a Cox Proportional Hazards survival model and a multiple logistic regression model from our dataset. Model diagnostics are also run.

# Project filtering
These scripts assume the longitudinal download counts, number of versions, number of issues opened, and number of issues closed are accessible from an external table in an SQL database. These projects were popular at least once in their history, receiving more than 10,000 downloads during any month.

Run ```project_filtering/retrieve_active_projects.R``` to find popular projects that had more than 1 total commit, issue opened or closed, or version released. 

Run ```heuristic/get_peaked_packages.R``` to find popular projects that peaked according to our heuristic definition. With the peaked projects marked, run ```project_filtering/generate_matching_pairs.R``` to find a matching set of non-peaked projects for each peaked project to obtain an equal number of peaked and non-peaked projects. This also removes projects that peaked early and their associated matched non-peaked project.

# Dataset curation
Run ```dataset_curation/get_commits.py``` to collect the number of commits over time for all projects. Data is merged into the same external table in the SQL database, retrieved through SQL queries, and merged into the final csv.

Run ```dataset_curation/get_contributors.py``` to collect the number of commits only by contributors for all projects. Data is merged into the final csv using ```dataset_curation/merge_contributors.R```, described later.

Run ```dataset_curation/get_size.py``` to collect the size of the project repository during the month the project peaked (for peaked projects) or the last month in our observation window (for non-peaked projects). Data is merged into the final csv during the process.

Run ```dataset_curation/check_archived.py``` to collect information about whether and when the repository was archived on GitHub during any month in our observation window. All data points before the project was archived were not labeled as ```archived=TRUE```, while all data points on and after the project was archived were labeled as ```archived=TRUE```. This labeling was implemented in ```dataset_curation/archived_labeling.R```.

# Data analysis.
The final csv used to build the Cox Proportional Hazards model and the multiple logistic regression model has 22 columns, and each row is a single data point in our model, representing a project’s activity on a certain month in our 6-year time window. Variables are listed below. Note that not all columns were included as independent variables in our regression models. The models are built and the diagnostics are run in ```survival_analysis.R```.
+ ```slug```: project repository name
+ ```numIssuesOpened```: number of issues opened each month
+ ```numIssuesClosed```: number of issues closed each month, excluding issues closed by the same person who opened it
+ ```numCommitsWithDups```: number of commits each month 
+ ```peaked```: dependent outcome variable (binary). A 0 indicates the project hasn’t peaked in that month yet, and a 1 indicates the project has peaked during that month. 
+ ```peakDate```: date project peaked of the form yyyy-mm.
+ ```yearMonth```: year and month of data point of the form yyyy-mm.
+ ```numDownloads```: number of times package of repository was downloaded each month.
+ ```peakedEarly```: binary flag indicating whether project is a peaked project that peaked within the first 6 months of our observation window. peakedEarly is also equal to TRUE for non-peaked packages that matched with a peakedEarly package.
+ ```isPeakedProject```: whether or not project peaked at any month in our observation window.
+ ```period```: number of months since beginning of observation window for each month. This incrementing month counter resets for each new project.
+ ```period_number```: the number of months before a project’s peak (or the total number of months between 2015-01 and 2020-12 for non-peaked projects).
+ ```archived```: whether or not the project is archived in that month.
+ ```numContributors```: number of commits by contributors each month.
+ ```numVersions```: number of versions released each month.
+ ```size```: size of the repository’s main branch during the peak date (or last month of observation window for non-peaked projects).
+ ```isSmall50k```: whether ```size``` is smaller than 50 kilobytes.
+ ```isSmall100k```: whether ```size``` is smaller than 100 kilobytes.
+ ```isSmall150k```: whether ```size``` is smaller than 150 kilobytes.
+ ```isSmallFirstQuartile```: whether ```size``` is smaller than the first quartile cutoff of the distribution of sizes for all project ```sizes``` in sample.
+ ```isSmallLower10Percent```: whether ```size``` is within the lower 10% of sizes for all project ```sizes``` in sample.



