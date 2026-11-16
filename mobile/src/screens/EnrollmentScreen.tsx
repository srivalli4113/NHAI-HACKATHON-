import React, {useState} from 'react';
import {Pressable, StyleSheet, Text, TextInput, View} from 'react-native';
import {enrollEmployee} from '../services/enrollmentService';
import {EmployeeProfile} from '../types/domain';
import {StatusPill} from '../components/StatusPill';

export function EnrollmentScreen() {
  const [employeeId, setEmployeeId] = useState('NHAI-1024');
  const [name, setName] = useState('Field Engineer Demo');
  const [department, setDepartment] = useState('Highway Operations');
  const [designation, setDesignation] = useState('Site Inspector');
  const [saved, setSaved] = useState<EmployeeProfile | null>(null);
  const [busy, setBusy] = useState(false);

  async function enroll() {
    setBusy(true);
    try {
      const profile = await enrollEmployee({
        frameId: `${employeeId}:${name}:front`,
        employeeId,
        name,
        department,
        designation,
      });
      setSaved(profile);
    } finally {
      setBusy(false);
    }
  }

  return (
    <View style={styles.screen}>
      <Text style={styles.title}>Offline Enrollment</Text>
      <Text style={styles.copy}>Captured templates stay encrypted on device and never require internet.</Text>

      <TextInput style={styles.input} value={employeeId} onChangeText={setEmployeeId} placeholder="Employee ID" />
      <TextInput style={styles.input} value={name} onChangeText={setName} placeholder="Name" />
      <TextInput style={styles.input} value={department} onChangeText={setDepartment} placeholder="Department" />
      <TextInput style={styles.input} value={designation} onChangeText={setDesignation} placeholder="Designation" />

      <Pressable style={styles.primaryButton} onPress={enroll} disabled={busy}>
        <Text style={styles.primaryText}>{busy ? 'Enrolling...' : 'Capture and Enroll'}</Text>
      </Pressable>

      {saved ? (
        <View style={styles.result}>
          <StatusPill label="Stored offline" tone="good" />
          <Text style={styles.resultText}>{saved.name} enrolled with a 192D local face template.</Text>
        </View>
      ) : null}
    </View>
  );
}

const styles = StyleSheet.create({
  screen: {gap: 12},
  title: {fontSize: 24, fontWeight: '800', color: '#101828'},
  copy: {fontSize: 14, lineHeight: 20, color: '#475467'},
  input: {
    borderColor: '#CBD5E1',
    borderRadius: 8,
    borderWidth: 1,
    color: '#101828',
    paddingHorizontal: 12,
    paddingVertical: 10,
  },
  primaryButton: {
    alignItems: 'center',
    backgroundColor: '#0B5FFF',
    borderRadius: 8,
    paddingVertical: 13,
  },
  primaryText: {color: '#FFFFFF', fontWeight: '800'},
  result: {
    borderColor: '#D0D5DD',
    borderRadius: 8,
    borderWidth: 1,
    gap: 8,
    padding: 12,
  },
  resultText: {color: '#344054'},
});
