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
  // static userId: number;
  constructor(private http: HttpClient) {
    console.log(this.userId)
  }
  expenseData:any;
  userLimits:any;
  userData:any;
  nextNumber = -1;
  public userId!: any;
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
 
  getLimitsForUser():any {
    console.log(this.userId);
    return this.http.get(`http://127.0.0.1:5002/limits/${this.userId}`);
  }


  getExpensesById(): any {
    console.log('id', this.userId);
    return this.http.get(`http://127.0.0.1:5002/id/${this.userId}`);
    
    // .subscribe(data => {
    //   this.userData = data;
    //   // this.expenseData = data as JSON;
    //   const nums = this.userData.map((dat:any) => dat.number ?? -1);
    //   console.log("nums", nums);

    //   console.log(Math.max(... nums));
    //   this.nextNumber = (Math.max(...nums)) + 1;
    //   console.log("next number", this.nextNumber);
    //   // console.log([...nums.entries()].reduce((a, e ) => e[1] > a[1] ? e : a))
    // })
  }


  getJournals() {
    return this.http.get<any>(
      'http://localhost:8080/Practice/api/v1/journals',
      this.httpOptions
    );
  }
}
