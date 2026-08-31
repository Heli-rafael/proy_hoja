import { ComponentFixture, TestBed } from '@angular/core/testing';

import { Plan } from './plan';

describe('Plan', () => {
  let component: Plan;
  let fixture: ComponentFixture<Plan>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [Plan]
    })
    .compileComponents();

    fixture = TestBed.createComponent(Plan);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
