import { Pipe, PipeTransform } from '@angular/core';
import { IStation, ISource } from './interfaces';

@Pipe({
  name: 'filterstations'
})
export class FilterstationsPipe implements PipeTransform {

  transform(value: IStation[], return_type, selected_source_id, selected_state_id, selected_district_id) {
    /* returns the stations filtered and uniquified by given return type (e.g state_id) */

    if(!value){
      return []
    }

    let filtered = [];

    if (return_type == "state_id"){
      if (selected_source_id){
        filtered = value.filter(s =>
          s.source_id === selected_source_id
        )
      }
    }

    if (return_type == "district_id"){
      if (selected_source_id && selected_state_id){
        filtered = value.filter(s =>
          s.source_id === selected_source_id && s.state_id === selected_state_id && s.district_id
        );
      }
    }

    if (return_type == "station_id"){
      if (selected_source_id && selected_state_id && selected_district_id){
        filtered = value.filter(s =>
          s.source_id === selected_source_id && s.state_id === selected_state_id && s.district_id === selected_district_id
        );
        console.log("filtered stations", filtered)
      }
    }


    if (filtered) {
      // remove duplicates
      if (return_type === "station_id"){
        // station_id are passed as id in get_stations. this handles this specific case
        return_type = "id"
      }
      filtered = filtered.filter( (item, index) => {
        return filtered.map( val => val[return_type]).indexOf(item[return_type]) === index
      })
    }

    return filtered
  }
}
