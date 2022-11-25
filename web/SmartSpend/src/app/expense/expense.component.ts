import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-expense',
  templateUrl: './expense.component.html',
  styleUrls: ['./expense.component.css']
})
export class ExpenseComponent {
  @Input() expense!: any;
  @Input() category!: String;
  @Input() cost!: String;
  @Input() timestamp!:String;

}
