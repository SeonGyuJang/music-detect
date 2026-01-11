/**
 * API 클라이언트 서비스
 */
import axios, { AxiosInstance } from 'axios';

// 백엔드 API URL (개발 환경)
const API_BASE_URL = 'http://localhost:8000/api/v1';

interface VideoSubmitRequest {
  url: string;
  platform: string;
  services?: string[];
}

interface VideoSubmitResponse {
  job_id: number;
  status: string;
  message: string;
}

interface SongResponse {
  id: number;
  title: string;
  artist: string;
  album?: string;
  release_date?: string;
  service: string;
  confidence: number;
  spotify_id?: string;
  apple_music_id?: string;
  isrc?: string;
  detected_at: string;
}

interface JobStatusResponse {
  job_id: number;
  status: string;
  progress: number;
  songs_detected: number;
  error_message?: string;
  songs: SongResponse[];
}

class ApiService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  /**
   * 비디오 URL 제출
   */
  async submitVideo(
    url: string,
    platform: string = 'unknown',
    services?: string[]
  ): Promise<VideoSubmitResponse> {
    const response = await this.client.post<VideoSubmitResponse>('/submit', {
      url,
      platform,
      services,
    });
    return response.data;
  }

  /**
   * 작업 상태 조회
   */
  async getJobStatus(jobId: number): Promise<JobStatusResponse> {
    const response = await this.client.get<JobStatusResponse>(`/job/${jobId}`);
    return response.data;
  }

  /**
   * 모든 노래 조회
   */
  async getAllSongs(limit: number = 50, offset: number = 0): Promise<SongResponse[]> {
    const response = await this.client.get<SongResponse[]>('/songs', {
      params: { limit, offset },
    });
    return response.data;
  }

  /**
   * 노래 삭제
   */
  async deleteSong(songId: number): Promise<void> {
    await this.client.delete(`/song/${songId}`);
  }

  /**
   * 헬스 체크
   */
  async healthCheck(): Promise<{ status: string; service: string }> {
    const response = await this.client.get('/health');
    return response.data;
  }
}

export default new ApiService();
export type { SongResponse, JobStatusResponse, VideoSubmitResponse };
