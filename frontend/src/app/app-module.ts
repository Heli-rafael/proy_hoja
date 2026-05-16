import { LOCALE_ID, NgModule, provideBrowserGlobalErrorListeners } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { AppRoutingModule } from './app-routing-module';
import { HttpClientModule } from '@angular/common/http';

// Interceptor
import { HTTP_INTERCEPTORS } from '@angular/common/http';
import { CsrfInterceptor } from '../service/auth/cookie.interceptor';

// Primeng
import { provideAnimationsAsync } from '@angular/platform-browser/animations/async';
import { providePrimeNG } from 'primeng/config';

import MyPreset from '../mypreset';
import { App } from './app';
import { Login } from './auth/login/login';
import { Chat } from './pages/chat/chat';
import { ConfirmationService, MessageService } from 'primeng/api';



// Configuración PrimeNG
// Principal
import { ButtonModule } from 'primeng/button';
import { InputTextModule } from 'primeng/inputtext';
import { IconFieldModule } from 'primeng/iconfield';
import { InputIconModule } from 'primeng/inputicon';



// Normal
import { DialogModule } from 'primeng/dialog';  // Importa el módulo
import { FileUploadModule } from 'primeng/fileupload'; // Asegúrate de que este import esté presente.

import { ToggleButtonModule } from 'primeng/togglebutton';
import { ToggleSwitchModule } from 'primeng/toggleswitch';
import { DatePickerModule } from 'primeng/datepicker';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { SelectButtonModule } from 'primeng/selectbutton';
import { SelectModule } from 'primeng/select';

import { FloatLabelModule } from 'primeng/floatlabel';
import { MultiSelectModule } from 'primeng/multiselect';

import { MegaMenuModule } from 'primeng/megamenu';
import { PanelMenuModule } from 'primeng/panelmenu';
import { AccordionModule } from 'primeng/accordion';
import { DrawerModule } from 'primeng/drawer';
import { ProgressSpinnerModule } from 'primeng/progressspinner';

import { TagModule } from 'primeng/tag';
import { SliderModule } from 'primeng/slider';
import { TooltipModule } from 'primeng/tooltip';
import { AutoFocusModule } from 'primeng/autofocus';
import { AvatarModule } from 'primeng/avatar';
import { ProgressBarModule } from 'primeng/progressbar';
import { PopoverModule } from 'primeng/popover';
import { DividerModule } from 'primeng/divider';
import { TextareaModule } from 'primeng/textarea';
import { ChartModule } from 'primeng/chart';
import { ConfirmDialogModule } from 'primeng/confirmdialog';
import { BlockUIModule } from 'primeng/blockui';
import { ReactiveFormsModule } from '@angular/forms';

import { MenuModule } from 'primeng/menu';

@NgModule({
  declarations: [
    App,
    Login,
    Chat
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    HttpClientModule,


    // Principal
    ButtonModule,
    InputTextModule,
    IconFieldModule,
    InputIconModule,

    // Normal
    DialogModule,
    FileUploadModule,
    ToggleButtonModule,
    ToggleSwitchModule,
    DatePickerModule,
    BrowserAnimationsModule,
    SelectButtonModule,
    SelectModule,
    FloatLabelModule,
    MultiSelectModule,
    // Estado
    TagModule,

    // TooltipModule,
    TooltipModule,

    AvatarModule,
    ProgressBarModule,
    DividerModule,
    TextareaModule,
    BlockUIModule,
    ChartModule,
    ReactiveFormsModule,
    // ConfirmDialogModule
    ConfirmDialogModule,

    // 
    PopoverModule,

    // Menús
    MegaMenuModule,
    PanelMenuModule,
    DrawerModule,
    AccordionModule,
    MenuModule,

    ProgressSpinnerModule,
  ],
  providers: [
    provideBrowserGlobalErrorListeners(),
    provideAnimationsAsync(),
    providePrimeNG({
        theme: {
            preset: MyPreset
        }
    }),

    // Interceptor
    {
      provide: HTTP_INTERCEPTORS,
      useClass: CsrfInterceptor,
      multi: true
    },
    { provide: LOCALE_ID, useValue: 'es-ES' },
    ConfirmationService,
    MessageService,
  ],
  bootstrap: [App]
})
export class AppModule { }
