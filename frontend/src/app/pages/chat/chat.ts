import { Component, HostListener, ViewChild, ElementRef  } from '@angular/core';
import { finalize, switchMap, tap } from 'rxjs/operators';
import { AuthService } from '../../../service/auth/auth.service';
import { MessageService } from 'primeng/api';
import { ThemeService, Theme } from '../../../service/theme/thema.service';
import { HttpClient } from '@angular/common/http';

import { ChatModel } from '../../../model/chat.model';
import { ChatService } from '../../../service/chat.service';
import { MensajeService } from '../../../service/mensaje.service';
import { MensajeModel } from '../../../model/mensaje.model';
import { DiagnosticoIAService } from '../../../service/diagnostico-ia.service';
import { PlantaService } from '../../../service/planta.service';
import { UserService } from '../../../service/user.service';
import { PlanModel, User } from '../../../model/user.model';
import { ActividadTratamientoModel } from '../../../model/actividad-tratamiento';

import { ProcessingService } from '../../../service/auth/processing.service';
import { Observable } from 'rxjs';
import { ConfirmationService } from 'primeng/api';
import { Router } from '@angular/router';


import {
  Subscription,
  interval
} from 'rxjs';

import {
  startWith,
  takeWhile,
} from 'rxjs/operators';

import {
  timer,
} from 'rxjs';

import {
  exhaustMap,
} from 'rxjs/operators';

@Component({
  selector: 'app-chat',
  standalone: false,
  templateUrl: './chat.html',
  styleUrl: './chat.css',
  providers: [ProcessingService],
})
export class Chat {

  // ==================================================
  // STATE
  // ==================================================

  // Drawer Menu
  sidebarVisible: boolean = true;

  sidebarCollapsed = false;

  toggleSidebar(): void {
    this.sidebarCollapsed = !this.sidebarCollapsed;
  }

  // Enviando mensaje
  isSendingMessage: boolean = false;

  // Intervalo de imagen
  intervaloImagen: any;
    
  user!: User;
  editableUser!: User;

  chats: ChatModel[] = [];
  planes: PlanModel[] = [];

  // Chat
  chatSeleccionado: ChatModel | null = null;

  // Lesiones activas IMAGEN
  lesionActiva: number | null = null;

  opcionActiva: 'diagnostico' | 'chat' = 'diagnostico';
  get mostrarDiagnostico(): boolean {
      return this.opcionActiva === 'diagnostico';
  }

  get mostrarChatIA(): boolean {
      return this.opcionActiva === 'chat';
  }
  
  tabActivo: 'diagnostico' | 'tratamiento' | 'plantratamiento' | 'analitica' = 'diagnostico';
  // Para filtros
  chatsFiltrados: ChatModel[] = [];

  textoBusqueda: string = '';

  // Filtros opciones
  filtroActivo: string = 'fecha';
  

  ordenFechaActivo: 'recientes' | 'antiguos' | null = 'recientes';

  severidadActivo: 'Leve' | 'Moderada' | 'Grave' | null = null;
  urgenciaActivo: 'Baja' | 'Media' | 'Alta' | null = null;

  filtroTieneValor(key: string): boolean {

    switch (key) {

        case 'fecha':
            return this.ordenFechaActivo !== null;

        case 'severidad':
            return this.severidadActivo !== null;

        case 'urgencia':
            return this.urgenciaActivo !== null;

        default:
            return false;
    }
  }

  filtros = [
    {
      key: 'fecha',
      label: 'Fecha',
      options: [
        { label: 'Más recientes', value: 'desc' },
        { label: 'Más antiguos', value: 'asc' }
      ]
    },
    {
      key: 'severidad',
      label: 'Severidad',
      type: 'multi',
      options: [
        { label: 'Leve', value: 'Leve' },
        { label: 'Moderada', value: 'Moderada' },
        { label: 'Grave', value: 'Grave' }
      ]
    },
    {
      key: 'urgencia',
      label: 'Urgencia',
      type: 'multi',
      options: [
        { label: 'Baja', value: 'Baja' },
        { label: 'Media', value: 'Media' },
        { label: 'Alta', value: 'Alta' }
      ]
    }
  ];

  // Obtener mensajes
  mensajes: MensajeModel[] = [];

  // Nuevo mensaje
  nuevoMensaje: string = '';
  
  diagnosticoSeleccionado: any = null;

  imagePreview: string | null = null;
  selectedFile: File | null = null;

  originalPicture = '';
  originalUser!: User;

  isAnalyzing: boolean = false;
  hasImage: boolean = false;

  isMobile: boolean = false;

  zoomImagen: number = 1;

  // Mensajes predeterminados
  quickMessages: string[] = [
    '¿Qué tratamiento tiene?',
    '¿Cómo aplico el tratamiento?',
    'Dosis del tratamiento',
    'Frecuencia del tratamiento',
    'Duración del tratamiento'
  ];

