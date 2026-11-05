"""Provided visualization: compare predicted and actual-score particles.

Extension: overlay original meshes only after verifying that their frame equals
the exported PCA frame. Additional ShapeWorks transforms must not be ignored.
"""
import argparse
import numpy as np
import matplotlib.pyplot as plt
from common import OUTPUT, LEVELS
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case'); parser.add_argument('--no-show',action='store_true')
    args=parser.parse_args(); data=np.load(OUTPUT/'reconstructions.npz',allow_pickle=False)
    ids=data['case_ids']; idx=0 if args.case is None else list(ids).index(args.case)
    fig=plt.figure(figsize=(12,7))
    all_points=np.vstack([data['predicted'][idx],data['actual'][idx]])
    mid=(all_points.max(0)+all_points.min(0))/2; radius=np.ptp(all_points,axis=0).max()/2
    for panel,(key,title) in enumerate([('predicted','Predicted scores'),('actual','Actual scores')],1):
        ax=fig.add_subplot(1,2,panel,projection='3d'); points=data[key][idx]
        for i,level in enumerate(LEVELS):
            p=points[i*256:(i+1)*256]
            ax.scatter(*p.T,s=2,color=plt.get_cmap('tab20')(i),label=level)
        ax.set(xlabel='X (mm)',ylabel='Y (mm)',zlabel='Z (mm)',title=title,
               xlim=(mid[0]-radius,mid[0]+radius),ylim=(mid[1]-radius,mid[1]+radius),zlim=(mid[2]-radius,mid[2]+radius))
        ax.set_box_aspect((1,1,1))
    ax.legend(loc='upper left',bbox_to_anchor=(1.02,1),markerscale=3,fontsize=8)
    fig.suptitle(str(ids[idx])); fig.tight_layout()
    target=OUTPUT/f'{ids[idx]}_comparison.png'; fig.savefig(target,dpi=160,bbox_inches='tight'); print(target)
    if not args.no_show: plt.show()
if __name__=='__main__': main()
