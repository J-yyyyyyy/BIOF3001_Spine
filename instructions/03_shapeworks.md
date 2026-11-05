# ShapeWorks practical and PCA export contract

Use the instructor's installed ShapeWorks Studio version. Menu wording can
differ between releases. Record the version, settings and elapsed time in your
report. These instructions describe the workflow; this package has not been
run through an interactive GUI optimization during preparation.

## Import and groom

1. Complete Exercise 2 and open `outputs/shapeworks_demo.xlsx` in Studio.
2. In Data, check subject names, 15 domains and T1–L3 order. Inspect orientation.
3. The meshes are already aligned. Skip geometry-changing grooming where
   supported, or use mesh grooming without further alignment/rescaling.
4. Preserve the arrangement of the whole spine. Do not centre or rigidly align
   each vertebra independently. Do not introduce Procrustes transformations in
   this baseline: the supplied centroid features are in the existing mesh frame.
5. Save the project under `outputs` so relative paths remain valid.

Additional grooming transforms are a valid advanced experiment only if their
effect on the landmarks and exported particle frame is tracked explicitly.

## Optimize correspondence, then analyze PCA

Set **256 particles for each of the 15 domains**, giving 3,840 particles per subject.
Use the installed defaults for other optimizer parameters for the first attempt;
record their actual numerical values. Disable extra pose/scale alignment for this
prealigned baseline. Begin with eight subjects, inspect the output, then use the
full cohort for the regression exercise. A small practice run and the full run
produce different PCA bases; never mix their exported files.

| Parameter | What to explain or observe |
|---|---|
| Particles per domain | Representation density, correspondence quality and compute cost |
| Relative weighting | Balance between surface coverage and population correspondence |
| Starting/ending regularization | Stabilization of covariance estimation during optimization |
| Iterations per split / final iterations | Time allowed for particle refinement and convergence |
| Normals / geodesic options | Additional surface information or distance choices |
| Procrustes and scaling | Whether pose or size are removed from the modeled variation |

After optimization, inspect correspondence coverage, the mean, principal modes
and explained variation. Use the combined whole-spine **shape-and-pose** PCA
representation if the version offers separate multi-level analyses. The baseline
needs one score vector for the concatenated 15-domain shape.

PCA sliders commonly express multiples of standard deviation. The corresponding
raw coefficient is that slider value times the square root of the eigenvalue.
The reconstruction code expects raw coefficients, not slider positions.

## Export and standardize filenames

Export the mean particles, eigenvectors and **raw component scores** from the
same saved project and analysis mode. Keep the original export files unchanged
in a separate subfolder. Prepare copies in this layout:

```text
outputs/pca_exports/
  scores.csv
  mean/
    T1.particles ... T12.particles L1.particles L2.particles L3.particles
  modes/
    pc1.txt pc2.txt pc3.txt ...
```

- Each mean file contains 256 lines of XYZ coordinates, separated by whitespace.
- Each mode file contains 11,520 numeric values: all 15 domains, with XYZ
  coordinates consecutive within each particle. An exported `(3840,3)` array
  has this layout when flattened row by row.
- Modes must be unit eigenvectors, not displaced meshes or vectors multiplied
  by square-root eigenvalues. Keep the same sign conventions as the score export.
- `scores.csv` has columns `case_id,pc1,pc2,pc3,...`. If Studio exports `name` and
  `p0,p1,p2,...`, rename these columns correspondingly. Use the names assigned
  in the input workbook. Do not infer correspondence by sorting rows separately.
- If mean domains are named `T__1` ... `T__15`, map them by domain number:
  1–12 mean T1–T12, 13 means L1, 14 L2, and 15 L3.
- Export raw scores as floating point, preserving precision.

Run `python scripts/03_import_pca_exports.py --modes 3`. The provided adapter
checks dimensions, IDs, finite values and eigenvector orthonormality, then writes
`outputs/pca.npz`. It does not solve the reconstruction exercise.

Before regression, verify one actual-score reconstruction against its exported
particles visually. It should share the same frame and anatomical ordering.
With only K modes, a difference caused by PCA truncation is expected. A reflected,
rotated or scrambled spine indicates an export/coordinate issue instead.

## References

- [Studio workflow](https://sciinstitute.github.io/ShapeWorks/latest/studio/getting-started-with-studio.html)
- [Optimization parameters](https://sciinstitute.github.io/ShapeWorks/workflow/parameters.html)
- [Raw score and mode convention, ShapeWorks support](https://shapeworks.discourse.group/t/orthogonal-shape-vectors/54)
- [PLSRegression API](https://scikit-learn.org/stable/modules/generated/sklearn.cross_decomposition.PLSRegression.html)
