import {
  CUSTOM_ELEMENTS_SCHEMA,
  NgModule,
  NO_ERRORS_SCHEMA,
} from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { MatChipsModule } from '@angular/material/chips';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { FormsModule } from '@angular/forms';
import {MatTableModule} from '@angular/material/table';
import {MatSortModule} from '@angular/material/sort';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { MatIconModule } from '@angular/material/icon';
import { HttpClientModule } from '@angular/common/http';
import {MatProgressBarModule} from '@angular/material/progress-bar';
import {MatRadioModule} from '@angular/material/radio';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { HeaderComponent } from './header/header.component';
import { HistoryComponent } from './history/history.component';
import { HomepageComponent } from './homepage/homepage.component';
import {MatPaginatorModule} from '@angular/material/paginator';

import {MatCardModule} from '@angular/material/card';
import { CategoryLimitsComponent } from './category-limits/category-limits.component';
import { ExpenseComponent } from './expense/expense.component';
import { ExpenseService } from './expense/expense.service';
import {MatButtonModule} from '@angular/material/button';
import { ReactiveFormsModule } from '@angular/forms';
import { AppService } from './app.service';
import { DashboardComponent } from './dashboard/dashboard.component';
import { AddExpensePageComponent } from './add-expense-page/add-expense-page.component';

@NgModule({
  schemas: [CUSTOM_ELEMENTS_SCHEMA, NO_ERRORS_SCHEMA],
  declarations: [AppComponent, HeaderComponent, HistoryComponent, HomepageComponent, CategoryLimitsComponent, ExpenseComponent, DashboardComponent, AddExpensePageComponent],
  imports: [
    BrowserModule,
    MatChipsModule,
    AppRoutingModule,
    HttpClientModule,
    MatInputModule,
    MatFormFieldModule,
    MatProgressBarModule,
    MatRadioModule,
    MatIconModule,
    ReactiveFormsModule,
    FormsModule,
    MatSortModule,
    MatButtonModule,
    MatTableModule,
    MatPaginatorModule,
MatCardModule,
    BrowserAnimationsModule,
  ],
  providers: [ExpenseService, AppService],
  bootstrap: [AppComponent],
})
export class AppModule {}
