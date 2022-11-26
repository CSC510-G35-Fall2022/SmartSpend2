import { T } from '@angular/cdk/keycodes';
import { Component, OnInit } from '@angular/core';
import { ThemePalette } from '@angular/material/core';
import { ProgressBarMode } from '@angular/material/progress-bar';
import { AppService } from '../app.service';
import { DashboardComponent } from '../dashboard/dashboard.component';

@Component({
  selector: 'app-category-limits',
  templateUrl: './category-limits.component.html',
  styleUrls: ['./category-limits.component.css']
})
export class CategoryLimitsComponent implements OnInit {
  color: ThemePalette = 'primary';
  mode: ProgressBarMode = 'determinate';
  monthlyValue = 50;
  dailyValue = 50;
  yearlyValue = 50;
  value = 1;
  bufferValue = 75;
  limits: any;
  currentSpent: any;
  foodProgress: any;
  monthProgress: any;

  constructor(public appService: AppService) {
    
   this.limits = {
      yearly: this.appService.userLimits.yearly ?? 0,
      daily: this.appService.userLimits.daily ?? 0,
      monthly: this.appService.userLimits.monthly ?? 0,
      food: this.appService.userLimits.Food ?? 0
    } 
    console.log('food limit', this.appService.userLimits.Food);
    this.foodProgress = 100 * this.findFoodSpent('Food') / Number(this.appService.userLimits.Food ?? 100) ;
    console.log('food progress: ' + this.foodProgress);
    this.monthProgress = 100 * 30 / Number(this.appService.userLimits.monthly ?? 100);

    
  }


  findFoodSpent(category: String): number {
    let temp = this.appService.userData.filter((data: { category: string; }) => (data.category == category))
    let val:number = 0;
    temp.map((data: {cost: number}) => val += Number(data.cost));
    return val;

  }
  ngOnInit(): void {
    
  }

  // let currentSpending = {

  // }
}

