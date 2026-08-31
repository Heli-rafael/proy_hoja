import { Component } from '@angular/core';
import { ThemeService, Theme } from '../../../service/theme/thema.service';
import { PlanModel, PlanPrecioModel, PlanCardModel, User } from '../../../model/user.model';
import { UserService } from '../../../service/user.service';
import { PlanService } from '../../../service/plan.service';
import { SolicitudCambioPlan } from '../../../model/solicitud-plan.model';
import { MessageService } from 'primeng/api';

@Component({
  selector: 'app-plan',
  standalone: false,
  templateUrl: './plan.html',
  styleUrl: './plan.css',
})
export class Plan {


  planes: PlanModel[] = [];
  planesPrecio: PlanPrecioModel [] = [];
  planesMostrar: PlanCardModel[] = [];
  
  billing: 'mensual' | 'anual' = 'mensual';
  user?: User;

  solicitudActual: SolicitudCambioPlan[] | null = [] ;



  constructor(
    private messageService: MessageService,
    private themeService: ThemeService,
    private userService: UserService,
    private planService: PlanService,
  ){} 


  ngOnInit(): void {
    this.cargarPlanes();
    this.cargarSolicitud();
    this.cargarPlanesPrecio();

    // THEME
    const chatTheme =
        (localStorage.getItem('user-theme') as Theme) ?? 'system';
  
    this.themeService.setTheme(chatTheme);  

    // USER
    this.userService.getProfile().subscribe(user => {
      this.user = user;
    });

  }

  cargarPlanes(): void {
    this.planService.getPlanes().subscribe({
      next: (res) => {
        this.planes = res;
      },
    });
  }

  cargarPlanesPrecio(): void {
    this.planService.getPrecioPlanes().subscribe({
      next: (res) => {
        this.planesPrecio = res;
        this.armarPlanes();
      },
    });
  }

  armarPlanes(){

    if(
      this.planes.length === 0 ||
      this.planesPrecio.length === 0
    ){
      return;
    }


    this.planesMostrar = this.planes
      .map(plan=>{

        const precio = this.planesPrecio.find(
          p =>
          p.plan.id === plan.id &&
          p.periodo === this.billing.toUpperCase()
        );


        if(!precio){
          return null;
        }


        return {
          plan,
          precio
        };

      })
      .filter(Boolean) as PlanCardModel[];

  }

  cambiarPeriodo(periodo:'mensual'|'anual'){

    this.billing = periodo;

    this.armarPlanes();

  }

  cargarSolicitud(){
    this.planService.obtenerSolicitudActual()
    .subscribe({
        next:(res)=>{
          this.solicitudActual = res;
        },
    });
  }

  obtenerIconoConfig(nombre: string): { icon: string; color: string } {

    switch (nombre.toLowerCase()) {

      case 'free':
        return {
          icon: 'leaf',
          color: 'var(--text-secondary)'
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
          color: 'var(--color-yellow-secondary)'
        };

      default:
        return {
          icon: 'package',
          color: 'var(--text-secondary)'
        };
    }
  }

  colorPlanSeleccionado(): string {
    return this.planSeleccionado
      ? this.obtenerIconoConfig(this.planSeleccionado.plan.nombre).color
      : 'transparent';
  }

  

  obtenerTextoBoton(planNombre: string, planActual: string): string {

    if (planNombre === planActual) {
        return 'Plan actual';
    }

    return 'Seleccionar plan';
  }

  obtenerSolicitudPendiente(planPrecioId:number){

    return this.solicitudActual?.find(
      s =>
      s.estado === 'PENDIENTE' &&
      s.plan_solicitado.id === planPrecioId
    );

  }

  // DIALOG
  planSeleccionado?: PlanCardModel;

  mostrarDialogPlan = false;

  metodoPago = '';

  voucher?: File;
  imagePreview?: string;

  observacion = '';

  seleccionarPlan(item: PlanCardModel): void {

    if (item.plan.nombre === 'Free') {
        return;
    }

    this.planSeleccionado =item;
    this.mostrarDialogPlan = true;
  }

  seleccionarArchivo(event:any){

    const file = event.target.files[0];

    if(!file){
      return;
    }

    // validar tamaño
    if(file.size > 5000000){
      this.messageService.add({
        severity: 'warn',
        summary: 'Archivo demasiado grande',
        detail: 'El comprobante no debe superar los 5MB.',
      });
      return;
    }

    this.voucher = file;

    // preview solo imágenes
    if(file.type.startsWith('image')){
      const reader = new FileReader();
      reader.onload = () => {
          this.imagePreview = reader.result as string;
      };
      reader.readAsDataURL(file);
    }else{
      this.imagePreview = undefined;
    }

  }

  eliminarArchivo(){
    this.voucher = undefined;
    this.imagePreview = undefined;
  }

  cerrarDialog(){
    this.mostrarDialogPlan = false;
    this.voucher = undefined;
    this.imagePreview = undefined;
    this.metodoPago = '';
    this.observacion = '';
  }

  enviarSolicitud(){
    if(!this.planSeleccionado){
      this.messageService.add({
          severity: 'warn',
          summary: 'Plan no seleccionado',
          detail: 'Debe seleccionar un plan para continuar.',
      });
      return;
    }

    if(!this.metodoPago){
      this.messageService.add({
          severity: 'warn',
          summary: 'Método de pago requerido',
          detail: 'Seleccione un método de pago.',
      });
      return;
    }

    if(!this.voucher){
      this.messageService.add({
          severity: 'warn',
          summary: 'Comprobante requerido',
          detail: 'Adjunte su comprobante de pago.',
      });
      return;
    }

    const formData = new FormData();

    formData.append(
    "plan_solicitado_id",
    this.planSeleccionado.precio.id.toString()
    );

    formData.append("metodo_pago",this.metodoPago);
    formData.append("comprobante",this.voucher);
    formData.append("observacion",this.observacion);

    this.mostrarDialogPlan = false;

    this.planService.enviarSolicitudCambioPlan(formData)
    .subscribe({

        next:(response)=>{
          this.messageService.add({
            severity:'success',
            summary:'Solicitud enviada',
            detail:'Tu solicitud fue enviada correctamente.'
          });
          this.cargarPlanes();
          this.cargarSolicitud();
          this.cerrarDialog();
        },

        error:(error)=>{
          this.messageService.add({
            severity:'error',
            summary:'Error',
            detail:'No se pudo enviar la solicitud.'
          });
        }
    });
  }

  
}
