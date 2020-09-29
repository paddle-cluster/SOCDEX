#!/usr/bin/env python
# coding: utf-8

# # stackUserViz #
# 
# 3 scripts for collecting, processing and visualizing user activity trajectories on Stack Exchange sites.
# 
# - The first script collects questions, answers, and comments from Stack Exchange sites for a particular user. It produces one CSV file with all questions, answer and comments. 
# - The second script collects reputation change events, orders the data, computes a running reputation score, and writes them to a CSV file.
# - The third script loads and processes the posting activity and reputation event files before summarizing and plotting the data. A short descriptive statistical summary is produced and saved as a text file and then a plot is generated showing posting activity as a stacked bar chart with questions, answers and comments, and reputation score as a line graph. Both datasets are aggregated and plotted monthly to show a continuous timeline that visualizes a user's activity on the platform as a trajectory.
# 
# To use these scripts, you will need a Stack Exchange API key that you put in a plain text file named stackApiKey.txt and put in the same directory as this notebook.


# Collect questions, answers and comments

from stackapi import StackAPI
from datetime import datetime
import csv
import pandas as pd
import sys
import os
import glob
import d6tstack.combine_csv

################################
# Edit collection settings here:
community = 'stackoverflow'
################################

keyfile = open('stackApiKey.txt', 'r') 
apiKey = keyfile.read() 

SITE = StackAPI(community, key=apiKey)
SITE.page_size = 100
SITE.max_pages = 10000

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

# Choose a user
userId = input("Which "+community+" user ID would you like to collect for? ")

# Get questions
questions = SITE.fetch('users/'+userId+'/questions', filter='withbody')
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
df['post_type']='question'
df.to_csv(community+'_'+userId+'_questions.csv')
print('Questions collected')

# Get comments
comments = SITE.fetch('users/'+userId+'/comments', filter='withbody')
df = pd.json_normalize(comments['items'],sep='_')
# Clean up
df.drop(comment_drop, inplace=True, axis=1, errors='ignore')
if 'creation_date' in df.columns:
    df['creation_date'] = pd.to_datetime(df['creation_date'], unit='s')
# Write processed trajectories to csv
df['post_type']='comment'
df.to_csv(community+'_'+userId+'_comments.csv')
print('Comments collected')
        
# Get answers
answers = SITE.fetch('users/'+userId+'/answers', filter='withbody')
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
df['post_type']='answer'
df.to_csv(community+'_'+userId+'_answers.csv')
print('Answers collected')

#Create a combined file
files = [community+'_'+userId+'_questions.csv', 
         community+'_'+userId+'_comments.csv',
         community+'_'+userId+'_answers.csv']
combined = d6tstack.combine_csv.CombinerCSV(files).to_csv_combine(community+'_'+userId+'.csv')
df = pd.read_csv(community+'_'+userId+'.csv', index_col=[0], dtype=object)
df.drop({'filepath', 'filename'}, inplace=True, axis=1, errors='ignore')
df.to_csv(community+'_'+userId+'.csv', index=False)
for file in files:
    os.remove(file)


# Collect reputation events

from stackapi import StackAPI
from datetime import datetime, timedelta
import time
import csv
import pandas as pd
import glob
import os
################################
# Edit collection settings here:
community = 'stackoverflow'
# Set the period for collection
startDate = datetime(2008, 9, 22)
#endDate = datetime(2020, 9, 29)
endDate = datetime.today()
# Set the length of each api call in days. 
step = 365
# Set a pause length in seconds to not violate the data cap on the API
pause = 2
################################

stepDate = startDate + timedelta(days=step)
keyfile = open('stackApiKey.txt', 'r') 
apiKey = keyfile.read() 

SITE = StackAPI(community, key=apiKey)
SITE.page_size = 100
SITE.max_pages = 1000

# Collect reputation events
userId = input('Which '+community+' user ID would you like to collect for?')

while stepDate < endDate:
    events = SITE.fetch('users/'+userId+'/reputation-history', fromdate=startDate, todate=stepDate)
    df = pd.json_normalize(events['items'],sep='_')
    df.to_csv('temp_'+startDate.strftime('%Y-%m-%d')+'_'+stepDate.strftime('%Y-%m-%d')+'.csv')
    time.sleep(pause)
    print(str(startDate)+' to '+str(stepDate)+' collected')
    startDate = stepDate + timedelta(days=1)
    stepDate = startDate + timedelta(days=step)

else:
    events = SITE.fetch('users/'+userId+'/reputation-history', fromdate=startDate, todate=endDate)
    df = pd.json_normalize(events['items'],sep='_')
    df.to_csv('temp_'+startDate.strftime('%Y-%m-%d')+'_'+stepDate.strftime('%Y-%m-%d')+'.csv')
    print(str(startDate)+' to '+str(endDate)+' collected')

# Stitch the yearly files together
files = list(glob.glob('temp_*.csv'))
li = []
for filename in files:
    df1 = pd.read_csv(filename, index_col=None, header=0)
    li.append(df1)
df = pd.concat(li, axis=0, ignore_index=True)
# Sort by creation_date
df = df.sort_values(by = 'creation_date') 

# Create nomalized timestamp timeline
df['time_delta'] = df['creation_date'].diff()
# Calculate cumulative sum of reputation
df['days'] = df['time_delta'].cumsum() / 86400
df['reputation'] = df['reputation_change'].cumsum()
# Convert timestamps to datetime
df['creation_date'] = pd.to_datetime(df['creation_date'], unit='s')

