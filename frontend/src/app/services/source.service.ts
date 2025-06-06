import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

import {
  SourceCreate,
  SourceRead,
  SourceUpdate
} from '../interfaces/source';

import { MessageResponse } from '../interfaces/message';

@Injectable({
  providedIn: 'root',
})
export class SourceService {
  private baseUrl = `${environment.apiBaseUrl}simulations/`;

  constructor(private http: HttpClient) {}

  getSources(simulationId: number): Observable<string[]> {
    return this.http.get<string[]>(`${this.baseUrl}${simulationId}/sources`);
  }

  createSource(
    simulationId: number,
    source: SourceCreate
  ): Observable<MessageResponse> {
    return this.http.post<MessageResponse>(`${this.baseUrl}${simulationId}/sources`, source);
  }

  getSource(simulationId: number, name: string): Observable<SourceRead> {
    return this.http.get<SourceRead>(`${this.baseUrl}${simulationId}/sources/${name}`);
  }

  updateSource(
    simulationId: number,
    name: string,
    source: SourceUpdate
  ): Observable<MessageResponse> {
    return this.http.put<MessageResponse>(`${this.baseUrl}${simulationId}/sources/${name}`, source);
  }

  deleteSource(simulationId: number, name: string): Observable<MessageResponse> {
    return this.http.delete<MessageResponse>(`${this.baseUrl}${simulationId}/sources/${name}`);
  }
}
