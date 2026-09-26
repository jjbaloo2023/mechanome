# Raw and annotated data for Shape2Fate

## Overview

This archive contains live-cell time-lapse TIRF-SIM datasets used in the development of Shape2Fate. Each dataset includes raw SIM data (all phases/orientations/frames in a single file). Depending on the experiment, additional files include SIM reconstructions (`-recon`), binary masks (`-mask.tif`), and manual annotations (`-annotations.csv`).  
Unless noted otherwise, data is provided in `.dv` format.

This dataset is related to the following paper:  
Shape2Fate: a morphology-aware deep learning framework for tracking endocytic and exocytic carriers in super-resolution TIRF-SIM. 



## Biological systems

Datasets were acquired from engineered mammalian cell lines expressing fluorescent reporters of clathrin-mediated endocytosis and cargo exocytosis. The following reporters are represented: EGFP-CLCa, SNAP-CLCa (JF-dye labelled), SBP-mEmerald-LAMP1, pHluorin-GLUT4, and Dynamin2-mRuby3.  
RUSH assays (`_STIM`) were stimulated with biotin; adipocyte GLUT4 datasets (`_STIM`) were stimulated with insulin. Further methodological details are provided in the associated manuscript.



## Imaging

Most TIRF-SIM experiments were carried out at the Micron Bioimaging Facility, University of Oxford, using a DeltaVision OMX SR inverted wide-field microscope equipped with a 60× 1.5-NA TIRF UPLAPO oil-immersion objective (Olympus) and a PCO Edge 4.2 sCMOS camera. Acquisition parameters are stored in the raw files metadata.



## Channel registration

Multicolour datasets were registered using 0.1 µm TetraSpeck™ fluorescent microspheres imaged under identical conditions as the experimental datasets. Registration was performed using the sub-pixel alignment method of Thevenaz et al. (IEEE Trans. Image Process., 1998; doi: 10.1109/83.650848), applying a similarity (scaled rotation) transformation. For each dataset, a corresponding transformation matrix is provided (`registration_transform.json`), mapping coordinates from the target channel to the source channel (i.e., inverse transform).



## Masks

Each image file is accompanied by a corresponding binary mask that delineates the in-focus, well-adhered regions of cells within the field of view. These masks were used to restrict all quantitative analyses to areas containing reliably imaged cells.



## Dataset groups  
Below is a summary of the included datasets:

| Dataset | Cell type | Format | Extras |
| :---- | :---- | :---- | :---- |
| Adipocytes-CME coupling | 3T3-L1 adipocytes pHluorin-GLUT4 SNAP-CLCa | `.dv` | Separate CME channel (`_subset`), Exocytosis productivity annotations, Masks |
| CME tracking testing | RPE-1 EGFP-CLCa | `.nd2` | Reconstruction, Tracking annotations |
| CME tracking validation | RPE-1 EGFP-CLCa | `.mrc` | Reconstruction, 3x tracking annotations |
| Dynamin productivity validation | RPE-1 Dyn2-mRuby3 SNAP-CLCa | `.dv` | Masks |
| Exocytosis tracking validation | HeLa SBP-mEmerald-LAMP1 | `.dv` | Reconstruction, Tracking annotations |
| RUSH-CME global coupling | SH-SY5Y SNAP-CLCa | `.dv` | Masks |
| RUSH-CME local coupling | SH-SY5Y SBP-mEmerald-LAMP1 SNAP-CLCa | `.dv` | Separate CME channel (`_subset`), Exocytosis productivity annotations, Masks |

