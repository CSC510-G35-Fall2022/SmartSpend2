import { HttpClient } from '@angular/common/http';
import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { AppService } from '../app.service';
import { ExpenseService } from '../expense/expense.service';

@Component({
  selector: 'app-homepage',
  templateUrl: './homepage.component.html',
  styleUrls: ['./homepage.component.css']
})
export class HomepageComponent {

  constructor(private httpClient: HttpClient, public appService: AppService,     private router: Router) {
  }
  serverData!: JSON;
  employeeData!: JSON;
  expenseData:any;
  userId: string = '';
  ngOnInit():void {
    this.sayHi();
    console.log(this.userId);
  }
  inputId(): void {
    console.log(this.userId);
    console.log(parseInt(this.userId) - 2)
    this.appService.userId = parseInt(this.userId);
    this.appService.getExpensesById();
    this.router.navigate(['dashboard/']);

  }

  sayHi() {
    this.httpClient.get('http://127.0.0.1:5002/').subscribe(data => {
      this.expenseData = data;
      
    })
  }

  getAllEmployees() {
    this.httpClient.get('http://127.0.0.1:5002/employees').subscribe(data => {
      this.employeeData = data as JSON;
      console.log(this.employeeData);
    })
  }

}
