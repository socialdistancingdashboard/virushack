library(tidyverse)
# devtools::install_github("JohannesFriedrich/hystReet")
library(hystReet)

places <- hystReet::get_hystreet_locations()

# scrape list of all stations' data:
# This needs to have written authorization by hystreet
# cf. 6.3 in https://hystreet.com/agbs_de.pdf
data <- places$id %>% 
  map(
    ~get_hystreet_station_data(
      hystreetId = .x,
      query = list(from = "2020-01-01",
                   to = "2020-03-20",
                   resolution = "hour")
      )
    )

# put measurement data in one dataframe:
df <- data %>% 
  set_names(paste(places$name, places$city)) %>%
  map("measurements") %>% 
  bind_rows(.id = "place") %>% 
  select(place, timestamp, pedestrians_count)


# write_csv(df, "hystreet_data.csv")
# # # plot stations time series as facets:
# ggplot(df, aes(x = timestamp, y = pedestrians_count, colour = weekdays(timestamp))) +
#   geom_path(group = 1) +
#   labs(x = "Date",
#        y = "Pedestrians",
#        colour = "Day") +
#   facet_wrap(~place)
