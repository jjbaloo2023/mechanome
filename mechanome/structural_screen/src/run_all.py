"""Run the full Stage 0-4 pipeline. CPU-light; fetches from RCSB/UniProt/OPM/QuickGO."""
import stage0_energy_scale, stage1_candidates
if __name__ == "__main__":
    print("Stage 0:", stage0_energy_scale.run())
    print("Stage 1:\n", stage1_candidates.run().to_string(index=False))
    print("\nStages 2-4 require structure downloads; see docs/REPORT.md for the full run.")
    print("Results and figures are in results/ and figures/.")
