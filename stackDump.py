#!/usr/bin/env python
# coding: utf-8

# # StackDump #
# 
# This script collects questions, answers and comments from Stack Exchange sites.
# 
# To use this script, you will need a Stack Exchange API key that you put in a plain text file named stackApiKey.txt and put in the same directory as this notebook.

# In[ ]:


from stackapi import StackAPI
from datetime import datetime, timedelta
import time
import csv
import pandas as pd

################################
# Edit collection settings here:
community = 'stackoverflow'
tag = 'python'
# Set the period for collection
startDate = datetime(2020, 5, 20)
endDate = datetime(2020, 5, 31)
# Set the length of each api call in days. 
# For popular tags on StackOverflow, comments often surpass the API threshold of 100,000 records by 3-4 days.
step = 3
# Set a pause length in seconds to not violate the data cap on the API
pause = 0
################################

stepDate = startDate + timedelta(days=step)
keyfile = open('stackApiKey.txt', 'r') 
apiKey = keyfile.read() 

SITE = StackAPI(community, key=apiKey)
SITE.page_size = 100
SITE.max_pages = 1000

# Items to be dropped from datasets
question_drop = ['owner_profile_image',
                 'owner_link',
                 'migrated_from_other_site_styling_tag_background_color',
                 'migrated_from_other_site_styling_tag_foreground_color',
                 'migrated_from_other_site_styling_link_color',
                 'migrated_from_other_site_related_sites',
                 'migrated_from_other_site_markdown_extensions',
                 'migrated_from_other_site_launch_date',
                 'migrated_from_other_site_open_beta_date',
                 'migrated_from_other_site_site_state',
                 'migrated_from_other_site_high_resolution_icon_url',
                 'migrated_from_other_site_twitter_account',
                 'migrated_from_other_site_favicon_url',
                 'migrated_from_other_site_icon_url',
                 'migrated_from_other_site_audience',
                 'migrated_from_other_site_site_url',
                 'migrated_from_other_site_api_site_parameter',
                 'migrated_from_other_site_logo_url',
                 'migrated_from_other_site_name',
                 'migrated_from_other_site_site_type',
                 'migrated_from_other_site_closed_beta_date',
                 'migrated_from_other_site_aliases']
comment_drop = ['owner_profile_image',
                'owner_link',
                'reply_to_user_profile_image',
                'reply_to_user_link']
answer_drop = ['owner_profile_image',
               'owner_link']

# Collect the datasets
while stepDate < endDate:
    # Get questions
    questions = SITE.fetch('questions', fromdate=startDate, todate=stepDate, tagged=tag, filter='withbody')
    df = pd.json_normalize(questions['items'],sep='_')
    # Clean up
    df.drop(question_drop, inplace=True, axis=1, errors='ignore')
    if 'last_activity_date' in df.columns:
        df['last_activity_date'] = pd.to_datetime(df['last_activity_date'], unit='s')
    if 'creation_date' in df.columns:
        df['creation_date'] = pd.to_datetime(df['creation_date'], unit='s')
    if 'last_edit_date' in df.columns:
        df['last_edit_date'] = pd.to_datetime(df['last_edit_date'], unit='s')
    if 'closed_date' in df.columns:
        df['closed_date'] = pd.to_datetime(df['closed_date'], unit='s')
    if 'migrated_from_on_date' in df.columns:
        df['migrated_from_on_date'] = pd.to_datetime(df['migrated_from_on_date'], unit='s')
    # Write processed trajectories to csv
    df.to_csv(community+'_'+tag+'_'+startDate.strftime('%Y-%m-%d')+'_'+stepDate.strftime('%Y-%m-%d')+'_questions.csv')
    print('Questions '+startDate.strftime('%Y-%m-%d')+' to '+stepDate.strftime('%Y-%m-%d')+' collected')
    time.sleep(pause)

    # Get comments
    comments = SITE.fetch('comments', fromdate=startDate, todate=stepDate, tagged=tag, filter='withbody')
    df = pd.json_normalize(comments['items'],sep='_')
    # Clean up
    df.drop(comment_drop, inplace=True, axis=1, errors='ignore')
    if 'creation_date' in df.columns:
        df['creation_date'] = pd.to_datetime(df['creation_date'], unit='s')
    # Write processed trajectories to csv
    df.to_csv(community+'_'+tag+'_'+startDate.strftime('%Y-%m-%d')+'_'+stepDate.strftime('%Y-%m-%d')+'_comments.csv')
    print('Comments '+startDate.strftime('%Y-%m-%d')+' to '+stepDate.strftime('%Y-%m-%d')+' collected')
    time.sleep(pause)
        
    # Get answers
    answers = SITE.fetch('answers', fromdate=startDate, todate=stepDate, tagged=tag, filter='withbody')
    df = pd.json_normalize(answers['items'],sep='_')
    # Clean up
    df.drop(answer_drop, inplace=True, axis=1, errors='ignore')
    if 'last_activity_date' in df.columns:
        df['last_activity_date'] = pd.to_datetime(df['last_activity_date'], unit='s')
    if 'creation_date' in df.columns:
        df['creation_date'] = pd.to_datetime(df['creation_date'], unit='s')
    if 'last_edit_date' in df.columns:
        df['last_edit_date'] = pd.to_datetime(df['last_edit_date'], unit='s')
    if 'community_owned_date' in df.columns:
        df['community_owned_date'] = pd.to_datetime(df['community_owned_date'], unit='s')
    # Write processed trajectories to csv
    df.to_csv(community+'_'+tag+'_'+startDate.strftime('%Y-%m-%d')+'_'+stepDate.strftime('%Y-%m-%d')+'_answers.csv')
    print('Answers '+startDate.strftime('%Y-%m-%d')+' to '+stepDate.strftime('%Y-%m-%d')+' collected')
    time.sleep(pause)
    # Adjust timeframe for next loop
    startDate = stepDate + timedelta(days=1)
    stepDate = startDate + timedelta(days=step)

