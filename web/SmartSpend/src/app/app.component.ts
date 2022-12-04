import { HttpClient, HttpHeaders } from '@angular/common/http';
import {COMMA, ENTER} from '@angular/cdk/keycodes';
import {Component, ElementRef, ViewChild} from '@angular/core';
import {FormControl} from '@angular/forms';
import {MatAutocompleteSelectedEvent} from '@angular/material/autocomplete';
import {MatChipInputEvent} from '@angular/material/chips';
import {Observable} from 'rxjs';
import {map, startWith} from 'rxjs/operators';
import { ExpenseService } from './expense/expense.service';
import { AppService } from './app.service';
import { ActivatedRoute, ParamMap } from '@angular/router';


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

  constructor(private httpClient: HttpClient, public expenseService: ExpenseService, private route: ActivatedRoute, public appService: AppService) {
  }
  serverData!: JSON;
  employeeData!: JSON;
  
  
  ngOnInit() {
    // this.appService.getExpensesById
    // console.log(this.appService.userId)

    // this.route.paramMap.subscribe((params: ParamMap) => {
    //   this.appService.userId = Number(params.get('id'));
    //   console.log(params);
    //   console.log('line38',this.appService.userId)
    //   // this.appService.userId = Number(params.get('id'));
    //   this.appService.getExpensesById().subscribe((expenses: any) => {
    //     console.log('logging expenses homepage', expenses);
    //     this.appService.userData = expenses;
    //   })
    // })
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
