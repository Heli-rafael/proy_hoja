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
import { KnobModule } from 'primeng/knob';
import { FormsModule } from '@angular/forms';
import { ToastModule } from 'primeng/toast';
import { PasswordModule } from 'primeng/password';

// Importacion de Google
import { SocialAuthServiceConfig } from '@abacritt/angularx-social-login';
import { GoogleLoginProvider } from '@abacritt/angularx-social-login';

// Comparar imagenes
import { ImageCompareModule } from 'primeng/imagecompare';
import { Inicio } from './pages/inicio/inicio';

// Menu
import { MenubarModule } from 'primeng/menubar';

// Locale
import { registerLocaleData } from '@angular/common';
import localeEs from '@angular/common/locales/es';
registerLocaleData(localeEs, 'es-ES');

// ICONS LUCIDE
import { LucideAngularModule } from 'lucide-angular';
import { Icons } from './icons.lucide';

// CHECKBOX
import { CheckboxModule } from 'primeng/checkbox';
import { Pruebas } from './pages/pruebas/pruebas';

// IMAGENES
import { GalleriaModule } from 'primeng/galleria';


@NgModule({
  declarations: [
    App,
    Login,
    Chat,
    Inicio,
    Pruebas
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
    KnobModule,
    FormsModule,
    ToastModule,
    PasswordModule,

    // Comparar imagenes
    ImageCompareModule,
    GalleriaModule,

    // Menu
    MenubarModule,

    // Checkbox
    CheckboxModule,

    // ICONS LUCIDE
    LucideAngularModule.pick(Icons),
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

    // Configuracion de Google
    {
      provide: 'SocialAuthServiceConfig',
      useValue: {
        autoLogin: false,
        providers: [
          {
            id: GoogleLoginProvider.PROVIDER_ID,
            provider: new GoogleLoginProvider(
              'TU_CLIENT_ID'
            )
          }
        ],
        onError: (err: any) => console.error(err)
      }
    },
    // Locale
    { provide: LOCALE_ID, useValue: 'es-ES' },
    
    // Confirmacion y Mensajes
    ConfirmationService,
    MessageService,
  ],
  bootstrap: [App]
})
export class AppModule { }
