import { Time } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { ThisReceiver } from '@angular/compiler';
import { Component, ViewChild } from '@angular/core';
import { MatPaginator } from '@angular/material/paginator';
import { MatSort } from '@angular/material/sort';
import { MatTableDataSource } from '@angular/material/table';
import { ActivatedRoute, ParamMap, Router } from '@angular/router';
import { AppService } from '../app.service';
import { ExpenseComponent } from '../expense/expense.component';
import { ExpenseService } from '../expense/expense.service';

@Component({
  selector: 'app-history',
  templateUrl: './history.component.html',
  styleUrls: ['./history.component.css'],
})
export class HistoryComponent {
  // expenses!: ExpenseComponent[]

  add() {
    this.router.navigate(['addExpensePage/']);
  }
  displayedColumns: string[] = ['id', 'name', 'progress', 'fruit'];
  columns: string[] = ['number', 'category', 'cost'];
  dataSource!: any;

  @ViewChild(MatPaginator)
  paginator!: MatPaginator;
  @ViewChild(MatSort)
  sort!: MatSort;
  expenses: any[] = [];
  expense!: [];

  constructor(
    public appService: AppService,
    private http: HttpClient,
    private router: Router,
    private route: ActivatedRoute
  ) {
    this.route.paramMap.subscribe((params: ParamMap) => {
      this.appService.userId = Number(params.get('id'));
      console.log(this.appService.userId)
    });
    this.appService.getExpensesById().subscribe((data: any) => {
      // this.expenses = Array(data);
      for (const prop in data) {
        this.expenses.push(data[prop]);
      }
      //
      this.dataSource = new MatTableDataSource(this.expenses);
    });
  }

  ngAfterViewInit() {
    if (this.dataSource) {
      this.dataSource.paginator = this.paginator;
      this.dataSource.sort = this.sort;
    }
  }


  ngOnInit(): void {

    // console.log(this.appService.userData);

    // this.route.paramMap.subscribe((params: ParamMap) => {
    //   this.appService.userId = Number(params.get('id'));
    // });
    // console.log(this.appService.userId);
    // this.appService.getExpensesById().subscribe((data: any) => {
    //   // this.expenses = Array(data);
    //   console.log(this.expenses);
    //   for (const prop in this.appService.userData) {
    //     this.expenses.push(this.appService.userData[prop]);
    //   }

    //   this.dataSource = new MatTableDataSource(this.expenses);
    // });
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
