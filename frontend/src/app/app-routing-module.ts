import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { Login } from './auth/login/login';
import { Chat } from './pages/chat/chat';

const routes: Routes = [
  {path: 'auth/login', component: Login},
  {path: 'page/chat', component: Chat},
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
