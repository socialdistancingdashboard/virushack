// rot f63366
// gelb f3b202
//gruen 04652a

import { Injectable, ViewChild, Component } from '@angular/core';
//import { Http, Headers, RequestOptionsm  } from '@angular/http';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { ISource, IStation, IRawData, IInputData } from './interfaces';
import * as moment from 'moment';
import localization from 'moment/locale/de'
import { Observable } from "rxjs"
import { filter, map, combineAll, withLatestFrom, finalize } from 'rxjs/operators';
import { of } from 'rxjs'
import { ChartComponent } from 'angular2-chartjs';
import { share } from 'rxjs/operators';

//import { BaseChartDirective } from 'ng2-charts';

//@ViewChild('chart1') chart1: ChartComponent;


@Injectable({
  providedIn: 'root'
})
export class DataService {
  stations$: Observable<IStation[]>
  sources$: Observable<ISource[]>
  source_spatial_level_lookup: any;

  color_palette = ["#d9046777", "#05aff277", "#f2bc1b77", "#f2440577","#7c05f277", "#04652a77"]
  chart_colors = { "0": "#04652a77", "1": "#f6336677"}

  id: IInputData[] = [{
    selected_source_id: undefined,
    selected_state_id: undefined,
    selected_district_id: undefined,
    selected_station_id: undefined,
    dataset: undefined,
  }] // id stands for input data

  chartcanvas: ChartComponent;
  req_list: any[] = []

  axis_count = 0

  errors = []

  data = {
    datasets: []
  }

  yAxes = [{
    id: '0',
    type: 'linear',
    position: 'left',
    ticks: {
      beginAtZero: true
    },
  }, {
    id: '1',
    type: 'linear',
    position: 'right',
    ticks: {
      beginAtZero: true
    },
    gridLines: {
      display:false
    }
  }]

  options = {
    maintainAspectRatio: false,
    responsive: true,
    //aspectRatio: 1,
    scales: {
      xAxes: [{
        display: true,
        id: "x-axis",
        type: 'time',
        time: {
          parser: 'YYYY-MM-DD HH:mm',
          tooltipFormat: 'LLLL',
          unit: 'day',
          unitStepSize: 1,
          displayFormats: {
            'day': 'll'
          }
        }
      }],
      yAxes: this.yAxes
    },
    plugins: {
      zoom: {
        pan: {
          enabled: true,
          mode: 'x'
        },
        zoom: {
          enabled: true,
          mode: 'x'
        }
      }
    },
    // annotation: {
    //   events: ["click"],
    //   annotations: [
    //     {
    //       drawTime: "beforeDatasetsDraw",
    //       id: "vline",
    //       type: "line",
    //       mode: "vertical",
    //       scaleID: "x-axis",
    //       value: moment("2020-03-02T11:00"),
    //       borderColor: "black",
    //       borderWidth: 2,
    //       label: {
    //         position: "top",
    //         backgroundColor: "red",
    //         content: "Test Label",
    //         enabled: true
    //       },
    //       onClick: function(e) {
    //         // The annotation is is bound to the `this` variable
    //         console.log("Annotation", e.type, this);
    //       }
    //     }
    //   ]
    // }
  }

  blink_status: boolean = true;

  add_chart(){
    this.id.push({
      selected_source_id: undefined,
      selected_state_id: undefined,
      selected_district_id: undefined,
      selected_station_id: undefined,
      dataset: undefined
    })
  }

  remove_chart(i: number){
    this.id.splice(i, 1);
    this.data.datasets = this.id.map( id => id.dataset)
    this.chartcanvas.chart.update()
  }

  new_source(event, i: number){
    this.errors = []
    const selected_source_id = event.value
    this.id[i].selected_state_id = null
    this.id[i].selected_district_id = null
    this.id[i].selected_station_id = null;

    this.get_station_data(
      selected_source_id,
      this.id[i].selected_state_id,
      this.id[i].selected_district_id,
      this.id[i].selected_station_id,
      i, null)
  }

  new_state(event, i: number){
    this.errors = []
    const selected_state_id = event.value
    this.id[i].selected_district_id = null
    this.id[i].selected_station_id = null;

    this.get_station_data(
      this.id[i].selected_source_id,
      selected_state_id,
      this.id[i].selected_district_id,
      this.id[i].selected_station_id,
      i, null)

  }

  new_district(event, i: number){
    this.errors = []
    const selected_district_id = event.value
    this.id[i].selected_station_id = null;

    this.get_station_data(
      this.id[i].selected_source_id,
      this.id[i].selected_state_id,
      selected_district_id,
      this.id[i].selected_station_id,
      i, null)

  }

  new_station(event, i:number, hourly:boolean){
    this.errors = []
    const selected_station_id = hourly !== null ? this.id[i].selected_station_id : event.value

    this.get_station_data(
      this.id[i].selected_source_id,
      this.id[i].selected_state_id,
      this.id[i].selected_district_id,
      selected_station_id,
      i, hourly);
  }

  hourly_data(event, i:number){
    console.log("HUUURA", event)
    this.new_station(null, i, event.checked)
  }



