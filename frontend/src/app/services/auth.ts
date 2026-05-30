import { Injectable, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { firstValueFrom } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly API = 'http://localhost:8000';
  private readonly TOKEN_KEY = 'waypoint_token';
  private readonly USER_KEY = 'waypoint_user';

  isLoggedIn = signal(this.hasToken());
  currentUserId = signal<number | null>(this.getUserId());

  constructor(private http: HttpClient, private router: Router) {}

  async register(data: {
    name: string;
    email: string;
    password: string;
    year_in_school: string;
    major: string;
    university: string;
  }): Promise<void> {
    const res: any = await firstValueFrom(
      this.http.post(`${this.API}/waypoint/auth/register`, data)
    );
    await this.login(data.email, data.password);
  }

  async login(email: string, password: string): Promise<void> {
    const res: any = await firstValueFrom(
      this.http.post(`${this.API}/waypoint/auth/login`, { email, password })
    );
    localStorage.setItem(this.TOKEN_KEY, res.access_token);
    this.isLoggedIn.set(true);

    // Fetch user id by getting profile
    const profile: any = await firstValueFrom(
      this.http.get(`${this.API}/waypoint/auth/me`, {
        headers: { Authorization: `Bearer ${res.access_token}` }
      })
    ).catch(() => null);

    // Decode user id from JWT
    const payload = JSON.parse(atob(res.access_token.split('.')[1]));
    const userId = parseInt(payload.sub);
    localStorage.setItem(this.USER_KEY, String(userId));
    this.currentUserId.set(userId);
  }

  logout(): void {
    localStorage.removeItem(this.TOKEN_KEY);
    localStorage.removeItem(this.USER_KEY);
    this.isLoggedIn.set(false);
    this.currentUserId.set(null);
    this.router.navigate(['/login']);
  }

  getToken(): string | null {
    return localStorage.getItem(this.TOKEN_KEY);
  }

  private hasToken(): boolean {
    return !!localStorage.getItem(this.TOKEN_KEY);
  }

  private getUserId(): number | null {
    const id = localStorage.getItem(this.USER_KEY);
    return id ? parseInt(id) : null;
  }
}