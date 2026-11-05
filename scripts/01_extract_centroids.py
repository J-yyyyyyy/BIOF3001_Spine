"""Load masks and provided transforms, call Exercise 1, save ordered centres."""
import argparse, json
import nibabel as nib
import numpy as np
from scipy.ndimage import find_objects
from common import ROOT, OUTPUT, LEVELS, LABELS, manifest, save_json
from student_tasks import label_centroid_ijk, apply_affine
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case',help='One case ID; omit to process the cohort')
    args=parser.parse_args()
    rows=[r for r in manifest() if args.case is None or r['case_id']==args.case]
    if not rows: raise ValueError('Unknown case ID')
    for row in rows:
        case=row['case_id']; image=nib.load(ROOT/row['mask'])
        mask=np.asarray(image.dataobj)
        # Locate each label once, then give the student function a small crop.
        # Some supplied masks store integer labels as float64. Validate before
        # conversion rather than silently rounding noninteger segmentation data.
        if not np.isfinite(mask).all() or mask.min()<0 or mask.max()>32767:
            raise ValueError('Expected nonnegative finite segmentation labels <= 32767')
        labels=mask.astype(np.int16)
        if not np.array_equal(mask,labels):
            raise ValueError('Segmentation labels must be integers')
        del mask
        boxes=find_objects(labels,max_label=max(LABELS))
        indices=[]
        for label in LABELS:
            box=boxes[label-1]
            if box is None: raise ValueError(f'{case}: label {label} is absent')
            offset=np.array([s.start for s in box])
            indices.append(label_centroid_ijk(labels[box],label)+offset)
        indices=np.stack(indices)
        world=apply_affine(indices,image.affine)
        metadata=json.loads((ROOT/row['transform']).read_text())
        aligned=apply_affine(world,np.asarray(metadata['world_ras_to_aligned']))
        if aligned.shape!=(15,3) or not np.isfinite(aligned).all():
            raise ValueError('Centres must be finite and have shape (15,3)')
        save_json(OUTPUT/'centroids'/f'{case}.json',dict(case_id=case,levels=LEVELS,
            voxel_ijk=indices.tolist(),world_ras_mm=world.tolist(),aligned_mm=aligned.tolist()))
        print('Saved',case,flush=True)
if __name__=='__main__': main()
