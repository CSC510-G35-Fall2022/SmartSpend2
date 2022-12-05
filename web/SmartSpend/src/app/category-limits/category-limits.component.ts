import { T } from '@angular/cdk/keycodes';
import { Component, OnInit } from '@angular/core';
import { ThemePalette } from '@angular/material/core';
import { ProgressBarMode } from '@angular/material/progress-bar';
import { ActivatedRoute, ParamMap } from '@angular/router';
import { AppService } from '../app.service';
import { DashboardComponent } from '../dashboard/dashboard.component';

@Component({
  selector: 'app-category-limits',
  templateUrl: './category-limits.component.html',
  styleUrls: ['./category-limits.component.css'],
})
export class CategoryLimitsComponent implements OnInit {
  color: ThemePalette = 'primary';
  mode: ProgressBarMode = 'determinate';
  monthlyValue = 50;
  dailyValue = 50;
  yearlyValue = 50;
  value = 1;
  food!: any;
  list: any = {};
  daily!: any;
  monthly!: any;
  yearly!: any;
  grocery!: any;
  bufferValue = 75;
  limits: any;
  currentSpent: any;
  foodProgress: any;
  monthProgress: any;

  constructor(public appService: AppService, public route: ActivatedRoute) {
    console.log('here');
    console.log('user limits', this.appService.userLimits);
    // this.appService.getLimitsForUser().subscribe((data: any) => {
    //   console.log('hi');
    //   this.appService.userLimits = data;
    //   console.log('this the data', data);
    //   this.appService.userLimits = data
    //   this.limits = {
    //     // yearly: this.appService.userLimits.yearly ?? 0,
    //     daily: this.appService.userLimits.daily ?? 0,
    //     monthly: this.appService.userLimits.monthly ?? 0,
    //     food: this.appService.userLimits.Food ?? 0
    //   }
    //   console.log('food limit', this.appService.userLimits.Food);
    //   this.foodProgress = 100 * this.findSpent('Food') / Number(this.appService.userLimits.Food ?? 100) ;
    //   console.log('food progress: ' + this.foodProgress);
    //   this.monthProgress = 100 * 30 / Number(this.appService.userLimits.monthly ?? 100);
    // });
  }

  findSpent(category: String): any {
    // console.log(this.appService.userLimits);
    if (this.appService.userLimits !== undefined) {
      let temp = this.appService.userData?.filter(
        (data: { category: string }) => data.category == category
      );
      let val: number = 0;
      temp.map((data: { cost: number }) => (val += Number(data.cost)));
      return val;
    }
    return 0;
  }

  getProgress(category: string) {
    // console.log('progress', category);
    var denominator = 10000;
    // console.log('denominator', denominator);
    if (category == 'Food') {
      denominator = this.appService.userLimits[0].Food;
    } else if (category == 'Groceries') {
      denominator = this.appService.userLimits[0]?.Groceries;
    } else if (category == 'Utilities') {
      denominator = this.appService.userLimits[0]?.Utilities;
    } else if (category == 'Transport') {
      denominator = this.appService.userLimits[0]?.Transport;
    } else if (category == 'daily') {
      denominator = this.appService.userLimits[0]?.daily;
    } else if (category == 'yearly') {
      denominator = this.appService.userLimits[0]?.yearly;
    } else if (category == 'monthly') {
      denominator = this.appService.userLimits[0]?.monthly;
    }
    // console.log('denominator', denominator)
    return (100 * this.findSpent(category)) / Number(denominator);
  }

  setLimit(field: string) {
    console.log(this.appService.userLimits[0]);
    console.log('before:', this.appService.userLimits[0]);

    this.appService.userLimits[0][field] = this.list[field];
    console.log('after update', this.list);
    console.log(
      "   this.appService.userLimits[0]['field']",
      this.appService.userLimits[0][field] ?? 'none'
    );
    console.log('after:', this.appService.userLimits[0]);
    this.appService.setLimitsforUser(this.appService.userLimits[0])
  }
  ngOnInit(): void {
    this.route.paramMap.subscribe((params: ParamMap) => {
      this.appService.userId = params.get('id');
    });
    console.log('id:', this.appService.userId);

    this.appService.getExpensesById().subscribe((data: any[]) => {
      this.appService.userData = data;
      this.appService.getLimitsForUser().subscribe((data: any) => {
        console.log('hi');
        this.appService.userLimits = data;
        console.log('this the data', data);
        this.appService.userLimits = data;
        this.limits = {
          // yearly: this.appService.userLimits.yearly ?? 0,
          daily: this.appService.userLimits.daily ?? 0,
          monthly: this.appService.userLimits.monthly ?? 0,
          food: this.appService.userLimits.Food ?? 0,
        };
        console.log('food limit', this.appService.userLimits.Food);
        this.foodProgress =
          (100 * this.findSpent('Food')) /
          Number(this.appService.userLimits.Food ?? 100);
        console.log('food progress: ' + this.foodProgress);
        this.monthProgress =
          (100 * 30) / Number(this.appService.userLimits.monthly ?? 100);
      });
    });
  }
}
