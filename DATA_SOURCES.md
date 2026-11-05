# Data sources and attribution

The segmentation masks are from the locally held VerSe collection. This package
contains an unchanged subset of mask files and derived vertebral surface meshes
prepared in Pengyu Lu's previous work. It contains no CT intensity images.
The derived meshes were extracted, remeshed and aligned before this workshop.
Coordinate transform metadata was recovered and checked during packaging.
The original acquisition/restructuring history of the local collection was not
independently reconstructed from download logs.

The [VerSe project](https://github.com/anjany/verse) identifies its data license as
[Creative Commons Attribution-ShareAlike 4.0](https://creativecommons.org/licenses/by-sa/4.0/).
Retain this attribution and the license link when sharing these masks and derived
data. The repository's MIT code license is separate from its data license.

References requested by the VerSe project:

- Sekuboyina et al. (2021), *VerSe: A Vertebrae Labelling and Segmentation Benchmark
  for Multi-detector CT Images*. Medical Image Analysis.
  https://doi.org/10.1016/j.media.2021.102166
- Löffler et al. (2020), *A Vertebral Segmentation Dataset with Fracture Grading*.
  Radiology: Artificial Intelligence. https://doi.org/10.1148/ryai.2020190138
- Liebl, Schinz et al., *A Computed Tomography Vertebral Segmentation Dataset with
  Anatomical Variations and Multi-Vendor Scanner Data*.
  https://arxiv.org/abs/2103.06360

`data/cohort_audit.csv` records inclusion and screening measurements.
`SHA256SUMS.txt` records checksums of the distributed data and workbook template.
