import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { AddExpensePageComponent } from './add-expense-page/add-expense-page.component';
import { AppComponent } from './app.component';
import { CategoryLimitsComponent } from './category-limits/category-limits.component';
import { DashboardComponent } from './dashboard/dashboard.component';
import { HeaderComponent } from './header/header.component';
import { HistoryComponent } from './history/history.component';
import { HomepageComponent } from './homepage/homepage.component';

const routes: Routes = [
  { path: 'homepage', component: HomepageComponent },
  {path: 'history', component: HistoryComponent},
  {path: 'limits', component: CategoryLimitsComponent},
  {path: 'dashboard', component: DashboardComponent},
  {path: 'addExpensePage', component: AddExpensePageComponent},

  {path: '', redirectTo: 'homepage', pathMatch:'full'},

];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
