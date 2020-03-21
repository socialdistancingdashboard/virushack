import json
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly
import datetime

st.write('Fahrräder')

# Selection box for cities
city = st.sidebar.selectbox(
	'Select city',
	('Karlsruhe', 'Freiburg_Wiwilibruecke', 'Freiburg_Hindenburgstr'))
	
# Input date range
start = st.sidebar.date_input('start', value=datetime.date(2020, 1, 1))
end = st.sidebar.date_input('end') # no value = today

# Flip date range if entered the wrong way
if (start>end):
	tmp = start
	start = end
	end = tmp

# Select whether last years data should be drawn
show_history = st.sidebar.checkbox('show data from previous year', value=True)

# Load data
file = 'bikecount_'+city+'_2013-2020.json'
with open(file,'r') as f:
	data = json.load(f)

# Prepare dataframe
tmp =[]
for d in data[:-2]:
	tmp.append((d[0],d[1]))
df = pd.DataFrame(tmp,columns=['date','bikecount'])
df['date']=df['date'].astype('datetime64[ns]')
df['bikecount']=df['bikecount'].astype(float)

# debug output
#st.write(df.dtypes)
#st.dataframe(df)

# fiter date range
df_filtered = df[( df['date'] > pd.to_datetime(start) ) & ( df['date'] < pd.to_datetime(end) ) ]

# filter also same range from last year
historystart = start.replace(year=start.year-1)
historyend = end.replace(year=end.year-1)

df_filtered_history = df[( df['date'] > pd.to_datetime(historystart) ) & ( df['date'] < pd.to_datetime(historyend) ) ]
df_filtered_history['date'] = df_filtered_history['date'] + pd.DateOffset(years=1)

# plot
fig=plt.figure()
if show_history:
	line_history, = plt.plot(df_filtered_history['date'],df_filtered_history['bikecount'],'lightsteelblue')
	line_history.set_label('Last year')
line, = plt.plot(df_filtered['date'],df_filtered['bikecount'],'tab:blue')
line.set_label('This year')
#plt.legend()
plt.title('Bikecount in '+city.replace('_', ' '))
plt.xlabel('Datum')
plt.ylabel('Fahrräder')
st.plotly_chart(fig)
