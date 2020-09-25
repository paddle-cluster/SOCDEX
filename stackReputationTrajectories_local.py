#!/usr/bin/env python
# coding: utf-8

# This notebook collects, assembles and plots reputation score trajectories for one or more StackOverflow users.
# 
# It requires a StackExchange API key that can be acquired here: https://api.stackexchange.com
# 
# Create a plain text file with an API key and another with one or more StackOverlow user ids arranged one per line.

# In[ ]:


# Collect StackOverflow reputation trajectories
import tkinter as tk
from tkinter import filedialog
from stackapi import StackAPI
from datetime import datetime
import csv
from IPython.display import clear_output
import pandas as pd

#Choose a plain text file with one or more StackOverflow user ids, one per line
root = tk.Tk()
root.withdraw()
userid_filename = filedialog.askopenfilename(title = 'Select text file with user ids')
print (str(userid_filename)+' selected')

# Collect reputation change events from user ids in the userid_filename txt file
community = 'stackoverflow'
apiKey = 'e8*PJJPB)W5I9H0)MHvvfA(('
SITE = StackAPI(community, key=apiKey)
SITE.page_size = 100
SITE.max_pages = 1000
userid = []

with open(userid_filename) as ids:
    userCount = 0
    for line in ids:
        clear_output(wait=True)
        userCount = userCount + 1
        userid = line.strip()
        # Collect reputation events
        events = SITE.fetch('users/'+userid+'/reputation-history')
        df = pd.json_normalize(events['items'],sep='_') 
        # Create nomalized timestamp timeline
        df = df.iloc[::-1]
        df['time_delta'] = df['creation_date'].diff()
        # Calculate cumulative sum of reputation
        df['days'] = df['time_delta'].cumsum() / 86400
        df['reputation'] = df['reputation_change'].cumsum()
        # Convert timestamps to datetime
        df['creation_date'] = pd.to_datetime(df['creation_date'], unit='s')
        # Write processed trajectories to csv
        df.to_csv('reputation_trajectory_'+userid+'.csv')
        print('Reputation trajectories collected: '+str(userCount))
print('All done')     


# In[ ]:


import pandas as pd
import csv
import dask.dataframe as dd
import altair as alt

df = dd.read_csv('reputation_trajectory_*.csv')
df = df.compute(index=0)
df['user_id'] = df['user_id'].astype('category')

selection = alt.selection_multi(fields=['user_id'], bind='legend')

chart = alt.Chart(df).mark_line().encode(
    x=alt.X('days', title='Normalized time in days'),
    y=alt.Y('reputation', title='Reputation score'),
    color='user_id',
    opacity=alt.condition(selection, alt.value(1), alt.value(0.2))
).properties(
    title='Reputation Trajectories',
    width=800,
    height=600
).add_selection(
    selection
)
chart.display()
chart.save('rep.html')


# In[ ]:


import altair as alt

alt.Chart(df).mark_bar().encode(x='reputation_change:Q', y='user_id:N', color='reputation_history_type:N')


# In[ ]:




