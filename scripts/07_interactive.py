"""Provided real-time viewer. Complete student_tasks.py first; no GUI TODOs.

Uses your saved PLS estimator and PCA basis, not the research demo weights.
Input: aligned millimetres, T1–L3. See instructions/05_interactive.md.
"""
from pathlib import Path
import argparse
import sys
import joblib
import numpy as np
from common import OUTPUT, LEVELS
from student_tasks import landmark_features, predict_scores, reconstruct_particles

SEGMENTS = tuple(LEVELS)
COLORS = ("#0B1026", "#0E1E41", "#123A6F", "#165792", "#1B6FAE",
          "#228CC3", "#37B7D6", "#62D5DA", "#8FE6C3", "#C2F0B3",
          "#F4F1A1", "#FEE07A", "#FDBA4A", "#F36B3E", "#C81D4F")

class StudentSpineModel:
    def __init__(self, path):
        # Load only model files produced by your own training script.
        data = joblib.load(path)
        if data.get('schema_version') != 1:
            raise ValueError('Unknown model format; rerun 04_train_pls.py.')
        self.model = data['model']
        self.mean = np.asarray(data['mean'])
        self.modes = np.asarray(data['modes'])
        self.case_ids = list(map(str, data['case_ids']))
        self.centres = np.asarray(data['centres'])
        self.default_case = data['default_case']
        if (self.mean.shape != (3840, 3) or self.modes.ndim != 2
                or self.modes.shape[1] != 11520 or self.modes.shape[0] < 1
                or self.centres.shape != (len(self.case_ids), 15, 3)
                or self.default_case not in self.case_ids
                or not all(np.isfinite(a).all() for a in (self.mean,self.modes,self.centres))):
            raise ValueError('Inconsistent model bundle; rerun training.')

    def predict(self, keypoints):
        keypoints = np.asarray(keypoints, dtype=float)
        if keypoints.shape != (15, 3) or not np.isfinite(keypoints).all():
            raise ValueError('Expected finite (15,3) aligned landmarks in millimetres.')
        # Identical preprocessing to training; do not normalize the curve here.
        features = landmark_features(keypoints[None, ...])
        scores = np.asarray(predict_scores(self.model, features))
        if scores.shape != (1, len(self.modes)) or not np.isfinite(scores).all():
            raise ValueError('predict_scores must return finite (1,K) scores.')
        particles = np.asarray(reconstruct_particles(scores, self.mean, self.modes))
        if particles.shape != (1,3840,3) or not np.isfinite(particles).all():
            raise ValueError('reconstruct_particles must return finite (1,3840,3).')
        return scores[0], particles[0]

    def split(self, particles):
        return np.split(particles, 15)

def save_particles(path, particles):
    """Write an ASCII PLY that opens in standard point-cloud viewers."""
    path = Path(path).expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="ascii", newline="\n") as output:
        output.write("ply\nformat ascii 1.0\n")
        output.write(f"element vertex {len(particles)}\n")
        output.write("property double x\nproperty double y\nproperty double z\nend_header\n")
        np.savetxt(output, particles, fmt="%.12g")
    return path


