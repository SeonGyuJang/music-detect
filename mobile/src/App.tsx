/**
 * 메인 앱 컴포넌트
 */
import React, { useEffect, useState } from 'react';
import { SafeAreaView, StyleSheet, Alert, StatusBar } from 'react-native';
import ShareMenu from 'react-native-share-menu';
import HomeScreen from './screens/HomeScreen';
import ProcessingScreen from './screens/ProcessingScreen';
import ApiService, { SongResponse } from './services/api';

type AppState = 'home' | 'processing';

const App: React.FC = () => {
  const [appState, setAppState] = useState<AppState>('home');
  const [currentJobId, setCurrentJobId] = useState<number | null>(null);

  useEffect(() => {
    // 공유 메뉴 리스너 등록
    const listener = ShareMenu.addNewShareListener(handleShare);

    return () => {
      listener.remove();
    };
  }, []);

  const handleShare = async (item?: { data: string; mimeType: string }) => {
    if (!item || !item.data) {
      console.log('공유 데이터 없음');
      return;
    }

    const url = item.data;
    console.log('공유된 URL:', url);

    // URL 유효성 검사
    if (!url.startsWith('http')) {
      Alert.alert('오류', '유효한 URL이 아닙니다.');
      return;
    }

    // 플랫폼 감지
    let platform = 'unknown';
    if (url.includes('instagram.com') || url.includes('instagr.am')) {
      platform = 'instagram';
    } else if (url.includes('tiktok.com')) {
      platform = 'tiktok';
    } else if (url.includes('youtube.com') || url.includes('youtu.be')) {
      platform = 'youtube';
    }

    try {
      // 서버에 비디오 제출
      const response = await ApiService.submitVideo(url, platform);

      setCurrentJobId(response.job_id);
      setAppState('processing');

      Alert.alert(
        '처리 시작',
        '영상에서 음악을 감지하고 있습니다. 잠시만 기다려주세요.',
      );
    } catch (error) {
      console.error('비디오 제출 실패:', error);
      Alert.alert('오류', '비디오 처리를 시작할 수 없습니다.');
    }
  };

  const handleProcessingComplete = (songs: SongResponse[]) => {
    setAppState('home');
    setCurrentJobId(null);

    if (songs.length === 0) {
      Alert.alert('완료', '음악을 찾을 수 없습니다.');
    } else {
      Alert.alert(
        '완료!',
        `${songs.length}개의 노래를 찾았습니다!`,
        [{ text: '확인', onPress: () => {} }],
      );
    }
  };

  const handleProcessingError = (error: string) => {
    setAppState('home');
    setCurrentJobId(null);
    Alert.alert('오류', error);
  };

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="dark-content" backgroundColor="#fff" />
      {appState === 'home' ? (
        <HomeScreen />
      ) : (
        currentJobId && (
          <ProcessingScreen
            jobId={currentJobId}
            onComplete={handleProcessingComplete}
            onError={handleProcessingError}
          />
        )
      )}
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
});

export default App;
