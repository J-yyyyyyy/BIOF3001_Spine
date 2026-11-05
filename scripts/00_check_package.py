"""Provided file-integrity check; no exercise implementation required."""
import argparse, hashlib, json
import numpy as np
from common import ROOT, LEVELS, manifest
def main():
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument('--hashes',action='store_true')
    args=parser.parse_args()
    if not (ROOT/'data/cases.csv').is_file():
        parser.exit(1,'Data not installed. See DATA_DOWNLOAD.md: download BIOF3001_Data.zip and place its data folder alongside scripts.\n')
    rows=manifest()
    for row in rows:
        for key in ['mask','transform','merged_mesh']:
            assert (ROOT/row[key]).is_file(),row[key]
        for level in LEVELS: assert (ROOT/'data/meshes'/row['case_id']/f'{level}.ply').is_file()
        transform=np.asarray(json.loads((ROOT/row['transform']).read_text())['world_ras_to_aligned'])
        assert transform.shape==(4,4) and np.isfinite(transform).all()
    if args.hashes:
        for line in (ROOT/'SHA256SUMS.txt').read_text().splitlines():
            expected,relative=line.split('  ',1)
            digest=hashlib.sha256()
            with (ROOT/relative).open('rb') as f:
                for chunk in iter(lambda:f.read(1024*1024),b''): digest.update(chunk)
            assert digest.hexdigest()==expected,relative
    print(f'Checked {len(rows)} cases, {len(rows)*15} individual meshes; CT volumes are not included.')
if __name__=='__main__': main()
