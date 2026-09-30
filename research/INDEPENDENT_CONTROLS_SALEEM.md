# Saleem et al. (2015): independent-control audit

## Scope and sources

Primary article: Saleem *et al.*, *Nature Communications* 6, 6249 (2015), DOI [10.1038/ncomms7249](https://doi.org/10.1038/ncomms7249), PMCID [PMC4346611](https://pmc.ncbi.nlm.nih.gov/articles/PMC4346611/), PMID [25695735](https://pubmed.ncbi.nlm.nih.gov/25695735/). I used the public article and its linked publisher/PMC records only. The linked `ncomms7249-s1.pdf` is 8.9 MB, above the registered 2 MB bound, so it was recorded but not downloaded or inspected.

## Source-derived account (158 words)

Saleem et al. reconstituted AP180/clathrin on GUVs and varied osmotic conditions. In Fig. 1, fluorescence and EM distinguish vesicles with large, small, or no visible deformation; Fig. 5 changes membrane composition to make a higher-rigidity GUV; its caption reports failed AP180/clathrin binding in key osmotic conditions. The Results model (Fig. 3a–c) treats a bud’s tension, bending rigidity, polymerization energy and coat line tension. For Fig. 3d–g, an aspirated GUV is coupled through a membrane nanotube to a streptavidin bead in an optical trap. Aspiration pressure sets tension; force is trap stiffness times bead displacement, with stiffness calibrated by viscous drag. The authors use tube force before clathrin to estimate the free-membrane bending modulus, then use force and apparent GUV-area changes after clathrin to infer polymerization-energy and line-tension parameters. Images are fluorescence/EM snapshots and the nanotube force is a resultant at the bead. The article is CC BY 4.0; its only linked supplement is the 8.9-MB PDF.

## Eligibility audit

| Requirement | What the source establishes | Limit for source separation |
|---|---|---|
| Observation geometry and units | Fig. 1 images GUV-scale fluorescence and EM of buds; Methods gives 5 um/100–200 nm figure scale bars and ImageJ analyses. Fig. 3 is an aspirated GUV plus tube, not a cell pit. | No released registered full membrane-profile stack, pose/reference convention, covariance, or per-GUV condition map. Visible GUV/tube/bud geometries cannot be interchanged. |
| Imposed or calibrated mechanics | Osmotic shock changes conditions; micropipette aspiration controls/calibrates membrane tension in the force experiment. Tube force uses a drag-calibrated optical-trap stiffness. Results reports free membrane kappa = 13 +/- 5 kBT from the no-clathrin tube relation. | The reported tension/force calibration is a scalar tether assay. It neither measures the spatial normal traction on a pit nor its balancing reaction. Tether resultant must not be treated as a pit traction map. |
| Rigidity perturbation | Fig. 5 uses a different lipid composition described as higher rigidity. Its primary PubMed figure caption reports that clathrin/AP180 fails to bind high-rigidity GUVs under key conditions. | The perturbation explicitly changes the coat-binding source state, in addition to membrane chemistry. It therefore cannot preserve curvature-source or traction fields and is not the required two calibrated kappas with preserved sources. |
| Source fields and force balance | The model has coat polymerization and line-tension parameters; inferred values are based on tube-force and apparent-area changes. | Neither a known spatial curvature-source field nor spatial applied/reaction traction is independently measured. Inferred model parameters cannot serve as independent source controls. |
| Sampling | Fluorescence experiments report 30–45 observations per condition from at least three independent experiments (PMC/PubMed figure text). | No public replicate-to-image/force linkage or raw observation record. |
| Public data contract | CC BY 4.0 article text/figures are public. Linked supplement: `ncomms7249-s1.pdf`, PDF, 8.9 MB, uninspected. PMC Associated Data lists that supplement, not a raw-data accession. | No accessible small raw table/image/force payload or stated raw-data license/identifier was evidenced. A reproducible numerical comparison cannot be contracted from inspected public material. |

## Decision

This is a **narrow calibration/reproduction precedent**, not support for the source-separation protocol. It shows that GUV tension and a tube-force resultant can be independently controlled or calibrated while coat morphology changes. It does not supply registered profiles plus two calibrated rigidities that preserve the same curvature and traction fields, or a spatial traction map with its reaction. The Fig. 5 lipid-rigidity change explicitly disrupts clathrin/AP180 binding in key conditions, and post-polymerization quantities are model-inferred. The empirical branch therefore stops here.

A minimum prospective test needs either (1) a spatial normal-traction map with its explicit balancing reaction, or (2) registered full GUV membrane profiles at two known, distinct independently measured kappas and known tensions, while the same purified coat/adaptor density preserves the curvature and load source fields. Each route requires released profiles, calibration traces, condition/replicate mapping, and a noise/observation model. The tether force may calibrate a reservoir mechanical scale, but cannot replace the spatial traction/reaction map in route 1.

## Exact locators

- PMC article, Abstract and introductory statement of GUV reconstitution: https://pmc.ncbi.nlm.nih.gov/articles/PMC4346611/
- Main-text Figs. 1–3 and 5 and their legends, including Fig. 3d apparatus: https://pmc.ncbi.nlm.nih.gov/articles/PMC4346611/#Fig3
- Publisher article, Results discussion of the tube assay and inferred parameters: https://www.nature.com/articles/ncomms7249
- Publisher Methods, “Clathrin polymerization energy measurements” and “Image analysis”: https://www.nature.com/articles/ncomms7249#Sec12
- PMC Supplementary Material / Associated Data listing: https://pmc.ncbi.nlm.nih.gov/articles/PMC4346611/#MOESM1
- PubMed public record and figure text: https://pubmed.ncbi.nlm.nih.gov/25695735/
