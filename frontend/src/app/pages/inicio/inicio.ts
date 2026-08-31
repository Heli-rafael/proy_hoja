import { Component } from '@angular/core';
import { MessageService } from 'primeng/api';
import { PlanModel, PlanPrecioModel, PlanCardModel } from '../../../model/user.model';
import { PlanService } from '../../../service/plan.service';
import { ThemeService } from '../../../service/theme/thema.service';
import { Router } from '@angular/router';

export interface LesionDetectada {
  id: number;
  title: string;
  description: string;
  type: string;
  confidence: number;
  bbox: {
    x1: number;
    y1: number;
    x2: number;
    y2: number;
  };
}

export interface CuidadoPlanta {
  titulo: string;
  descripcion: string;
  consejo: string;
  imagen: string;
}

@Component({
  selector: 'app-inicio',
  standalone: false,
  templateUrl: './inicio.html',
  styleUrl: './inicio.css',
})
export class Inicio {

  planes: PlanModel[] = [];
  planesPrecio: PlanPrecioModel [] = [];
  planesMostrar: PlanCardModel[] = [];

  billing: 'mensual' | 'anual' = 'mensual';

  // DETECCIONES
  lesionesDetectadas: LesionDetectada[] = [
    {
      id: 1,
      title: 'Deterioro de tejido pálido',
      description: 'Área localizada de decoloración grisácea blanquecina y deterioro del tejido en las pinnas de un fronde central del helecho.',
      type: 'tissue_deterioration',
      confidence: 0.94,
      bbox: {
        x1: 0.564,
        y1: 0.361,
        x2: 0.750,
        y2: 0.640
      }
    },
    {
      id: 2,
      title: 'Punteado clorótico',
      description: 'Punteado fino y localizado con pequeñas áreas de clorosis y moteado en las pinnulas inferiores izquierdas.',
      type: 'chlorosis',
      confidence: 0.91,
      bbox: {
        x1: 0.180,
        y1: 0.590,
        x2: 0.428,
        y2: 1.032
      }
    },
    
  ];

  constructor(
    private router: Router,
    private messageService: MessageService,
    private planService: PlanService,
    private themeService: ThemeService
  ) {}

  openLogin() {
    this.router.navigate(["/auth/login"]);
  }

  openRegister() {
    this.router.navigate(['/auth/login'], {
      queryParams: {
        view: 'register'
      }
    });
  }

  showDemoMessage() {
    this.messageService.add({
      severity: 'warn',
      summary: 'Función no disponible',
      detail: 'Esta opción aún no está habilitada.'
    });
  }

  ngOnInit(): void {
    this.cargarPlanesPrecio();
    this.cargarPlanes();
    this.themeService.useSystemTheme();    
  }

  ngAfterViewInit(): void {
    this.configurarObserverNavegacion();
    this.configurarObserverFuncionamiento();
    this.configurarObserverCuidados();
  }

  ngOnDestroy(): void {

    this.detenerCarrusel();

    if (this.observerFuncionamiento) {
      this.observerFuncionamiento.disconnect();
    }

    if (this.observerSecciones) {
      this.observerSecciones.disconnect();
    }

    if (this.observerCuidados) {
      this.observerCuidados.disconnect();
    }

  }
  
  // FUNCIONAMIENTO - CARRUSEL
  private configurarObserverFuncionamiento(): void {
    const seccionFuncionamiento = document.getElementById('funcionamiento');
    if (!seccionFuncionamiento) {
      return;
    }

    this.observerFuncionamiento =
      new IntersectionObserver(
        (entries) => {

          const entry = entries[0];

          if (entry.isIntersecting) {
            this.iniciarCarrusel();
          } else {
            this.detenerCarrusel();
          }
        },
        {threshold: 0.35}
      );
    this.observerFuncionamiento.observe(
      seccionFuncionamiento
    );
  }

  // CUIDADOS - CARRUSEL
  private configurarObserverCuidados(): void {
    const seccionCuidados = document.getElementById('cuidados');
    if (!seccionCuidados) {
      return;
    }
    this.observerCuidados =
      new IntersectionObserver(
        (entries) => {

          const entry = entries[0];

          if (entry.isIntersecting) {
            this.iniciarCarruselCuidados();
          } else {
            this.detenerCarruselCuidados();
          }
        },
        {threshold: 0.35}
      );
    this.observerCuidados.observe(
      seccionCuidados
    );
  }

