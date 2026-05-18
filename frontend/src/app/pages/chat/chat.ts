import { Component, HostListener, ViewChild, ElementRef  } from '@angular/core';
import { finalize, switchMap, tap } from 'rxjs/operators';
import { AuthService } from '../../../service/auth/auth.service';

import { ChatModel } from '../../../model/chat.model';
import { ChatService } from '../../../service/chat.service';
import { MensajeService } from '../../../service/mensaje.service';
import { MensajeModel } from '../../../model/mensaje.model';
import { MenuItem } from 'primeng/api';
import { DiagnosticoIAService } from '../../../service/diagnostico-ia.service';
import { PlantaService } from '../../../service/planta.service';
import { UserService } from '../../../service/user.service';
import { User } from '../../../model/user.model';

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
  sidebarVisible: boolean = true;
  chatVisible: boolean = true;
    
  user: User | null = null;

  chats: ChatModel[] = [];
  chatSeleccionado: ChatModel | null = null;

  mensajes: MensajeModel[] = [];
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

        this.cargarChats();
      }),

      finalize(() => {
        this.isAnalyzing = false;
      })

    ).subscribe({
      error: (err) => {
        console.error(err);
      }
    });
  }

  enviarMensaje(): void {

    if (!this.nuevoMensaje.trim()) return;

    if (!this.chatSeleccionado?.id) return;

    const payload = {
      chat: this.chatSeleccionado.id,
      texto: this.nuevoMensaje
    };

    this.mensajeService.enviarMensaje(payload)
      .subscribe({
        next: (res: any) => {

          // agregar mensaje usuario
          this.mensajes.push(res.usuario);

          // agregar respuesta IA
          this.mensajes.push(res.ia);

          // limpiar input
          this.nuevoMensaje = '';

          // hacer scroll al final
          setTimeout(() => {
            this.scrollToBottom();
          }, 150);
        },
        error: (err) => {
          console.error(err);
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