  // ==================================================
  // CONSTRUCTOR
  // ==================================================
  constructor(
    public processing: ProcessingService,
    private confirmationService: ConfirmationService,
    private authService: AuthService,
    private messageService: MessageService,
     private themeService: ThemeService,

    private userService: UserService,
    public router:Router,
    private http:HttpClient,

    private chatService: ChatService,
    private diagnosticoService: DiagnosticoIAService,
    private plantaService: PlantaService,
    private mensajeService: MensajeService,
  ) {
  }

  // ==================================================
  // LOGICA DE INICICIALIZACION
  // ==================================================

  ngOnInit(): void {
    this.cargarChats();
    this.checkScreen();
    this.cargarPlanes();

    // THEME
    const chatTheme =
        (localStorage.getItem('user-theme') as Theme) ?? 'system';

    this.settings.theme = chatTheme;

    this.themeService.setTheme(chatTheme);   

    // USER
    this.userService.getProfile().subscribe(user => {
      this.user = user;
      this.editableUser = { ...user };
      this.originalPicture = user.picture;
    });

    // BIENVENIDA DE GOOGLE
    const loginWelcome = sessionStorage.getItem('loginWelcome');

    if (loginWelcome) {
      const res = JSON.parse(loginWelcome);

      this.messageService.add({
        severity: 'success',
        summary: 'Bienvenido',
        detail: `Hola, ${res.first_name}`,
        icon: 'pi pi-google'
      });
      sessionStorage.removeItem('loginWelcome');
    }
  }

  toggleMenu(): void {
    this.sidebarVisible = !this.sidebarVisible;
  }

  // OBTENER DATOS
  get planFree(): PlanModel | null {
    return this.planes.find(plan => plan.orden === 1) ?? null;
  }

  get planActual(): PlanModel {
    const plan = this.planFree;

    if (!this.user) {
      return plan as PlanModel;
    }

    const fechaFin = this.user.suscripcion?.fin;

    if (!fechaFin || new Date(fechaFin) <= new Date()) {
      return plan as PlanModel;
    }

    return this.user.plan;
  }

  get tieneSuscripcionActiva(): boolean {
    return !!(
      this.user?.suscripcion &&
      this.user.suscripcion.fin &&
      new Date(this.user.suscripcion.fin) > new Date()
    );
  }

  get suscripcionVencida(): boolean {
    if (!this.user?.suscripcion) {
      return false;
    }
    if (!this.user.suscripcion.fin) {
      return false;
    }
    return new Date(this.user.suscripcion.fin) <= new Date();

  }
  get chatsFijados() {
    return this.chatsFiltrados.filter(chat => chat.is_pinned);
  }

  get chatsRecientes() {
    return this.chatsFiltrados.filter(chat => !chat.is_pinned);
  }

  get tituloSeccionChats(): string {
    if (this.filtroActivo === 'fecha') {
      return this.ordenFechaActivo === 'recientes'
        ? 'Recientes'
        : 'Más antiguos';
    }

    const filtro = this.filtros.find(f => f.key === this.filtroActivo);
    return filtro?.label ?? 'Chats';
  }
 
  // ==================================================
  // FILTROS
  // ==================================================

  aplicarFiltros(): void {

    let resultado = [...this.chats];

    // FECHA
    resultado.sort((a, b) => {

      const dateA = new Date(a.creado_en ?? 0).getTime();
      const dateB = new Date(b.creado_en ?? 0).getTime();

      return this.ordenFechaActivo  === 'recientes'
        ? dateB - dateA
        : dateA - dateB;
    });

    // Texto
    if (this.textoBusqueda?.trim()) {

      const texto = this.textoBusqueda.toLowerCase().trim();

      resultado = resultado.filter(chat => {

        const titulo = chat.titulo?.toLowerCase() ?? '';
        const enfermedad_detectada = chat.diagnostico?.enfermedad_detectada?.toLowerCase() ?? '';
        const planta = chat.diagnostico?.planta?.nombre?.toLowerCase() ?? '';

        return (
          titulo.includes(texto) ||
          enfermedad_detectada.includes(texto) ||
          planta.includes(texto)
        );
      });
    }

    // FECHA
    if (this.filtroActivo === 'fecha') {

      resultado.sort((a, b) => {

        const dateA = new Date(a.creado_en ?? 0).getTime();
        const dateB = new Date(b.creado_en ?? 0).getTime();

        if (this.ordenFechaActivo === 'antiguos') {
          return dateA - dateB;
        }

        // Por defecto: MÁS RECIENTES
        return dateB - dateA;
      });
    }

    // SEVERIDAD
    if (this.severidadActivo) {
      resultado = resultado.filter(chat =>
        chat.diagnostico?.severidad === this.severidadActivo
      );
    }

    // URGENCIA
    if (this.urgenciaActivo) {
      resultado = resultado.filter(chat =>
        chat.diagnostico?.urgencia === this.urgenciaActivo
      );
    }

    this.chatsFiltrados = resultado;
  }

