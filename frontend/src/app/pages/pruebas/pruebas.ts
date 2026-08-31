import { Component } from '@angular/core';
import {
  MenuItem,
  MegaMenuItem,
  ConfirmationService,
  MessageService
} from 'primeng/api';

import { ThemeService, Theme } from '../../../service/theme/thema.service';
@Component({
  selector: 'app-pruebas',
  standalone: false,
  templateUrl: './pruebas.html',
  styleUrl: './pruebas.css',
})
export class Pruebas {

  // =========================================================
  // THEME
  // =========================================================

  currentTheme: 'light' | 'dark' | 'system' = 'system';

  // =========================================================
  // INPUTS
  // =========================================================

  textValue = '';

  searchValue = '';

  passwordValue = '';

  textareaValue = '';

  floatValue = '';

  emailValue = '';


  // =========================================================
  // SELECT
  // =========================================================

  cities = [
    {
      name: 'Madrid',
      code: 'MAD'
    },
    {
      name: 'Barcelona',
      code: 'BCN'
    },
    {
      name: 'Valencia',
      code: 'VAL'
    },
    {
      name: 'Sevilla',
      code: 'SEV'
    },
    {
      name: 'Bilbao',
      code: 'BIO'
    }
  ];

  selectedCity: any = null;

  selectedCities: any[] = [];


  // =========================================================
  // CONTROLS
  // =========================================================

  toggleValue = false;

  checkboxValue = false;

  sliderValue = 50;

  knobValue = 65;


  // =========================================================
  // DATE
  // =========================================================

  dateValue: Date | null = null;


  // =========================================================
  // BUTTON
  // =========================================================

  loading = false;


  // =========================================================
  // PROGRESS
  // =========================================================

  progressValue = 65;


  // =========================================================
  // TOGGLE BUTTON
  // =========================================================

  toggleButtonValue = false;


  // =========================================================
  // SELECT BUTTON
  // =========================================================

  selectButtonOptions = [
    'Opción 1',
    'Opción 2',
    'Opción 3'
  ];

  selectedOption = 'Opción 1';


  // =========================================================
  // DIALOG
  // =========================================================

  dialogVisible = false;


  // =========================================================
  // DRAWER
  // =========================================================

  drawerVisible = false;


  // =========================================================
  // BLOCK UI
  // =========================================================

  blocked = false;


  // =========================================================
  // MENUS
  // =========================================================

  menuItems: MenuItem[] = [

    {
      label: 'Inicio',
      icon: 'pi pi-home'
    },

    {
      label: 'Usuarios',
      icon: 'pi pi-users',
      items: [
        {
          label: 'Lista',
          icon: 'pi pi-list'
        },
        {
          label: 'Crear',
          icon: 'pi pi-plus'
        }
      ]
    },

    {
      label: 'Configuración',
      icon: 'pi pi-cog',
      items: [
        {
          label: 'General',
          icon: 'pi pi-sliders-h'
        },
        {
          label: 'Seguridad',
          icon: 'pi pi-shield'
        }
      ]
    },

    {
      separator: true
    },

    {
      label: 'Cerrar sesión',
      icon: 'pi pi-sign-out'
    }

  ];


  // =========================================================
  // MEGA MENU
  // =========================================================

  megaMenuItems: MegaMenuItem[] = [

    {
      label: 'Productos',
      icon: 'pi pi-box',
      items: [
        [
          {
            label: 'Categorías',
            items: [
              {
                label: 'Software'
              },
              {
                label: 'Hardware'
              }
            ]
          }
        ],
        [
          {
            label: 'Servicios',
            items: [
              {
                label: 'Consultoría'
              },
              {
                label: 'Soporte'
              }
            ]
          }
        ]
      ]
    },

    {
      label: 'Empresa',
      icon: 'pi pi-building',
      items: [
        [
          {
            label: 'Información',
            items: [
              {
                label: 'Nosotros'
              },
              {
                label: 'Contacto'
              }
            ]
          }
        ]
      ]
    }

  ];


  // =========================================================
  // CHART
  // =========================================================

  chartData: any;

  chartOptions: any;


  // =========================================================
  // GALLERIA
  // =========================================================

