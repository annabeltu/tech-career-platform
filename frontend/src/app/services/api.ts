import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { AuthService } from './auth';
import {
  Profile, RoadmapAction, Opportunity,
  SavedOpportunity, Resume, Conversation, Message
} from '../models';

@Injectable({ providedIn: 'root' })
export class ApiService {
  private readonly API = 'http://localhost:8000';

  constructor(private http: HttpClient, private auth: AuthService) {}

  private headers(): HttpHeaders {
    return new HttpHeaders({ Authorization: `Bearer ${this.auth.getToken()}` });
  }

  private get<T>(path: string): Promise<T> {
    return firstValueFrom(this.http.get<T>(`${this.API}${path}`, { headers: this.headers() }));
  }

  private post<T>(path: string, body: any): Promise<T> {
    return firstValueFrom(this.http.post<T>(`${this.API}${path}`, body, { headers: this.headers() }));
  }

  private delete<T>(path: string): Promise<T> {
    return firstValueFrom(this.http.delete<T>(`${this.API}${path}`, { headers: this.headers() }));
  }

  // Profile
  getProfile(userId: number): Promise<any> {
    return this.get(`/waypoint/users/${userId}/profile`);
  }

  createProfile(userId: number, data: Partial<Profile>): Promise<any> {
    return this.post(`/waypoint/users/${userId}/profile`, data);
  }

  updateProfile(userId: number, data: Partial<Profile>): Promise<any> {
    return firstValueFrom(
      this.http.put<any>(`${this.API}/waypoint/users/${userId}/profile`, data, { headers: this.headers() })
    );
  }

  // Roadmap
  getRoadmap(userId: number): Promise<{ current_stage: number; actions: RoadmapAction[] }> {
    return this.get(`/waypoint/users/${userId}/roadmap`);
  }

  // Opportunities
  getOpportunities(filters?: Record<string, string>): Promise<{ count: number; opportunities: Opportunity[] }> {
    const params = filters ? '?' + new URLSearchParams(filters).toString() : '';
    return this.get(`/waypoint/opportunities${params}`);
  }

  getSavedOpportunities(userId: number): Promise<{ saved_opportunities: SavedOpportunity[] }> {
    return this.get(`/waypoint/users/${userId}/saved-opportunities`);
  }

  saveOpportunity(userId: number, opportunityId: number): Promise<any> {
    return this.post(`/waypoint/users/${userId}/saved-opportunities`, {
      opportunity_id: opportunityId,
      deadline_reminder: false
    });
  }

  unsaveOpportunity(userId: number, opportunityId: number): Promise<any> {
    return this.delete(`/waypoint/users/${userId}/saved-opportunities/${opportunityId}`);
  }

  // Resumes
  uploadResume(userId: number, rawText: string): Promise<any> {
    return this.post(`/waypoint/users/${userId}/resumes`, { raw_text: rawText });
  }

  getResumeFeedback(userId: number, resumeId: number): Promise<any> {
    return this.post(`/waypoint/users/${userId}/resumes/${resumeId}/feedback`, {});
  }

  getResume(userId: number, resumeId: number): Promise<Resume> {
    return this.get(`/waypoint/users/${userId}/resumes/${resumeId}`);
  }

  // Conversations
  getConversations(userId: number): Promise<{ conversations: Conversation[] }> {
    return this.get(`/waypoint/users/${userId}/conversations`);
  }

  createConversation(userId: number, title: string): Promise<any> {
    return this.post(`/waypoint/users/${userId}/conversations`, { title });
  }

  getMessages(userId: number, conversationId: number): Promise<{ messages: Message[] }> {
    return this.get(`/waypoint/users/${userId}/conversations/${conversationId}/messages`);
  }

  sendMessage(userId: number, conversationId: number, content: string): Promise<any> {
    return this.post(`/waypoint/users/${userId}/conversations/${conversationId}/messages`, { content });
  }

  deleteConversation(userId: number, conversationId: number): Promise<any> {
    return this.delete(`/waypoint/users/${userId}/conversations/${conversationId}`);
  }
}