  // FILTRO DE SELECCION
  seleccionarFiltro(key: string, popover: any): void {
    this.filtroActivo = key;
    this.aplicarFiltros();
  }

  limpiarFiltros(): void {
    this.severidadActivo = null;
    this.urgenciaActivo = null;
    this.ordenFechaActivo = 'recientes';
    this.textoBusqueda = '';

    this.aplicarFiltros();
  }

  // TOGGLE DE OPCIONES
  toggleFijar(chat: any) {
    this.chatService.togglePinned(chat.id).subscribe(res => {
      chat.is_pinned = res.is_pinned;
    });
  }

  obtenerValorFiltro(key: string): string {

    switch (key) {

        case 'fecha':
            return this.ordenFechaActivo === 'recientes'
                ? 'Recientes'
                : 'Antiguos';

        case 'severidad':
            return this.severidadActivo ?? '';

        case 'urgencia':
            return this.urgenciaActivo ?? '';

        default:
            return '';
    }
}

  toggleOrdenFecha(valor: 'recientes' | 'antiguos'): void {
    if (this.ordenFechaActivo === valor) {
      this.ordenFechaActivo = null;
    } else {
      this.ordenFechaActivo = valor;
    }

    this.aplicarFiltros();
  }

  toggleSeveridad(valor: 'Leve' | 'Moderada' | 'Grave'): void {
    if (this.severidadActivo === valor) {
      this.severidadActivo = null;
    } else {
      this.severidadActivo = valor;
    }

    this.aplicarFiltros();
  }

  toggleUrgencia(valor: 'Baja' | 'Media' | 'Alta'): void {
    if (this.urgenciaActivo === valor) {
      this.urgenciaActivo = null;
    } else {
      this.urgenciaActivo = valor;
    }

    this.aplicarFiltros();
  }

  onBuscarChats(): void {
    this.aplicarFiltros();
  }

  // ==================================================
  // OBTENER DATOS
  // ==================================================

  cargarChats(): void {

    this.chatService.getMisChats()
      .subscribe(data => {

        this.chats = data.sort((a, b) =>
          new Date(b.creado_en ?? 0).getTime() -
          new Date(a.creado_en ?? 0).getTime()
        );

        this.aplicarFiltros();

        const chatGuardadoId = localStorage.getItem('chatSeleccionadoId');

        if (chatGuardadoId) {

          const chatEncontrado = this.chats.find(
            c => c.id === Number(chatGuardadoId)
          );

          if (chatEncontrado) {
            this.seleccionarChat(chatEncontrado);
            return;
          }
        }

      });
  }

  private cargarMensajes(chat: ChatModel): void {

    this.mensajes = chat.mensajes ?? [];

    setTimeout(() => {
      this.scrollToBottom();
    }, 150);
  }

  cargarPlanes(): void {
    this.userService.getPlan().subscribe({
      next: (res) => {
        this.planes = res;
      },
      error: (err) => {
        console.error('Error cargando plan', err);
      }
    });
  }