# Write processed reputation events to csv
df.to_csv(community+'_'+userId+'_reputation.csv')

# Clean up temporary files
files = list(glob.glob('temp_*.csv'))
for file in files:
    os.remove(file)

print('Reputation events collected')


# Import user data and visualize it

import pandas as pd
import csv
import numpy as np
from mpl_axes_aligner import align
import matplotlib.pyplot as plt
get_ipython().run_line_magic('matplotlib', 'inline')

community = 'stackoverflow'
userId = input("Which "+community+" user ID would you like to make a snapshot for? ")

df = pd.read_csv(community+'_'+userId+'.csv', parse_dates=['creation_date'])
repdf = pd.read_csv(community+'_'+userId+'_reputation.csv', parse_dates=['creation_date'])

# Descriptive stats
date = df['creation_date']
since = date.min()
print('Active since: '+str(since))

rep = repdf['reputation']
max_rep = rep.max()
print('Reputation: '+str(max_rep))

posts = df.shape[0]
print('Posts: '+str(posts))

df2 = df['post_type'].value_counts()
print(df2)

with open(community+'_'+userId+'_stats.txt', "a") as file:
    file.write('User ID: '+str(userId)+'\n')
    file.write('Active since: '+str(since)+'\n')
    file.write('Reputation: '+str(max_rep)+'\n')
    file.write('Posts: '+str(posts)+'\n')
    df2.to_csv(file, header=None, index='post_type', sep=' ', mode='a')

# Plot activity and reputation on a single figure

# Process posting data
df['month_year'] = pd.to_datetime(df['creation_date']).map(lambda dt: dt.replace(day=1))
df['month_year'] = pd.to_datetime(df['month_year']).dt.date
df1 = df.groupby(['month_year', 'post_type'])['creation_date'].count().reset_index(name='count')
df1 = df1.pivot(index='month_year', columns='post_type', values='count')
df1.index = pd.to_datetime(df1.index)
df1 = df1.resample('MS').asfreq().fillna(0)
df1 = df1.reset_index()
df1.month_year = df1.month_year.dt.date
df1.month_year = df1.month_year.astype('object')
df1[['Answers', 'Comments', 'Questions']] = df1[['answer', 'comment', 'question']].astype('int64') 

# Process reputation data
repdf1 = repdf[['creation_date', 'reputation']].copy()
repdf1['month_year'] = pd.to_datetime(repdf1['creation_date']).map(lambda dt: dt.replace(day=1))
repdf1['month_year'] = pd.to_datetime(repdf1['month_year']).dt.date
repdf1 = repdf1.groupby(['month_year'], sort=False)['reputation'].max()
repdf1.index = pd.to_datetime(repdf1.index)
repdf1 = repdf1.resample('MS').asfreq().fillna(method='ffill')
repdf1 = repdf1.reset_index()
repdf1.month_year = repdf1.month_year.dt.date
repdf1.month_year = repdf1.month_year.astype('object')
repdf1['Reputation'] = repdf1['reputation'].astype('int64')

# Create a merged dataframe
merged = pd.merge(df1, repdf1, on=['month_year'], how='outer')
merged.month_year = pd.to_datetime(merged.month_year)
merged = merged.sort_values('month_year').reset_index(drop=True)

# Plot the figures
fig, ax = plt.subplots(figsize = (15,4))
ax.axhline(0, color='#EEEEEE')
ax1 = merged[['Answers', 'Comments', 'Questions']].plot(kind='bar', legend=False, stacked=True, color=['#284E60', '#F99B45', '#63AAC0'], width=0.8, ax=ax)
ax2 = merged['Reputation'].plot(ax=ax, secondary_y=True, color='#D95980', linewidth=2)

# Axis
align.yaxes(ax1, 0.0, ax2, 0.0, 0.1)
ax.set_xticklabels([t if not i%5 else "" for i,t in enumerate(ax.get_xticklabels())])

# Labels
ax.set_xlabel('Month of Participation', labelpad=10, color='#333333')
ax1.set_ylabel('Posts', labelpad=15, color='#333333')
ax2.set_ylabel('Reputation Score', labelpad=15, color='#333333') 
plt.title('Participation trajectory for '+community+' user '+userId, fontsize=15, color='#333333', loc='left', pad=5)

# Style
for ax in (ax1, ax2):
    ax.spines["top"].set_visible(False)    
    ax.spines["bottom"].set_visible(False)    
    ax.spines["right"].set_visible(False)    
    ax.spines["left"].set_visible(False)
    ax.tick_params(bottom=False, left=False, right=False)
    ax.set_axisbelow(True)
    ax.xaxis.grid(False)
    ax.tick_params(axis='x', pad=-20)
    ax.ticklabel_format(useOffset=False, style='plain', axis='y')
ax1.yaxis.grid(True, color='#EEEEEE')

# Legend
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
leg = ax.legend(lines1 + lines2, labels1 + labels2, frameon=False, loc='upper right', ncol=4, bbox_to_anchor=(1, 1.1))
for text in leg.get_texts():
    plt.setp(text, color = '#333333')

# Save and show figure
save = plt.gcf()
plt.show()
save.savefig(community+'_'+userId+'.png')
