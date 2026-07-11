import { Component } from '@angular/core';
import { MessageService } from 'primeng/api';
import { Plan } from '../../../model/user.model';
import { PlanService } from '../../../service/plan.service';
import { ThemeService } from '../../../service/theme/thema.service';

@Component({
  selector: 'app-inicio',
  standalone: false,
  templateUrl: './inicio.html',
  styleUrl: './inicio.css',
})
export class Inicio {

  planes: Plan[] = [];

  constructor(
    private messageService: MessageService,
    private planService: PlanService,
    private themeService: ThemeService
  ) {}

  showDemoMessage() {
    this.messageService.add({
      severity: 'warn',
      summary: 'Función no disponible',
      detail: 'Esta opción aún no está habilitada.'
    });
  }

  ngOnInit(): void {

    this.cargarPlanes();
    this.themeService.useSystemTheme();    

  }

  cargarPlanes(): void {
    this.planService.getPlanes().subscribe({
      next: (res) => {
        this.planes = res;
        console.log(this.planes);
      },
      error: (err) => {
        console.error('Error cargando plan', err);
      }
    });
  }

  obtenerTextoBoton(nombre: string): string {

    switch (nombre.toLowerCase()) {

      case 'free':
        return 'Obtener gratis';

      case 'pro':
        return 'Obtener Pro';

      case 'business':
        return 'Obtener Business';

      case 'enterprise':
        return 'Contactar ventas';

      default:
        return 'Elegir plan';
    }

  }

  seleccionarPlan(plan: Plan): void {

    if (plan.nombre === 'Free') {
      return;
    }

    if (plan.nombre === 'Enterprise') {
      this.contactSales();
      return;
    }

    this.selectPlan(plan.nombre);

  }

  selectPlan(plan: string) {
    console.log('Plan seleccionado:', plan);
  }

  contactSales() {
    console.log('Contactar ventas');
  }

  obtenerIconoConfig(nombre: string): { icon: string; color: string } {

    switch (nombre.toLowerCase()) {

      case 'free':
        return {
          icon: 'leaf',
          color: 'var(--color-grey)'
        };

      case 'pro':
        return {
          icon: 'zap',
          color: 'var(--color-primary)'
        };

      case 'business':
        return {
          icon: 'building-2',
          color: 'var(--color-purple)'
        };

      case 'enterprise':
        return {
          icon: 'crown',
          color: 'var(--color-yellow)'
        };

      default:
        return {
          icon: 'package',
          color: 'var(--color-grey)'
        };
    }
  }
  

}
