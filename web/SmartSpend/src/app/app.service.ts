import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';


@Injectable({
  providedIn: 'root'
})
export class AppService {
  public httpOptions = {
    headers: new HttpHeaders({
      'Access-Control-Allow-Origin': '*',
      Authorization: 'authkey',
      userid: '1'
    })
  };
  static userId: number;
  constructor(private http: HttpClient) {}
  expenseData:any;
  userData:any;
    userId!: any;
  rootURL = '/api';

  sendExpense(expense: any) {
    this.http.post('http://127.0.0.1:5002/tests', expense).subscribe(data => {
        console.log(data);
      })
  }


  getExpenses() {
    this.http.get('http://127.0.0.1:5002/').subscribe(data => {
      this.expenseData = data;
      // this.expenseData = data as JSON;
      console.log(this.expenseData);
    })
  }

  getExpensesById() {
    this.http.get(`http://127.0.0.1:5002/id/${this.userId}`).subscribe(data => {
      this.userData = data;
      
      // this.expenseData = data as JSON;
      console.log(this.userData);


    })
  }


  getJournals() {
    return this.http.get<any>(
      'http://localhost:8080/Practice/api/v1/journals',
      this.httpOptions
    );
  }
}
