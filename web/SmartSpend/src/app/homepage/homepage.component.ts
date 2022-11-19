import { HttpClient } from '@angular/common/http';
import { Component } from '@angular/core';

@Component({
  selector: 'app-homepage',
  templateUrl: './homepage.component.html',
  styleUrls: ['./homepage.component.css']
})
export class HomepageComponent {

  constructor(private httpClient: HttpClient) {
  }
  serverData!: JSON;
  employeeData!: JSON;
  expenseData:any;
  
  ngOnInit():void {
    this.sayHi();
  }

  sayHi() {
    this.httpClient.get('http://127.0.0.1:5002/').subscribe(data => {
      this.expenseData = data;
      
      // this.expenseData = data as JSON;
      // console.log(this.expenseData);


    })
  }

  getAllEmployees() {
    this.httpClient.get('http://127.0.0.1:5002/employees').subscribe(data => {
      this.employeeData = data as JSON;
      console.log(this.employeeData);
    })
  }

}
