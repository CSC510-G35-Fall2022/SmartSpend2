import { HttpClient } from '@angular/common/http';
import { Component } from '@angular/core';
import { ActivatedRoute, ParamMap, Router } from '@angular/router';
import { AppService } from '../app.service';
import { ExpenseService } from '../expense/expense.service';

@Component({
  selector: 'app-homepage',
  templateUrl: './homepage.component.html',
  styleUrls: ['./homepage.component.css']
})
export class HomepageComponent {

  constructor(private httpClient: HttpClient, public appService: AppService, private router: Router, private route: ActivatedRoute) {
  }
  serverData!: JSON;
  employeeData!: JSON;
  expenseData:any;
  userId: any;
  ngOnInit():void {
    this.sayHi();
    console.log(this.userId);
    
      this.route.paramMap.subscribe((params: ParamMap) => {
        this.userId = params.get('id')
        console.log(this.userId)
        this.appService.userId = Number(params.get('id'));
        this.appService.getExpensesById().subscribe((expenses: any) => {
          console.log('logging expenses homepage', expenses);
          this.appService.userData = expenses;
        })
        console.log('userId',this.appService.userId)
        this.router.navigate([`${this.userId}/dashboard/`]);
      })
    
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
