import { Component } from '@angular/core';
import { MessageService } from 'primeng/api';

@Component({
  selector: 'app-inicio',
  standalone: false,
  templateUrl: './inicio.html',
  styleUrl: './inicio.css',
})
export class Inicio {

  constructor(private messageService: MessageService) {}

  showDemoMessage() {
    this.messageService.add({
      severity: 'warn',
      summary: 'Función no disponible',
      detail: 'Esta opción aún no está habilitada.'
    });
  }

}
