import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { DashComponent } from './dash/dash.component';
import { HttpClientModule } from '@angular/common/http';
import { NgxChartsModule } from '@swimlane/ngx-charts';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';

import {MatSelectModule} from '@angular/material/select'; 
import {MatCardModule} from '@angular/material/card'; 
import {MatIconModule} from '@angular/material'
import {MatButtonModule} from '@angular/material/button'; 
import {MatSlideToggleModule} from '@angular/material/slide-toggle'; 

import { ChartModule } from 'angular2-chartjs';
import { FilterstationsPipe } from './filterstations.pipe';

@NgModule({
  declarations: [
    AppComponent,
    DashComponent,
    FilterstationsPipe
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    HttpClientModule,
    NgxChartsModule,
    BrowserAnimationsModule,
    MatSelectModule,
    MatCardModule,
    MatIconModule,
    MatButtonModule,
    ChartModule,
    MatSlideToggleModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
