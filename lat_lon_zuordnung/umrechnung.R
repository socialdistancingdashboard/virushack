library(tidyverse)
library(eurostat)
library(sf)

#plz zuordnung von https://www.suche-postleitzahl.org/downloads
ort_landkreis_tbl <- read_csv("plz/zuordnung_plz_ort_landkreis.csv") %>% 
  select(plz, ort, landkreis, bundesland)

#plz shape file von https://www.suche-postleitzahl.org/downloads
plz_sf <- read_sf("plz/plz-5stellig.shp") %>% 
  left_join(y = ort_landkreis_tbl, by = "plz")



nuts_sf <- get_eurostat_geospatial(nuts_level="all", year = "2016") %>% 
  filter(CNTR_CODE == "DE")
