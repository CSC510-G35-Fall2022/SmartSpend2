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
  // {path: ':id/homepage', component: HomepageComponent },
  {path: ':id/history', component: HistoryComponent},
  {path: ':id/limits', component: CategoryLimitsComponent},
  {path: ':id/dashboard', component: DashboardComponent},
  {path: ':id/addExpensePage', component: AddExpensePageComponent},

  {path: ':id', redirectTo: ':id/dashboard', pathMatch:'full'},
  {path: '', component: AppComponent},

];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