def launch_gui(model, keypoints, output_path):
    # GUI dependencies are deliberately optional for CLI/headless use.
    from PyQt5 import QtCore, QtWidgets
    import pyvista as pv
    from pyvistaqt import QtInteractor

    class CurveAndPCQtApp(QtWidgets.QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("BIOF3001 — your landmark-to-spine model")
            self.resize(1400, 850)
            self.keypoints = keypoints.copy()
            self.initial_keypoints = keypoints.copy()
            self.controls = []
            self.actors = []
            central = QtWidgets.QWidget()
            self.setCentralWidget(central)
            layout = QtWidgets.QHBoxLayout(central)
            panel = QtWidgets.QWidget()
            panel.setMaximumWidth(480)
            panel_layout = QtWidgets.QVBoxLayout(panel)
            for text in ("15 aligned landmarks (T1–L3): edit X / Y / Z in mm",
                         "Your PLS + PCA model • edits explore predictions, not test accuracy"):
                label = QtWidgets.QLabel(text)
                label.setWordWrap(True)
                panel_layout.addWidget(label)
            scroll = QtWidgets.QScrollArea()
            scroll.setWidgetResizable(True)
            fields = QtWidgets.QWidget()
            grid = QtWidgets.QGridLayout(fields)
            for j, text in enumerate(("Point", "X", "Y", "Z")):
                grid.addWidget(QtWidgets.QLabel(text), 0, j)
            # Slider ticks represent 0.01 mm; coordinates remain in the training frame.
            lower = keypoints.min(axis=0) - 30.0
            upper = keypoints.max(axis=0) + 30.0
            self.timer = QtCore.QTimer(self)
            self.timer.setSingleShot(True)
            self.timer.setInterval(40)
            self.timer.timeout.connect(self.update_views)
            for i, name in enumerate(SEGMENTS):
                grid.addWidget(QtWidgets.QLabel(name), i + 1, 0)
                for j in range(3):
                    cell = QtWidgets.QWidget()
                    cell_layout = QtWidgets.QVBoxLayout(cell)
                    cell_layout.setContentsMargins(0, 0, 0, 0)
                    spin = QtWidgets.QDoubleSpinBox()
                    spin.setMinimumWidth(0)
                    spin.setDecimals(2)
                    spin.setRange(float(lower[j]), float(upper[j]))
                    spin.setSingleStep(0.1)
                    spin.setValue(float(keypoints[i, j]))
                    slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
                    slider.setMinimumWidth(0)
                    slider.setRange(int(np.floor(lower[j] * 100)), int(np.ceil(upper[j] * 100)))
                    slider.setValue(int(round(keypoints[i, j] * 100)))
                    slider.valueChanged.connect(
                        lambda value, p=i, c=j: self.edit_point(p, c, value / 100))
                    spin.valueChanged.connect(
                        lambda value, p=i, c=j: self.edit_point(p, c, value))
                    cell_layout.addWidget(spin)
                    cell_layout.addWidget(slider)
                    grid.addWidget(cell, i + 1, j + 1)
                    self.controls.append((spin, slider))
            scroll.setWidget(fields)
            panel_layout.addWidget(scroll)
            buttons = QtWidgets.QHBoxLayout()
            for title, callback in (("Reset", self.reset_keypoints), ("Save PLY…", self.save_current)):
                button = QtWidgets.QPushButton(title)
                button.clicked.connect(callback)
                buttons.addWidget(button)
            panel_layout.addLayout(buttons)
            visibility = QtWidgets.QGroupBox("Visible vertebrae")
            checks = QtWidgets.QGridLayout(visibility)
            self.checkboxes = []
            for i, name in enumerate(SEGMENTS):
                checkbox = QtWidgets.QCheckBox(name)
                checkbox.setChecked(True)
                checkbox.toggled.connect(self.update_visibility)
                checks.addWidget(checkbox, i // 5, i % 5)
                self.checkboxes.append(checkbox)
            panel_layout.addWidget(visibility)
            self.status = QtWidgets.QLabel()
            self.status.setWordWrap(True)
            panel_layout.addWidget(self.status)
            layout.addWidget(panel, 2)
            # Render explicitly on edits rather than running two idle render timers.
            self.left = QtInteractor(central, auto_update=False, multi_samples=0)
            self.right = QtInteractor(central, auto_update=False, multi_samples=0)
            for plotter in (self.left, self.right):
                plotter.set_background("white")
                plotter.add_axes()
                layout.addWidget(plotter, 2)
            self.status.setText("Preparing predicted particles...")

        def initialize_views(self):
            # The native render windows must be visible before the first scene render.
            print("Initializing 3D views...", flush=True)
            self.update_views(initial=True)
            print("3D views ready: input landmarks on the left, prediction on the right.",
                  flush=True)

        def edit_point(self, point, coordinate, value):
            self.keypoints[point, coordinate] = value
            spin, slider = self.controls[point * 3 + coordinate]
            for widget in (spin, slider):
                widget.blockSignals(True)
            spin.setValue(float(value))
            slider.setValue(int(round(value * 100)))
            for widget in (spin, slider):
                widget.blockSignals(False)
            self.timer.start()

        def reset_keypoints(self):
            for i in range(15):
                for j in range(3):
                    self.edit_point(i, j, self.initial_keypoints[i, j])

        def update_visibility(self):
            for actor, checkbox in zip(self.actors, self.checkboxes):
                actor.SetVisibility(checkbox.isChecked())
            self.right.render()

        def update_views(self, initial=False):
            try:
                scores, particles = model.predict(self.keypoints)
            except ValueError as error:
                self.status.setText(str(error))
                return
            if initial:
                self.keypoint_cloud = pv.PolyData(self.keypoints.copy())
                self.curve = pv.lines_from_points(self.keypoints)
                # Plain GL points avoid sphere-impostor shader issues on some drivers.
                self.left.add_points(self.keypoint_cloud, color="crimson", point_size=10,
                                     render_points_as_spheres=False, render=False)
                self.left.add_mesh(self.curve, color="gray", line_width=2, render=False)
                self.left.add_text("Input landmarks (aligned mm)", font_size=10, color="black", render=False)
                self.right.add_text("Predicted particles (PCA frame, mm)", font_size=10, color="black", render=False)
                self.clouds = []
                for points, color in zip(model.split(particles), COLORS):
                    cloud = pv.PolyData(points.copy())
                    self.clouds.append(cloud)
                    self.actors.append(self.right.add_points(
                        cloud, color=color, point_size=5, render_points_as_spheres=False,
                        render=False))
                for plotter in (self.left, self.right):
                    plotter.view_yz()
                    plotter.reset_camera()
            else:
                self.keypoint_cloud.points = self.keypoints.copy()
                self.curve.points = self.keypoints.copy()
                for cloud, points in zip(self.clouds, model.split(particles)):
                    cloud.points = points.copy()
            self.left.render()
            self.right.render()
            self.status.setText(f"{len(particles):,} particles • PCs: " +
                                ", ".join(f"{value:.3f}" for value in scores))

        def save_current(self):
            filename, _ = QtWidgets.QFileDialog.getSaveFileName(
                self, "Save all 15 reconstructed vertebrae", str(output_path), "Point cloud (*.ply)")
            if filename:
                try:
                    _, particles = model.predict(self.keypoints)
                    path = save_particles(filename, particles)
                    self.status.setText(f"Saved all 15 vertebrae: {path}")
                except (OSError, ValueError) as error:
                    self.status.setText(f"Save failed: {error}")

        def closeEvent(self, event):
            self.timer.stop()
            self.left.close()
            self.right.close()
            event.accept()

    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([sys.argv[0]])
    window = CurveAndPCQtApp()
    window.show()
    QtCore.QTimer.singleShot(0, window.initialize_views)
    return app.exec_()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model',type=Path,default=OUTPUT/'interactive_model.joblib')
    parser.add_argument('--case',help='Start from this case; defaults to the first held-out case')
    parser.add_argument('--headless',action='store_true',help='Export without GUI dependencies')
    parser.add_argument('--output',type=Path,default=OUTPUT/'interactive_particles.ply')
    args=parser.parse_args(argv)
    try:
        model=StudentSpineModel(args.model)
        case=args.case or model.default_case
        if case not in model.case_ids:
            raise ValueError(f'Unknown case {case}; use a case from the PCA cohort.')
        points=model.centres[model.case_ids.index(case)].copy()
        scores,particles=model.predict(points)
        print(f'Starting case: {case}; aligned input in mm; {len(scores)} PCA scores')
        if args.headless:
            print(save_particles(args.output,particles))
            print('PC scores:',scores)
            return 0
        return launch_gui(model,points,args.output)
    except ImportError as error:
        parser.exit(1,f'{error}\nInstall requirements_interactive.txt for the GUI, or use --headless.\n')
    except NotImplementedError as error:
        parser.exit(1,f'{error}\nComplete Exercises 3 and 4 in student_tasks.py first.\n')
    except (OSError,ValueError,KeyError) as error:
        parser.exit(1,f'{error}\nRun 04_train_pls.py after completing your functions and PCA import.\n')

if __name__=='__main__':
    sys.exit(main())
