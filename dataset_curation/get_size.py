import git
from datetime import date, time
import subprocess
from git import Repo, Commit
import csv
import os
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings("ignore")
import re

d = pd.read_csv("/data3/emilyngu/final_subset_NA.csv")
df = pd.DataFrame(d)
df2 = pd.read_csv("/data3/emilyngu/final_subset_NA_unique_slugs.csv")

for i in range(0,len(df2)):
    s = orig = df2['slug'][i]
    ind = (df['slug'] == orig)
    if re.search(r'    .*', df['size'][ind].head(1).to_string()) is not None and re.search(r'0\.0', df['size'][ind].head(1).to_string()) is None:
        print(str(i)+", "+orig)
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
    # count = 0
    flag = False

    ########## if path doesn't exist, clone it to tardigrade databse /data3/emilyngu
    if os.path.exists(a) == False:
        try:
            Repo.clone_from("https://github.com/"+st, a)
        except:
            print("Error with cloning repo, "+str(i)+", "+orig)
            continue 
    
    os.chdir(a)
     
    start_date = re.search(r'\w{4}-\w{2}', df['yearMonth'][ind].head(1).to_string()).group()
    end_date = re.search(r'\w{4}-\w{2}', df['yearMonth'][ind].tail(1).to_string()).group()
    start_year = int(start_date[0:4])
    end_year = int(end_date[0:4]) 
    start_month = int(start_date[5:7]) 
    last_month = int(end_date[5:7])
            

    # first year
    for month in range(start_month, 13):
        if month<10:
            date = start_date[0:4]+"-0"+str(month)
        else:
            date = start_date[0:4]+"-"+str(month)
            # try:
        try:
            commit_hash = subprocess.check_output(['git', 'rev-list', '-n', '1', f'--before="{date}"', 'master'], stderr=subprocess.DEVNULL).decode().strip()
        except:
            try:
                commit_hash = subprocess.check_output(['git', 'rev-list', '-n', '1', f'--before="{date}"', 'main'], stderr=subprocess.DEVNULL).decode().strip()
            except:
                try:
                    commit_hash = subprocess.check_output(['git', 'rev-list', '-n', '1', f'--before="{date}"', 'HEAD'], stderr=subprocess.DEVNULL).decode().strip()
                except:
                    print("Error with getting size for "+orig+", "+str(i)+", on date: "+date)
                    continue
        try:
            if commit_hash != '':
                subprocess.run(['git', 'checkout', commit_hash], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT, check=True)
                command = ['du', '-sb', '--exclude=.git', a]
                output = subprocess.check_output(command).decode().strip()
                size_in_bytes = int(output.split()[0])
            else:
                size_in_bytes = 0
            pos = (df['slug'] == orig) & (df['yearMonth'] == date)
            df.loc[ pos , 'size'] = size_in_bytes/1000 
        except:
            print("Error with getting size for "+orig+", "+str(i)+", on date: "+date)  


    # middle years
    for year in range (start_year+1, end_year):
        for month in range(1, 13):
            if month<10:
                date = str(year)+"-0"+str(month)
            else:
                date = str(year)+"-"+str(month)
            # try:
            try:
                commit_hash = subprocess.check_output(['git', 'rev-list', '-n', '1', f'--before="{date}"', 'master'], stderr=subprocess.DEVNULL).decode().strip()
            except:
                try:
                    commit_hash = subprocess.check_output(['git', 'rev-list', '-n', '1', f'--before="{date}"', 'main'], stderr=subprocess.DEVNULL).decode().strip()
                except:
                    try:
                        commit_hash = subprocess.check_output(['git', 'rev-list', '-n', '1', f'--before="{date}"', 'HEAD'], stderr=subprocess.DEVNULL).decode().strip()
                    except:
                        print("Error with getting size for "+orig+", "+str(i)+", on date: "+date)
                        continue
            try:
                if commit_hash != '':
                    subprocess.run(['git', 'checkout', commit_hash], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT, check=True)
                    command = ['du', '-sb', '--exclude=.git', a]
                    output = subprocess.check_output(command).decode().strip()
                    size_in_bytes = int(output.split()[0])
                else:
                    size_in_bytes = 0
                pos = (df['slug'] == orig) & (df['yearMonth'] == date)
                df.loc[ pos , 'size'] = size_in_bytes/1000 
            except:
                print("Error with getting size for "+orig+", "+str(i)+", on date: "+date)

    # last year
    for month in range(1, last_month+1):
        if month<10:
            date = str(end_year)+"-0"+str(month)
        else:
            date = str(end_year)+"-"+str(month)
        # try:
        try:
            commit_hash = subprocess.check_output(['git', 'rev-list', '-n', '1', f'--before="{date}"', 'master'], stderr=subprocess.DEVNULL).decode().strip()
        except:
            try:
                commit_hash = subprocess.check_output(['git', 'rev-list', '-n', '1', f'--before="{date}"', 'main'], stderr=subprocess.DEVNULL).decode().strip()
            except:
                try:
                    commit_hash = subprocess.check_output(['git', 'rev-list', '-n', '1', f'--before="{date}"', 'HEAD'], stderr=subprocess.DEVNULL).decode().strip()
                except:
                    print("Error with getting size for "+orig+", "+str(i)+", on date: "+date)
                    continue
        try:
            if commit_hash != '':
                subprocess.run(['git', 'checkout', commit_hash], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT, check=True)
                command = ['du', '-sb', '--exclude=.git', a]
                output = subprocess.check_output(command).decode().strip()
                size_in_bytes = int(output.split()[0])
            else:
                size_in_bytes = 0
            pos = (df['slug'] == orig) & (df['yearMonth'] == date)
            df.loc[ pos , 'size'] = size_in_bytes/1000 
        except:
            print("Error with getting size for "+orig+", "+str(i)+", on date: "+date)    
    if i%10 == 0:
        print(orig + " "+str(i))
        df.to_csv("/data3/emilyngu/final_subset_NA_size.csv")
df.to_csv("/data3/emilyngu/final_subset_NA_size.csv")

