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
import git
from datetime import date, time
import requests
from prometheus_client import start_http_server, Summary, Counter
from pydriller.repository import Repository  
from pydriller.metrics.process.commits_count import CommitsCount
import pydriller # Pydriller is the library we use to go through the commits on disc 
from git import Repo, Commit
import csv
import os
import pandas as pd
import numpy as np
from git import Repo
from builtins import any as b_any
import stscraper as scraper
import warnings
warnings.filterwarnings("ignore")
from urllib.request import urlopen
from bs4 import BeautifulSoup
from time import strptime
import re

d = pd.read_csv("final_subset_peaked_early.csv")
df = pd.DataFrame(d)
df['size'] = None
df2 = pd.DataFrame(df['slug'].unique(), columns=['slug'])

for i in range(0,len(df2)):
    s = orig = df2['slug'][i]
    ind = (df['slug'] == orig)

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

    if os.path.exists(a) == False:
        a = "/data2/christian/npm/repos/"+st
        if os.path.exists(a) == False:
            a = "/data2/christian/npm/repos2/"+st
            if os.path.exists(a) == False:
                try:
                    a = "/data3/emilyngu/" + st
                    Repo.clone_from("https://github.com/"+st, a)
                except:
                    print("Error with cloning repo, "+str(i)+", "+a)
                    continue 
                if os.path.exists(a) == False:
                    print("Error with cloning repo, "+str(i)+", "+a)
                    continue 
    
    os.chdir(a)
     
    end_date = re.search(r'\w{4}-\w{2}', df['yearMonth'][ind].tail(1).to_string()).group()
    end_year = int(end_date[0:4])  
    last_month = int(end_date[5:7])


    if last_month<10:
        date = str(end_year)+"-0"+str(last_month)
    else:
        date = str(end_year)+"-"+str(last_month)
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
                continue
    try:
        if commit_hash != '':
            subprocess.run(['git', 'checkout', commit_hash], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT, check=True)
            command = ['du', '-sb', '--exclude=.git', a]
            output = subprocess.check_output(command).decode().strip()
            size_in_bytes = int(output.split()[0])
        else:
            size_in_bytes = 0
        df.loc[ ind , 'size'] = size_in_bytes/1000 
    except:
        print("Error with getting size for "+orig+", "+str(i)+", on date: "+date)

df.to_csv("final_subset_peaked_early.csv")