else:
    # Get questions
    questions = SITE.fetch('questions', fromdate=startDate, todate=endDate, tagged=tag, filter='withbody')
    df = pd.json_normalize(questions['items'],sep='_')
    # Clean up
    df.drop(question_drop, inplace=True, axis=1, errors='ignore')
    if 'last_activity_date' in df.columns:
        df['last_activity_date'] = pd.to_datetime(df['last_activity_date'], unit='s')
    if 'creation_date' in df.columns:
        df['creation_date'] = pd.to_datetime(df['creation_date'], unit='s')
    if 'last_edit_date' in df.columns:
        df['last_edit_date'] = pd.to_datetime(df['last_edit_date'], unit='s')
    if 'closed_date' in df.columns:
        df['closed_date'] = pd.to_datetime(df['closed_date'], unit='s')
    if 'migrated_from_on_date' in df.columns:
        df['migrated_from_on_date'] = pd.to_datetime(df['migrated_from_on_date'], unit='s')
    # Write processed trajectories to csv
    df.to_csv(community+'_'+tag+'_'+startDate.strftime('%Y-%m-%d')+'_'+endDate.strftime('%Y-%m-%d')+'_questions.csv')
    print('Questions '+startDate.strftime('%Y-%m-%d')+' to '+endDate.strftime('%Y-%m-%d')+' collected')
    time.sleep(pause)

    # Get comments
    comments = SITE.fetch('comments', fromdate=startDate, todate=endDate, tagged=tag, filter='withbody')
    df = pd.json_normalize(comments['items'],sep='_')
    # Clean up
    df.drop(comment_drop, inplace=True, axis=1, errors='ignore')
    if 'creation_date' in df.columns:
        df['creation_date'] = pd.to_datetime(df['creation_date'], unit='s')
    # Write processed trajectories to csv
    df.to_csv(community+'_'+tag+'_'+startDate.strftime('%Y-%m-%d')+'_'+endDate.strftime('%Y-%m-%d')+'_comments.csv')
    print('Comments '+startDate.strftime('%Y-%m-%d')+' to '+endDate.strftime('%Y-%m-%d')+' collected')
    time.sleep(pause)
        
    # Get answers
    answers = SITE.fetch('answers', fromdate=startDate, todate=endDate, tagged=tag, filter='withbody')
    df = pd.json_normalize(answers['items'],sep='_')
    # Clean up
    df.drop(answer_drop, inplace=True, axis=1, errors='ignore')
    if 'last_activity_date' in df.columns:
        df['last_activity_date'] = pd.to_datetime(df['last_activity_date'], unit='s')
    if 'creation_date' in df.columns:
        df['creation_date'] = pd.to_datetime(df['creation_date'], unit='s')
    if 'last_edit_date' in df.columns:
        df['last_edit_date'] = pd.to_datetime(df['last_edit_date'], unit='s')
    if 'community_owned_date' in df.columns:
        df['community_owned_date'] = pd.to_datetime(df['community_owned_date'], unit='s')
    # Write processed trajectories to csv
    df.to_csv(community+'_'+tag+'_'+startDate.strftime('%Y-%m-%d')+'_'+endDate.strftime('%Y-%m-%d')+'_answers.csv')
    print('Answers '+startDate.strftime('%Y-%m-%d')+' to '+endDate.strftime('%Y-%m-%d')+' collected')
print('All done')    


# In[ ]:


import pandas as pd
import sys
import glob
import d6tstack.combine_csv

# Combine files as one per month per post type
community = 'stackoverflow'
tag = 'python'
year = 2020
month = 5

