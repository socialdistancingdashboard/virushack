devtools::install_local("hystReet-master/")
# Get HYSTREET API TOKEN by view-source:https://hystreet.com/locations/148 search for apiToken get 24 chracters token
Sys.setenv(HYSTREET_API_TOKEN = readChar("apikey", 27))
library(hystReet)

#Is working?
stats <- get_hystreet_stats()

#Get Locations
locations <- get_hystreet_locations()

#Get all Data Lists into one list
alldata <- list()

for (id in unique(locations$id))
{
  data <- get_hystreet_station_data(
    hystreetId = id,
    query = list(
      from = "2020-01-01",
      to = "2020-03-20",
      resolution = "hour"
    )
  )
  alldata[[as.character(id)]] <- data
}

#saveRDS(alldata, file = "hystreet_20_01_01_u_20_03_20_hour.rds")
alldata <- readRDS("hystreet_20_01_01_u_20_03_20_hour.rds")

everything <- list()
for (stationid in names(alldata))
{
  listtemp <- alldata[[stationid]]
  datestart <-
    format(listtemp$metadata$earliest_measurement_at,
           format = "%Y-%m-%d",
           tz = "")
  dateend <-
    format(listtemp$metadata$latest_measurement_at,
           format = "%Y-%m-%d",
           tz = "")
  
  data <- get_hystreet_station_data(
    hystreetId = as.numeric(stationid),
    query = list(
      from =  datestart,
      to =   dateend,
      resolution = "hour"
    )
  )
  everything[[stationid]] <- data
}
warnings()
#saveRDS(everything, file = "alldata_earliest_latest_per_station.rds")
everything <- readRDS(file = "rds/alldata_earliest_to_latest_per_station.rds")

data_long <- data.frame(
  stationid = NA,
  name = NA,
  city = NA,
  statistics_today_count = NA,
  statistics_timerange_count = NA,
  liftime_count = NA,
  metadata_measured_from = NA,
  metadata_measured_to = NA,
  earliest_measurement_at = NA,
  latest_measurement_at = NA,
  lon = NA,
  lat = NA
)

data_long <- cbind(data_long, everything[[1]]$measurements[1, ])
data_long <- data_long[-1, ]
incident_data <-data.frame(stationid=NA, id=NA,name=NA,icon=NA, description=NA,active_from=NA,active_to=NA)
incident_data <- incident_data[-1,]

for (listnames in names(everything))
{
  listdata <- everything[[listnames]]
  incdata <- listdata$incidents
  if(is.data.frame(incdata))
  {
  incident_data_temp <-data.frame(stationid=listnames, id=incdata$id,name=incdata$name,icon=incdata$icon, description=incdata$description,active_from=incdata$active_from,active_to=incdata$active_to)
  incident_data <- rbind(incident_data, incident_data_temp)
  }
  station_location <- as.character(unique(paste0(listdata$name,",",listdata$city)))
  df <- as.data.frame(ggmap::geocode(station_location))
  lon <- df[,1]
  lat <- df[,2]

  rows <- nrow(listdata$measurements)
  if(!is.null(rows))
  {
  data_long_temp <- data.frame(
    stationid =  rep(listdata$id, rows),
    name = rep(listdata$name, rows),
    city = rep(listdata$city, rows),
    statistics_today_count = rep(listdata$statistics$today_count, rows),
    statistics_timerange_count = rep(listdata$statistics$timerange_count, rows),
    liftime_count = rep(listdata$statistics$lifetime_count, rows),
    metadata_measured_from = rep(listdata$metadata$measured_from, rows),
    metadata_measured_to = rep(listdata$metadata$measured_to, rows),
    earliest_measurement_at = rep(listdata$metadata$earliest_measurement_at, rows),
    latest_measurement_at = rep(listdata$metadata$latest_measurement_at, rows),
    lon = rep( df[,1], rows),
    lat = rep( df[,2], rows)
    )
  data_long_temp <- cbind(data_long_temp, listdata$measurements)
  print(listnames)
  data_long <- rbind(data_long, data_long_temp)
  }
}



#write.csv(data_long,"long_alldata_hystreet.csv")
#write.csv(incident_data,"incidents_data_hystreet.csv")
#saveRDS(data_long,"last_data.rds")
#write.csv(latest,"long_alldata_hystreet.csv", row.names = F)
latest <- readRDS("rds/last_data.rds")
missingkrahnstrasse <- c(8.0131, 52.2983)
latest[which(is.na(latest$lon)),]$lon <- missingkrahnstrasse[1]
latest[which(is.na(latest$lat)),]$lat <- missingkrahnstrasse[2]

library(ggmap)
library(dplyr)
register_google(key = readChar("googleconsolekey", 39))

map <- get_map("Germany", zoom = 6, maptype = "toner")


ggmap(map) %>% 
  group_by(y) geom_point(aes(x = lon, y = lat,  colour = stationid), data = latest, size = 0.5) + 
  theme(legend.position="bottom")
