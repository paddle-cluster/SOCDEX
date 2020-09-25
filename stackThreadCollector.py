#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from stackapi import StackAPI
from datetime import datetime
import time
import json
import csv
import urllib.request
from IPython.display import clear_output

#Setup collection criteria:
community = 'meta.stackoverflow'

keyfile = open('stackApiKey.txt', 'r') 
apiKey = keyfile.read() 

SITE = StackAPI(community, key=apiKey)
SITE.page_size = 100
SITE.max_pages = 1000

#Example queries:
#Questions: 'questions', fromdate=datetime(2018,1,1), todate=datetime(2018,1,31), tagged='python', filter='withbody'
#Answers to specific questions: 'questions/' + str(item.get('question_id')) + '/answers', order = 'desc', sort='votes', filter='withbody'
#Free text: 'search/advanced', q='expert* reputation*'

##Change search criteria here:
threads = SITE.fetch('search/advanced', q='expert* reputation*')

with open('threads.txt', 'w') as outfile:
    json.dump(threads, outfile)

print('Data collected')


# In[ ]:


#Write a spreadsheet with the question ids and titles

keylist = ['user_id', 'display_name', 'reputation', 'question_id', 'creation_date', 'title', 'view_count', 'answer_count', 'score', 'accepted_answer_id']

with open('threads.csv', 'w') as output:
    csvwriter = csv.writer(output)
    csvwriter.writerow(keylist)
    
    for items in threads['items']:
        row = [str(items['owner'].get('user_id')), str(items['owner'].get('display_name')), str(items['owner'].get('reputation')), str(items.get('question_id')), str(datetime.fromtimestamp(items.get('creation_date'))), str(items.get('title')), str(items.get('view_count')), str(items.get('answer_count')), str(items.get('score')), str(items.get('accepted_answer_id'))]
        csvwriter.writerow(row)

print('Spreadsheet done')


# In[ ]:


# Save html files

#ADD A CHECK FOR THREAD DUPLICATION...

fileCount = 0
for items in threads['items']:
    clear_output(wait=True)
    id = str(items.get('question_id'))
    urllib.request.urlretrieve ('http://www.stackprinter.com/export?format=HTML&service=meta.stackoverflow&printer=false&question='+id, id+'.html')
    print('Question '+id+' - File '+str(fileCount))
    fileCount = fileCount+1
    time.sleep(10)
    
print('Threads saved')


# In[ ]:


Convert html files to odt for import to Nvivo with Pandoc from the commandline

for f in *.html; do pandoc "$f" -s -o ${f%.html}.odt; done