  seleccionarChat(chat: ChatModel): void {

    this.chatSeleccionado = chat;

    //if (this.isMobile) {
    //  this.sidebarVisible = false;
    //}

    if (chat?.id) {
      localStorage.setItem('chatSeleccionadoId', String(chat.id));
    }

    this.diagnosticoSeleccionado = chat.diagnostico;

    this.actividadesAgrupadas = this.agruparActividades(
      chat.diagnostico?.actividades || []
    );
    
    this.cargarMensajes(chat);
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
          color: 'var(--text-secondary)'
        };
    }
  }

  // ==================================================
  // ENVIAR ANALISIS
  // ==================================================

  progreso = 0;
  private pollingSubscription?: Subscription;

  enviarAnalisis(): void {

    // VALIDAR ARCHIVO
    if (!this.selectedFile) {
      console.warn('No hay imagen seleccionada.');
      return;
    }

    // INICIAR ESTADO DE ANALISIS
    this.isAnalyzing = true;
    this.progreso = 0;

    // CANCELAR POLLING ANTERIOR
    this.pollingSubscription?.unsubscribe();
    this.pollingSubscription = undefined;

    // SUBIR IMAGEN
    this.plantaService.subirImagen(this.selectedFile).subscribe({

      next: (res: any) => {

        // OBTENER CHAT ID
        const chatId = res?.chat?.id;

        if (!chatId) {
          console.error('No se recibió el ID del chat.', res);

          this.isAnalyzing = false;
          this.mostrarErrorAnalisis({
            error: {
              error: 'No se recibió el ID del chat.'
            }
          });

          return;
        }

        // OBTENER DIAGNOSTICO ID
        const diagnosticoId = res?.chat?.diagnostico?.id ?? res?.diagnostico?.id;

        if (!diagnosticoId) {
          console.error('No se recibió el ID del diagnóstico.', res);

          this.isAnalyzing = false;
          this.mostrarErrorAnalisis({
            error: {
              error: 'No se recibió el ID del diagnóstico.'
            }
          });

          return;
        }

        this.iniciarPollingImagen(diagnosticoId, chatId);
      },

      // ERROR
      error: (err) => {
        console.error('ERROR ANALIZANDO:', err);

        this.isAnalyzing = false;
        this.progreso = 0;

        this.pollingSubscription?.unsubscribe();
        this.pollingSubscription = undefined;

        this.mostrarErrorAnalisis(err);
      }
    });
  }

  iniciarPollingImagen(diagnosticoId: number, chatId: number): void {
    this.pollingSubscription?.unsubscribe();

    this.pollingSubscription = timer(0, 3000)
      .pipe(
        exhaustMap(() =>
          this.diagnosticoService.getDiagnosticoProgreso(diagnosticoId)
        ),

        tap((respuesta) => {
          this.progreso = Number(respuesta?.progreso ?? 0);
        }),

        takeWhile(
          (respuesta) => {
            const estado = respuesta?.estado_imagen;

            return estado !== 'Completado' && estado !== 'Error';
          },
          true
        )
      )
      .subscribe({
        next: (respuesta) => {
          const estado = respuesta?.estado_imagen;

          if (estado === 'Completado') {
            this.progreso = 100;

            this.pollingSubscription?.unsubscribe();
            this.pollingSubscription = undefined;

            this.cargarResultadoFinal(chatId);
            return;
          }

          if (estado === 'Error') {
            this.pollingSubscription?.unsubscribe();
            this.pollingSubscription = undefined;

            this.isAnalyzing = false;
            this.progreso = 0;

            this.messageService.add({
              severity: 'error',
              summary: 'Error en el análisis',
              detail: 'No se pudo completar el análisis.'
            });
          }
        },

        error: (err) => {
          console.error('ERROR POLLING:', err);

          this.pollingSubscription?.unsubscribe();
          this.pollingSubscription = undefined;

          this.isAnalyzing = false;
          this.progreso = 0;
        }
      });
  }


  cargarResultadoFinal(chatId: number): void {

    this.chatService.getChatPorId(chatId).subscribe({

      next: (chatCompleto) => {

        const estado = chatCompleto?.diagnostico?.estado_imagen;

        if (estado !== 'Completado') {
          console.warn(
            'El diagnóstico todavía no está completado.',
            estado
          );

          const diagnosticoId = chatCompleto?.diagnostico?.id;

          if (diagnosticoId && chatCompleto?.id) {
            this.iniciarPollingImagen(diagnosticoId, chatCompleto.id);
          }

          return;
        }

        this.chatSeleccionado = chatCompleto;

        this.diagnosticoSeleccionado = chatCompleto.diagnostico;

        this.actividadesAgrupadas = this.agruparActividades(
          chatCompleto?.diagnostico?.actividades ?? []
        );

        this.progreso = 100;

        this.isAnalyzing = false;

        if (chatCompleto.id) {
          localStorage.setItem(
            'chatSeleccionadoId',
            String(chatCompleto.id)
          );
        }

        this.chatService.getMisChats().subscribe({
          next: (chats) => {
            this.chats = chats.sort(
              (a, b) =>
                new Date(b.creado_en ?? 0).getTime() -
                new Date(a.creado_en ?? 0).getTime()
            );

            this.aplicarFiltros();
          },
        });

        if (chatCompleto.id) {
          this.mensajeService.obtenerMensajes(chatCompleto.id).subscribe({
            next: (mensajes) => {
              this.mensajes = mensajes;

              setTimeout(() => {
                this.scrollToBottom();
              }, 150);
            },

            error: (err) => {
              console.error('ERROR CARGANDO MENSAJES:', err);
            }
          });
        }

        this.messageService.add({
          severity: 'success',
          summary: 'Análisis completado',
          detail: 'El diagnóstico de tu cultivo está listo.'
        });
      },

      error: (err) => {
        console.error('ERROR OBTENIENDO RESULTADO FINAL:', err);

        this.isAnalyzing = false;

        this.messageService.add({
          severity: 'error',
          summary: 'Error',
          detail: 'No se pudo obtener el resultado final del diagnóstico.'
        });
      }
    });
  }


  mostrarErrorAnalisis(err: any): void {

    const backendError =
      err?.error?.detalle ||
      err?.error?.error ||
      err?.error?.imagen?.[0] ||
      err?.error?.non_field_errors?.[0] ||
      err?.error?.detail ||
      (typeof err?.error === 'string' ? err.error : null) ||
      err?.message ||
      'Error inesperado al analizar la imagen.';

    this.isAnalyzing = false;
    this.progreso = 0;

    this.pollingSubscription?.unsubscribe();
    this.pollingSubscription = undefined;

    this.messageService.add({
      severity: 'error',
      summary: 'Imagen rechazada',
      detail: backendError
    });
  }

  // MENSAJE INTERACCION
  enviarQuickMessage(texto: string): void {
    if (this.isSendingMessage) return;

    this.nuevoMensaje = texto;
    this.enviarMensaje();
  }

  enviarMensaje(): void {

    if (!this.nuevoMensaje.trim()) return;

    if (!this.chatSeleccionado?.id) return;

    if (this.isSendingMessage) return;

    const textoUsuario = this.nuevoMensaje;
    
    // MENSAJE USUARIO
    
    const mensajeTemporalUsuario: MensajeModel = {
      chat: this.chatSeleccionado.id,
      texto: textoUsuario,
      tipo: 'usuario',
      creado_en: new Date()
    };

    this.mensajes.push(mensajeTemporalUsuario);
    
    // MENSAJE IA

    const mensajeTemporalIA: MensajeModel = {
      chat: this.chatSeleccionado.id,
      texto: 'Analizando planta...',
      tipo: 'ia',
      creado_en: new Date()
    };

    this.mensajes.push(mensajeTemporalIA);

    // limpiar input
    this.nuevoMensaje = '';

    // Bloquemos la interaccion
    this.isSendingMessage = true;

    // scroll inmediato
    setTimeout(() => {
      this.scrollToBottom();
    }, 50);


    const payload = {
      chat: this.chatSeleccionado.id,
      texto: textoUsuario
    };

    this.mensajeService.enviarMensaje(payload)
    .subscribe({

      next: (res: any) => {

        // reemplazar mensaje IA temporal
        const index = this.mensajes.indexOf(mensajeTemporalIA);

        if (index !== -1) {
          this.mensajes[index] = res.ia;
        }

        this.isSendingMessage = false;

        setTimeout(() => {
          this.scrollToBottom();
        }, 50);
      },

      error: (err) => {

        console.error(err);

        // mostrar error amigable
        mensajeTemporalIA.texto =
          'Error obteniendo respuesta IA';

        this.isSendingMessage = false;
      }
    });
  }

  // ==================================================
  // UI ACTIONS
  // ==================================================

  logout(): void {
    this.authService.logout().subscribe();
  }

  // Nuevo escaneo

  crearNuevoEscaneo(): void {
    this.chatSeleccionado = null;
    this.diagnosticoSeleccionado = null;
    this.mensajes = [];
    this.cancelarImagen();
    this.isAnalyzing = false;
    if (this.isMobile) {
      this.sidebarVisible = false;
    }
    localStorage.removeItem('chatSeleccionadoId');
  }

  // ACCIONES CRUD

  // EDITAR CHAT DIAGNOSTICO
  chatEditando: ChatModel | null = null;
  nuevoTitulo: string = '';
  mostrarModalEditar: boolean = false;

  editarChat(chat: any) {
    this.chatEditando = chat;
    this.nuevoTitulo = chat.titulo;
    this.mostrarModalEditar = true;
  }

  guardarTituloChat() {

    if (!this.chatEditando) return;

    const titulo = this.nuevoTitulo.trim();
    if (!titulo) return;

    this.chatService.updateChatTitle(this.chatEditando.id!, titulo)
      .subscribe({
        next: () => {

          this.chatEditando!.titulo = titulo; // update UI

          this.cerrarModalEditar();
        },
        error: (err) => {
          console.error(err);
        }
      });
  }

  cerrarModalEditar() {
    this.mostrarModalEditar = false;
    this.chatEditando = null;
    this.nuevoTitulo = '';
  }

  // ELIMINAR CHAT DIAGNOSTICO
  mostrarDialogEliminar: boolean = false;
  chatAEliminar: ChatModel | null = null;

  eliminarChat(chat: any) {
    this.chatAEliminar = chat;
    this.mostrarDialogEliminar = true;
  }

  confirmarEliminarChat() {

    const chat = this.chatAEliminar;
    if (!chat) return;

    const plantaId = chat?.diagnostico?.planta?.id;

    if (plantaId) {

      this.plantaService.eliminarPlanta(plantaId).subscribe({
        next: () => {

          this.cargarChats();

          this.messageService.add({
            severity: 'success',
            summary: 'Eliminado',
            detail: 'Chat y diagnóstico eliminados'
          });

          this.cerrarDialogEliminar();
        },

        error: () => {
          this.messageService.add({
            severity: 'error',
            summary: 'Error',
            detail: 'No se pudo eliminar el chat y el diagnóstico'
          });

          this.cerrarDialogEliminar();
        }
      });

    } else {
      this.cerrarDialogEliminar();
    }
  }

  cerrarDialogEliminar() {
    this.mostrarDialogEliminar = false;
    this.chatAEliminar = null;
  }

  // ==================================================
  // IMAGE HANDLING
  // ==================================================
  onFileSelected(event: any): void {
    const file = event.target.files[0];
    if (!file) return;

    this.selectedFile = file;
    this.hasImage = true;

    const reader = new FileReader();
    reader.onload = () => {
      this.imagePreview = reader.result as string;
    };

    reader.readAsDataURL(file);
  }

  tomarFoto(): void {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'image/*';
    input.capture = 'environment';

    input.onchange = (e: any) => this.onFileSelected(e);
    input.click();
  }

  cancelarImagen(): void {
    this.imagePreview = null;
    this.selectedFile = null;
    this.hasImage = false;
  }

  // ==================================================
  // FUNCION DEL CALENDARIO
  // ==================================================

  actividadesAgrupadas: {
    semana: number;
    actividades: ActividadTratamientoModel[];
  }[] = [];

  agruparActividades(actividades: ActividadTratamientoModel[]) {

    const grupos: Record<number, ActividadTratamientoModel[]> = {};

    actividades.forEach(act => {
      if (!grupos[act.semana]) {
        grupos[act.semana] = [];
      }
      grupos[act.semana].push(act);
    });

    return Object.entries(grupos).map(([semana, actividades]) => ({
      semana: Number(semana),
      actividades: actividades as ActividadTratamientoModel[]
    }));
  }

  onActividadChange(act: ActividadTratamientoModel): void {

    const nuevoEstado = act.completada;

    this.diagnosticoService.actualizarActividad(act.id!, {
      completada: nuevoEstado
    }).subscribe({
      next: () => {
        this.messageService.add({
          severity: 'success',
          summary: 'Actualizado',
          detail: nuevoEstado
            ? 'Actividad completada'
            : 'Actividad marcada como pendiente'
        });
      },
      error: (err) => {
        console.error(err);

        // rollback
        act.completada = !nuevoEstado;

        this.messageService.add({
          severity: 'error',
          summary: 'Error',
          detail: 'No se pudo guardar el avance'
        });
      }
    });
  }

  // ==================================================
  // OPCIONES DEL USUARIO
  // ==================================================
  
  // MODAL PLANES
  upgradePlan() {
    this.router.navigate(['/page/plan']);
  }
  
  // ==================================================
  // MODAL PERSONALIZACION
  // ==================================================
  // openPersonalizacion(){}

  // ==================================================
  // MODAL PERFIL
  // ==================================================
  showProfileDialog: boolean = false;

  openPerfil() {
    this.showProfileDialog = true;
    this.editableUser = { ...this.user };
  }

  guardarPerfilModal() {
    this.guardarPerfil();
    this.showProfileDialog = false;
    this.removeSelectedAvatar();
  }
  
  closePerfil() {
    this.showProfileDialog = false;

    this.editableUser = { ...this.originalUser };
    this.removeSelectedAvatar();
  }

  // ==================================================
  // MODAL CONGIGURACION
  // ==================================================
  showSettingsModal: boolean = false;

  openConfiguracion() {
    this.showSettingsModal = true;

    this.editableUser = { ...this.user };
    this.removeSelectedAvatar();
  }

  closeConfiguracion() {
    this.showSettingsModal = false;

    this.editableUser = { ...this.originalUser };
    this.removeSelectedAvatar();
  }

  activeSection = 'general';

  // Obtener la opcion actual
  get activeSectionTitle(): string {
    return this.menuItems.find(
      item => item.id === this.activeSection
    )?.label || 'Configuración';
  }

  // Menu opciones
  menuItems = [
    {
      id: 'general',
      label: 'General',
      icon: 'monitor'
    },
    {
      id: 'perfil',
      label: 'Perfil',
      icon: 'user'
    },
    {
      id: 'notifications',
      label: 'Notificaciones',
      icon: 'bell'
    },
    {
      id: 'security',
      label: 'Seguridad & 2FA',
      icon: 'shield'
    },
    {
      id: 'ai',
      label: 'Preferencias IA',
      icon: 'sparkles'
    },
    {
      id: 'integrations',
      label: 'Integraciones',
      icon: 'plug'
    },
    {
      id: 'data',
      label: 'Mis datos',
      icon: 'download'
    }
  ];

  changeTheme(theme: Theme): void {
    this.settings.theme = theme;

    localStorage.setItem('user-theme', theme);

    this.themeService.setTheme(theme);
  }

  settings = {
    theme: (localStorage.getItem('user-theme') as Theme) || 'system',
  };

  saveSettings() {
    this.guardarPerfil();
  }

  removeSelectedAvatar(fileInput?: HTMLInputElement): void {

    this.selectedFile = null;
    this.editableUser.picture = this.originalPicture;

    if (fileInput) {
      fileInput.value = '';
    }
  }

  onAvatarChange(event: any) {

    const file = event.target.files[0];
    if (!file) return;

    this.selectedFile = file;

    const reader = new FileReader();

    reader.onload = () => {
        this.editableUser.picture = reader.result as string;
    };

    reader.readAsDataURL(file);
  }

  guardarPerfil() {

    if (!this.editableUser) return;

    const formData = new FormData();

    formData.append("username", this.editableUser.username);
    formData.append("first_name", this.editableUser.first_name ?? '');
    formData.append("last_name", this.editableUser.last_name ?? '');
    formData.append("email", this.editableUser.email);
    formData.append("phone", this.editableUser.phone ?? '');

    if (this.selectedFile) {
      formData.append("picture", this.selectedFile);
    }

    this.userService.editarUsuario(this.user.id, formData)
      .subscribe({
        next: resp => {
          this.messageService.add({
            severity: 'success',
            summary: 'Listo',
            detail: 'Perfil actualizado correctamente'
          });
        },
        error: err => {
          this.messageService.add({
            severity: 'error',
            summary: 'Error',
            detail: 'No se pudo actualizar el perfil'
          });
        }
      });
  }

  // CONFIGURACION - SEGURIDAD
  //PASSWORD
  passwordDialog: boolean = false;

  passwordForm = {
      actualPassword: '',
      nuevoPassword: '',
      repetirPassword: ''
  };
  abrirModalPassword() {
    this.passwordDialog = true;
  }

  cambiarPassword() {

    if (!this.passwordForm.actualPassword) {
        return;
    }

    if (this.passwordForm.nuevoPassword !== this.passwordForm.repetirPassword) {
        return;
    }

    const payload = {
        actualPassword: this.passwordForm.actualPassword,
        password: this.passwordForm.nuevoPassword
    };

    this.userService.cambiarPassword(payload).subscribe({
      next: (res) => {

        // limpiar formulario
        this.passwordForm = {
            actualPassword: '',
            nuevoPassword: '',
            repetirPassword: ''
        };

        // cerrar modal
        this.passwordDialog = false;

        this.messageService.add({
            severity: 'success',
            summary: 'Éxito',
            detail: 'Contraseña cambiada correctamente'
        });

      },

      error: (err) => {
        this.messageService.add({
            severity: 'error',
            summary: 'Error',
            detail: err?.error?.error || 'No se pudo cambiar la contraseña'
        });
      }
    });
  }

  passwordRequirements = [
    {
      id: 'minLength',
      label: 'Mínimo 6 caracteres',
      test: (v: string) => v?.length >= 6
    },
    {
      id: 'uppercase',
      label: 'Una letra mayúscula',
      test: (v: string) => /[A-Z]/.test(v)
    },
    {
      id: 'lowercase',
      label: 'Una letra minúscula',
      test: (v: string) => /[a-z]/.test(v)
    },
    {
      id: 'number',
      label: 'Un número',
      test: (v: string) => /[0-9]/.test(v)
    },
    {
      id: 'symbol',
      label: 'Un símbolo especial',
      test: (v: string) => /[^a-zA-Z0-9]/.test(v)
    }
  ];

  isPasswordValid(): boolean {
    return this.passwordRequirements.every(r =>
      r.test(this.passwordForm.nuevoPassword)
    );
  }

  // CONFIGURACION - DESCARGAR FORMATOS
  downloadFile(blob: Blob, name: string) {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = name;
    a.click();
  }

  // Procesamiento de exportación de archivos
  private exportFile(
    obs$: Observable<Blob>,
    filename: string,
    successMsg: string,
    errorMsg: string
  ) {
    if (!this.processing.start()) return;

    this.messageService.add({
      severity: 'info',
      summary: 'Procesando',
      detail: 'Generando archivo...'
    });

    obs$.pipe(
      finalize(() => this.processing.stop())
    ).subscribe({
      next: (blob) => {
        this.downloadFile(blob, filename);

        this.messageService.add({
          severity: 'success',
          summary: 'Listo',
          detail: successMsg
        });
      },
      error: () => {
        this.messageService.add({
          severity: 'error',
          summary: 'Error',
          detail: errorMsg
        });
      }
    });
  }

  // Historial Diagnosticos
  exportarDiagnosticoExcel() {
    this.exportFile(
      this.diagnosticoService.exportDiagnosticosExcel(),
      'diagnostico.xlsx',
      'Excel de diagnósticos generado',
      'Error al generar Excel'
    );
  }
  exportarDiagnosticosPDF() {
    this.exportFile(
      this.diagnosticoService.exportDiagnosticosPDF(),
      'diagnostico.pdf',
      'PDF de diagnósticos generado',
      'Error al generar PDF'
    );
  }
  exportarDiagnosticoPDF(diagnostico: any) {
    this.exportFile(
      this.diagnosticoService.exportDiagnosticoPDF(diagnostico.id),
      `diagnostico_${diagnostico.id}.pdf`,
      'Archivo generado',
      'Error al generar PDF'
    );
  }

  // Historial Chats
  exportarChatsExcel() {
    this.exportFile(
      this.chatService.exportChatsExcel(),
      'chats.xlsx',
      'Excel de chats generado',
      'Error al generar Excel'
    );
  }

  // Descargar imagen
  exportarDiagnosticoImagen(diagnostico: any) {

    if (!diagnostico?.imagen) {
      this.messageService.add({
        severity: 'warn',
        summary: 'Sin imagen',
        detail: 'Este diagnóstico no tiene una imagen disponible.'
      });

      return;
    }

    this.exportFile(
      this.http.get(diagnostico.imagen, {
        responseType: 'blob'
      }),
      `diagnostico_${diagnostico.id}.png`,
      'Imagen descargada correctamente',
      'Error al descargar imagen'
    );
  }

  // ==================================================
  // RESPONSIVE
  // ==================================================
  private lastIsMobile = false;

  @HostListener('window:resize')
  checkScreen(): void {
    const mobile = window.innerWidth <= 768;
    this.isMobile = mobile;

    // solo ejecuta cuando cambia de desktop → mobile
    if (mobile && !this.lastIsMobile) {
      this.sidebarVisible = false;
    }

    this.lastIsMobile = mobile;
  }

  @ViewChild('scrollContainer', { static: false })
  scrollContainer!: ElementRef;
  scrollToBottom(): void {

    if (!this.scrollContainer) return;

    try {
      const el = this.scrollContainer.nativeElement;

      el.scrollTop = el.scrollHeight;

    } catch (e) {
      console.log('scroll error', e);
    }
  }
  
  // ==================================================
  // IMAGENES
  // ==================================================
  
  mostrarLesiones = true;

  // Detectar posición
  activeIndex: number = 0;

  zoom: number = 1.5;
  rotation: number = 0;

  get zoomPercentage(): number {
    return Math.round(this.zoom * 100);
  }

  toggleLesiones() {
    this.mostrarLesiones = !this.mostrarLesiones;
  }

  zoomIn() {
    this.zoom += 0.2;
  }

  zoomOut() {
    if (this.zoom > 0.4) this.zoom -= 0.2;
  }

  rotateRight() {
    this.rotation += 90;
  }

  rotateLeft() {
    this.rotation -= 90;
  }

  reset() {
    this.zoom = 1;
    this.rotation = 0;

    this.posX = 0;
    this.posY = 0;

    this.startX = 0;
    this.startY = 0;

    this.isDragging = false;
  }

  // Escritorio
  isDragging = false;
  posX = 0;
  posY = 0;
  startX = 0;
  startY = 0;

  startDrag(event: MouseEvent) {
    this.isDragging = true;
    this.startX = event.clientX - this.posX;
    this.startY = event.clientY - this.posY;
  }

  onDrag(event: MouseEvent) {
    if (!this.isDragging) return;

    this.posX = event.clientX - this.startX;
    this.posY = event.clientY - this.startY;
  }

  stopDrag() {
    this.isDragging = false;
  }

  // Moviles
  touchStartX = 0;
  touchStartY = 0;

  startTouch(event: TouchEvent) {
    const touch = event.touches[0];

    this.isDragging = true;

    this.touchStartX = touch.clientX - this.posX;
    this.touchStartY = touch.clientY - this.posY;
  }

  onTouchMove(event: TouchEvent) {
    if (!this.isDragging) return;

    const touch = event.touches[0];

    this.posX = touch.clientX - this.touchStartX;
    this.posY = touch.clientY - this.touchStartY;
  }

  // ACORDEON - PLAGAS RELACIONADAS
  getPlagasClass(riesgo: string): string {
    switch (riesgo?.toLowerCase().trim()) {
      case 'alto':
        return 'risk-high';

      case 'medio':
        return 'risk-medium';

      case 'bajo':
        return 'risk-low';

      default:
        return 'risk-default';
    }
  }

  // CALENDARIO INTERACCION
  semanaSeleccionada:any = null;

  seleccionarSemana(grupo:any){
    this.semanaSeleccionada = grupo;
  }

  // PORCENTAJE DEL ESTADO DE PLANTA
  getHealthStatus(porcentaje: number) {

  if (porcentaje <= 20) {
    return {
      label: 'Estado crítico',      
      class: 'health-critical'
    };
  }

  if (porcentaje <= 40) {
    return {
      label: 'Estado muy bajo',      
      class: 'health-very-low'
    };
  }

  if (porcentaje <= 60) {
    return {
      label: 'Estado bajo',      
      class: 'health-low'
    };
  }

  if (porcentaje <= 80) {
    return {
      label: 'Estado moderado',      
      class: 'health-moderate'
    };
  }

  return {
    label: 'Estado saludable',    
    class: 'health-healthy'
  };
}
    
}
