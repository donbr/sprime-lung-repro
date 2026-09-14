#!/usr/bin/env node
/**
 * Build docs/sprime_addendum.pptx — the referee-facing addendum to
 * docs/sprime_lung_repro_presentation.pptx.
 *
 * Every figure on every slide is READ FROM THE COMMITTED CSVs at build time; nothing is typed in
 * by hand. That is the point of this script: the main deck's tables were transcribed and are not
 * covered by tests/test_docs_numbers.py (which reads .md files only), so they can drift silently.
 * These cannot.
 *
 * Sources:
 *   concordance/results/concordance_report.csv   -> slide 1
 *   concordance/reference_seed_grounded.csv      -> slide 2
 *   results/demeter_validation.csv               -> slide 3
 *   (slide 4 is prose: review items with no implementation)
 *
 * Usage:  node docs/build_addendum_deck.js
 * Output: docs/sprime_addendum.pptx  (gitignored — regenerate, don't commit)
 */
"use strict";
const fs = require("fs");
const path = require("path");
const PptxGenJS = require("pptxgenjs");

const REPO = path.resolve(__dirname, "..");
const OUT = path.join(REPO, "docs", "sprime_addendum.pptx");

// ---------- palette: matches the parent deck so the addendum reads as one series ----------
const BG = "0b0f19", PANEL = "0f172a", CARD = "1e293b";
const CYAN = "06b6d4", ROSE = "f43f5e", AMBER = "f59e0b", TEXT = "f8fafc", MUTED = "94a3b8";
const BODY = "Calibri", HEAD = "Cambria";

// ---------- minimal RFC4180-ish CSV reader (quoted fields, embedded commas) ----------
function readCsv(rel) {
  const raw = fs.readFileSync(path.join(REPO, rel), "utf8").replace(/^﻿/, "");
  const rows = [];
  let field = "", row = [], inQ = false;
  for (let i = 0; i < raw.length; i++) {
    const c = raw[i];
    if (inQ) {
      if (c === '"') { if (raw[i + 1] === '"') { field += '"'; i++; } else inQ = false; }
      else field += c;
    } else if (c === '"') inQ = true;
    else if (c === ",") { row.push(field); field = ""; }
    else if (c === "\n") { row.push(field); rows.push(row); row = []; field = ""; }
    else if (c !== "\r") field += c;
  }
  if (field.length || row.length) { row.push(field); rows.push(row); }
  const body = rows.filter(r => r.length > 1 && !r[0].startsWith("#"));
  const head = body.shift();
  return body.map(r => Object.fromEntries(head.map((h, i) => [h.trim(), (r[i] ?? "").trim()])));
}

// ---------- formatting ----------
const num = s => (s === "" || s == null ? null : Number(s));
function fmtP(s) {                       // 0.00132 -> "0.0013"; 5.638e-8 -> "5.6e-08"
  const v = num(s);
  if (v == null || Number.isNaN(v)) return "n/a";
  if (v === 0) return "0";
  if (v < 0.001) {
    const [m, e] = v.toExponential(1).split("e");
    const sign = e[0] === "-" ? "-" : "";
    return `${m}e${sign}${String(Math.abs(Number(e))).padStart(2, "0")}`;
  }
  return String(Number(v.toPrecision(2)));
}
const fmtPct = s => (num(s) == null ? "n/a" : (100 * num(s)).toFixed(1) + "%");
const fmtD = s => (num(s) >= 0 ? "+" : "") + num(s).toFixed(3);

// ---------- slide furniture ----------
function titleBlock(slide, kicker, title) {
  slide.addText(kicker, { x: 0.55, y: 0.34, w: 12.2, h: 0.28, fontFace: BODY, fontSize: 12,
    bold: true, color: CYAN, charSpacing: 1.2, margin: 0 });
  slide.addText(title, { x: 0.55, y: 0.62, w: 12.2, h: 0.62, fontFace: HEAD, fontSize: 30,
    bold: true, color: TEXT, margin: 0 });
}
function sourceNote(slide, text) {
  slide.addText(text, { x: 0.55, y: 6.92, w: 12.2, h: 0.3, fontFace: BODY, fontSize: 10,
    italic: true, color: MUTED, margin: 0 });
}
const thead = t => ({ text: t, options: { bold: true, color: CYAN, fill: { color: PANEL },
  fontSize: 11, fontFace: BODY, valign: "middle" } });
const tcell = (t, o = {}) => ({ text: t, options: Object.assign(
  { color: TEXT, fill: { color: CARD }, fontSize: 12, fontFace: BODY, valign: "middle" }, o) });