  // NAVBAR
  private configurarObserverNavegacion(): void {

    const secciones = [
      'inicio',
      'funcionamiento',
      'caracteristicas',
      'planes',
      'cuidados'
    ];

    const elementos = secciones
      .map(id => document.getElementById(id))
      .filter((element): element is HTMLElement => !!element);

    if (elementos.length === 0) {
      return;
    }

   this.observerSecciones =
    new IntersectionObserver(
      (entries) => {

        const visibles = entries
          .filter(entry => entry.isIntersecting)
          .sort(
            (a, b) =>
              b.intersectionRatio -
              a.intersectionRatio
          );

        if (visibles.length > 0) {

          this.seccionActiva =
            (visibles[0].target as HTMLElement).id;

        }

      },
      {
        threshold: [0.15, 0.3, 0.5, 0.7],
        rootMargin: '-90px 0px -45% 0px'
      }
    );

    elementos.forEach(elemento => {

      this.observerSecciones.observe(elemento);

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

  cargarPlanes(): void {
    this.planService.getPlanes().subscribe({
      next: (res) => {
        this.planes = res;
        this.armarPlanes();
      },
      error: (err) => {
      }
    });
  }
  cargarPlanesPrecio(): void {
    this.planService.getPrecioPlanes().subscribe({
      next: (res) => {
        this.planesPrecio = res;
        this.armarPlanes();
      },
      error: (err) => {
      }
    });
  }

  cambiarPeriodo(periodo:'mensual'|'anual'){

    this.billing = periodo;

    this.armarPlanes();

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

  seleccionarPlan() {
    this.router.navigate(['/page/plan']);
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
          color: 'var(--color-yellow-secondary)'
        };

      default:
        return {
          icon: 'package',
          color: 'var(--color-grey)'
        };
    }
  }
  

  /*=========================================================
          CORRUSEL
  =========================================================*/
  imagenesPlantas: string[] = [
    '/landingpage/carrusel/jardin-botanico.webp',
    '/landingpage/carrusel/mini-huerto.webp',
    '/landingpage/carrusel/planta-ciudad.webp',
    '/landingpage/carrusel/planta-flor.webp',
    '/landingpage/carrusel/planta-monstera.webp',
    '/landingpage/carrusel/planta-riego.webp',
    '/landingpage/carrusel/planta-ventana.webp',
    '/landingpage/carrusel/plantas-arquitectura.webp',
    '/landingpage/carrusel/plantas-balcon.webp',
    '/landingpage/carrusel/plantas-decorativas.webp',
    '/landingpage/carrusel/plantas-interior.webp',
  ];

  trackByImagen(index: number, imagen: string): string {
    return imagen;
  }

  // =========================================================
  // FUNCIONAMIENTO - CARRUSEL
  // =========================================================

  pasoActual = 0;

  private intervaloCarrusel: any;
  private observerFuncionamiento!: IntersectionObserver;

  pasos = [
    {
      titulo: 'Toma una foto',
      descripcion: 'Captura o sube una imagen de tu planta. Procura que las hojas y las zonas afectadas sean claramente visibles para obtener un análisis más preciso.',
      imagen: 'landingpage/funcionamiento/paso-1.png'
    },

    {
      titulo: 'La IA analiza',
      descripcion: 'Nuestro sistema de inteligencia artificial procesa la imagen e identifica patrones relacionados con enfermedades, plagas y posibles daños en la planta.',
      imagen: 'landingpage/funcionamiento/paso-2.png'
    },

    {
      titulo: 'Obtén el diagnóstico',
      descripcion: 'Recibe un diagnóstico acompañado de un nivel de confianza para comprender qué problema podría estar afectando a tu cultivo.',
      imagen: 'landingpage/funcionamiento/paso-3.png'
    },

    {
      titulo: 'Aplica la recomendación',
      descripcion: 'Consulta recomendaciones de tratamiento y prevención para actuar rápidamente y proteger la salud de tus plantas.',
      imagen: 'landingpage/funcionamiento/paso-4.png'
    }
  ];

  iniciarCarrusel(): void {
    this.detenerCarrusel();
    this.intervaloCarrusel = setInterval(() => {
      this.pasoActual =
        (this.pasoActual + 1) % this.pasos.length;
    }, 6000);
  }

  detenerCarrusel(): void {
    if (this.intervaloCarrusel) {
      clearInterval(this.intervaloCarrusel);
      this.intervaloCarrusel = null;
    }
  }

  pasoSiguiente(): void {
    this.pasoActual =
      (this.pasoActual + 1) % this.pasos.length;
    this.iniciarCarrusel();
  }


  pasoAnterior(): void {
    this.pasoActual =
      (this.pasoActual - 1 + this.pasos.length)
      % this.pasos.length;
    this.iniciarCarrusel();
  }

  seleccionarPaso(index: number): void {
    this.pasoActual = index;
    this.iniciarCarrusel();
  }

  // =========================================================
  // CUIDADOS - CARRUSEL
  // =========================================================

  cuidadoActual = 0;

  private intervaloCuidados: any;
  private observerCuidados!: IntersectionObserver;

  cuidadosPlanta: CuidadoPlanta[] = [
    {
      titulo: 'Riega de forma adecuada',
      descripcion: 'El agua es fundamental para mantener una planta saludable, pero cada especie necesita una cantidad diferente. Evita tanto la falta de agua como el exceso.',
      consejo: 'Comprueba la humedad del sustrato antes de volver a regar y evita que el agua quede acumulada.',
      imagen: 'landingpage/cuidados/riego.webp'
    },
    {
      titulo: 'Proporciona suficiente luz',
      descripcion: 'La iluminación influye directamente en el crecimiento de las plantas. Algunas necesitan luz directa mientras que otras prefieren espacios con iluminación indirecta.',
      consejo: 'Observa las necesidades de cada especie y coloca la planta en un lugar con la iluminación adecuada.',
      imagen: 'landingpage/cuidados/luz.webp'
    },
    {
      titulo: 'Cuida el suelo y los nutrientes',
      descripcion: 'Un sustrato saludable permite que las raíces reciban agua, oxígeno y nutrientes. Con el tiempo, el suelo puede perder parte de sus propiedades.',
      consejo: 'Utiliza un sustrato adecuado para cada tipo de planta y proporciona nutrientes cuando sea necesario.',
      imagen: 'landingpage/cuidados/suelo.webp'
    },
    {
      titulo: 'Revisa hojas y tallos',
      descripcion: 'Las hojas y los tallos pueden mostrar señales tempranas de estrés, enfermedades o presencia de plagas.',
      consejo: 'Revisa periódicamente manchas, cambios de color, deformaciones o pequeños insectos.',
      imagen: 'landingpage/cuidados/inspeccion.webp'
    },
    {
      titulo: 'Anticiparse es cuidar mejor',
      descripcion: 'La prevención es una de las mejores formas de proteger tus plantas. Mantener una buena ventilación y detectar los primeros síntomas puede evitar que un problema se extienda.',
      consejo: 'Aísla las plantas afectadas y actúa rápidamente cuando detectes síntomas sospechosos.',
      imagen: 'landingpage/cuidados/prevencion.webp'
    }
  ];

  iniciarCarruselCuidados(): void {
    this.detenerCarruselCuidados();
    this.intervaloCuidados = setInterval(() => {
      this.cuidadoActual =
        (this.cuidadoActual + 1) %
        this.cuidadosPlanta.length;
    }, 12000);

  }

  detenerCarruselCuidados(): void {
    if (this.intervaloCuidados) {
      clearInterval(this.intervaloCuidados);
      this.intervaloCuidados = null;
    }
  }

  cuidadoSiguiente(): void {
    this.cuidadoActual =
      (this.cuidadoActual + 1) %
      this.cuidadosPlanta.length;
    this.iniciarCarruselCuidados();
  }

  cuidadoAnterior(): void {
    this.cuidadoActual =
      (this.cuidadoActual - 1 + this.cuidadosPlanta.length) %
      this.cuidadosPlanta.length;
    this.iniciarCarruselCuidados();
  }

  seleccionarCuidado(index: number): void {
    this.cuidadoActual = index;
    this.iniciarCarruselCuidados();
  }

  /*=========================================================
          CTA FINAL
  =========================================================*/
  scrollToSection(id: string): void {

    const element = document.getElementById(id);

    if (element) {
      element.scrollIntoView({
        behavior: 'smooth',
        block: 'start'
      });
    }

  }

  // =========================================================
  // CARACTERISTICAS
  // =========================================================

  featureDemo: 'diagnostico' | 'asistente' = 'diagnostico';

  setFeatureDemo(demo: 'diagnostico' | 'asistente'): void {
    this.featureDemo = demo;
    if (demo === 'asistente') {
        this.startTypingAnswer();
    }
  }
  
  // LETRAS MENSAJE IA
  answerText = `Parece una infección por hongos en las hojas.
    Retira las partes afectadas y mejora la ventilación.
    Como tratamiento natural, aplica infusión de ajo como pulverización foliar, evitando el sol directo.
    Jabón potásico: 10 mL/L, pulverizar cada 7 días.`;

  displayedAnswer = '';

  startTypingAnswer(): void {
    this.displayedAnswer = '';
    let index = 0;
    const typingSpeed = 25;
    const type = () => {
        if (index < this.answerText.length) {
            this.displayedAnswer += this.answerText[index];
            index++;
            setTimeout(type, typingSpeed);
        }
    };
    setTimeout(type, 3200);
  }

  // =========================================================
  // NAVBAR - SECCIÓN ACTIVA
  // =========================================================
  menuMobileAbierto = false;
  seccionActiva = 'inicio';

  
  private observerSecciones!: IntersectionObserver;

  toggleMenuMobile(): void {
    this.menuMobileAbierto = !this.menuMobileAbierto;
  }

  cerrarMenuMobile(): void {
    this.menuMobileAbierto = false;
  }
  

}
