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
  numbers!: any;

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
      this.numbers = (data.map((expense: { number: any; }) => expense.number))

      //
      this.dataSource = new MatTableDataSource(this.expenses);
    });
  }

  ngAfterViewInit() {
    // console.log(this.dataSource)
    if (this.dataSource) {
      this.dataSource.paginator = this.paginator;
      this.dataSource.sort = this.sort;
    }
  }
  delete(number: any) {
    console.log('delete', number);
    this.appService.delete(number).subscribe((data: any) => {console.log('delete', data);});
  }

  // applyFilter(event: Event) {
  //   const filterValue = (event.target as HTMLInputElement).value;
  //   this.dataSource.filter = filterValue.trim().toLowerCase();

  //   if (this.dataSource.paginator) {
  //     this.dataSource.paginator.firstPage();
  //   }
  // }

deleteAll(){
  this.appService.deleteAll().subscribe((data: any) => {console.log(data);});
}
  ngOnInit(): void {


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
