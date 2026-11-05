"""Fill the supplied single-row workbook using Exercise 2."""
import argparse
import hashlib
import os
from pathlib import Path
import shutil
from openpyxl import load_workbook
from common import ROOT, OUTPUT, manifest
from student_tasks import mesh_row
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--subset',choices=['demo','all'],default='demo')
    parser.add_argument('--unique-mesh-names', action='store_true',
                        help='Copy meshes with case IDs to avoid particle filename collisions')
    args=parser.parse_args()
    rows=manifest()
    if args.subset=='demo': rows=[r for r in rows if r['demo']=='1']
    suffix='_unique' if args.unique_mesh_names else ''
    path=OUTPUT/f'shapeworks_{args.subset}{suffix}.xlsx'
    wb=load_workbook(ROOT/'templates/shapeworks_example.xlsx'); ws=wb['data']
    ws.delete_rows(2,ws.max_row)
    for row in rows:
        values=mesh_row(row['case_id'],ROOT,path.parent)
        if len(values)!=17: raise ValueError('Expected name, notes and 15 mesh paths')
        if args.unique_mesh_names:
            # Studio can derive particle filenames from mesh basenames.
            # Preserve original data; give each copied input a globally unique name.
            for index, relative in enumerate(values[2:], start=2):
                source=path.parent/relative
                target=OUTPUT/'shapeworks_inputs'/row['case_id']/f"{row['case_id']}_{source.name}"
                target.parent.mkdir(parents=True, exist_ok=True)
                if not target.exists():
                    shutil.copy2(source, target)
                if hashlib.sha256(source.read_bytes()).digest()!=hashlib.sha256(target.read_bytes()).digest():
                    raise ValueError(f'Copied mesh differs from source: {target}')
                values[index]=Path(os.path.relpath(target, path.parent)).as_posix()
        ws.append(values)
    wb.save(path); print(path)
if __name__=='__main__': main()