  set_yaxis_ids(){
    if(!this.data.datasets) return

    if (this.data.datasets.length <= 2){
      this.data.datasets.forEach((ds, index) => {
        ds.yAxisID = index.toString()
      })
    } else {
      let units = this.data.datasets.map( ds => ds.unit)
      let unique_units = units.filter( (unit, index) => units.indexOf(unit) === index)
      if (unique_units.length > 2){
        throw new Error("Es ist nicht möglich mehr als zwei verschiedene Einheiten darzustellen")
      }
      this.data.datasets.forEach( (ds, index) => {
        ds.yAxisID = unique_units.indexOf(ds.unit).toString()
        ds.backgroundColor = this.chart_colors[ds.yAxisID]
        console.log(ds.label, "auf yAxisID", ds.yAxisID)
      })
    }
    // reset colors
    this.data.datasets.forEach( (ds, index) => {

      ds.backgroundColor = this.color_palette[index]
      if (ds.yAxisID === "0"){
        ds.label = ds.label_raw.replace(")", ", linke Achse)")
      } else {
        ds.label = ds.label_raw.replace(")", ", rechte Achse)")
      }
    })
  }


  get_station_data(source_id, state_id, district_id, station_id, chartid: number, hourly){
    // this.data.datasets[chartid] = null;

    const param = {
      source_id: source_id,
      state_id: state_id,
      district_id: district_id,
      station_id: station_id,
      sample_interval: hourly ? "hourly" : "daily",
    }

    const request_url = "https://yrxhzhs22a.execute-api.eu-central-1.amazonaws.com/Prod/get-station-data/"
    const req = this.http
    .post(request_url, JSON.stringify(param), {})
    .pipe( finalize(() => this.req_list.splice(this.req_list.indexOf(req),1)))
    .toPromise()
    .then( (result: IRawData) => {
    //  console.log("current chart_id", chartid)
      // this.remove_chart_from_data(chartid)

      if(!result.meta || !result.data){
        console.log("ERROR NO DATA for params", param)
      } else {

        console.log(result)
        const ylabel = result.meta.ylabel
        const yAxisID = "0" // just a dummy, will be updated below

        const dataset = {
          "chart_id": chartid,
          "label_raw": ylabel,
          "label": ylabel,
          "available_intervals": result.meta.available_intervals,
          "yAxisID": yAxisID,
          "unit": result.meta.unit,
          "backgroundColor": "#ff0000",
          "data": result.data.map(
            val => { return { "x": moment(val.dt) , "y": val.score} }
          )
        }

        //this.data.datasets[chartid] = dataset
        this.id[chartid].dataset = dataset
        this.data.datasets = this.id.map( id => id.dataset)
        this.set_yaxis_ids()
        this.chartcanvas.chart.update()
      }

      console.log("processed data", this.data)
    })
    .catch( (err) => {
      this.on_error(err)
    })
    this.req_list.push(req)
  }

  on_error(err){
    /* replace with error service */
    this.errors.push(err)
    console.log(err)
  }


  constructor(private http: HttpClient ) {
    moment.locale('de', localization);
    console.log(moment().format("LLLL"))

    let req;
    let request_url

    request_url = "https://yrxhzhs22a.execute-api.eu-central-1.amazonaws.com/Prod/get-stations"
    this.stations$ = this.http.get<IStation[]>(request_url, {})

    req = this.stations$
    .pipe( finalize(() => this.req_list.splice(this.req_list.indexOf(req),1)))
    .pipe(share())
    .subscribe( (data) => {
      console.log("stations", data)
    })
    this.req_list.push(req)

    // dont display corona "scores"
    let source_blacklist = [
      "corona_dead",
      /* "corona_infected", */
      "corona_recovered",
      // "score_fraunhofer_day_ahead_auction",
      // "score_fraunhofer_import_balance",
      // "score_fraunhofer_intraday_continuous_average_price",
      // "score_fraunhofer_intraday_continuous_id1_price",
      // "score_fraunhofer_intraday_continuous_id3_price",
      // "score_fraunhofer_load"
      ]
    request_url = "https://yrxhzhs22a.execute-api.eu-central-1.amazonaws.com/Prod/get-sources"
    req = this.sources$ = this.http.get<ISource[]>(request_url, {})
    .pipe( finalize(() => this.req_list.splice(this.req_list.indexOf(req),1)))
    .pipe( map( source => {
        return source.filter( source => source_blacklist.indexOf(source.id) === -1 )}))
    .pipe(share())


    this.req_list.push(req)

    this.sources$.subscribe((data)=>{
      console.log("sources", data)
      let source_spatial_level_lookup = []
      data.forEach( val => {
        source_spatial_level_lookup[val.id] = val.spatial_level
      })

      this.source_spatial_level_lookup = source_spatial_level_lookup
      console.log("LOOKUP", this.source_spatial_level_lookup)
    })

    /* handles the rockets animation while app is loading stuff */
    setInterval(()=>{
      if (this.req_list.length > 0){
        this.blink_status = !this.blink_status
      } else {
        this.blink_status = true
      }
    }, 300)

  }
}

