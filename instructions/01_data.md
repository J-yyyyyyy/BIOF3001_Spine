# Understand the data before coding

## Cases, levels and geometry

`data/cases.csv` is the case manifest. Every file path is relative to the package
root. Keep case IDs as strings. The `demo` field selects eight cases for GUI
practice; `regression_split` is a fixed seeded split for the later exercise.

One subject has 15 meshes ordered:

`T1 T2 T3 T4 T5 T6 T7 T8 T9 T10 T11 T12 L1 L2 L3`

These correspond to mask labels 8–22. The masks may also contain other labels;
ignore them for this task. Label 0 is background. Do not sort level names
alphabetically: that places T10 before T2.

There is one full-volume mask per case. The voxel values are anatomical labels,
not CT intensities. CT volumes and precomputed centroid answers are not supplied.

## What does the landmark mean?

In this exercise, the landmark is the arithmetic mean of all voxel indices with
that vertebra's label. It is a **whole-vertebra segmentation centroid**. It is a
practical surrogate for the project's VBC input, not a separately annotated
vertebral-body centre. Posterior elements affect its position. Mesh vertex means,
surface-area centroids and mask-volume centroids are different definitions.

## Coordinate chain

1. `nibabel` returns indices in `(i,j,k)` order.
2. The NIfTI affine maps those indices to physical RAS millimetres.
3. `world_ras_to_aligned` maps RAS millimetres to the supplied meshes' frame.

Both maps use homogeneous column-vector convention:

`p_out_h = matrix @ [x, y, z, 1]`

Use the supplied transform once. Do not add another RAS/LPS flip or independently
rotate the centroids. The paired source meshes came from a legacy extractor that
used positive spacing and the SimpleITK LPS origin without the direction matrix.
The supplied map explicitly accounts for this convention and the subsequent
whole-spine alignment. Students do not need to reconstruct that preprocessing.

The affine was recovered from corresponding vertices in original and aligned
meshes. Maximum vertex reproduction error is below 0.00001 mm in this package.
This measures the transform fit, not anatomical mesh accuracy. Centroids were
also checked against original per-level mesh bounds.

The supplied alignment itself was obtained from complete source geometry.
Consequently, this exercise is conditional on prealigned data; it does not test
landmark-only estimation of orientation on a previously unseen scan.

## Data screening

All 71 supplied cases have the 15 required labels and paired meshes. Target labels
that touched any outer image face were excluded (15 source cases). No mask was
cropped, resampled or relabelled for packaging. No manual completeness review
was performed. Visually inspect representative masks/meshes and discuss limitations.