  images = [
    {
      itemImageSrc: 'https://picsum.photos/id/1015/1000/600',
      thumbnailImageSrc: 'https://picsum.photos/id/1015/250/150',
      alt: 'Imagen 1'
    },
    {
      itemImageSrc: 'https://picsum.photos/id/1016/1000/600',
      thumbnailImageSrc: 'https://picsum.photos/id/1016/250/150',
      alt: 'Imagen 2'
    },
    {
      itemImageSrc: 'https://picsum.photos/id/1018/1000/600',
      thumbnailImageSrc: 'https://picsum.photos/id/1018/250/150',
      alt: 'Imagen 3'
    },
    {
      itemImageSrc: 'https://picsum.photos/id/1020/1000/600',
      thumbnailImageSrc: 'https://picsum.photos/id/1020/250/150',
      alt: 'Imagen 4'
    }
  ];


  // =========================================================
  // IMAGE COMPARE
  // =========================================================

  compareImages = {
    left: 'https://picsum.photos/id/1015/1000/600',
    right: 'https://picsum.photos/id/1016/1000/600'
  };


  // =========================================================
  // CONSTRUCTOR
  // =========================================================

  constructor(
    public themeService: ThemeService,
    private confirmationService: ConfirmationService,
    private messageService: MessageService
  ) {}


  // =========================================================
  // INIT
  // =========================================================

  ngOnInit(): void {

    this.currentTheme =
      this.themeService.getCurrentTheme();

    this.themeService.theme$.subscribe(theme => {

      this.currentTheme = theme;

      this.updateChart();

    });

    this.updateChart();

  }


  // =========================================================
  // THEME
  // =========================================================

  setTheme(theme: Theme): void {

    this.themeService.setTheme(theme);

  }


  // =========================================================
  // BUTTON LOADING
  // =========================================================

  simulateLoading(): void {

    if (this.loading) {
      return;
    }

    this.loading = true;

    setTimeout(() => {

      this.loading = false;

      this.messageService.add({
        severity: 'success',
        summary: 'Completado',
        detail: 'La operación terminó correctamente.'
      });

    }, 1500);

  }


  // =========================================================
  // CONFIRM
  // =========================================================

  confirmDelete(): void {

    this.confirmationService.confirm({

      message: '¿Estás seguro de que quieres eliminar este elemento?',

      header: 'Confirmar eliminación',

      icon: 'pi pi-exclamation-triangle',

      acceptLabel: 'Eliminar',

      rejectLabel: 'Cancelar',

      acceptButtonStyleClass: 'p-button-danger',

      rejectButtonStyleClass: 'p-button-secondary',

      accept: () => {

        this.messageService.add({
          severity: 'success',
          summary: 'Eliminado',
          detail: 'El elemento fue eliminado.'
        });

      },

      reject: () => {

        this.messageService.add({
          severity: 'info',
          summary: 'Cancelado',
          detail: 'La operación fue cancelada.'
        });

      }

    });

  }


  // =========================================================
  // TOAST
  // =========================================================

  showSuccess(): void {

    this.messageService.add({
      severity: 'success',
      summary: 'Success',
      detail: 'Operación realizada correctamente.'
    });

  }


  showInfo(): void {

    this.messageService.add({
      severity: 'info',
      summary: 'Información',
      detail: 'Este es un mensaje informativo.'
    });

  }


  showWarn(): void {

    this.messageService.add({
      severity: 'warn',
      summary: 'Advertencia',
      detail: 'Ten cuidado con esta acción.'
    });

  }


  showError(): void {

    this.messageService.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Ha ocurrido un error.'
    });

  }


  // =========================================================
  // CHART
  // =========================================================

  private updateChart(): void {

    const dark =
      this.currentTheme === 'dark';

    const textColor =
      dark
        ? '#f8fafc'
        : '#334155';

    const gridColor =
      dark
        ? '#334155'
        : '#e2e8f0';

    this.chartData = {

      labels: [
        'Enero',
        'Febrero',
        'Marzo',
        'Abril',
        'Mayo',
        'Junio'
      ],

      datasets: [

        {
          label: 'Ventas',

          data: [
            65,
            59,
            80,
            81,
            56,
            75
          ],

          backgroundColor: '#10b981',

          borderColor: '#10b981',

          borderWidth: 1,

          borderRadius: 8

        }

      ]

    };


    this.chartOptions = {

      responsive: true,

      maintainAspectRatio: false,

      plugins: {

        legend: {
          labels: {
            color: textColor
          }
        }

      },

      scales: {

        x: {
          ticks: {
            color: textColor
          },

          grid: {
            color: gridColor
          }
        },

        y: {
          ticks: {
            color: textColor
          },

          grid: {
            color: gridColor
          }
        }

      }

    };

  }
}
