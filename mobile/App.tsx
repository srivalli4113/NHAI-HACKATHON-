import React, {useState} from 'react';
import {SafeAreaView, ScrollView, StatusBar, StyleSheet, Text, Pressable, View} from 'react-native';
import {EnrollmentScreen} from './src/screens/EnrollmentScreen';
import {RecognitionScreen} from './src/screens/RecognitionScreen';
import {SyncScreen} from './src/screens/SyncScreen';

type Tab = 'enroll' | 'recognize' | 'sync';

export default function App() {
  const [tab, setTab] = useState<Tab>('recognize');

  return (
    <SafeAreaView style={styles.safe}>
      <StatusBar barStyle="dark-content" backgroundColor="#F8FAFC" />
      <ScrollView contentContainerStyle={styles.container}>
        <Text style={styles.brand}>FaceGuard Edge</Text>
        <Text style={styles.subtitle}>Secure offline face recognition for NHAI field operations</Text>

        <View style={styles.tabs}>
          <TabButton active={tab === 'enroll'} label="Enroll" onPress={() => setTab('enroll')} />
          <TabButton active={tab === 'recognize'} label="Recognize" onPress={() => setTab('recognize')} />
          <TabButton active={tab === 'sync'} label="Sync" onPress={() => setTab('sync')} />
        </View>

        {tab === 'enroll' ? <EnrollmentScreen /> : null}
        {tab === 'recognize' ? <RecognitionScreen /> : null}
        {tab === 'sync' ? <SyncScreen /> : null}
      </ScrollView>
    </SafeAreaView>
  );
}

function TabButton({active, label, onPress}: {active: boolean; label: string; onPress: () => void}) {
  return (
    <Pressable style={[styles.tab, active && styles.activeTab]} onPress={onPress}>
      <Text style={[styles.tabText, active && styles.activeTabText]}>{label}</Text>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  safe: {backgroundColor: '#F8FAFC', flex: 1},
  container: {
    gap: 18,
    padding: 20,
  },
  brand: {
    color: '#101828',
    fontSize: 30,
    fontWeight: '900',
  },
  subtitle: {
    color: '#475467',
    fontSize: 15,
    lineHeight: 21,
  },
  tabs: {
    backgroundColor: '#E9EEF5',
    borderRadius: 8,
    flexDirection: 'row',
    padding: 4,
  },
  tab: {
    alignItems: 'center',
    borderRadius: 6,
    flex: 1,
    paddingVertical: 10,
  },
  activeTab: {
    backgroundColor: '#FFFFFF',
  },
  tabText: {
    color: '#475467',
    fontWeight: '700',
  },
  activeTabText: {
    color: '#0B5FFF',
  },
});
