import { Component } from '@angular/core';
import { ThemePalette } from '@angular/material/core';
import { ProgressBarMode } from '@angular/material/progress-bar';

@Component({
  selector: 'app-category-limits',
  templateUrl: './category-limits.component.html',
  styleUrls: ['./category-limits.component.css']
})
export class CategoryLimitsComponent {
  color: ThemePalette = 'primary';
  mode: ProgressBarMode = 'determinate';
  monthlyValue = 50;
  dailyValue = 50;
  yearlyValue = 50;

  value = 1;
  bufferValue = 75;
}
