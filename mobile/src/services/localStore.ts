import uuid from 'react-native-uuid';
import EncryptedStorage from 'react-native-encrypted-storage';
import {AttendanceEvent, EmployeeProfile} from '../types/domain';

const EMPLOYEES_KEY = 'faceguard.employees.v1';
const QUEUE_KEY = 'faceguard.attendance.queue.v1';

export async function saveEmployee(profile: Omit<EmployeeProfile, 'id' | 'createdAt' | 'active'>): Promise<EmployeeProfile> {
  const employees = await loadEmployees();
  const next: EmployeeProfile = {
    ...profile,
    id: String(uuid.v4()),
    createdAt: new Date().toISOString(),
    active: true,
  };
  const deduped = employees.filter(employee => employee.employeeId !== next.employeeId);
  await EncryptedStorage.setItem(EMPLOYEES_KEY, JSON.stringify([...deduped, next]));
  return next;
}

export async function loadEmployees(): Promise<EmployeeProfile[]> {
  const raw = await EncryptedStorage.getItem(EMPLOYEES_KEY);
  return raw ? (JSON.parse(raw) as EmployeeProfile[]) : [];
}

export async function enqueueAttendance(event: Omit<AttendanceEvent, 'id' | 'syncStatus' | 'attempts'>): Promise<AttendanceEvent> {
  const queue = await loadAttendanceQueue();
  const next: AttendanceEvent = {
    ...event,
    id: String(uuid.v4()),
    syncStatus: 'pending',
    attempts: 0,
  };
  await EncryptedStorage.setItem(QUEUE_KEY, JSON.stringify([...queue, next]));
  return next;
}

export async function loadAttendanceQueue(): Promise<AttendanceEvent[]> {
  const raw = await EncryptedStorage.getItem(QUEUE_KEY);
  return raw ? (JSON.parse(raw) as AttendanceEvent[]) : [];
}

export async function replaceAttendanceQueue(events: AttendanceEvent[]): Promise<void> {
  await EncryptedStorage.setItem(QUEUE_KEY, JSON.stringify(events));
}

export async function purgeSyncedAttendance(syncedIds: string[]): Promise<number> {
  const queue = await loadAttendanceQueue();
  const pending = queue.filter(event => !syncedIds.includes(event.id));
  await replaceAttendanceQueue(pending);
  return queue.length - pending.length;
}