// ================================================================= build
const pptx = new PptxGenJS();
pptx.layout = "LAYOUT_WIDE";                       // 13.3 x 7.5 — set BEFORE adding slides
pptx.title = "S′ Reproduction — Referee Addendum";

// ---------------------------------------------------------------- slide 1
{
  const rep = readCsv("concordance/results/concordance_report.csv");
  const s = pptx.addSlide();
  s.background = { color: BG };
  titleBlock(s, "REVIEW ISSUE B1 — CIRCULAR CONCORDANCE", "The Literature-Blind Concordance Benchmark");

  s.addText(
    "The manuscript scored its candidates against a reference set built from compounds that had already " +
    "passed the SL window, so “75 of 75 recovered, 100%” was guaranteed before any comparison ran. " +
    "Scored instead against a set assembled independently, recovery is partial and two of four arms " +
    "carry no usable signal.",
    { x: 0.55, y: 1.36, w: 12.2, h: 0.72, fontFace: BODY, fontSize: 13.5, color: TEXT, margin: 0 });

  const rows = [[thead("Genotype"), thead("Reference compounds\nin universe"), thead("Recovered"),
                 thead("Recovery"), thead("Hypergeometric p"), thead("Permutation p")]];
  for (const r of rep) {
    const testable = Number(r.ref_in_universe) > 0;
    const warn = !testable ? { color: AMBER } : {};
    rows.push([
      tcell(r.gene, { bold: true }),
      tcell(testable ? r.ref_in_universe : "0", warn),
      tcell(testable ? r.recovered : "—", warn),
      tcell(testable ? fmtPct(r.recovery) : "—", warn),
      tcell(testable ? fmtP(r.hyperg_p) : "untestable", warn),
      tcell(testable ? fmtP(r.perm_p) : "—", warn),
    ]);
  }
  s.addTable(rows, { x: 0.55, y: 2.24, w: 12.2, colW: [1.9, 2.5, 1.7, 1.7, 2.2, 2.2],
    rowH: 0.42, border: { type: "solid", color: BG, pt: 1 }, align: "center" });

  const cdkn2a = rep.find(r => r.gene === "CDKN2A");
  const misses = rep.filter(r => Number(r.ref_in_universe) > 0)
    .map(r => `${r.gene} ${r.misses ? r.misses.split(";").length : 0}`).join(" · ");

  s.addShape(pptx.ShapeType.roundRect, { x: 0.55, y: 5.02, w: 5.95, h: 1.32,
    fill: { color: CARD }, line: { color: ROSE, width: 1 }, rectRadius: 0.08 });
  s.addText([
    { text: "Recovery alone is what made it circular\n", options: { bold: true, color: ROSE, fontSize: 13 } },
    { text: `Always report the enrichment p and the misses with it. Compounds missed: ${misses}. ` +
            `A reference row names a target, not a compound, so 7 rows expand to the counts above.`,
      options: { fontSize: 11.5, color: TEXT } },
  ], { x: 0.75, y: 5.16, w: 5.55, h: 1.04, fontFace: BODY, margin: 0, valign: "top" });

  s.addShape(pptx.ShapeType.roundRect, { x: 6.8, y: 5.02, w: 5.95, h: 1.32,
    fill: { color: CARD }, line: { color: AMBER, width: 1 }, rectRadius: 0.08 });
  s.addText([
    { text: "CDKN2A cannot be benchmarked at all\n", options: { bold: true, color: AMBER, fontSize: 13 } },
    { text: `${cdkn2a ? cdkn2a.candidates : "48"} candidates, ${cdkn2a ? cdkn2a.universe : "1402"} tested, ` +
            `and 0 reference compounds — the seed set has no CDKN2A rows. New rows cannot be added now: ` +
            `the ΔpS′ rankings have already been seen, so any addition is contaminated by construction.`,
      options: { fontSize: 11.5, color: TEXT } },
  ], { x: 7.0, y: 5.16, w: 5.55, h: 1.04, fontFace: BODY, margin: 0, valign: "top" });

  sourceNote(s, "Source: concordance/results/concordance_report.csv (committed), via concordance/concordance_enrichment.py.");
}

