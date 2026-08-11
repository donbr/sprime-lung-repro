# Bio-research connectors — how they support this analysis

The numeric pipeline in this repo is **deterministic and offline** — it must never call a network service at
runtime (that would break reproducibility and CI). The bio-research MCP connectors are used one step
**upstream**, in an interactive Claude session, to **curate and verify the inputs** the pipeline then
consumes as frozen files. Keep that boundary:

```
  bio-research connectors (interactive, Claude-driven)         deterministic repo (offline, CI-safe)
  ─────────────────────────────────────────────────           ─────────────────────────────────────
  PubMed   → find/verify SL literature → PMIDs/DOIs   ┐
  ChEMBL   → confirm true compound MoA/target         ├─►  frozen  concordance/reference_set.csv  ─►  concordance_enrichment.py
  ORCS     → flag common-essential vs selective       ┘        (+ notes on MoA corrections)             run_all.py / demeter_validation.py
```

## Status (verified live in this session, no extra authorization required)

| Connector | Tool | Status | Verified example |
|---|---|---|---|
| BioGRID ORCS (CRISPR essentiality) | `get_orcs_essentiality(entrez_id)` | **live** | AURKB (9212) returns per-screen essentiality (large payload — filter with `hit_only`) |
| ChEMBL (mechanism of action) | `get_mechanism(chembl_id)` | **live** | `CHEMBL415049` → "Serine/threonine-protein kinase **Aurora-B inhibitor**", target CHEMBL2185, max phase 3 |
| PubMed (literature) | `search / get_article_metadata / full_text` | **live** | PMID 30373917 → Gong 2019, *RB1*-loss → **AURKA** synthetic lethal, [DOI](https://doi.org/10.1158/2159-8290.CD-18-0469) |

*(PubMed usage requires attribution: "According to PubMed," with the article DOI linked, per the connector's
terms.)*

**Require authorization before use** (OAuth in an interactive Claude session — a maintainer must connect
them): the full `biosciences-mcp` (Open Targets, UniProt, STRING, Ensembl, HGNC, IUPHAR, WikiPathways,
PubChem, ClinicalTrials), `synapse`, and `biorxiv`. Until connected, those capabilities are unavailable.

## Where they add value here

1. **Literature-blind concordance reference set** (`concordance/`). The whole point of that rebuild is a
   reference list assembled from the literature, not from ΔpS′. **PubMed** finds and confirms the
   genotype-specific SL papers and gives each reference row a real PMID/DOI; the protocol requires exactly
   that provenance.
2. **Fixing MoA misannotations.** The referee review flagged PRISM's MOA layer as sometimes wrong (e.g.
   barasertib labeled "electrolyte reabsorption inhibitor"). **ChEMBL** `get_mechanism` gives the correct
   target — barasertib = Aurora-B — so the target→compound expansion in `concordance_enrichment.py` maps to
   the right compounds instead of trusting PRISM's annotation.
3. **Selective vs pan-essential.** **BioGRID ORCS** distinguishes genotype-selective targets from
   common-essential genes (PLK1/CHEK1/KIF11 are pan-essential), which is how the reference set should label
   "report the differential, not the raw dependency." This complements the **DEMETER2** RNAi module
   (`demeter_validation.py`) — CRISPR (ORCS) and RNAi (DEMETER2) as orthogonal cross-checks.

## Why they are not baked into `run_all.py`
These calls are interactive (need a Claude session), rate-limited, and their results change as databases
update — the opposite of what a reproducible pipeline needs. So they live at the **curation boundary**: run
them once, record the results into the frozen input files (with PMIDs/DOIs and a freeze date), and commit
those files. The pipeline then reproduces identically forever from the committed inputs.

## Usability for ongoing research
The edge connectors (ORCS, ChEMBL) and PubMed are usable now for exactly this kind of grounding, and the set
is expandable: connecting `biosciences-mcp` adds Open Targets (target–disease evidence), UniProt/STRING
(protein/interaction context), and ClinicalTrials (translational status) — all useful for extending the
reference set and interpreting hits, once authorized in an interactive session.
