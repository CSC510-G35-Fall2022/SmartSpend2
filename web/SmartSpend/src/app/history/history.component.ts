import { Time } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { Component, ViewChild } from '@angular/core';
import { MatPaginator } from '@angular/material/paginator';
import { MatSort } from '@angular/material/sort';
import { MatTableDataSource } from '@angular/material/table';
import { Router } from '@angular/router';
import { AppService } from '../app.service';
import { ExpenseComponent } from '../expense/expense.component';
import { ExpenseService } from '../expense/expense.service';

@Component({
  selector: 'app-history',
  templateUrl: './history.component.html',
  styleUrls: ['./history.component.css']
})
export class HistoryComponent {
  // expenses!: ExpenseComponent[]

  ngOnInit(): void {
    console.log(this.appService.userData);
    
  }
  add() {
    this.router.navigate(['addExpensePage/']);

  }

  displayedColumns: string[] = ['id', 'name', 'progress', 'fruit'];
  columns: string[] = ['number', 'category', 'cost'];
  dataSource: MatTableDataSource<UserData>;

  @ViewChild(MatPaginator)
  paginator!: MatPaginator;
  @ViewChild(MatSort)
  sort!: MatSort;
  expenses: any[] = [];
  expense!: [];


  constructor(public appService: AppService, private http: HttpClient, private router: Router) {
    // Create 100 users
    appService.getExpenses();

    this.http.get('http://127.0.0.1:5002/').subscribe(data => {this.expenses = Array(data); console.log(this.expenses);})

    for(const prop in appService.expenseData) {
      this.expenses.push(appService.expenseData[prop])
    }
    // this.expenses = Array.from(appService.expenseData);
    // console.log(this.expenses);
    // const users = Array.from({length: 100}, (_, k) => createNewUser(k + 1));
    this.dataSource = new MatTableDataSource(this.expenses);

    // Assign the data to the data source for the table to render
    // this.dataSource = new MatTableDataSource(users);
  }

  ngAfterViewInit() {
    this.dataSource.paginator = this.paginator;
    this.dataSource.sort = this.sort;
  }

  applyFilter(event: Event) {
    const filterValue = (event.target as HTMLInputElement).value;
    this.dataSource.filter = filterValue.trim().toLowerCase();

    if (this.dataSource.paginator) {
      this.dataSource.paginator.firstPage();
    }
  }
}

export interface UserData {
  id: string;
  name: string;
  progress: string;
  fruit: string;
}
export interface ExpenseData {
  cost: number;
  category: string;
  user_telegram_id: number;
  timestamp: Time;

}




