# Package preparation checks

- Screened all 86 source cases for required labels, mask boundary contact,
  paired per-level meshes and recovered coordinate transforms.
- Included 71 cases and excluded 15 with target labels on a scan boundary.
- Checked 1,065 per-level mesh paths and 71 merged-spine/mask/transform sets.
- Verified that a common affine reproduces the original-to-aligned mesh vertices
  to less than 0.00001 mm, and that mapped mask centroids lie within the original
  per-level mesh bounds (3 mm tolerance).
- Opened and inspected the exported Excel example and checked generated full
  workbook paths for all 71 cases.
- Ran six synthetic exercise checks with temporary reference implementations.
- Ran the centroid driver on one real mask and checked its aligned centres.
- Ran the export adapter, split/CV driver, reconstruction and plotting together
  with synthetic PCA exports. This checks software plumbing, not model accuracy.
- Confirmed all seven student TODO functions remain unimplemented.

The exercise smoke test used the existing local Python 3.8.19 environment:
NumPy 1.24.4, SciPy 1.10.0, nibabel 3.2.1, scikit-learn 1.3.2, pandas 2.0.3,
openpyxl 3.1.5 and matplotlib 3.7.5. The setup guide recommends a newer Python
environment for students; a fresh installation of those newer dependency
resolutions has not been tested during packaging.

ShapeWorks GUI import/optimization was not run during this preparation. The
Excel schema follows the existing project and official documentation. No
pretrained regressor, completed exercise solutions, or optimized PCA outputs
are included. The instructor should rehearse the GUI workflow on the target
teaching machines and record the chosen ShapeWorks version/settings.

The automated screening does not replace visual anatomical quality control.
The original mesh extraction may introduce surface approximation errors.
