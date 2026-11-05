# Download the workshop data

The data are a separate download because Moodle has a 100 MB upload limit.

1. Download `BIOF3001_Moodle_Code.zip` from Moodle and extract it. You should have
   a folder called `BIOF3001_Spine_Workshop` containing `scripts` and `instructions`.
2. Open the **Workshop data (HKU OneDrive)** link supplied on Moodle. Sign in with
   your HKU account if requested and download `BIOF3001_Data.zip` (about 435 MB).
3. Extract the data ZIP. Copy its **`data` folder** into `BIOF3001_Spine_Workshop`,
   alongside `scripts`. Do not put it inside `scripts` or `outputs`.

The result should look like this:

```text
BIOF3001_Spine_Workshop/
    data/
        masks/
        meshes/
        merged_spines/
        transforms/
        cases.csv
        cohort_audit.csv
        label_map.csv
    scripts/
    instructions/
    templates/
    outputs/
    README.md
    requirements.txt
    SHA256SUMS.txt
```

Then follow the Python setup in `README.md` and run:

```powershell
python scripts/00_check_package.py --hashes
```

It should report **71 cases and 1,065 individual meshes**. The hash check verifies
that the downloaded files match the supplied dataset. Keep `DATA_SOURCES.md` for
the data attribution. The download includes segmentation masks, not CT images.

You download the data only once. Keep the code and data together when moving the
project to another folder. No completed answers or trained models are included.
