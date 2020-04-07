import { Component,Injectable, ViewChild,  OnInit, Pipe, PipeTransform, ElementRef, AfterViewInit } from '@angular/core';
import { DataService } from './data.service';
import 'chartjs-plugin-zoom';
import 'chartjs-plugin-annotation';
import { ChartComponent } from 'angular2-chartjs';

import { BaseChartDirective } from 'chart.js-v2'; 

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnInit, AfterViewInit{
  // allows to update canvas manually
  @ViewChild("chartcanvas", {static: false}) chartcanvas: BaseChartDirective;

  constructor(
    public ds: DataService
  ) { }

  ngAfterViewInit(): void{
    console.log("NG AFTER INIT", this.chartcanvas)
    this.ds.chartcanvas = this.chartcanvas
  }

  ngOnInit(): void { }
}