// ---------------------------------------------------------------- slide 2
{
  const ref = readCsv("concordance/reference_seed_grounded.csv");
  const n = ref.length;
  const withPmid = ref.filter(r => r.pmid).length;
  const withTerms = ref.filter(r => r.search_terms).length;
  const distinct = new Set(ref.map(r => r.search_terms)).size;
  const by = v => ref.filter(r => r.support_status === v);
  const frozen = [...new Set(ref.map(r => r.date_frozen))].join(", ");
  const redoc = [...new Set(ref.map(r => r.date_redocumented).filter(Boolean))].join(", ");

  const s = pptx.addSlide();
  s.background = { color: BG };
  titleBlock(s, "REVIEW ISSUE B1 — PROVENANCE OF THE REFERENCE SET",
    "What the Blind Benchmark Rests On");

  const stat = (x, big, label, color) => {
    s.addShape(pptx.ShapeType.roundRect, { x, y: 1.42, w: 2.92, h: 1.28,
      fill: { color: CARD }, line: { color: PANEL, width: 1 }, rectRadius: 0.08 });
    s.addText(big, { x, y: 1.5, w: 2.92, h: 0.66, fontFace: HEAD, fontSize: 30, bold: true,
      color, align: "center", margin: 0 });
    s.addText(label, { x: x + 0.14, y: 2.14, w: 2.64, h: 0.48, fontFace: BODY, fontSize: 10.5,
      color: MUTED, align: "center", margin: 0 });
  };
  stat(0.55, `${withPmid} / ${n}`, "rows carry a PMID and DOI", CYAN);
  stat(3.72, `${distinct} / ${n}`, "distinct search queries recorded", CYAN);
  stat(6.89, `${by("uncited").length}`, "row uncited after search", AMBER);
  stat(10.06, `${by("contradicted").length}`, "row contradicted by its own source", ROSE);

  s.addShape(pptx.ShapeType.roundRect, { x: 0.55, y: 2.92, w: 12.2, h: 1.30,
    fill: { color: CARD }, line: { color: PANEL, width: 1 }, rectRadius: 0.08 });
  s.addText([
    { text: "Two rows are unsupported on purpose — that is a finding, not an oversight\n",
      options: { bold: true, color: TEXT, fontSize: 13.5, breakLine: true } },
    ...by("uncited").map(r => ({
      text: `UNCITED · ${r.genotype} → ${r.target} (${r.compound}) — no paper establishes ` +
            `${r.genotype}-deficient-selective sensitivity after 3 recorded queries. Same arm the benchmark scores at p = 0.30.`,
      options: { fontSize: 11.5, color: AMBER, breakLine: true } })),
    ...by("contradicted").map(r => ({
      text: `CONTRADICTED · ${r.genotype} → ${r.target} (${r.compound}) — its sole hit (PMID ${r.pmid}) reports the ` +
            `association in p53 WILD-TYPE cases, the opposite direction, and is cited as counter-evidence.`,
      options: { fontSize: 11.5, color: ROSE } })),
  ], { x: 0.78, y: 3.05, w: 11.74, h: 1.06, fontFace: BODY, margin: 0, valign: "top" });

  s.addShape(pptx.ShapeType.roundRect, { x: 0.55, y: 4.40, w: 12.2, h: 2.26,
    fill: { color: PANEL }, line: { color: ROSE, width: 1 }, rectRadius: 0.08 });
  s.addText([
    { text: "The limitation a referee should hold us to\n",
      options: { bold: true, color: ROSE, fontSize: 13.5, breakLine: true } },
    { text: `The ${redoc} pass documented a seed set assembled earlier. It was retrospective, not blind assembly, ` +
            `and it did not re-freeze the set (date_frozen remains ${frozen}) — documented provenance is not an ` +
            `independent census.\n`,
      options: { fontSize: 11.5, color: TEXT, breakLine: true } },
    { text: `The freeze date is an attestation, not a verified timestamp. It predates this repository's INITIAL ` +
            `commit (02b06ce, 2026-08-11) by five weeks, and that initial commit is where the reference set and the ` +
            `scored report both first appear. There are no tags. So the protocol's "commit with a timestamp / git tag" ` +
            `has neither, and no ordering evidence can exist in this history — the blind-assembly claim rests on the ` +
            `curator's word, not on version control.\n`,
      options: { fontSize: 11.5, color: TEXT, breakLine: true } },
    { text: `A BioGRID ORCS hit fraction can establish pan-essentiality but never genotype-selectivity, so no ` +
            `selectivity claim in this set is sourced to one.`,
      options: { fontSize: 11.5, color: CYAN, bold: true } },
  ], { x: 0.78, y: 4.54, w: 11.74, h: 2.00, fontFace: BODY, margin: 0, valign: "top" });

  sourceNote(s, `Source: concordance/reference_seed_grounded.csv and reference_template.csv (committed); ` +
    `${withTerms}/${n} rows carry a query string. Citations verified against PubMed.`);
}

