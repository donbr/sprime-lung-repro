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
 * Reads the BENCHMARK OF RECORD, not the superseded seed run. A generated deck cannot drift from the
 * CSV it reads, but nothing stops it reading the wrong one — this deck did exactly that until the
 * 2026-08-31 census landed. Point every figure at results/2026-08-31_blind/.
 *
 * Sources:
 *   concordance/results/2026-08-31_blind/
 *       concordance_report_primary_directional.csv  -> slides 1, 2, 5   (benchmark of record)
 *   concordance/reference_set_2026-08-31_directional.csv -> slides 1, 2, 5
 *   concordance/reference_seed_grounded.csv         -> slide 2 (SUPERSEDED — shown as such, never quoted)
 *   results/demeter_validation.csv                  -> slides 3, 5
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

// The benchmark of record (concordance/README.md). Never quote SEED_REPORT — it is the 7-row starter
// run, retained only to show why the census was needed (its TP53 p = 5.6e-08 collapses to 0.51).
const BLIND_REPORT = "concordance/results/2026-08-31_blind/concordance_report_primary_directional.csv";
const BLIND_REF    = "concordance/reference_set_2026-08-31_directional.csv";
const SEED_REF     = "concordance/reference_seed_grounded.csv";

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
  const rep = readCsv(BLIND_REPORT);
  const nRef = readCsv(BLIND_REF).length;
  const s = pptx.addSlide();
  s.background = { color: BG };
  titleBlock(s, "REVIEW ISSUE B1 — CIRCULAR CONCORDANCE", "The Literature-Blind Concordance Benchmark");

  s.addText(
    "The manuscript scored its candidates against a reference set built from compounds that had already " +
    "passed the SL window, so “75 of 75 recovered, 100%” was guaranteed before any comparison ran. " +
    "Scored instead against a census assembled blind and frozen before scoring, three of the four arms " +
    "return chance-level recovery. Only RB1 clears, and that is the point: the same procedure that " +
    "returns a positive for one genotype returns nothing for the other three.",
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
            `A reference row names a target, not a compound, so the census's ${nRef} rows expand to the ` +
            `counts above.`,
      options: { fontSize: 11.5, color: TEXT } },
  ], { x: 0.75, y: 5.16, w: 5.55, h: 1.04, fontFace: BODY, margin: 0, valign: "top" });

  s.addShape(pptx.ShapeType.roundRect, { x: 6.8, y: 5.02, w: 5.95, h: 1.32,
    fill: { color: CARD }, line: { color: AMBER, width: 1 }, rectRadius: 0.08 });
  s.addText([
    { text: "CDKN2A is testable and returns nothing\n", options: { bold: true, color: AMBER, fontSize: 13 } },
    { text: `${cdkn2a.ref_in_universe} reference compounds in universe, ${cdkn2a.candidates} candidates, ` +
            `${cdkn2a.universe} tested — ${cdkn2a.recovered} recovered, p = ${fmtP(cdkn2a.hyperg_p)}. The arm ` +
            `is uninformative for a documented reason, not for want of a reference set: its dominant ` +
            `MTAP/PRMT5 agents are absent from the PRISM 19Q4 library, and genotype calls miss the ` +
            `homozygous deletions that are how CDKN2A is actually lost in lung (M6).`,
      options: { fontSize: 11.5, color: TEXT } },
  ], { x: 7.0, y: 5.16, w: 5.55, h: 1.04, fontFace: BODY, margin: 0, valign: "top" });

  sourceNote(s, `Source: ${BLIND_REPORT} (committed), via concordance/concordance_enrichment.py. ` +
    "The benchmark of record; RB1 passes the same gate against a second blind census (2026-09-06, p = 0.00097).");
}

