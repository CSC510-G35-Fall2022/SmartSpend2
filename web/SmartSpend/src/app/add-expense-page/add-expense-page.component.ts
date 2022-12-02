import { getLocaleTimeFormat } from '@angular/common';
import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { AppService } from '../app.service';

@Component({
  selector: 'app-add-expense-page',
  templateUrl: './add-expense-page.component.html',
  styleUrls: ['./add-expense-page.component.css']
})
export class AddExpensePageComponent {
  constructor(private fb: FormBuilder, public appService: AppService) {
    
  }
  category = ""
  cost = 0
  public expenseForm: FormGroup = this.fb.group({
    category: [this.category, [Validators.required]],
    cost: [this.cost, [Validators.required]]
  });

  addExpense() {
    
    console.log(Date.now())

    let expense = {
      'user_telegram_id': this.appService.userId,
      'category':  this.expenseForm.controls['category'].value,
      'cost': this.expenseForm.controls['cost'].value,
      'timestamp': Date.now(),
      'number': this.appService.nextNumber
    }
    console.log(expense);
    this.appService.sendExpense(expense);


  }
}