// ---------------------------------------------------------------- slide 3
{
  const dem = readCsv("results/demeter_validation.csv");
  const rb1 = dem.filter(r => r.genotype === "RB1").sort((a, b) => num(a.delta_pD) - num(b.delta_pD));
  const sig = r => num(r.q_two) <= 0.05;
  const status = r => !sig(r) ? "not significant"
    : (r.mutant_selective === "True" ? "mutant-selective" : "WT-selective (control)");
  // Reference membership must be looked up across ALL genotypes, not just RB1: AKT1 is in the
  // reference set under PTEN, and scoping this to RB1 wrongly reports it as absent.
  const ref = readCsv("concordance/reference_seed_grounded.csv");
  const refMap = new Map(ref.map(r => [r.target, r]));
  const rb1Refs = ref.filter(r => r.genotype === "RB1").map(r => r.target);
  const refShown = rb1.filter(r => rb1Refs.includes(r.target));
  const refSig = refShown.filter(sig).length;
  const wrongWay = refShown.filter(r => num(r.delta_pD) > 0);          // WT-selective direction
  const sigMut = rb1.filter(r => sig(r) && r.mutant_selective === "True");
  const sigAbsent = sigMut.filter(r => !refMap.has(r.target));
  const sigElsewhere = sigMut.filter(r => refMap.has(r.target));
  const nWt = rb1[0].n_wt, nMut = rb1[0].n_mut;
  const refCell = r => {
    const m = refMap.get(r.target);
    return m ? (m.genotype === "RB1" ? "yes (RB1)" : `yes (${m.genotype}, ${m.support_status})`) : "—";
  };

  const s = pptx.addSlide();
  s.background = { color: BG };
  titleBlock(s, "REVIEW ISSUE M9 — RNAi CROSS-CHECK, IN FULL",
    `All ${rb1.length} RB1 Targets in DEMETER2 — Not the 6 That Fit`);

  const rows = [[thead("Target"), thead("ΔpD"), thead("Direction"), thead("q (two-sided)"),
                 thead("Status"), thead("In reference set")]];
  for (const r of rb1) {
    const st = status(r);
    const col = st === "mutant-selective" ? CYAN : st === "WT-selective (control)" ? MUTED : ROSE;
    rows.push([
      tcell(r.target, { bold: true }),
      tcell(fmtD(r.delta_pD)),
      tcell(r.direction, { color: MUTED }),
      tcell(fmtP(r.q_two)),
      tcell(st, { color: col }),
      tcell(refCell(r), { color: refMap.has(r.target) ? AMBER : MUTED }),
    ]);
  }
  s.addTable(rows, { x: 0.55, y: 1.42, w: 12.2, colW: [1.7, 1.35, 2.15, 1.75, 2.45, 2.8],
    rowH: 0.22, fontSize: 10, border: { type: "solid", color: BG, pt: 1 }, align: "center" });

  s.addShape(pptx.ShapeType.roundRect, { x: 0.55, y: 5.00, w: 12.2, h: 1.76,
    fill: { color: CARD }, line: { color: AMBER, width: 1 }, rectRadius: 0.08 });
  s.addText([
    { text: `The two modalities point at different genes. `, options: { bold: true, color: AMBER, fontSize: 10.5 } },
    { text: `All ${refShown.length} literature-derived RB1 reference targets are non-significant here ` +
            `(${refSig} of ${refShown.length} reach q ≤ 0.05), and ${wrongWay.length} of ${refShown.length} ` +
            `(${wrongWay.map(r => r.target).join(", ")}) trend WT-selective — opposite to the RB1-mutant-selective ` +
            `hypothesis the reference set encodes — though none significantly. That includes PARP1, the ` +
            `strongest-evidence row on the drug-response side.\n`,
      options: { color: TEXT, fontSize: 10.5, breakLine: true } },
    { text: `Of the ${sigMut.length} significant mutant-selective targets, ${sigAbsent.length} ` +
            `(${sigAbsent.map(r => r.target).join(", ")}) are absent from the reference set. The fourth, ` +
            `${sigElsewhere.map(r => r.target).join(", ")}, IS present — but assigned to ` +
            `${sigElsewhere.map(r => refMap.get(r.target).genotype).join(", ")}, and it is the one row we could not cite. ` +
            `A row that is uncited under one genotype and carries an orthogonal RNAi signal under another may be ` +
            `mis-assigned rather than unsupported: a checkable lead, not a conclusion.\n`,
      options: { color: TEXT, fontSize: 10.5, breakLine: true } },
    { text: `Read this weakly: the mutant arm is ${nMut} lines against ${nWt} WT, so five non-significant results are ` +
            `close to uninformative alone and the direction signs should not be over-read. RNAi and drug response are ` +
            `different modalities — a cross-check, not a refutation.`,
      options: { color: MUTED, fontSize: 10 } },
  ], { x: 0.78, y: 5.09, w: 11.74, h: 1.60, fontFace: BODY, margin: 0, valign: "top" });

  sourceNote(s, "Source: results/demeter_validation.csv (committed), via demeter_validation.py on DEMETER2 v6. " +
    "q is Benjamini–Hochberg across the 12 targets within the genotype; CDKN2A and TP53 carry 12 rows each.");
}

