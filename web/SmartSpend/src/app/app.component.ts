import { HttpClient, HttpHeaders } from '@angular/common/http';
import {COMMA, ENTER} from '@angular/cdk/keycodes';
import {Component, ElementRef, ViewChild} from '@angular/core';
import {FormControl} from '@angular/forms';
import {MatAutocompleteSelectedEvent} from '@angular/material/autocomplete';
import {MatChipInputEvent} from '@angular/material/chips';
import {Observable} from 'rxjs';
import {map, startWith} from 'rxjs/operators';


@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {
  separatorKeysCodes: number[] = [ENTER, COMMA];
  value = 'Clear me';


  fruitInput!: ElementRef<HTMLInputElement>;
  // constructor(private http: HttpClient){}
  title = 'SmartSpend';

  constructor(private httpClient: HttpClient) {
  }
  serverData!: JSON;
  employeeData!: JSON;
  
  

  sayHi() {
    this.httpClient.get('http://127.0.0.1:5002/').subscribe(data => {
      this.serverData = data as JSON;
      console.log(this.serverData);
    })
  }

  getAllEmployees() {
    this.httpClient.get('http://127.0.0.1:5002/employees').subscribe(data => {
      this.employeeData = data as JSON;
      console.log(this.employeeData);
    })
  }
  // public httpOptions = {
  //   headers: new HttpHeaders({
  //     'Access-Control-Allow-Origin': '*',
  //     Authorization: 'authkey',
  //     userid: '1'
  //   })
  // };

  // getJournals() {
  //   return this.http.get<any>(
  //     'http://localhost:8080/Practice/api/v1/journals',
  //     this.httpOptions
  //   );
  // }
}
