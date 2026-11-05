# Python exercises

Implement only the TODOs in `scripts/student_tasks.py` initially. Functions should
return arrays instead of writing files; the numbered drivers handle outputs.

## Exercise 1: mask to ordered landmarks

**Implement:** `label_centroid_ijk` and `apply_affine`.

For each label, calculate the number of voxels and the sum of their index
coordinates, then divide. Check for an empty label before dividing. Use floating
point output; rounding would lose subvoxel information. Large arrays are best
processed one axial slice at a time to avoid full-volume coordinate grids.

Apply the NIfTI affine and then the supplied case transform. The driver saves
voxel, RAS and aligned coordinates as `(15,3)` arrays in anatomical order.

**Check:** the synthetic affine test includes rotation, unequal scaling and
translation. Passing an identity-transform example alone is insufficient.
Inspect one real case before processing the whole cohort.

**Discuss:** Why does voxel spacing matter? Why is a centroid not necessarily the
centre of the vertebral body? Why does a mask-derived landmark depend on segmentation?

## Exercise 2: generate the ShapeWorks workbook

**Implement:** `mesh_row`.

The output is one row per subject: `name`, `notes`, `shape_1` through `shape_15`.
The value in `name` must be the manifest case ID so exported scores can be joined
by identity. Generate relative paths from the output workbook's directory to
the meshes. Check file existence before returning a row. The driver handles
Excel file creation from the provided example.

**Check:** open the workbook and verify that shape_12 is T12 and shape_13 is L1.
Import the eight-case example in Studio. A successful import should show eight
subjects, each with 15 domains—not 120 unrelated subjects or one merged domain.

## Exercise 3: landmarks to PCA scores

**Implement:** `landmark_features`, `fit_pls`, `predict_scores`.

The baseline input is 15 aligned 3D centres, flattened to 45 features. The output
is K raw PCA scores. Start with K=3. PLS finds latent directions linking X and Y;
its `n_components` parameter is distinct from the number of PCA outputs.

Use `PLSRegression(scale=True, max_iter=1000)`. The supplied driver selects among
small component counts with three-fold cross-validation on training subjects,
refits using all training subjects, and evaluates once on the reserved subjects.
No test data should influence component selection or standardization.

**Check:** compare against predicting the training mean score vector for everyone.
Inspect `outputs/regression_report.json`. Scores must remain floating point.

**Interpretation:** the introductory SSM is shared across the cohort. The fixed
holdout is therefore a regression test conditional on that SSM and prealignment.
A research extension would fit correspondence/PCA on training subjects only,
establish test correspondence in the fixed training model, project test shapes
into that basis, and avoid test-derived alignment information.

## Exercise 4: scores to particles

**Implement:** `reconstruct_particles`.

The mean has shape `(3840,3)`, modes `(K,11520)`, and scores `(N,K)`.
Flatten the mean in point-major XYZ order, form the weighted sum of mode rows,
add the mean and reshape to `(N,3840,3)`. Each consecutive 256-point block is
one vertebra in the agreed order. Point index is a correspondence identity:
never independently sort particles by their coordinates.

**Check:** zero scores reconstruct the mean; a single nonzero score moves the
shape along exactly one mode. Do not multiply raw scores by square-root
eigenvalues. That scaling is needed only when starting from standard-deviation
slider values instead of raw coefficients.

The driver reconstructs both predicted scores and actual exported scores. Their
particle difference isolates regression error in the retained PCA subspace.
It does not measure PCA truncation or mask-to-surface error.

The supplied plotter uses identical axis ranges for the two reconstructions and
colours vertebrae consistently. Use `--no-show` when saving on a machine without
an interactive display. An optional exercise is to annotate centroid errors or
overlay supplied meshes, after verifying their frame matches the exported points.

## Suggested submission

Submit the completed TODO file, environment version list, generated import
workbook, recorded ShapeWorks settings, regression report and one comparison
figure. In a short discussion, explain the coordinate chain, the two kinds of
latent dimension, the baseline comparison and the shared-SSM evaluation limit.
Do not submit the mask/mesh data in the code repository.
