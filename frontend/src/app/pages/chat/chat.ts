import { Component, HostListener, ViewChild, ElementRef  } from '@angular/core';
import { finalize, switchMap, tap } from 'rxjs/operators';
import { AuthService } from '../../../service/auth/auth.service';
import { MessageService } from 'primeng/api';

import { ChatModel } from '../../../model/chat.model';
import { ChatService } from '../../../service/chat.service';
import { MensajeService } from '../../../service/mensaje.service';
import { MensajeModel } from '../../../model/mensaje.model';
import { MenuItem } from 'primeng/api';
import { DiagnosticoIAService } from '../../../service/diagnostico-ia.service';
import { PlantaService } from '../../../service/planta.service';
import { UserService } from '../../../service/user.service';
import { Plan, User } from '../../../model/user.model';

@Component({
  selector: 'app-chat',
  standalone: false,
  templateUrl: './chat.html',
  styleUrl: './chat.css',
})
export class Chat {

  // =========================
  // STATE
  // =========================

  // Drawer Menu
  sidebarVisible: boolean = true;

  // Drawer Chat
  chatVisible: boolean = true;

  // Enviando mensaje
  isSendingMessage: boolean = false;

  // Intervalo de imagen
  intervaloImagen: any;
    
  user: User | null = null;

  chats: ChatModel[] = [];
  plan: Plan[] = [];
  chatSeleccionado: ChatModel | null = null;

  // Obtener mensajes
  mensajes: MensajeModel[] = [];

  // Nuevo mensaje
  nuevoMensaje: string = '';
  
  diagnosticoSeleccionado: any = null;

  imagePreview: string | null = null;
  selectedFile: File | null = null;

  isAnalyzing: boolean = false;
  hasImage: boolean = false;

  isMobile: boolean = false;

  // =========================
  // CONSTRUCTOR
  // =========================
  constructor(
    private authService: AuthService,
    private messageService: MessageService,

    private chatService: ChatService,
    private diagnosticoService: DiagnosticoIAService,
    private plantaService: PlantaService,
    private mensajeService: MensajeService,
    private userService: UserService
  ) {
  }

  // =========================
  // LIFECYCLE
  // =========================
  ngOnInit(): void {
    this.cargarChats();
    this.checkScreen();
    this.cargarPerfil();
  }

  // =========================
  // DATA (API)
  // =========================
  cargarChats(): void {

    this.chatService.getMisChats()
      .subscribe(data => {

        this.chats = data.sort((a, b) =>
          new Date(b.creado_en ?? 0).getTime() -
          new Date(a.creado_en ?? 0).getTime()
        );

        // seleccionar primer chat automáticamente
        if (this.chats.length > 0) {
          this.seleccionarChat(this.chats[0]);
        }
      });
  }

  cargarPerfil(): void {
    this.userService.getProfile().subscribe({
      next: (res) => {
        this.user = res;
      },
      error: (err) => {
        console.error('Error cargando perfil', err);
      }
    });
  }

  seleccionarChat(chat: ChatModel): void {

    this.chatSeleccionado = chat;

    this.diagnosticoSeleccionado = chat.diagnostico;

    this.mensajeService.obtenerMensajes(chat.id!)
      .subscribe({
        next: (mensajes) => {
          this.mensajes = mensajes;
          setTimeout(() => {
            this.scrollToBottom();
          }, 150);
        },
        error: (err) => {
          console.error(err);
        }
      });
  }

  enviarAnalisis(): void {
    if (!this.selectedFile) return;

    this.isAnalyzing = true;

    this.plantaService.subirImagen(this.selectedFile).pipe(

      switchMap((res: any) => {
        const chatId = res?.chat?.id;

        if (!chatId) {
          throw new Error('No chatId');
        }

        return this.chatService.getChatPorId(chatId);
      }),

      tap((chatCompleto) => {
        this.chatSeleccionado = chatCompleto;
        this.diagnosticoSeleccionado = chatCompleto.diagnostico;

        const estado =
          chatCompleto.diagnostico?.estado_imagen;

        if (
          estado === 'Pendiente' ||
          estado === 'Procesando'
        ) {
          this.iniciarPollingImagen(chatCompleto.id!);
        }
        this.cargarChats();
      }),

      finalize(() => {
        this.isAnalyzing = false;
      })

    ).subscribe({
      error: (err) => {

        console.log(err);
        
        const backendError =
          err?.error?.detalle ||
          err?.error?.error ||
          'Error inesperado al analizar la imagen';

        this.messageService.add({
          severity: 'error',
          summary: 'Imagen rechazada',
          detail: backendError
        });

        this.isAnalyzing = false;
      }
    });
  }

  iniciarPollingImagen(chatId: number): void {

    let intentos = 0;
    const MAX_INTENTOS = 40;
    
    this.intervaloImagen = setInterval(() => {

      intentos++;

      if (intentos >= MAX_INTENTOS) {
        clearInterval(this.intervaloImagen);

        this.messageService.add({
          severity: 'warn',
          summary: 'Tiempo agotado',
          detail: 'La generación de imagen tardó demasiado.'
        });

        return;
      }

      this.chatService.getChatPorId(chatId)
        .subscribe({

          next: (chatActualizado) => {

            this.chatSeleccionado = chatActualizado;
            this.diagnosticoSeleccionado = chatActualizado.diagnostico;

            const estado = chatActualizado.diagnostico?.estado_imagen;

            if (estado === 'Completado') {
              clearInterval(this.intervaloImagen);

              this.messageService.add({
                severity: 'success',
                summary: 'Imagen lista',
                detail: 'La imagen ya fue generada.'
              });
            }

            if (estado === 'Error') {
              clearInterval(this.intervaloImagen);

              this.messageService.add({
                severity: 'error',
                summary: 'Error',
                detail: 'No se pudo generar la imagen.'
              });
            }
          },

          error: () => {
            console.log("Error en polling");
          }

        });

    }, 8000);
  }

  enviarMensaje(): void {

    if (!this.nuevoMensaje.trim()) return;

    if (!this.chatSeleccionado?.id) return;

    if (this.isSendingMessage) return;

    const textoUsuario = this.nuevoMensaje;
    
    // =========================
    // MENSAJE OPTIMISTA USUARIO
    // =========================
    
    const mensajeTemporalUsuario: MensajeModel = {
      chat: this.chatSeleccionado.id,
      texto: textoUsuario,
      tipo: 'usuario',
      creado_en: new Date()
    };

    this.mensajes.push(mensajeTemporalUsuario);
    
    // =========================
    // MENSAJE TEMPORAL IA
    // =========================

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

  // =========================
  // UI ACTIONS
  // =========================

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
  }

  // Acciones CRUD

  editarChat(chat: any) {
      console.log('Editar', chat);
      // tu lógica aquí
  }

  eliminarChat(chat: any) {
    const id = chat.id;

    const plantaId = chat?.diagnostico?.planta?.id;

    // Eliminamos planta porque tiene CASCADE
    if (plantaId) {
      this.plantaService.eliminarPlanta(plantaId).subscribe({
        next: () => {
          this.cargarChats();
          console.log('Planta eliminada:', plantaId);
        },
        error: (err) => {
          console.error('Error eliminando planta:', err);
        }
      });
    }
  }

  // =========================
  // IMAGE HANDLING
  // =========================
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

  // =========================
  // RESPONSIVE
  // =========================
  @HostListener('window:resize')
  checkScreen(): void {
    const mobile = window.innerWidth <= 768;

    this.isMobile = mobile;

    if (mobile) {
      this.sidebarVisible = false;
      this.chatVisible = false;
    }
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
  
  
}
