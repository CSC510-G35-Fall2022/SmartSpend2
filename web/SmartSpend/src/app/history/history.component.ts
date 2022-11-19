import { Component } from '@angular/core';
import { ExpenseComponent } from '../expense/expense.component';
import { ExpenseService } from '../expense/expense.service';

@Component({
  selector: 'app-history',
  templateUrl: './history.component.html',
  styleUrls: ['./history.component.css']
})
export class HistoryComponent {
  expenses!: ExpenseComponent[]
  constructor(public expenseService: ExpenseService) {}

  ngOnInit(): void {
    this.expenseService.getExpenses();
    console.log(this.expenseService.expenseData);
    
  }




}
