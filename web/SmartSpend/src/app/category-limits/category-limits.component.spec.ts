import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CategoryLimitsComponent } from './category-limits.component';

describe('CategoryLimitsComponent', () => {
  let component: CategoryLimitsComponent;
  let fixture: ComponentFixture<CategoryLimitsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ CategoryLimitsComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(CategoryLimitsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
