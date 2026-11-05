"""Standardize copies of the full-cohort Studio exports; preserve originals."""
import shutil

import numpy as np
import pandas as pd
from openpyxl import load_workbook
from common import OUTPUT, LEVELS, manifest


def main():
    table = pd.read_csv(OUTPUT / 'full_pca_scores.csv')
    table = table.rename(columns={'name': 'case_id', **{f'p{i}': f'pc{i+1}' for i in range(71)}})
    expected = {row['case_id'] for row in manifest()}
    if len(table) != 71 or set(table['case_id']) != expected or table['case_id'].duplicated().any():
        raise ValueError('Expected exactly the 71 manifest subjects')
    mean = np.vstack([np.loadtxt(OUTPUT / f'full_run_current_particles_{i}.particles') for i in range(1, 16)])
    modes = np.stack([np.loadtxt(OUTPUT / f'full_pca_eignevectors{i}.eval').ravel() for i in range(3)])
    # Check exported scores against actual subject particles in the same frame.
    sheet = load_workbook(OUTPUT / 'full_run.xlsx', data_only=True)['data']
    rows = list(sheet.values)
    records = [dict(zip(rows[0], row)) for row in rows[1:]]
    by_id = {row['name']: row for row in records}
    projected = []
    for case in table['case_id']:
        row = by_id[case]
        points = np.vstack([np.loadtxt(OUTPUT / row[f'world_particles_{i}']) for i in range(1, 16)])
        projected.append((points.ravel() - mean.ravel()) @ modes.T)
    scores = table[['pc1', 'pc2', 'pc3']].to_numpy(float)
    difference = np.max(np.abs(np.asarray(projected) - scores))
    if not np.allclose(projected, scores, atol=0.05, rtol=1e-4):
        raise ValueError(f'Scores disagree with particle projections: max difference {difference}')
    folder = OUTPUT / 'pca_exports'
    (folder / 'mean').mkdir(parents=True, exist_ok=True)
    (folder / 'modes').mkdir(exist_ok=True)
    for i, level in enumerate(LEVELS, 1):
        shutil.copy2(OUTPUT / f'full_run_current_particles_{i}.particles', folder / 'mean' / f'{level}.particles')
    for i in range(3):
        shutil.copy2(OUTPUT / f'full_pca_eignevectors{i}.eval', folder / 'modes' / f'pc{i+1}.txt')
    table.to_csv(folder / 'scores.csv', index=False)
    print(f'Prepared 71 subjects; score/particle projection max difference: {difference:.6f}')


if __name__ == '__main__':
    main()
