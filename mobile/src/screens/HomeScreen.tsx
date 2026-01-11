/**
 * 홈 스크린 - 저장된 노래 목록
 */
import React, { useEffect, useState, useCallback } from 'react';
import {
  View,
  Text,
  FlatList,
  StyleSheet,
  TouchableOpacity,
  RefreshControl,
  Alert,
  Linking,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import ApiService, { SongResponse } from '../services/api';

const HomeScreen: React.FC = () => {
  const [songs, setSongs] = useState<SongResponse[]>([]);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);

  const loadSongs = async () => {
    try {
      setLoading(true);
      const data = await ApiService.getAllSongs();
      setSongs(data);
    } catch (error) {
      console.error('노래 로드 실패:', error);
      Alert.alert('오류', '노래 목록을 불러올 수 없습니다.');
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    await loadSongs();
    setRefreshing(false);
  }, []);

  useEffect(() => {
    loadSongs();
  }, []);

  const handleDelete = async (songId: number) => {
    Alert.alert(
      '삭제 확인',
      '이 노래를 삭제하시겠습니까?',
      [
        { text: '취소', style: 'cancel' },
        {
          text: '삭제',
          style: 'destructive',
          onPress: async () => {
            try {
              await ApiService.deleteSong(songId);
              setSongs(songs.filter(s => s.id !== songId));
            } catch (error) {
              Alert.alert('오류', '노래 삭제에 실패했습니다.');
            }
          },
        },
      ],
    );
  };

  const openSpotify = (spotifyId?: string) => {
    if (spotifyId) {
      Linking.openURL(`spotify:track:${spotifyId}`);
    }
  };

  const openAppleMusic = (appleMusicId?: string) => {
    if (appleMusicId) {
      Linking.openURL(`music://music.apple.com/song/${appleMusicId}`);
    }
  };

  const renderSong = ({ item }: { item: SongResponse }) => (
    <View style={styles.songCard}>
      <View style={styles.songInfo}>
        <Text style={styles.songTitle}>{item.title}</Text>
        <Text style={styles.songArtist}>{item.artist}</Text>
        {item.album && <Text style={styles.songAlbum}>{item.album}</Text>}
        <View style={styles.metadata}>
          <Text style={styles.service}>{item.service}</Text>
          <Text style={styles.confidence}>
            {(item.confidence * 100).toFixed(0)}% 확신
          </Text>
        </View>
      </View>

      <View style={styles.actions}>
        {item.spotify_id && (
          <TouchableOpacity
            onPress={() => openSpotify(item.spotify_id)}
            style={styles.actionButton}>
            <Icon name="music-note" size={24} color="#1DB954" />
          </TouchableOpacity>
        )}
        {item.apple_music_id && (
          <TouchableOpacity
            onPress={() => openAppleMusic(item.apple_music_id)}
            style={styles.actionButton}>
            <Icon name="music-note" size={24} color="#FA243C" />
          </TouchableOpacity>
        )}
        <TouchableOpacity
          onPress={() => handleDelete(item.id)}
          style={styles.actionButton}>
          <Icon name="delete" size={24} color="#FF5252" />
        </TouchableOpacity>
      </View>
    </View>
  );

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Icon name="library-music" size={32} color="#6200EA" />
        <Text style={styles.headerTitle}>내 음악</Text>
      </View>

      {songs.length === 0 && !loading ? (
        <View style={styles.emptyState}>
          <Icon name="music-off" size={64} color="#ccc" />
          <Text style={styles.emptyText}>저장된 노래가 없습니다</Text>
          <Text style={styles.emptySubtext}>
            인스타그램이나 틱톡에서 영상을 공유해보세요!
          </Text>
        </View>
      ) : (
        <FlatList
          data={songs}
          renderItem={renderSong}
          keyExtractor={item => item.id.toString()}
          refreshControl={
            <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
          }
          contentContainerStyle={styles.listContainer}
        />
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 20,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    marginLeft: 12,
    color: '#333',
  },
  listContainer: {
    padding: 16,
  },
  songCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  songInfo: {
    flex: 1,
  },
  songTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 4,
  },
  songArtist: {
    fontSize: 16,
    color: '#666',
    marginBottom: 4,
  },
  songAlbum: {
    fontSize: 14,
    color: '#999',
    marginBottom: 8,
  },
  metadata: {
    flexDirection: 'row',
    gap: 12,
  },
  service: {
    fontSize: 12,
    color: '#6200EA',
    fontWeight: '600',
    textTransform: 'uppercase',
  },
  confidence: {
    fontSize: 12,
    color: '#4CAF50',
  },
  actions: {
    flexDirection: 'row',
    gap: 8,
  },
  actionButton: {
    padding: 8,
  },
  emptyState: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 40,
  },
  emptyText: {
    fontSize: 20,
    fontWeight: '600',
    color: '#666',
    marginTop: 16,
  },
  emptySubtext: {
    fontSize: 14,
    color: '#999',
    marginTop: 8,
    textAlign: 'center',
  },
});

export default HomeScreen;
