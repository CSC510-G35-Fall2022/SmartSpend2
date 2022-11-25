import { Component } from '@angular/core';
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
  expenses!: ExpenseComponent[]
  constructor(public appService: AppService, private router: Router
    ) {}

  ngOnInit(): void {
    console.log(this.appService.userData);
    
  }
  add() {
    this.router.navigate(['addExpensePage/']);

  }




}
