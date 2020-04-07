import { Observable } from "rxjs"

export interface IInputData {
  selected_source_id: string,
  selected_state_id: string,
  selected_district_id: string,
  selected_station_id: string,
  dataset: any
}

export interface IRawData {
  "meta": {
    "ylabel": string,
    "desc_short": string,
    "desc_long": string, 
    "sample_interval": string,
    "agg_level": string,
    "agg_level_id": string,
    "agg_mode": string,
    "unit": string,
    "available_intervals": string
  },
  "data": {
    "dt": string,
    "score": number
  }[]
}

export interface DataPoint {
  "name": Date,
  "value": number
}

export interface Data {
  "name": string,
  "series": DataPoint[]
}[]


export interface IStation {
  id: number,
  source_id: string,
  description: string,
  district_id: string,
  district: string,
  district_type: string,
  state_id: string,
  state: string,
  country_id: string,
  country: string
}

export interface Locations{
  countries: Country[],
  states: State[],
  districts: District[]
}
export interface ISource {
  id: string, 
  desc_short: string, 
  desc_long: string,
}

export interface Country {
  country_id: string,
  country: string
}

export interface State {
  country_id: string,
  country: string,
  state_id: string,
  state: string
}

export interface District {
  district_id: string,
  district: string,
  state_id: string,
  state: string,
  country_id: string,
  country: string,
  lat: number,
  lon: number
}