"""Implement these functions. Keep signatures and return shapes unchanged.

Run scripts/check_exercises.py after each exercise. TODOs intentionally raise
NotImplementedError; the surrounding file loading and saving is already supplied.
"""
import os
from pathlib import Path

import numpy as np

def label_centroid_ijk(mask, label):
    
    """Exercise 1A: mean voxel index of a nonzero vertebral label.

    mask: (I,J,K), as returned by nibabel; NOT SimpleITK's (K,J,I).
    Return: float array (3,) in i,j,k order. Raise ValueError if absent.
    """
    mask = np.asarray(mask)
    if mask.ndim != 3:
        raise ValueError("mask must be a 3D array with shape (I, J, K)")

    count = 0
    sum_i = 0.0
    sum_j = 0.0
    sum_k = 0.0

    # 逐 slice 累加，避免生成三个全容积坐标网格
    for i in range(mask.shape[0]):
        js, ks = np.nonzero(mask[i] == label)
        n = js.size
        if n == 0:
            continue

        count += n
        sum_i += i * n
        sum_j += js.sum()
        sum_k += ks.sum()

    if count == 0:
        raise ValueError(f"Label {label} not found in mask")

    return np.array(
        [sum_i / count, sum_j / count, sum_k / count],
        dtype=float
    )

def apply_affine(points, matrix):
    """Exercise 1B: map (N,3) points using a (4,4) affine; return (N,3).

    Matrix convention: column vectors, p_out = M @ [x,y,z,1].
    Hint: append homogeneous ones and handle row/column orientation carefully.
    Do not perform another RAS/LPS flip: the supplied transform includes it.
    """
    points = np.asarray(points, dtype=float)
    matrix = np.asarray(matrix, dtype=float)
    if points.ndim != 2 or points.shape[1] != 3:
        raise ValueError('points must have shape (N,3)')
    if matrix.shape != (4, 4):
        raise ValueError('matrix must have shape (4,4)')
    # 行向量存储的点：旋转/缩放后，再加平移。
    return points @ matrix[:3, :3].T + matrix[:3, 3]

def mesh_row(case_id, package_root, workbook_directory):
    """Exercise 2: return [case_id, '', path_T1, ..., path_L3] (17 strings).

    Use data/meshes/<case_id>/<level>.ply. Make paths relative to the OUTPUT
    workbook directory so moving the whole package preserves them. Validate
    every file exists. T1,T2,...,T12,L1,L2,L3 is anatomical, not lexical order.
    Hint: pathlib + os.path.relpath; forward slashes are portable.
    """
    levels = [f'T{i}' for i in range(1, 13)] + ['L1', 'L2', 'L3']
    paths = []
    for level in levels:
        mesh = Path(package_root) / 'data' / 'meshes' / case_id / f'{level}.ply'
        if not mesh.is_file():
            raise FileNotFoundError(mesh)
        paths.append(Path(os.path.relpath(mesh, workbook_directory)).as_posix())
    return [case_id, '', *paths]

def landmark_features(centres):
    """Exercise 3A: (N,15,3) -> (N,45) features.

    Baseline: flatten the already aligned coordinates in anatomical order.
    Keep physical scale for this baseline. PLS will learn training-set scaling.
    Translation/chain-length normalization is an optional ablation, not required.
    Apply identical preprocessing at fit and prediction time.
    """
    centres = np.asarray(centres, dtype=float)
    if centres.ndim != 3 or centres.shape[1:] != (15, 3):
        raise ValueError('centres must have shape (N,15,3)')
    return centres.reshape(centres.shape[0], 45)

def fit_pls(x_train, y_train, n_components):
    """Exercise 3B: return a fitted sklearn PLSRegression estimator.

    X: (N,45); Y: (N,K) raw PC scores. Use scale=True and max_iter=1000.
    Fit ONLY the training fold. Never fit a scaler on validation/test data.
    n_components counts PLS latent variables, NOT output PCA modes.
    """
    from sklearn.cross_decomposition import PLSRegression

    # Scaling is learned only from the training data supplied to this call.
    model = PLSRegression(n_components=n_components, scale=True, max_iter=1000)
    return model.fit(x_train, y_train)

def predict_scores(model, features):
    """Exercise 3C: use the fitted model; return (N,K) predictions."""
    predicted = np.asarray(model.predict(features), dtype=float)
    # Keep the output dimension even when there is only one PCA target.
    if predicted.ndim == 1:
        predicted = predicted[:, None]
    return predicted

def reconstruct_particles(scores, mean, modes):
    """Exercise 4: (N,K), (3840,3), (K,11520) -> (N,3840,3).

    Each row of modes is one UNIT PCA eigenvector. Scores are RAW projection
    coefficients, not standard-deviation slider values. Combine the weighted
    modes with the flattened mean. Do not multiply by sqrt(eigenvalue) again.
    A zero-score vector must return the mean exactly.
    """
    scores = np.asarray(scores, dtype=float)
    mean = np.asarray(mean, dtype=float)
    modes = np.asarray(modes, dtype=float)
    if mean.shape != (3840, 3):
        raise ValueError('mean must have shape (3840,3)')
    if scores.ndim != 2 or modes.shape != (scores.shape[1], mean.size):
        raise ValueError('Expected scores (N,K) and modes (K,11520)')
    # Raw scores already contain the mode amplitude: no eigenvalue scaling.
    return (mean.ravel() + scores @ modes).reshape(scores.shape[0], 3840, 3)
