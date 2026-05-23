import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { Login } from './auth/login/login';
import { Chat } from './pages/chat/chat';
import { AuthGuard } from '../service/auth/auth.guard';
import { Inicio } from './pages/inicio/inicio';

const routes: Routes = [
  { path: '', redirectTo: 'page/inicio', pathMatch: 'full' },
  {path: 'page/inicio', component: Inicio},
  {path: 'auth/login', component: Login},
  {path: 'page/chat', component: Chat, canActivate: [AuthGuard]},
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
