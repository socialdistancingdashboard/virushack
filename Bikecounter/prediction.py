import json
import os
import pandas as pd
import numpy as np
from datetime import datetime
import statsmodels.formula.api as sm
from matplotlib import pyplot as plt

os.chdir(os.path.dirname(__file__))

data = json.load(open("fahrrad_zaehler.json", "r"))

for d in data:
  df = pd.DataFrame(np.array(
    data[d][:-1]), columns=["date", "bike_count"])
  df.date = df.date.apply(
    lambda x: datetime(
      int(x.split("/")[2]),
      int(x.split("/")[0]),
      int(x.split("/")[1])
    )
  )
  df["year"] = df.date.apply(lambda x: x.year)
  df["month"] = df.date.apply(lambda x: x.month)
  df["weekday"] = df.date.apply(lambda x: x.weekday())
  df["bike_count"] = df.bike_count.astype("float16")

  df = df.join(pd.get_dummies(df.weekday, prefix="weekday"))
  df = df.join(pd.get_dummies(df.month, prefix="month"))

  df["workingday"] = df["weekday"].apply(lambda x: 1 if x < 5 else 0)
  df["saturday"] = df["weekday_5"]
  df["sunday"] = df["weekday_6"]


  result = sm.ols(formula="""
    bike_count ~ 
    year +
    month_1 + 
    month_2 + 
    month_3 + 
    month_4 + 
    month_5 + 
    month_6 + 
    month_7 + 
    month_8 + 
    month_9 + 
    month_10 + 
    month_11 + 
    month_12 +   
    weekday_0 + 
    weekday_1 + 
    weekday_2 + 
    weekday_3 + 
    weekday_4 + 
    weekday_5 + 
    weekday_6 
  """, data=df).fit()
  result.summary()

  df["bike_count_prediction"] = result.predict(df)

  df[(df.date > datetime(2019,1,1))].plot(
    x="date", 
    y=["bike_count", "bike_count_prediction"],
    linewidth=1,
    title=d)

  plt.ylabel("bike count")

  plt.tight_layout()
  plt.savefig("data_viz_%s.png" % d)

  break

lens = [print(a) for a in data[d]]

df.head()
df.info()