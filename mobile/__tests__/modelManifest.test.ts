import {totalModelBudgetMb} from '../src/engine/modelManifest';

test('keeps proposed model footprint below the hackathon limit', () => {
  expect(totalModelBudgetMb()).toBeLessThanOrEqual(20);
});