files = list(glob.glob('*_'+str(year)+'-'+str(month).zfill(2)+'-*questions.csv'))
combined = d6tstack.combine_csv.CombinerCSV(files).to_csv_combine(community+'_'+tag+'_'+str(year)+'-'+str(month).zfill(2)+'_questions.csv')
df = pd.read_csv(community+'_'+tag+'_'+str(year)+'-'+str(month).zfill(2)+'_questions.csv', index_col=[0])
df['post_type']='question'
df.rename(columns={'question_id': 'post'}, inplace=True)
df.drop({'filepath', 'filename'}, inplace=True, axis=1, errors='ignore')
df.to_csv(community+'_'+tag+'_'+str(year)+'-'+str(month).zfill(2)+'_questions.csv', index=False)
    
# Combine comment files
files = list(glob.glob('*_'+str(year)+'-'+str(month).zfill(2)+'-*comments.csv'))
combined = d6tstack.combine_csv.CombinerCSV(files).to_csv_combine(community+'_'+tag+'_'+str(year)+'-'+str(month).zfill(2)+'_comments.csv')
df = pd.read_csv(community+'_'+tag+'_'+str(year)+'-'+str(month).zfill(2)+'_comments.csv', index_col=[0])
df['post_type']='comment'
df.rename(columns={'comment_id': 'post', 'post_id': 'reply_to'}, inplace=True)
df.drop({'filepath', 'filename'}, inplace=True, axis=1, errors='ignore')
df.to_csv(community+'_'+tag+'_'+str(year)+'-'+str(month).zfill(2)+'_comments.csv', index=False)
    
# Combine answer files
files = list(glob.glob('*_'+str(year)+'-'+str(month).zfill(2)+'-*answers.csv'))
combined = d6tstack.combine_csv.CombinerCSV(files).to_csv_combine(community+'_'+tag+'_'+str(year)+'-'+str(month).zfill(2)+'_answers.csv')
df = pd.read_csv(community+'_'+tag+'_'+str(year)+'-'+str(month).zfill(2)+'_answers.csv', index_col=[0])
df['post_type']='answer'
df.rename(columns={'answer_id': 'post', 'question_id': 'reply_to'}, inplace=True)
df.drop({'filepath', 'filename'}, inplace=True, axis=1, errors='ignore')
df.to_csv(community+'_'+tag+'_'+str(year)+'-'+str(month).zfill(2)+'_answers.csv', index=False)

print('All done')


# In[ ]:


# Create a combined file of all posts for a month
community = 'stackoverflow'
tag = 'python'
year = 2020
month = 5
files = [community+'_'+tag+'_'+str(year)+'-'+str(month).zfill(2)+'_questions.csv', 
         community+'_'+tag+'_'+str(year)+'-'+str(month).zfill(2)+'_comments.csv',
         community+'_'+tag+'_'+str(year)+'-'+str(month).zfill(2)+'_answers.csv']
combined = d6tstack.combine_csv.CombinerCSV(files).to_csv_combine(community+'_'+tag+'_'+str(year)+'-'+str(month).zfill(2)+'.csv')
df = pd.read_csv(community+'_'+tag+'_'+str(year)+'-'+str(month).zfill(2)+'.csv', index_col=[0], dtype=object)
df.drop({'filepath', 'filename'}, inplace=True, axis=1, errors='ignore')
df.to_csv(community+'_'+tag+'_'+str(year)+'-'+str(month).zfill(2)+'.csv', index=False)


# In[ ]:


# Create monthly combined files by post creation date BROKEN
import pandas as pd
import sys
import glob
import d6tstack.combine_csv

community = 'stackoverflow'
tag = 'python'
year = 2020
startMonth = 3
endMonth = 5

files = list(glob.glob('*.csv'))

combined = d6tstack.combine_csv.CombinerCSV(files).to_csv_combine(community+'_'+tag+'_'+str(year)+'-'+str(startMonth).zfill(2)+'_'+str(endMonth).zfill(2)+'.csv')
df = pd.read_csv(community+'_'+tag+'_'+str(year)+'-'+str(startMonth).zfill(2)+'_'+str(endMonth).zfill(2)+'.csv', index_col=[0], dtype=object)
df.drop({'filepath', 'filename'}, inplace=True, axis=1, errors='ignore')
df.to_csv(community+'_'+tag+'_'+str(year)+'-'+str(startMonth).zfill(2)+'_'+str(endMonth).zfill(2)+'.csv', index=False)

month = startMonth
while month <= endMonth:
    m = df['creation_date'].str.contains('-'+str(month).zfill(2)+'-')
    df2 = df[m].reset_index(drop=True)
    df2.to_csv(community+'_'+tag+'_'+str(year)+'-'+str(month).zfill(2)+'_creation.csv')
    month = month + 1

print('All done')

