"""Small synthetic checks. Missing TODOs are reported as NOT IMPLEMENTED."""
import numpy as np
import student_tasks as task
from common import ROOT, OUTPUT, manifest
def main():
    checks=[]
    def centroid():
        m=np.zeros((5,7,9),dtype=np.uint8); m[1:3,2:4,4:6]=8
        np.testing.assert_allclose(task.label_centroid_ijk(m,8),[1.5,2.5,4.5])
        try: task.label_centroid_ijk(m,9)
        except ValueError: return
        raise AssertionError('Missing labels must raise ValueError')
    def affine():
        m=np.array([[0,-2,0,10],[3,0,0,-2],[0,0,4,1],[0,0,0,1]])
        np.testing.assert_allclose(task.apply_affine(np.array([[1,2,3],[0,0,0]]),m),[[6,1,13],[10,-2,1]])
    def paths():
        case=manifest()[0]['case_id']; row=task.mesh_row(case,ROOT,OUTPUT)
        assert len(row)==17 and row[0]==case
        assert [__import__('pathlib').Path(p).stem for p in row[2:]]==[f'T{i}' for i in range(1,13)]+['L1','L2','L3']
        assert all((OUTPUT/p).is_file() for p in row[2:])
    def features():
        x=np.arange(90).reshape(2,15,3)
        expected=np.array([list(range(45)),list(range(45,90))])
        np.testing.assert_array_equal(task.landmark_features(x),expected)
    def pls():
        x=np.arange(20,dtype=float).reshape(-1,1); y=np.c_[2*x[:,0]+3,-x[:,0]]
        model=task.fit_pls(x,y,1)
        np.testing.assert_allclose(task.predict_scores(model,x),y,atol=1e-5)
    def pca():
        mean=np.zeros((3840,3)); modes=np.zeros((2,11520)); modes[0,0]=1; modes[1,1]=1
        out=task.reconstruct_particles(np.array([[0,0],[2,-3]]),mean,modes)
        assert out.shape==(2,3840,3)
        np.testing.assert_allclose(out[0],mean); np.testing.assert_allclose(out[1,0],[2,-3,0])
    failed=0
    for name,fn in [('1A centroid',centroid),('1B affine',affine),('2 paths',paths),('3A features',features),('3B/C PLS',pls),('4 PCA',pca)]:
        try: fn(); print(name,': PASS')
        except NotImplementedError: print(name,': NOT IMPLEMENTED'); failed+=1
        except Exception as e: print(name,': FAIL:',e); failed+=1
    return int(failed>0)
if __name__=='__main__': raise SystemExit(main())
