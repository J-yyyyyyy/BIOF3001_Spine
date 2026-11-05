# See your own model respond to landmark edits

This interface is provided. There are no additional assessed GUI functions.
Complete the existing feature, PLS prediction and particle reconstruction TODOs.
The viewer calls those functions whenever you edit a coordinate.

## Prepare and launch

From the package folder, using the same Python environment as your training:

```powershell
python -m pip install -r requirements_interactive.txt
python scripts/04_train_pls.py
python scripts/05_reconstruct.py
python scripts/07_interactive.py
```

Training saves `outputs/interactive_model.joblib`: the fitted estimator, its PCA
mean and modes, and the cohort's aligned landmarks. The PCA exports and centroids
must already exist. No pretrained answer model is included in this package.
Load only model bundles you created or trust; joblib files contain Python objects.

The first held-out case is selected by default. To start with another case:

```powershell
python scripts/07_interactive.py --case sub-verse502
```

Choose a case included in your imported PCA cohort. Restart with `--case` to switch.

## Interact

1. The left panel lists T1 through L3. Edit X, Y or Z with the numeric field or
   slider. Values are **aligned millimetres**. Start with small changes of 1–5 mm.
2. The middle view shows the input landmarks and connecting curve. The right view
   shows the predicted 3,840 particles, coloured by vertebral level. Rotate and
   zoom the 3D views using the mouse.
3. The displayed raw PC scores update with the particles. Updates are scheduled
   after a 40 ms pause in editing; rendering speed depends on your computer.
4. Use the vertebral checkboxes to inspect individual levels. Reset restores
   the starting landmarks. Save PLY exports all 15 predicted vertebrae, including
   hidden ones, as a point cloud. It does not export a triangulated mesh.

The live path is:

`edited landmarks → your landmark_features → your predict_scores → your reconstruct_particles → display`

There is no retraining during interaction. The viewer reuses the fitted model.
It does not use the weights or curve-length normalization of the research demo.
If you change feature preprocessing, retrain before launching the viewer again.

## Interpretation

A change to one centre can affect several vertebrae because PCA modes describe
coordinated variation across the spine. The output is a statistical prediction;
it is not constrained to pass exactly through your edited centres. Large edits
may leave the range represented by the training cohort.

The input is in the supplied aligned frame and the particles use your PCA export
frame. Keep the course alignment settings consistent. The two separate views do
not establish that an overlay is valid after additional ShapeWorks transforms.

Edits explore model behaviour. They do not provide new ground truth or measure
test accuracy. Use the fixed held-out evaluation and `06_visualize.py` for the
comparison with actual-score reconstructions.

## Without a desktop / troubleshooting

```powershell
python scripts/07_interactive.py --headless --output outputs/live_check.ply
```

This runs the same prediction path without Qt or PyVista. Missing model: rerun
`04_train_pls.py`. TODO error: complete the named function. Missing GUI module:
install the optional requirements in the same environment. Keep the saved model
in its training environment; rerun training after changing scikit-learn versions.
