import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AddExpensePageComponent } from './add-expense-page.component';

describe('AddExpensePageComponent', () => {
  let component: AddExpensePageComponent;
  let fixture: ComponentFixture<AddExpensePageComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ AddExpensePageComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AddExpensePageComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
