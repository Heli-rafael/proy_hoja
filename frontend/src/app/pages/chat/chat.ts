import { Component } from '@angular/core';
import { AuthService } from '../../../service/auth/auth.service';

import { ChatModel } from '../../../model/chat.model';
import { ChatService } from '../../../service/chat.service';
import { MensajeService } from '../../../service/mensaje.service';
import { MensajeModel } from '../../../model/mensaje.model';
import { MenuItem } from 'primeng/api';
import { DiagnosticoIAService } from '../../../service/diagnostico-ia.service';
import { PlantaService } from '../../../service/planta.service';
@Component({
  selector: 'app-chat',
  standalone: false,
  templateUrl: './chat.html',
  styleUrl: './chat.css',
})
export class Chat {

  sidebarVisible: boolean = false;
  chats: ChatModel[] = [];
  chatSeleccionado: ChatModel | null = null;

  imagePreview: string | null = null;
  selectedFile: File | null = null;
  isAnalyzing: boolean = false;

  opcionesChat: MenuItem[] = [
    { label: 'Editar nombre', icon: 'pi pi-pencil', command: () => this.editarNombre() },
    { label: 'Eliminar', icon: 'pi pi-trash', styleClass: 'text-red-500', command: () => this.eliminarChat() }
  ];
  // =========================
  // Constructor
  // =========================

  constructor(
    private authService: AuthService,
    private chatService: ChatService,
    private diagnosticoService: DiagnosticoIAService,
    private plantaService: PlantaService,
  ){}

  logout(){
    this.authService.logout().subscribe();
  }

  ngOnInit() {
    this.cargarChats();
  }

  cargarChats() {
    this.chatService.getMisChats().subscribe(data => this.chats = data);
  }

  seleccionarChat(chat: ChatModel) {
    this.chatSeleccionado = chat;
  }

  editarNombre() {
    console.log('Editando...', this.chatSeleccionado);
    // Aquí abrirías un diálogo para cambiar el título
  }

  eliminarChat() {
    if (this.chatSeleccionado?.id) {
      this.chatService.eliminarChat(this.chatSeleccionado.id).subscribe(() => {
        this.chats = this.chats.filter(c => c.id !== this.chatSeleccionado?.id);
        this.chatSeleccionado = null;
      });
    }
  }

  // Al hacer clic en "Nuevo Escaneo" en el sidebar, simplemente limpiamos la selección
  crearNuevoEscaneo() {
    this.chatSeleccionado = null;
    this.cancelarImagen();
    this.sidebarVisible = false; // Opcional: cerrar sidebar en móvil
  }

  onFileSelected(event: any) {
    const file = event.target.files[0];
    if (file) {
      this.selectedFile = file;
      const reader = new FileReader();
      reader.onload = () => this.imagePreview = reader.result as string;
      reader.readAsDataURL(file);
    }
  }

  tomarFoto() {
    // En móviles, el input file con 'capture' abre la cámara
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'image/*';
    input.capture = 'environment'; // Cámara trasera
    input.onchange = (e) => this.onFileSelected(e);
    input.click();
  }

  cancelarImagen() {
    this.imagePreview = null;
    this.selectedFile = null;
  }

  enviarAnalisis() {
    if (!this.selectedFile) return;

    this.isAnalyzing = true;

    this.plantaService.subirImagen(this.selectedFile).subscribe({
      next: (respuestaBackend) => {
        // Asumiendo que tu backend es inteligente y al crear la planta 
        // te devuelve el 'chat' vinculado en la misma respuesta:
        const nuevoChat = respuestaBackend.chat; 
        
        this.chats.unshift(nuevoChat);
        this.seleccionarChat(nuevoChat);
        
        this.isAnalyzing = false;
        this.cancelarImagen();
        console.log("Análisis completado por el servidor");
      },
      error: (err) => {
        console.error("Error en el servidor", err);
        this.isAnalyzing = false;
      }
    });
  }
}
