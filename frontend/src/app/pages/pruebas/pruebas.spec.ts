import { ComponentFixture, TestBed } from '@angular/core/testing';

import { Pruebas } from './pruebas';

describe('Pruebas', () => {
  let component: Pruebas;
  let fixture: ComponentFixture<Pruebas>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [Pruebas]
    })
    .compileComponents();

    fixture = TestBed.createComponent(Pruebas);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
