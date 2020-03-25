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
  province_abbs = {
    'Baden-Württemberg' : 'BW',
    'Bayern' : 'BY',
    'Berlin' : 'BE',
    'Brandenburg' : 'BB',
    'Bremen' : 'HB',
    'Hamburg' : 'HH',
    'Hessen' : 'HE',
    'Mecklenburg-Vorpommern' : 'MV',
    'Niedersachsen' : 'NI',
    'Nordrhein-Westfalen' : 'NW',
    'Rheinland-Pfalz' : 'RP',
    'Saarland' : 'SL',
    'Sachsen' : 'SN',
    'Sachsen-Anhalt' : 'ST',
    'Schleswig-Holstein' : 'SH',
    'Thüringen' : 'TH'
  }
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
    month_columns = ['month_'+ str(i) for i in range(1,13)]
    df = df.join(pd.get_dummies(df.month, prefix="month").reindex(columns=month_columns, fill_value=0))


    # for d in self.dummies:
    #   df[d] = df[d.split("_")[0]].apply(lambda x: 1 if x == d.split("_")[1] else 0)

    return df

  def train(
    self,
    path_to_training_data="whole_json1.json",
    out_path="prediction_parameters"):

    """ This trains and saves a model for all stations found in
    path.json file. Output folder defaults to /prediction_parameters."""

    data_json = json.load(open(path_to_training_data, "r"))
    data = pd.DataFrame(eval(data_json))

    # take care of dtypes
    data.date = data.date.apply(lambda x: datetime.strptime(x, '%Y-%m-%d'))
    data.bike_count = pd.to_numeric(data.bike_count)
    data.lon = pd.to_numeric(data.lon)
    data.lat = pd.to_numeric(data.lat)


    stations = data.name.unique()

    for station in stations:
      print("start training for station %s", station)
      # load data and skip last row. Last row contains the overall sum.
      df = data[data.name == station]

      # define new columns for regression (happens inplace)
      df = self.enrich_df(df)

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
        weekday_6 +
        temperature +
        precipitation +
        snowdepth +
        windspeed +
        sunshine +
        is_holiday
      """, data=df[(df.date < datetime(2020, 1, 1))]).fit()


      result.save(os.path.join(out_path, station + ".model"))

      # visualize
      df["bike_count_prediction"] = result.predict(df)

      df[(df.date > datetime(2019,1,1))].plot(
        x="date",
        y=["bike_count", "bike_count_prediction"],
        linewidth=1,
        title="""
          trained with data until 2020-01-01 \n
          displayed data from 2019 onwards \n
          Station %s""" % station)
      plt.ylabel("bike count")
      plt.tight_layout()
      plt.savefig(os.path.join(out_path, "prediction_%s.png" % station))
      plt.close()
      print("model and visualization saved to '%s'" % out_path)

  def predict_single(self, station_string, day, temperature, precipitation, snowdepth, windspeed, sunshine, is_holiday, path_to_models="prediction_parameters" ):
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

  def predict_series(self, station_string, days, temperatures, precipitations, snowdepths, windspeeds, sunshines, is_holidays, path_to_models="prediction_parameters" ):
    """ Predict all given days. Returns a dataframe with date and prediction """
    if not type(days) == pd.core.series.Series:
      assert "Please pass days as a pandas Series. E.g. days = df['date']"

    df = pd.DataFrame()
    df["date"] = days
    df['temperature']=temperatures
    df['precipitation']=precipitations
    df['snowdepth']=snowdepths
    df['windspeed']=windspeeds
    df['sunshine']=sunshines
    df['is_holiday']=is_holidays
    df = self.enrich_df(df)
    model = load_pickle(os.path.join(path_to_models, station_string + ".model"))
    df["prediction"] = model.predict(df)
    return df[["date", "prediction"]]


if __name__ == "__main__":
  # instance of class
  BP = BikePrediction()

  # run training on all classes
  #BP.train()
  lat = '48.130472'
  lon = '11.581846'
  date_day = datetime(2020,3,23)
  stations = requests.get(
      'https://api.meteostat.net/v1/stations/nearby?lat={}&lon={}&limit=20&key=L8ouyjgU'.format(lat,
                                                                                                lon))
  #loop over next stations if current station has no data for today
  for station in stations.json()['data']:
    print('station_tried', station)
    print(str(date_day).split()[0])
    closest_station = station['id']
    weather_data = requests.get(
        'https://api.meteostat.net/v1/history/daily?station={}&start={}&end={}&key=L8ouyjgU'.format(closest_station,
                                                                                                    str(date_day).split()[0],
                                                                                                    str(date_day).split()[0]))
    if weather_data.json()['data']:
      print('last reading at station on: ', weather_data.json()['data'][-1]['date'])
      print('date today', str(date_day).split()[0])
    if weather_data.json()['data'] and weather_data.json()['data'][-1]['date'] == str(date_day).split()[0] :
      break
    list( myBigList[i] for i in [87, 342, 217, 998, 500] )
  print(weather_data.json()['data'])
  temperature, precipitation, snowdepth, windspeed, sunshine = list( weather_data.json()['data'][0][key] for key in ['temperature',
                                                                                                                     'precipitation',
                                                                                                                     'snowdepth',
                                                                                                                     'windspeed',
                                                                                                                     'sunshine'
                                                                                                                    ])
  province_public_holidays = []
  geolocator = Nominatim(user_agent="specify_your_app_name_here")
  location = geolocator.reverse(str(lat) + "," + str(lon))
  #if state doesn't exist
  if 'state' in location.raw['address']:
    province = location.raw['address']['state']
  else:
    province = location.raw['address']['city']
  province_abb = province_abbs[province]
  print(date_day.year)
  for date in holidays.DE(years=date_day.year, prov=province_abb):
    province_public_holidays.append(str(date))
  #print(station_weather_df)
  is_holiday = [1 if str(date_day) in province_public_holidays else 0]

  # make a single prediction
  prediction = BP.predict_single(
    station_string="Munich (DE)",
    day=date_day,
    temperature=temperature or 0,
    precipitation=precipitation or 0,
    snowdepth=snowdepth or 0,
    windspeed=windspeed or 0,
    sunshine=sunshine or 0,
    is_holiday=is_holiday or 0
  )
  print(prediction)
  df_munich = df_new[df_new['name']=='Munich (DE)']

  BP.predict_series(
    station_string="Munich (DE)",
    days=df_munich.date,
    temperatures=df_munich.temperature,
    precipitations=df_munich.precipitation,
    snowdepths=df_munich.snowdepth,
    windspeeds=df_munich.windspeed,
    sunshines=df_munich.sunshine,
    is_holidays=df_munich.is_holiday
  )
