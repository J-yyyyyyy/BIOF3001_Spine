"""Provided split/CV/report plumbing; implement Exercise 3 to fit the regressor.

The fixed split evaluates regression within a SHARED SSM. It is not an external
validation of the whole shape-model pipeline. See the exercise instructions.
"""
import numpy as np
import joblib
from sklearn.model_selection import KFold
from common import OUTPUT, manifest, read_centres, save_json
from student_tasks import landmark_features, fit_pls, predict_scores
def main():
    pca=np.load(OUTPUT/'pca.npz',allow_pickle=False)
    ids=pca['case_ids']; y=pca['scores']
    split={r['case_id']:r['regression_split'] for r in manifest()}
    if any(c not in split for c in ids): raise ValueError('PCA case IDs must match the package manifest')
    x=landmark_features(np.stack([read_centres(c) for c in ids]))
    train=np.array([split[c]=='train' for c in ids]); test=~train
    if train.sum()<6 or test.sum()<1:
        raise ValueError('Use the full cohort exports for PLS, not the small GUI demo')
    cv=list(KFold(n_splits=3,shuffle=True,random_state=42).split(x[train]))
    candidates=[n for n in [1,2,3,5,8] if n<min(len(a) for a,b in cv) and n<=x.shape[1]]
    trials=[]
    for n in candidates:
        errors=[]
        for a,b in cv:
            model=fit_pls(x[train][a],y[train][a],n)
            predicted=np.asarray(predict_scores(model,x[train][b]))
            if predicted.shape!=y[train][b].shape: raise ValueError('Prediction shape mismatch')
            errors.append(float(np.mean((predicted-y[train][b])**2)))
        trials.append(dict(pls_components=n,cv_rmse=float(np.sqrt(np.mean(errors)))))
    best=min(trials,key=lambda t:t['cv_rmse'])
    model=fit_pls(x[train],y[train],best['pls_components'])
    pred=np.asarray(predict_scores(model,x[test]))
    if pred.shape!=y[test].shape: raise ValueError('Prediction shape mismatch')
    baseline=np.broadcast_to(y[train].mean(0),y[test].shape)
    save_json(OUTPUT/'regression_report.json',dict(cv=trials,selected=best,
        test_rmse=float(np.sqrt(np.mean((pred-y[test])**2))),
        mean_score_baseline_rmse=float(np.sqrt(np.mean((baseline-y[test])**2))),
        training_cases=ids[train].tolist(),test_cases=ids[test].tolist(),
        scope='Regression holdout within a shared SSM; not external pipeline validation'))
    np.savez(OUTPUT/'predicted_scores.npz',case_ids=ids[test],predicted=pred,actual=y[test])
    # Keep this estimator and its PCA basis together for the provided live viewer.
    # The viewer calls the same student feature/prediction/reconstruction functions.
    joblib.dump(dict(model=model,mean=pca['mean'],modes=pca['modes'],
        case_ids=ids,centres=np.stack([read_centres(c) for c in ids]),
        default_case=str(ids[test][0]),schema_version=1),OUTPUT/'interactive_model.joblib')
    print('Saved predictions and regression_report.json')
    print('Saved interactive_model.joblib; after Exercise 4, run scripts/07_interactive.py')
if __name__=='__main__': main()
