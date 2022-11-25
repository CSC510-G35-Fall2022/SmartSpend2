import { HttpClient, HttpHeaders } from '@angular/common/http';
import {COMMA, ENTER} from '@angular/cdk/keycodes';
import {Component, ElementRef, ViewChild} from '@angular/core';
import {FormControl} from '@angular/forms';
import {MatAutocompleteSelectedEvent} from '@angular/material/autocomplete';
import {MatChipInputEvent} from '@angular/material/chips';
import {Observable} from 'rxjs';
import {map, startWith} from 'rxjs/operators';
import { ExpenseService } from './expense/expense.service';


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

  constructor(private httpClient: HttpClient, public expenseService: ExpenseService) {
  }
  serverData!: JSON;
  employeeData!: JSON;
  
  
  ngOnInit() {
    // this.expenseService.getExpenses();
    // console.log(this.expenseService.expenseData);
    
  }
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

}
