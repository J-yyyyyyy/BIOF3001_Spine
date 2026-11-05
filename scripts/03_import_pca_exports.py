"""Provided adapter: validates the standard export layout and packs pca.npz.

See instructions/03_shapeworks.md for the export layout and score convention.
No shape model is trained in this script. No student reconstruction is supplied.
"""
import argparse
import numpy as np
import pandas as pd
from common import ROOT, OUTPUT, LEVELS
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory',type=str,default=str(OUTPUT/'pca_exports'))
    parser.add_argument('--modes',type=int,default=3)
    args=parser.parse_args()
    from pathlib import Path
    folder=Path(args.directory); k=args.modes
    if k<1: raise ValueError('Use at least one PCA mode')
    mean=np.vstack([np.loadtxt(folder/'mean'/f'{level}.particles') for level in LEVELS])
    modes=np.stack([np.loadtxt(folder/'modes'/f'pc{i+1}.txt').reshape(-1) for i in range(k)])
    table=pd.read_csv(folder/'scores.csv',dtype={'case_id':str})
    ids=table['case_id'].to_numpy(dtype=str)
    scores=table[[f'pc{i+1}' for i in range(k)]].to_numpy(dtype=float)
    if mean.shape!=(3840,3) or modes.shape!=(k,11520):
        raise ValueError('Require 15 x 256 mean particles and matching full-spine modes')
    if len(set(ids))!=len(ids) or len(ids)<=k:
        raise ValueError('Case IDs must be unique; use fewer modes than subjects')
    if not all(np.isfinite(x).all() for x in [mean,modes,scores]):
        raise ValueError('Non-finite PCA export values')
    if not np.allclose(modes@modes.T,np.eye(k),atol=0.01):
        raise ValueError('Expected orthonormal eigenvectors, not displaced shapes or scaled modes')
    np.savez(OUTPUT/'pca.npz',mean=mean,modes=modes,scores=scores,case_ids=ids)
    print('Saved',OUTPUT/'pca.npz','with',len(ids),'subjects and',k,'modes')
if __name__=='__main__': main()
