import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';


@Injectable({
  providedIn: 'root'
})
export class ExpenseService {
  public httpOptions = {
    headers: new HttpHeaders({
      'Access-Control-Allow-Origin': '*',
      Authorization: 'authkey',
      userid: '1'
    })
  };
  constructor(private http: HttpClient) {}
  expenseData:any;

  rootURL = '/api';

  getExpenses() {
    this.http.get('http://127.0.0.1:5002/').subscribe(data => {
      this.expenseData = data;
      
      // this.expenseData = data as JSON;
      console.log(this.expenseData);


    })
  }


  getJournals() {
    return this.http.get<any>(
      'http://localhost:8080/Practice/api/v1/journals',
      this.httpOptions
    );
  }
}
