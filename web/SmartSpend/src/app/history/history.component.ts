import { Component } from '@angular/core';
import { ExpenseComponent } from '../expense/expense.component';

@Component({
  selector: 'app-history',
  templateUrl: './history.component.html',
  styleUrls: ['./history.component.css']
})
export class HistoryComponent {
  expenses!: ExpenseComponent[]

  


}
