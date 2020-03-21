from matplotlib import pyplot as plt
import os
import pandas as pd
from datetime import datetime
os.chdir(os.path.dirname(__file__))

dir, folders, files = next(os.walk("data"))

master = pd.DataFrame()
for f in folders:
  print(f)
  path = os.path.join(dir, f, f + ".json")
  df = pd.read_json(path)
  df = df.reset_index()
  master = pd.concat([master, df])

master = master.reset_index()
#master.date = master.date.apply(lambda x: datetime(
#  x.split("-")[0] ,x.split("-")[1], x.split("-")[2]))


lineProducts = ["bus", "national", "nationalExpress", "regional", "suburban"]
fig, axes = plt.subplots(nrows=len(lineProducts), ncols=1)
fig.set_figheight(10)
fig.set_figwidth(5)
for index, lineProduct in enumerate(lineProducts):
  master[master["index"]==lineProduct].plot(
    x="date", 
    y=["planned_stops", "cancelled_stops"],
    title=lineProduct,
    ax=axes[index],
    sharex=True)
plt.tight_layout()
plt.savefig("data_viz.png")