"""Exercise 4: reconstruct test shapes and export particles by vertebral level."""
import numpy as np
from common import OUTPUT, LEVELS, save_json
from student_tasks import reconstruct_particles
def main():
    pca=np.load(OUTPUT/'pca.npz',allow_pickle=False)
    predictions=np.load(OUTPUT/'predicted_scores.npz',allow_pickle=False)
    predicted=reconstruct_particles(predictions['predicted'],pca['mean'],pca['modes'])
    actual=reconstruct_particles(predictions['actual'],pca['mean'],pca['modes'])
    expected=(len(predictions['case_ids']),3840,3)
    if predicted.shape!=expected or actual.shape!=expected: raise ValueError(f'Expected {expected}')
    if not np.isfinite(predicted).all(): raise ValueError('Non-finite reconstruction')
    np.savez(OUTPUT/'reconstructions.npz',case_ids=predictions['case_ids'],predicted=predicted,actual=actual)
    errors=[]
    for case,points,reference in zip(predictions['case_ids'],predicted,actual):
        folder=OUTPUT/'particles'/case; folder.mkdir(parents=True,exist_ok=True)
        for i,level in enumerate(LEVELS):
            np.savetxt(folder/f'{level}.particles',points[i*256:(i+1)*256],fmt='%.6f')
        errors.append(dict(case_id=str(case),mean_particle_error_mm=float(np.linalg.norm(points-reference,axis=1).mean())))
    save_json(OUTPUT/'particle_errors.json',errors)
    print('Saved particles; errors compare predicted vs actual-score reconstruction, not ground-truth surface')
if __name__=='__main__': main()