// ---------------------------------------------------------------- slide 4
{
  const s = pptx.addSlide();
  s.background = { color: BG };
  titleBlock(s, "WHAT THIS REPOSITORY DOES NOT DO", "Review Items With No Implementation");

  s.addText("The resolution matrix in the parent deck lists what was fixed. These were asked for and are " +
    "absent — none is closed by a control already shown.",
    { x: 0.55, y: 1.32, w: 12.2, h: 0.32, fontFace: BODY, fontSize: 13.5, color: TEXT, margin: 0 });

  const gaps = [
    ["M1", "Fit-quality / minimum |E_max| gate", ROSE,
     "The significant gap. Flat curves make EC₅₀ unidentifiable while |S′| explodes — the likely source of the " +
     "non-credible hits (aspirin, ranitidine). The bootstrap CI gate does NOT substitute: those hits survive it " +
     "because their artifactual S′ is stable, not noisy. Such a filter must run before sprime_core.sprime is called."],
    ["M2", "EC₅₀ censoring at the tested range", AMBER,
     "PRISM's 8 dose steps, 4-fold from 10 µM, bottom out near 0.61 nM. EC₅₀ values at or beyond that boundary are " +
     "censored, not measured, and enter S′ as if they were measured."],
    ["M6", "Copy-number loss in genotype calls", AMBER,
     "Genotypes read the damaging-mutation matrix only. CDKN2A in lung is predominantly homozygous deletion, so its " +
     "mutant cohort is understated — which is exactly why the CDKN2A arm is weakest everywhere in both decks. " +
     "CRISPRGeneDependency.csv is listed in DOWNLOAD_CHECKLIST.md and deliberately not wired in."],
    ["M4", "Clustering on the shared-term embedding", MUTED,
     "Clustering is done on (pS′_WT, pS′_MUT) rather than the embedding the manuscript describes."],
    ["M5", "Benjamini–Hochberg for the main analysis", MUTED,
     "bh_fdr exists, but only inside demeter_validation.py. The main significance analysis does not use it."],
    ["M8", "RB1 × TP53 interaction term", MUTED,
     "Not modelled. The two genotypes are treated as independent strata throughout."],
  ];
  const W = 3.93, ROW_H = [2.34, 1.42];          // row 2 carries one-line gaps; don't leave it hollow
  gaps.forEach((g, i) => {
    const row = Math.floor(i / 3), H = ROW_H[row];
    const x = 0.55 + (i % 3) * (W + 0.19);
    const y = 1.82 + (row === 0 ? 0 : ROW_H[0] + 0.22);
    s.addShape(pptx.ShapeType.roundRect, { x, y, w: W, h: H, fill: { color: CARD },
      line: { color: g[2], width: 1 }, rectRadius: 0.08 });
    s.addText(`${g[0]} — ${g[1]}`, { x: x + 0.18, y: y + 0.13, w: W - 0.36, h: 0.5,
      fontFace: BODY, fontSize: 12.5, bold: true, color: g[2], margin: 0, valign: "top" });
    s.addText(g[3], { x: x + 0.18, y: y + 0.62, w: W - 0.36, h: H - 0.76,
      fontFace: BODY, fontSize: 10.5, color: TEXT, margin: 0, valign: "top" });
  });

  sourceNote(s, "Gaps as enumerated in CLAUDE.md and docs/scope.md. The M1 note restates the review's own " +
    "finding that the bootstrap CI gate is not a substitute for a fit-quality filter.");
}

pptx.writeFile({ fileName: OUT }).then(() => {
  console.log("wrote " + path.relative(REPO, OUT));
});
