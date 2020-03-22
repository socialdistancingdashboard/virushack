import json
import os
import pandas as pd
import numpy as np
from datetime import datetime
import statsmodels.formula.api as sm
from matplotlib import pyplot as plt
from statsmodels.iolib.smpickle import load_pickle

try: 
  # modifies path if used in ipython / jupyter
  get_ipython().__class__.__name__
  os.chdir(os.path.dirname(__file__))
except:
  pass


class BikePrediction:
  def __init__(self):
    self.dummies = ["month_" + str(i+1) for i in range(12)]
    self.dummies.extend(["weekday_" + str(i) for i in range(7)])

  def enrich_df(self, df):
    """ Adds dummy variables to dataframe """
    df["year"] = df.date.apply(lambda x: x.year)
    df["month"] = df.date.apply(lambda x: x.month)
    df["weekday"] = df.date.apply(lambda x: x.weekday())
    if "bike_count" in df:
      # only for training
      df["bike_count"] = df.bike_count.astype("float16")
    df = df.join(pd.get_dummies(df.weekday, prefix="weekday"))
    df = df.join(pd.get_dummies(df.month, prefix="month"))
    return df

  def train(
    self,
    path_to_training_data="fahrrad_zaehler.json", 
    out_path="prediction_parameters"):
    
    """ This trains and saves a model for all stations found in 
    path.json file. Output folder defaults to /prediction_parameters."""

    data = json.load(open("fahrrad_zaehler.json", "r"))

    for d in data:
      print("start training for station %s", d)
      # load data and skip last row. Last row contains the overall sum.
      df = pd.DataFrame(np.array(
        data[d][:-1]), columns=["date", "bike_count"])

      # transform "YYYY/MM/DD" to datetime object
      df.date = df.date.apply(
        lambda x: datetime(
          int(x.split("/")[2]),
          int(x.split("/")[0]),
          int(x.split("/")[1])
        )
      )

      # define new columns for regression (happens inplace)
      df = self.enrich_df(df)

      # these are not used at the moment
      # df["workingday"] = df["weekday"].apply(lambda x: 1 if x < 5 else 0)
      # df["saturday"] = df["weekday_5"]
      # df["sunday"] = df["weekday_6"]

      # Perform regression but use data only until 2020-01-01
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
      """, data=df[(df.date < datetime(2020, 1, 1))]).fit()

      result.save(os.path.join(out_path, d + ".model"))

      # visualize
      df["bike_count_prediction"] = result.predict(df)

      df[(df.date > datetime(2019,1,1))].plot(
        x="date", 
        y=["bike_count", "bike_count_prediction"],
        linewidth=1,
        title="""
          trained with data until 2020-01-01 \n
          displayed data from 2019 onwards \n
          Station %s""" % d)
      plt.ylabel("bike count")
      plt.tight_layout()
      plt.savefig(os.path.join(out_path, "prediction_%s.png" % d))
      plt.close()
      print("model and visualization saved to '%s'" % out_path)

  def predict_single(self, station_string, day, path_to_models="prediction_parameters" ):
    """ Makes a prediction for a station_string and a given day """
    if not type(day) == datetime:
      raise "Please pass a proper datetime object."


    df = pd.DataFrame([day], columns=["date"])
    self.enrich_df(df)
    for d in self.dummies:
      if not d in df:
        df[d] = 0
    df["month_" + str(df.iloc[0].month)] = 1
    df["weekday_" + str(df.iloc[0].weekday)] = 1

    # load model and predict
    model = load_pickle(os.path.join(path_to_models, station_string + ".model"))
    df["prediction"] = model.predict(df)
    # return prediction as plain number
    return df.iloc[0]["prediction"]

  def predict_series(self, station_string, days, path_to_models="prediction_parameters" ):
    """ Predict all given days. Returns a dataframe with date and prediction """
    if not type(days) == pd.core.series.Series:
      assert "Please pass days as a pandas Series. E.g. days = df['date']"

    df = pd.DataFrame()
    df["date"] = days    
    df = self.enrich_df(df)
    model = load_pickle(os.path.join(path_to_models, station_string + ".model"))
    df["prediction"] = model.predict(df)
    return df[["date", "prediction"]]


if __name__ == "__main__":
  # instance of class
  BP = BikePrediction()
  
  # run training on all classes
  # BP.train()

  # make a single prediction
  prediction = BP.predict_single(
    station_string="('9.92926', '51.53692')",
    day=datetime(2020,1,1)
  )

  BP.predict_series(
    station_string="('9.92926', '51.53692')",
    days=df.date
  )
