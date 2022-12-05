import { DatePipe, formatDate, getLocaleTimeFormat } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { AppService } from '../app.service';

@Component({
  selector: 'app-add-expense-page',
  templateUrl: './add-expense-page.component.html',
  styleUrls: ['./add-expense-page.component.css'],
})
export class AddExpensePageComponent implements OnInit {
  constructor(private fb: FormBuilder, public appService: AppService) {
    // let date =  {{today | date:'yyyy-MM-ddTHH:mm:ss.SSS':'+0:00'Z}};
  }
  category!: any;
  cost!: any;
  today = new Date();
  public expenseForm: FormGroup = this.fb.group({
    category: [this.category, [Validators.required]],
    cost: [this.cost, [Validators.required]],
  });

  addExpense() {
    let nextNumber = -1;
    this.appService.getExpensesById().subscribe((data: any) => {
      const nums = data.map((dat: any) => dat.number ?? -1);
      nextNumber = Math.max(...nums) + 1;
      console.log('number',nextNumber);
      if (nextNumber  < -1) {
        nextNumber = 0;
      }
      let expense = {
        user_telegram_id: this.appService.userId,
        category: this.expenseForm.controls['category'].value,
        cost: Number(this.expenseForm.controls['cost'].value),
        timestamp: formatDate(
          new Date(),
          'yyyy-MM-dd HH:mm:ss.SSSSSS',
          'en-US'
        ),
        number: nextNumber,
      };
      // let expense = {
      //   user_telegram_id: this.appService.userId,
      //   category: this.expenseForm.controls['category'].value,
      //   cost: Number(this.expenseForm.controls['cost'].value),
      //   timestamp: 
      //     new Date('yyyy-MM-dd HH:mm:ss.SSSSSS'),
      //   number: nextNumber,
      // };

      console.log(nextNumber)
      this.appService.sendExpense(expense);
    });
  }
  ngOnInit() {}
}
