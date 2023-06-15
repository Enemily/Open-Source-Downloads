from git import Repo
import pandas as pd
import os
from prometheus_client import start_http_server
from pydriller.repository import Repository  

df_long = pd.read_csv("final_subset_peaked_early.csv")
df = pd.DataFrame(df_long['slug'].unique(), columns=['slug'])

dfOfficial = pd.DataFrame()

for i in range(0, len(df)):
    # try:
    s = df['slug'][i]
    ind = (df_long['slug'] == df['slug'][i])
    try:
        end_date = df_long['peakDate'][ind].iloc[0]
    except:
        print("error getting peak date: "+str(i)+", "+s)
        continue

    try:
        if s.find('/tree/') != -1:
            s = s[0:s.find('/tree/')]
    except:
        pass
    try:
        if s.find('.git') != -1:
            s = s[0:s.find('.git')]
    except:
        pass
    try:
        if s.find('.com') != -1:
            s = s[s.find('.com')+5:]
    except:
        pass
    try:
        if s.find('.org') != -1:
            s = s[s.find('.org')+5:]
    except:
        pass
    try:
        if s[len(s)-1] == '/':
            s = s[0:len(s)-1]
    except:
        pass
    try:
        if '/master/' in s:
            s = s[0:s.find('/master/')]
    except:
        pass
    try:
        if '/packages/' in s:
            s = s[0:s.find('/packages/')]
    except:
        pass
    try:
        if '/main/' in s:
            s = s[0:s.find('/main/')]
    except:
        pass

    if s.find('/')!=-1:
        st = s.replace(s[s.find('/')], '_____')

    ########## get the path of the repo
    a = "/data3/emilyngu/" + st

    ########## if path doesn't exist, clone it to tardigrade databse /data3/emilyngu
    if os.path.exists(a) == False:
        try:
            repo = Repo.clone_from("https://github.com/"+st, a)
            try:
                thing = len(list(Repository(a).traverse_commits()))
            except:
                print("error with listing repository: "+s+", "+str(i))
                continue 
        except:
            print("error with listing repository: "+s+", "+str(i))
            continue
    else:
        try:
            repo = Repo(a)
        except:
            print("error with listing repository: "+s+", "+str(i))
            continue 
    try:
        commits = list(repo.iter_commits())
    except:
        print("error with listing repository: "+s+", "+str(i))
        continue   
    # Extract the contributors and their commit months within the date range
    try:
        contributors = {}
        start_date = '2015-01-01'
        end_date = end_date + '-01'
        for commit in commits:
            commit_date = commit.committed_datetime.date().isoformat()
            if start_date <= commit_date <= end_date:
                author_name = commit.author.name
                commit_month = commit_date[:7] + '-01'
                if author_name in contributors:
                    contributors[author_name].add(commit_month)
                else:
                    contributors[author_name] = {commit_month}

        # Count the number of contributors per month
        contributor_counts = []
        for month in pd.date_range(start=start_date, end=end_date, freq='MS'):
            month_str = month.strftime('%Y-%m-%d')
            contributors_at_month = [contributor for contributor, months in contributors.items() if month_str in months]
            contributor_count = len(contributors_at_month)
            contributor_counts.append((month_str, contributor_count))

        # Create a DataFrame from the contributor counts
        contributor_df = pd.DataFrame(contributor_counts, columns=['Month', 'ContributorCount'])
        contributor_df['slug'] = df['slug'][i]
        dfOfficial = pd.concat([dfOfficial, contributor_df], ignore_index=True)

        if sum(contributor_df['ContributorCount']) == 0:
            print(s +" has zero contributors. "+ str(i))
            df_long.loc[ ind, 'numContributors'] = 0
    except:
        print("Error with grabbing contributors, "+str(i)+" "+ s)

dfOfficial.to_csv("coxData_contributors.csv")



