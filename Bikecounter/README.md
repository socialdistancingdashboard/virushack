# Bikecounter
Worldwide data from bicycle counters in cities: http://www.eco-public.com/ParcPublic/?id=4586#

# Example for station Munich (DE)

  ![Zeigt die Fahrradzahlen](prediction_parameters/prediction_Munich%20(DE).png "Visualisierung")
  
# Explanation
The blue line represents actual data, the orange line is the prediction. Orange values are used as a reference for a non-corona scenario.

The prediction is computed by training a linear regression model using the following features:  
  + year,  
  + month_1,  
  + month_2,  
  + month_3,  
  + month_4,  
  + month_5,  
  + month_6,  
  + month_7,  
  + month_8,  
  + month_9,  
  + month_10,  
  + month_11,  
  + month_12,  
  + weekday_0,  
  + weekday_1,  
  + weekday_2,  
  + weekday_3,  
  + weekday_4,  
  + weekday_5,  
  + weekday_6,  
  + temperature,  
  + precipitation,  
  + snowdepth,  
  + windspeed,  
  + sunshine,  
  + is_holiday (whether the current date is a public holiday at the current location)  
        
A seperate model is trained for each Landkreis using data up until 01-01-2020. The daily predictions returned by the models are the bike_counts that would be expected at the respective locations given the date and weather information. These prediction values therefore allow for a comparison with the actual bike_counts to observe trends during the Covid-19 outbreak.
