# how does public transportation react to corona?

We assume that social distancing is related to public transportation. Therefore we look for correlation between the number of available trains (measured in scheduled train stops per district) and social distancing measurements. We collect the number of *scheduled* and *actual* number of stops per district. Differences in these numbers show the **reaction of the train operators** to the corona-crisis. 

The origin of this data is not particulary clear...

Hava a look in /summaries for daily summary files (json).

## time perios
* upload started at 27.01.2020
* upload ended at (currently running, data is uploaded at the end of the day)

## Missing values
* 2020-01-29 (skipped because uncomplete data)
* 2020-02-01 (missing)
* 2020-03-08 (missing)
* 2020-03-09 (missing)
* 2020-03-10 (missing)

## scheduled / actual stops per train type:
* national
* nationalExpress
* regional
* suburban
* bus

## what data
* How many stops were scheduled per district (to be exact: geo coordinates of station)
* How many stops actually happened

## Json Format
```json
{
  'date': '2020-03-01',
  'planned_stops': {
      'bus': 169,
      'national': 2379,
      'nationalExpress': 3359,
      'regional': 106760,
      'suburban': 132891
  },
  'cancelled_stops': {
      'bus': 0.0,
      'national': 35.0,
      'nationalExpress': 73.0,
      'regional': 1146.0,
      'suburban': 1202.0}
  }
}
```

## data preview 2020-01-27 to 2020-03-20
![data preview](summaries/data_viz.png "Visualization")
   
### Interpretation (german below)
(english)
* One does notice the weekends as drops in scheduled stops
* One does notice a significant peak in cancelled stops on 2020-02-08/09 due to hurricane Sabrina
* Busses were reduced from mid of february. Reason unclear.
* One does notice a rise in cancelled trains with the beginning of corona

(deutsch)
* Man erkennt die Wochenenden als (planmäßige) Reduktion der geplanten Zughalte.
* Man erkennt einen starken Peak am 2020-02-08/09. Hier hat das Sturmtief Sabrina zugeschlagen
* Busse sind ab mitte Februar massiv eingeschränt worden (warum?)
* Man sieht (schwach) in den letzten Tagen einen Anstieg in den Ausfällen bei allen "Zugtypen". Hier kann man von Corona-bedingten Ausfällen ausgehen.