import os
import pandas as pd
import stscraper as scraper
from urllib.request import urlopen
from bs4 import BeautifulSoup
from time import strptime

df_long = pd.read_csv("final_subset_peaked_early.csv")
df = pd.DataFrame(df_long['slug'].unique(), columns=['slug'])



for i in range(0, len(df)):
    s = df['slug'][i]
    datePeak = 202012
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
        url = "https://github.com/" + s
        html = urlopen(url).read()
        soup = BeautifulSoup(html, features="html.parser")
        
        # kill all script and style elements
        for script in soup(["script", "style"]):
            script.extract()    # rip it out
        # get text
        text = soup.get_text()
        # break into lines and remove leading and trailing space on each
        lines = (line.strip() for line in text.splitlines())
        # break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # drop blank lines
        text = '\n'.join(chunk for chunk in chunks if chunk)

        if text.find("archived by the owner on") == -1:
            df_long.loc[ (df_long['slug'] == s)  , 'archived'] = False
            continue
        else:
            df_long.loc[ (df_long['slug'] == s)  , 'archived'] = True

        month = text[text.find("archived by the owner on")+25:text.find("archived by the owner on")+28]
        month = strptime(month,'%b').tm_mon

        if text[text.find("archived by the owner on")+30] == ",":
            year = text[text.find("archived by the owner on")+32:text.find("archived by the owner on")+36]
            yearMonth = year + "-"+str(month)
        elif text[text.find("archived by the owner on")+30].isdigit():
            year = text[text.find("archived by the owner on")+33:text.find("archived by the owner on")+37]
            yearMonth = year + "-"+str(month)



        df_long.loc[ (df_long['slug'] == s)  , 'archivedAt'] = yearMonth 
    except:
        print("Error with repo info or getting archivedAt date:")

df_long.to_csv("final_subset_peaked_early.csv")
