/**
 * 처리 중 화면 - 비디오 분석 진행 상황 표시
 */
import React, { useEffect, useState, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ActivityIndicator,
  ScrollView,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import ApiService, { JobStatusResponse, SongResponse } from '../services/api';

interface Props {
  jobId: number;
  onComplete: (songs: SongResponse[]) => void;
  onError: (error: string) => void;
}

const ProcessingScreen: React.FC<Props> = ({ jobId, onComplete, onError }) => {
  const [status, setStatus] = useState<JobStatusResponse | null>(null);
  const [polling, setPolling] = useState(true);

  const checkStatus = useCallback(async () => {
    try {
      const data = await ApiService.getJobStatus(jobId);
      setStatus(data);

      if (data.status === 'completed') {
        setPolling(false);
        onComplete(data.songs);
      } else if (data.status === 'failed') {
        setPolling(false);
        onError(data.error_message || '처리 중 오류가 발생했습니다');
      }
    } catch (error) {
      console.error('상태 확인 실패:', error);
      setPolling(false);
      onError('작업 상태를 확인할 수 없습니다');
    }
  }, [jobId, onComplete, onError]);

  useEffect(() => {
    if (!polling) return;

    // 초기 호출
    checkStatus();

    // 2초마다 폴링
    const interval = setInterval(checkStatus, 2000);

    return () => clearInterval(interval);
  }, [polling, checkStatus]);

  const getStatusIcon = () => {
    if (!status) return 'hourglass-empty';
    switch (status.status) {
      case 'pending':
        return 'hourglass-empty';
      case 'processing':
        return 'sync';
      case 'completed':
        return 'check-circle';
      case 'failed':
        return 'error';
      default:
        return 'help';
    }
  };

  const getStatusText = () => {
    if (!status) return '대기 중...';
    switch (status.status) {
      case 'pending':
        return '작업 대기 중...';
      case 'processing':
        return '음악 감지 중...';
      case 'completed':
        return '완료!';
      case 'failed':
        return '실패';
      default:
        return status.status;
    }
  };

  const getStatusColor = () => {
    if (!status) return '#999';
    switch (status.status) {
      case 'pending':
        return '#FF9800';
      case 'processing':
        return '#2196F3';
      case 'completed':
        return '#4CAF50';
      case 'failed':
        return '#F44336';
      default:
        return '#999';
    }
  };

  return (
    <View style={styles.container}>
      <View style={styles.statusContainer}>
        <Icon name={getStatusIcon()} size={80} color={getStatusColor()} />
        <Text style={[styles.statusText, { color: getStatusColor() }]}>
          {getStatusText()}
        </Text>

        {status && status.status === 'processing' && (
          <>
            <View style={styles.progressBar}>
              <View
                style={[styles.progressFill, { width: `${status.progress}%` }]}
              />
            </View>
            <Text style={styles.progressText}>{status.progress}%</Text>
            <ActivityIndicator
              size="large"
              color="#6200EA"
              style={styles.spinner}
            />
          </>
        )}

        {status && status.songs_detected > 0 && (
          <View style={styles.songsInfo}>
            <Icon name="library-music" size={32} color="#6200EA" />
            <Text style={styles.songsText}>
              {status.songs_detected}개 노래 발견!
            </Text>
          </View>
        )}
      </View>

      {status && status.songs.length > 0 && (
        <ScrollView style={styles.songsList}>
          <Text style={styles.songsListTitle}>감지된 노래:</Text>
          {status.songs.map(song => (
            <View key={song.id} style={styles.songItem}>
              <Icon name="music-note" size={20} color="#6200EA" />
              <View style={styles.songItemInfo}>
                <Text style={styles.songItemTitle}>{song.title}</Text>
                <Text style={styles.songItemArtist}>{song.artist}</Text>
              </View>
            </View>
          ))}
        </ScrollView>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  statusContainer: {
    alignItems: 'center',
    justifyContent: 'center',
    padding: 40,
    backgroundColor: '#fff',
    marginBottom: 16,
  },
  statusText: {
    fontSize: 24,
    fontWeight: 'bold',
    marginTop: 20,
  },
  progressBar: {
    width: '100%',
    height: 8,
    backgroundColor: '#e0e0e0',
    borderRadius: 4,
    marginTop: 20,
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#6200EA',
    borderRadius: 4,
  },
  progressText: {
    fontSize: 16,
    color: '#666',
    marginTop: 8,
  },
  spinner: {
    marginTop: 20,
  },
  songsInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 24,
    gap: 12,
  },
  songsText: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
  },
  songsList: {
    flex: 1,
    paddingHorizontal: 16,
  },
  songsListTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 12,
  },
  songItem: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#fff',
    padding: 12,
    borderRadius: 8,
    marginBottom: 8,
    gap: 12,
  },
  songItemInfo: {
    flex: 1,
  },
  songItemTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
  },
  songItemArtist: {
    fontSize: 14,
    color: '#666',
    marginTop: 2,
  },
});

export default ProcessingScreen;
