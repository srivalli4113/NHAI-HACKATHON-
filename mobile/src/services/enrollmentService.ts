import {embedFrame} from '../engine/faceEngine';
import {saveEmployee} from './localStore';

export async function enrollEmployee(input: {
  frameId: string;
  employeeId: string;
  name: string;
  department: string;
  designation: string;
}) {
  const embedding = await embedFrame(input.frameId);
  return saveEmployee({
    employeeId: input.employeeId.trim(),
    name: input.name.trim(),
    department: input.department.trim(),
    designation: input.designation.trim(),
    embedding: embedding.vector,
  });
}