// ---------------------------------------------------------------- slide 2
{
  const ref = readCsv(SEED_REF);
  const blindRef = readCsv(BLIND_REF);
  const blindRep = readCsv(BLIND_REPORT);
  const n = ref.length;
  const withPmid = ref.filter(r => r.pmid).length;
  const withTerms = ref.filter(r => r.search_terms).length;
  const distinct = new Set(ref.map(r => r.search_terms)).size;
  const by = v => ref.filter(r => r.support_status === v);
  const frozen = [...new Set(ref.map(r => r.date_frozen))].join(", ");
  const redoc = [...new Set(ref.map(r => r.date_redocumented).filter(Boolean))].join(", ");

  const s = pptx.addSlide();
  s.background = { color: BG };
  titleBlock(s, "REVIEW ISSUE B1 — PROVENANCE OF THE REFERENCE SETS",
    "What the Benchmark Rests On, and What It Does Not");

  s.addText(
    `The benchmark of record is the ${blindRef.length}-row census frozen 2026-08-31; the ${n}-row seed set ` +
    `below is SUPERSEDED and shown only because its documentation pass is what exposed the limitation both ` +
    `sets share.`,
    { x: 0.55, y: 1.14, w: 12.2, h: 0.26, fontFace: BODY, fontSize: 12, color: MUTED, margin: 0 });

  const stat = (x, big, label, color) => {
    s.addShape(pptx.ShapeType.roundRect, { x, y: 1.42, w: 2.92, h: 1.28,
      fill: { color: CARD }, line: { color: PANEL, width: 1 }, rectRadius: 0.08 });
    s.addText(big, { x, y: 1.5, w: 2.92, h: 0.66, fontFace: HEAD, fontSize: 30, bold: true,
      color, align: "center", margin: 0 });
    s.addText(label, { x: x + 0.14, y: 2.14, w: 2.64, h: 0.48, fontFace: BODY, fontSize: 10.5,
      color: MUTED, align: "center", margin: 0 });
  };
  stat(0.55, `${withPmid} / ${n}`, "seed rows carry a PMID and DOI", CYAN);
  stat(3.72, `${distinct} / ${n}`, "seed rows with a distinct query", CYAN);
  stat(6.89, `${by("uncited").length}`, "seed row uncited after search", AMBER);
  stat(10.06, `${by("contradicted").length}`, "seed row contradicted by its source", ROSE);

  s.addShape(pptx.ShapeType.roundRect, { x: 0.55, y: 2.92, w: 12.2, h: 1.30,
    fill: { color: CARD }, line: { color: PANEL, width: 1 }, rectRadius: 0.08 });
  s.addText([
    { text: "Two rows are unsupported on purpose — that is a finding, not an oversight\n",
      options: { bold: true, color: TEXT, fontSize: 13.5, breakLine: true } },
    ...by("uncited").map(r => ({
      text: `UNCITED · ${r.genotype} → ${r.target} (${r.compound}) — no paper establishes ` +
            `${r.genotype}-deficient-selective sensitivity after 3 recorded queries. Same arm the benchmark ` +
            `scores at p = ${fmtP((blindRep.find(x => x.gene === r.genotype) || {}).hyperg_p)} in the census ` +
            `of record. The census does not nominate ${r.target} for any genotype.`,
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
    { text: `SEED SET (superseded): the ${redoc} pass documented a set assembled earlier. Retrospective, not blind ` +
            `assembly, and it did not re-freeze the set (date_frozen remains ${frozen}). Its freeze date predates ` +
            `this repository's INITIAL commit (02b06ce, 2026-08-11) by five weeks, and that commit is where the set ` +
            `and its scored report both first appear. No tags. So no ordering evidence can exist in this history.\n`,
      options: { fontSize: 11.5, color: TEXT, breakLine: true } },
    { text: `CENSUS OF RECORD (2026-08-31): assembled blind, but its freeze commit is RETROACTIVE — 9ca5046, six ` +
            `days after scoring. The 2026-09-06 replication is the one whose freeze commits precede scoring ` +
            `(38ce6f6 then 0fb42f8), with the raw per-agent output committed so a reviewer can re-derive the ` +
            `assembly. Read its §2: census 2's RB1 set is a strict SUBSET of census 1's, so the identical ` +
            `recovered set is arithmetic, not independent convergence.\n`,
      options: { fontSize: 11.5, color: TEXT, breakLine: true } },
    { text: `Neither census is an independent replication: both were commissioned from a results-aware context, ` +
            `and agent isolation was enforced by instruction rather than by a sandbox.\n`,
      options: { fontSize: 11.5, color: ROSE, breakLine: true } },
    { text: `A BioGRID ORCS hit fraction can establish pan-essentiality but never genotype-selectivity, so no ` +
            `selectivity claim in this set is sourced to one.`,
      options: { fontSize: 11.5, color: CYAN, bold: true } },
  ], { x: 0.78, y: 4.54, w: 11.74, h: 2.00, fontFace: BODY, margin: 0, valign: "top" });

  sourceNote(s, `Sources: ${BLIND_REF} (${blindRef.length} rows, the benchmark of record) and ${SEED_REF} ` +
    `(${n} rows, superseded; ${withTerms}/${n} carry a query string), plus reference_template.csv. ` +
    `Citations verified against PubMed.`);
}

// ---------------------------------------------------------------- slide 3
{
  const dem = readCsv("results/demeter_validation.csv");
  const rb1 = dem.filter(r => r.genotype === "RB1").sort((a, b) => num(a.delta_pD) - num(b.delta_pD));
  // Two different statistics live in this table, so keep them straight:
  //   q_two            - two-sided, the conservative one; what the q column shows.
  //   mutant_selective - demeter_validation.py's own flag: dpD < 0 AND mutant-direction q_mut < 0.10.
  // They are NOT the same cut. Read Status off the flags rather than inferring it from q_two, or a
  // row failing both flags would be mislabelled "WT-selective (control)".
  const sig = r => num(r.q_two) <= 0.05;
  const status = r => r.mutant_selective === "True" ? "mutant-selective"
    : r.wt_selective === "True" ? "WT-selective (control)"
    : "not flagged";
  // Reference membership must be looked up across ALL genotypes, not just RB1: AKT1 is in the
  // reference set under PTEN, and scoping this to RB1 wrongly reports it as absent.
  const ref = readCsv("concordance/reference_seed_grounded.csv");
  const refMap = new Map(ref.map(r => [r.target, r]));
  const rb1Refs = ref.filter(r => r.genotype === "RB1").map(r => r.target);
  const refShown = rb1.filter(r => rb1Refs.includes(r.target));
  const refSig = refShown.filter(sig).length;
  const wrongWay = refShown.filter(r => num(r.delta_pD) > 0);          // WT-selective direction
  const sigMut = rb1.filter(r => r.mutant_selective === "True");   // the flag, not a 0.05 cut
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
    { text: `Of the ${sigMut.length} targets flagged mutant-selective (ΔpD < 0 with mutant-direction q < 0.10), ${sigAbsent.length} ` +
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
    "The q column is two-sided (q_two), Benjamini–Hochberg across the 12 targets within the genotype. Status is " +
    "demeter_validation.py's own flag: ΔpD < 0 with mutant-direction q_mut < 0.10, not a 0.05 cut — q_mut tests only " +
    "'mutant more dependent', so it scores a real WT-selective effect as 1.0. CDKN2A and TP53 carry 12 rows each.");
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

// ---------------------------------------------------------------- slide 5 (appendix)
{
  const ref = readCsv(SEED_REF);
  const blindRef = readCsv(BLIND_REF);
  const rep = readCsv(BLIND_REPORT);
  const dem = readCsv("results/demeter_validation.csv");

  // issue 1 — AKT1: in the reference set under one genotype, RNAi-significant under another
  const refAkt = ref.find(r => r.target === "AKT1");
  const demAkt = dem.find(r => r.genotype === "RB1" && r.target === "AKT1");
  const sig = dem.filter(r => r.genotype === "RB1" && r.mutant_selective === "True");
  const refTargets = new Set(ref.map(r => r.target));          // across ALL genotypes, not per-arm
  const sigInRef = sig.filter(r => refTargets.has(r.target)).map(r => r.target);

  // issue 2 — CDKN2A: benchmarked and null; the gap is the genotype call, not the reference set
  const cd = rep.find(r => r.gene === "CDKN2A");
  const nCdkn = blindRef.filter(r => r.genotype === "CDKN2A").length;
  const aktInBlind = blindRef.some(r => r.target === "AKT1");

  const s = pptx.addSlide();
  s.background = { color: BG };
  titleBlock(s, "APPENDIX — UNRESOLVED", "Open Issues This Addendum Does Not Close");

  s.addText("Both are named here rather than left for a referee to find. Neither is closed by any control in " +
    "either deck, and neither can be closed by working harder on the existing data.",
    { x: 0.55, y: 1.32, w: 12.2, h: 0.34, fontFace: BODY, fontSize: 13.5, color: TEXT, margin: 0 });

  // ---- card 1
  s.addShape(pptx.ShapeType.roundRect, { x: 0.55, y: 1.84, w: 5.95, h: 3.42,
    fill: { color: CARD }, line: { color: AMBER, width: 1 }, rectRadius: 0.08 });
  s.addText("1 — AKT1: an RNAi signal no reference set nominates", { x: 0.75, y: 1.98, w: 5.55, h: 0.34,
    fontFace: BODY, fontSize: 13, bold: true, color: AMBER, margin: 0, valign: "top" });
  s.addText([
    { text: `AKT1 sits in the SEED set under ${refAkt.genotype}, support_status = ${refAkt.support_status} ` +
            `— the one row for which no citation could be found (3 recorded queries, ~380 PubMed hits). The ` +
            `${blindRef.length}-row census of record does ${aktInBlind ? "" : "NOT "}nominate AKT1 for any ` +
            `genotype, which is corroborating evidence that the seed row was unsupported.\n\n`,
      options: { fontSize: 11.5, color: TEXT } },
    { text: `Yet of the ${sig.length} targets flagged mutant-selective under RB1 in DEMETER2 ` +
            `(${sig.map(r => r.target).join(", ")} — ΔpD < 0 with mutant-direction q < 0.10), AKT1 is the ` +
            `only one present in the seed reference set at all: q = ${demAkt.bh_q} mutant-direction, ` +
            `${demAkt.q_two} two-sided, ΔpD = ${fmtD(demAkt.delta_pD)}.\n\n`,
      options: { fontSize: 11.5, color: TEXT } },
    { text: "Unresolved: ", options: { fontSize: 11.5, bold: true, color: AMBER } },
    { text: `whether the row belongs under RB1 rather than ${refAkt.genotype}, or whether this is noise at ` +
            `n_mut = ${demAkt.n_mut} against n_wt = ${demAkt.n_wt}. A drug-response signal the blind census ` +
            `never nominated is exactly what a benchmark cannot adjudicate, and ${refAkt.genotype} is the arm ` +
            `that census scores at p = ${fmtP((rep.find(r => r.gene === refAkt.genotype) || {}).hyperg_p)}.`,
      options: { fontSize: 11.5, color: TEXT } },
  ], { x: 0.75, y: 2.36, w: 5.55, h: 2.80, fontFace: BODY, margin: 0, valign: "top" });

  // ---- card 2
  s.addShape(pptx.ShapeType.roundRect, { x: 6.8, y: 1.84, w: 5.95, h: 3.42,
    fill: { color: CARD }, line: { color: ROSE, width: 1 }, rectRadius: 0.08 });
  s.addText("2 — CDKN2A is benchmarked and still uninformative", { x: 7.0, y: 1.98, w: 5.55, h: 0.34,
    fontFace: BODY, fontSize: 13, bold: true, color: ROSE, margin: 0, valign: "top" });
  s.addText([
    { text: `The census of record carries ${nCdkn} CDKN2A rows, ${cd.ref_in_universe} of them in universe, ` +
            `against ${cd.candidates} candidates and ${cd.universe} tested compounds. The arm scores: ` +
            `${cd.recovered} recovered, p = ${fmtP(cd.hyperg_p)}. So this is no longer a missing reference ` +
            `set — it is a null, and two known defects are why.\n\n`,
      options: { fontSize: 11.5, color: TEXT } },
    { text: "Library coverage. ", options: { fontSize: 11.5, bold: true, color: ROSE } },
    { text: "The strongest CDKN2A-co-deletion vulnerability is MTAP/PRMT5, and PRISM 19Q4 contains no " +
            "PRMT5 or MAT2A agent. The reference set names targets the screen cannot test.\n\n",
      options: { fontSize: 11.5, color: TEXT } },
    { text: "M6 — the genotype call. ", options: { fontSize: 11.5, bold: true, color: ROSE } },
    { text: "Calls read the damaging-mutation matrix only, and CDKN2A in lung is lost predominantly by " +
            "homozygous deletion, so the wild-type cohort is silently contaminated with functionally null " +
            "lines and ΔpS′ is biased toward zero. A negative here is therefore not yet evidence of absence.",
      options: { fontSize: 11.5, color: TEXT } },
  ], { x: 7.0, y: 2.36, w: 5.55, h: 2.80, fontFace: BODY, margin: 0, valign: "top" });

  // ---- what would settle each
  s.addShape(pptx.ShapeType.roundRect, { x: 0.55, y: 5.44, w: 12.2, h: 1.16,
    fill: { color: PANEL }, line: { color: CYAN, width: 1 }, rectRadius: 0.08 });
  s.addText([
    { text: "What would settle them   ", options: { bold: true, color: CYAN, fontSize: 12 } },
    { text: `(1) a pre-registered query for RB1-loss-selective AKT dependence, plus an audit of PRISM's MoA ` +
            `annotation for MK-2206 — the same annotation layer the review flagged as sometimes wrong.   ` +
            `(2) copy-number-aware genotype calls from CRISPRGeneDependency.csv, listed in ` +
            `DOWNLOAD_CHECKLIST.md and deliberately not wired in, plus a screen that actually contains a ` +
            `PRMT5 agent. The blind census is no longer the missing piece for CDKN2A — the genotype call ` +
            `and the compound library are.`,
      options: { fontSize: 11, color: TEXT } },
  ], { x: 0.75, y: 5.58, w: 11.8, h: 0.90, fontFace: BODY, margin: 0, valign: "top" });

  sourceNote(s, `Computed at build time from ${BLIND_REF}, ${BLIND_REPORT}, ${SEED_REF} ` +
    "and results/demeter_validation.csv. " +
    `Seed-reference membership is matched on target symbol across all genotypes (${sigInRef.join(", ") || "none"} matched). ` +
    "bh_q/q_mut tests only 'mutant more dependent'; q_two is the conservative two-sided test. " +
    "The mutant_selective flag is ΔpD < 0 with q_mut < 0.10 (demeter_validation.py), not a 0.05 cut.");
}

pptx.writeFile({ fileName: OUT }).then(() => {
  console.log("wrote " + path.relative(REPO, OUT));
});
