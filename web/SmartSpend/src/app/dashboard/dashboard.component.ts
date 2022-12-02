import {HttpClient} from '@angular/common/http';
import {Component, ViewChild, AfterViewInit} from '@angular/core';
import {MatPaginator} from '@angular/material/paginator';
import {MatSort, SortDirection} from '@angular/material/sort';
import {merge, Observable, of as observableOf} from 'rxjs';
import {catchError, map, startWith, switchMap} from 'rxjs/operators';
import { AppService } from '../app.service';

import {MatTableDataSource} from '@angular/material/table';
import { Time } from '@angular/common';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css']
})
export class DashboardComponent {
  displayedColumns: string[] = ['id', 'name', 'progress', 'fruit'];
  columns: string[] = ['number', 'category', 'cost'];
  dataSource: MatTableDataSource<UserData>;

  @ViewChild(MatPaginator)
  paginator!: MatPaginator;
  @ViewChild(MatSort)
  sort!: MatSort;
  expenses: any[] = [];
  expense!: [];


  constructor(public appService: AppService, private http: HttpClient) {
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

// /** Builds and returns a new User. */
// function createNewUser(id: number): UserData {
//   const name =
//     NAMES[Math.round(Math.random() * (NAMES.length - 1))] +
//     ' ' +
//     NAMES[Math.round(Math.random() * (NAMES.length - 1))].charAt(0) +
//     '.';

//   return {
//     id: id.toString(),
//     name: name,
//     progress: Math.round(Math.random() * 100).toString(),
//     fruit: FRUITS[Math.round(Math.random() * (FRUITS.length - 1))],
//   };
// }


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

