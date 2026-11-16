export function normalize(vector: number[]): number[] {
  const norm = Math.sqrt(vector.reduce((sum, value) => sum + value * value, 0));
  if (norm === 0) {
    return vector;
  }
  return vector.map(value => value / norm);
}

export function cosineSimilarity(a: number[], b: number[]): number {
  if (a.length !== b.length || a.length === 0) {
    return 0;
  }
  const aNorm = Math.sqrt(a.reduce((sum, value) => sum + value * value, 0));
  const bNorm = Math.sqrt(b.reduce((sum, value) => sum + value * value, 0));
  if (aNorm === 0 || bNorm === 0) {
    return 0;
  }
  const dot = a.reduce((sum, value, index) => sum + value * b[index], 0);
  return dot / (aNorm * bNorm);
}

export function cosineDistance(a: number[], b: number[]): number {
  return 1 - cosineSimilarity(a, b);
}

export function stableMockEmbedding(seed: string, dimensions = 192): number[] {
  let state = 2166136261;
  for (let index = 0; index < seed.length; index += 1) {
    state ^= seed.charCodeAt(index);
    state = Math.imul(state, 16777619);
  }
  const values = Array.from({length: dimensions}, () => {
    state ^= state << 13;
    state ^= state >>> 17;
    state ^= state << 5;
    return ((state >>> 0) % 2000) / 1000 - 1;
  });
  return normalize(values);
}
