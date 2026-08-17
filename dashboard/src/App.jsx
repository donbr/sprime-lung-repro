import React, { useState, useMemo, useEffect } from 'react';
import { 
  Activity, 
  BarChart3, 
  FlaskConical, 
  Layers, 
  CheckCircle2, 
  AlertTriangle, 
  Info, 
  Sliders, 
  ShieldCheck,
  Dna,
  Presentation,
  ChevronLeft,
  ChevronRight
} from 'lucide-react';
import './index.css';

// --- DATASETS DERIVED FROM REPOSITORY EXECUTION ---
const GENE_DATA = {
  PTEN: {
    tested: 883,
    rawCandidates: 97,
    nullMean: 97.0,
    empP: 0.461,
    permFDR: 1.00,
    offset: -0.015,
    centredCandidates: 3,
    ciExcl0: 85,
    strictCI: 26,
    pctEliminated: "73.2%",
    status: "FDR 1.00 (Pure Noise)",
    statusColor: "pill-red"
  },
  CDKN2A: {
    tested: 1402,
    rawCandidates: 48,
    nullMean: 41.7,
    empP: 0.315,
    permFDR: 0.87,
    offset: -0.050,
    centredCandidates: 6,
    ciExcl0: 29,
    strictCI: 3,
    pctEliminated: "93.8%",
    status: "FDR 0.87 (High Noise)",
    statusColor: "pill-red"
  },
  RB1: {
    tested: 1360,
    rawCandidates: 94,
    nullMean: 63.6,
    empP: 0.095,
    permFDR: 0.68,
    offset: 0.073,
    centredCandidates: 5,
    ciExcl0: 67,
    strictCI: 16,
    pctEliminated: "83.0%",
    status: "FDR 0.68 (Marginal Signal)",
    statusColor: "pill-amber"
  },
  TP53: {
    tested: 1402,
    rawCandidates: 16,
    nullMean: 20.3,
    empP: 0.596,
    permFDR: 1.27,
    offset: -0.125,
    centredCandidates: 3,
    ciExcl0: 4,
    strictCI: 1,
    pctEliminated: "93.8%",
    status: "FDR 1.27 (Pure Noise)",
    statusColor: "pill-red"
  }
};

const DEMETER_RNAI = [
  { gene: 'RB1', target: 'CDK6', deltaPD: 0.400, direction: 'WT-selective', qTwo: 0.00004, isControl: true },
  { gene: 'RB1', target: 'CDK4', deltaPD: 0.336, direction: 'WT-selective', qTwo: 0.0081, isControl: true },
  { gene: 'RB1', target: 'SKP2', deltaPD: -0.317, direction: 'mutant-selective', qTwo: 0.0081, isMutant: true },
  { gene: 'RB1', target: 'CCNE2', deltaPD: -0.152, direction: 'mutant-selective', qTwo: 0.0127, isMutant: true },
  { gene: 'RB1', target: 'E2F4', deltaPD: -0.127, direction: 'mutant-selective', qTwo: 0.0127, isMutant: true },
  { gene: 'RB1', target: 'AKT1', deltaPD: -0.104, direction: 'mutant-selective', qTwo: 0.0493, isMutant: true },
  { gene: 'RB1', target: 'AURKB', deltaPD: -0.120, direction: 'mutant-selective', qTwo: 0.5487, isNS: true },
  { gene: 'TP53', target: 'KIF11', deltaPD: -0.317, direction: 'mutant-selective', qTwo: 0.1159, isNS: true }
];

const PRESETS = [
  {
    name: "Doxorubicin / A549 (Anchor)",
    upper: 100.0,
    lower: 0.103,
    ec50: 0.24491,
    hill: 1.0,
    cRef: 1.0,
    desc: "Validation anchor point: S' = 6.7040 (correcting original 7.38 error)"
  },
  {
    name: "Partial Kill (Emax < 50%)",
    upper: 100.0,
    lower: 60.0,
    ec50: 0.1,
    hill: 1.2,
    cRef: 1.0,
    desc: "IC50 is undefined because response fails to reach 50% kill, but S' remains well-behaved"
  },
  {
    name: "Disinhibitory / Proliferative",
    upper: 120.0,
    lower: 20.0,
    ec50: 1.0,
    hill: 1.0,
    cRef: 1.0,
    desc: "Upper asymptote > 100% (cell proliferation). S' becomes negative."
  },
  {
    name: "Flat Noise Artifact (Aspirin)",
    upper: 100.0,
    lower: 98.0,
    ec50: 0.001,
    hill: 0.8,
    cRef: 1.0,
    desc: "Flat curve with noise. Illustrates Issue M1 fit-quality gap where unidentifiable EC50 causes S' explosion"
  }
];

const SLIDES = [
  {
    title: "1. Executive Overview & Repository Purpose",
    subtitle: "sprime-lung-repro: Reproducible S′ Drug Response Analysis",
    content: (
      <div>
        <p style={{ marginBottom: '1rem', color: 'var(--text-muted)' }}>
          A deterministic, checksum-guarded computational biology reproduction suite evaluating S′ drug-response metrics across PTEN, CDKN2A, RB1, and TP53 backgrounds in 94 lung cancer cell lines.
        </p>

        <div className="grid-2col" style={{ marginTop: '1.5rem' }}>
          <div className="metric-box highlight">
            <div className="metric-lbl">Key Scientific Finding</div>
            <div style={{ fontSize: '1.1rem', fontWeight: '700', color: 'var(--accent-cyan)', marginTop: '0.25rem' }}>
              Most Proposed Hits Are Background Noise
            </div>
            <div className="metric-val-sub" style={{ marginTop: '0.5rem' }}>
              PTEN (FDR 1.00), CDKN2A (FDR 0.87), and TP53 (FDR 1.27) fail permutation nulls. Only RB1 (FDR 0.68) exhibits marginal signal.
            </div>
          </div>

          <div className="metric-box alert-box">
            <div className="metric-lbl">Strict Gate Impact</div>
            <div style={{ fontSize: '1.1rem', fontWeight: '700', color: 'var(--accent-rose)', marginTop: '0.25rem' }}>
              73% to 94% Candidate Elimination
            </div>
            <div className="metric-val-sub" style={{ marginTop: '0.5rem' }}>
              Requiring the whole 95% bootstrap CI to remain ≤ −2.0 drastically thins candidate hit lists across all four genes.
            </div>
          </div>
        </div>
      </div>
    )
  },
  {
    title: "2. Why Standard Curve Metrics Fail on HTS Data",
    subtitle: "Limitations of IC50 and AUC on Non-Canonical Dose-Response Curves",
    content: (
      <div>
        <div className="grid-2col">
          <div className="metric-box">
            <div className="metric-lbl" style={{ color: 'var(--accent-rose)' }}>Absolute IC50 Limitations</div>
            <ul style={{ fontSize: '0.85rem', color: 'var(--text-muted)', paddingLeft: '1.2rem', marginTop: '0.5rem' }}>
              <li><strong>High Missingness</strong>: Undefined if drug fails to achieve 50% kill (Emax &lt; 50%).</li>
              <li><strong>Explodes on Flat Curves</strong>: Returns arbitrary infinity values.</li>
            </ul>
          </div>

          <div className="metric-box">
            <div className="metric-lbl" style={{ color: 'var(--accent-amber)' }}>Area Under Curve (AUC) Limitations</div>
            <ul style={{ fontSize: '0.85rem', color: 'var(--text-muted)', paddingLeft: '1.2rem', marginTop: '0.5rem' }}>
              <li><strong>Loss of Directionality</strong>: Confounds partial kill with cell proliferation (y_max &gt; 100%).</li>
              <li><strong>Slope Insensitive</strong>: Ignores transition steepness.</li>
            </ul>
          </div>
        </div>

        <div className="metric-box highlight" style={{ marginTop: '1.25rem' }}>
          <div className="metric-lbl">The S′ Operational Solution</div>
          <div style={{ fontFamily: 'var(--font-mono)', fontSize: '1.1rem', color: 'var(--accent-cyan)', marginTop: '0.25rem' }}>
            S′ = asinh((Emax / EC50) × 1 µM)
          </div>
          <div className="metric-val-sub" style={{ marginTop: '0.35rem' }}>
            Combines response span (Emax) and relative potency (EC50) into a continuous, signed metric (S′ &gt; 0 inhibition, S′ &lt; 0 disinhibition).
          </div>
        </div>
      </div>
    )
  },
  {
    title: "3. Mathematical Formulation & ΔpS′ Threshold",
    subtitle: "Pharmacologic Meaning of ΔpS′ ≤ −2.0",
    content: (
      <div>
        <p style={{ color: 'var(--text-muted)', marginBottom: '1rem' }}>
          Over the active response regime (pS′ ≳ 1), a fixed differential gap <strong>ΔpS′ = pS′_WT − pS′_Mut ≤ −2.0</strong> mathematically converges to requiring a <strong>≥ e² ≈ 7.389× greater potency-efficacy ratio</strong> in mutant cells vs. wild-type cells.
        </p>

        <div className="metric-box highlight" style={{ marginBottom: '1.25rem' }}>
          <div className="metric-lbl">Corrected Worked Example Anchor</div>
          <div style={{ fontSize: '1.25rem', fontWeight: '700', color: 'var(--text-main)' }}>
            Doxorubicin / A549: S′ = <span style={{ color: 'var(--accent-cyan)' }}>6.7040</span>
          </div>
          <div className="metric-val-sub">
            Inputs: y_max = 100%, y_min = 0.103%, EC50 = 0.24491 µM. Corrects original manuscript error (7.382) and is frozen in tests/test_synthetic.py.
          </div>
        </div>
      </div>
    )
  },
  {
    title: "4. Control 1: Label-Permutation Null Model",
    subtitle: "2,000 Genotype Shuffles Reveal Background Noise Floor",
    content: (
      <div>
        <table className="custom-table" style={{ marginBottom: '1rem' }}>
          <thead>
            <tr>
              <th>Gene</th>
              <th>Tested</th>
              <th>Candidates (ΔpS′ ≤ −2)</th>
              <th>Null Mean</th>
              <th>Empirical p</th>
              <th>Perm FDR</th>
            </tr>
          </thead>
          <tbody>
            {Object.entries(GENE_DATA).map(([g, d]) => (
              <tr key={g}>
                <td style={{ fontWeight: '700' }}>{g}</td>
                <td>{d.tested}</td>
                <td style={{ fontWeight: '600', color: 'var(--accent-cyan)' }}>{d.rawCandidates}</td>
                <td>{d.nullMean.toFixed(1)}</td>
                <td>{d.empP.toFixed(3)}</td>
                <td>
                  <span className={`pill ${d.permFDR > 0.8 ? 'pill-red' : 'pill-amber'}`}>
                    {d.permFDR.toFixed(2)}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        <p className="metric-val-sub">
          Candidate lists generated by un-gated cutoffs are statistically indistinguishable from random noise for PTEN, CDKN2A, and TP53.
        </p>
      </div>
    )
  },
  {
    title: "5. Control 3: Bootstrap CI Uncertainty Gate",
    subtitle: "Sampling Resampling (B=2,000) Eliminates 73% to 94% of Candidates",
    content: (
      <div>
        <table className="custom-table">
          <thead>
            <tr>
              <th>Gene</th>
              <th>Point Candidates</th>
              <th>CI &lt; 0 (Loose Gate)</th>
              <th>CI ≤ −2.0 (Strict Gate)</th>
              <th>% Candidates Eliminated</th>
            </tr>
          </thead>
          <tbody>
            {Object.entries(GENE_DATA).map(([g, d]) => (
              <tr key={g}>
                <td style={{ fontWeight: '700' }}>{g}</td>
                <td>{d.rawCandidates}</td>
                <td>{d.ciExcl0}</td>
                <td style={{ fontWeight: '700', color: 'var(--accent-pink)' }}>{d.strictCI}</td>
                <td style={{ fontWeight: '700', color: 'var(--accent-rose)' }}>{d.pctEliminated}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    )
  },
  {
    title: "6. Control 4: DEMETER2 RNAi Target Recovery",
    subtitle: "Orthogonal Validation of RB1-Loss Vulnerabilities",
    content: (
      <div>
        <table className="custom-table">
          <thead>
            <tr>
              <th>Gene</th>
              <th>Target</th>
              <th>Effect Size (ΔpD)</th>
              <th>Direction</th>
              <th>q (q_two)</th>
              <th>Validation Status</th>
            </tr>
          </thead>
          <tbody>
            {DEMETER_RNAI.map((r, idx) => (
              <tr key={idx}>
                <td style={{ fontWeight: '700' }}>{r.gene}</td>
                <td style={{ fontWeight: '600', color: 'var(--accent-cyan)' }}>{r.target}</td>
                <td>{r.deltaPD > 0 ? `+${r.deltaPD.toFixed(3)}` : r.deltaPD.toFixed(3)}</td>
                <td>{r.direction}</td>
                <td>{r.qTwo < 0.0001 ? '<0.0001' : r.qTwo.toFixed(4)}</td>
                <td>
                  {r.isControl && <span className="pill pill-purple">WT-Selective Control</span>}
                  {r.isMutant && <span className="pill pill-green">Mutant-Selective (Validated)</span>}
                  {r.isNS && <span className="pill pill-amber">Non-Significant</span>}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    )
  },
  {
    title: "7. Primitive Feature Engineering Hierarchy",
    subtitle: "From Raw Assay Signals to Cohort Selectivity Features",
    content: (
      <div className="grid-3col">
        <div className="metric-box">
          <div className="metric-lbl" style={{ color: 'var(--accent-cyan)' }}>Tier 1: Raw Primitives</div>
          <ul style={{ fontSize: '0.85rem', color: 'var(--text-muted)', listStyle: 'none' }}>
            <li>• Concentration (C_k)</li>
            <li>• Readout Signal (I_k)</li>
            <li>• Negative Control (I_DMSO)</li>
            <li>• Positive Control (I_pos)</li>
            <li>• Time Zero Signal (I_t0)</li>
          </ul>
        </div>
        <div className="metric-box">
          <div className="metric-lbl" style={{ color: 'var(--accent-blue)' }}>Tier 2: 4PL Fits</div>
          <ul style={{ fontSize: '0.85rem', color: 'var(--text-muted)', listStyle: 'none' }}>
            <li>• Upper Asymptote (y_max)</li>
            <li>• Lower Asymptote (y_min)</li>
            <li>• Potency (EC50)</li>
            <li>• Hill Slope (h)</li>
            <li>• Emax Span</li>
          </ul>
        </div>
        <div className="metric-box highlight">
          <div className="metric-lbl" style={{ color: 'var(--accent-purple)' }}>Tier 3 & 4: Metrics</div>
          <ul style={{ fontSize: '0.85rem', color: 'var(--text-muted)', listStyle: 'none' }}>
            <li>• <strong>S′ Index</strong></li>
            <li>• Absolute IC50</li>
            <li>• AUC &amp; GR50</li>
            <li>• Differential ΔpS′</li>
          </ul>
        </div>
      </div>
    )
  },
  {
    title: "8. Summary & Best Practice Recommendations",
    subtitle: "Guidelines for Pharmacogenomic Discovery Pipelines",
    content: (
      <div className="funnel-step-list">
        <div className="metric-box highlight">
          <div style={{ fontWeight: '700', color: 'var(--accent-cyan)' }}>1. Adopt S′ Metric for Non-Canonical Curves</div>
          <div className="metric-val-sub">Use S′ over IC50/AUC to handle partial killing and disinhibition without missingness.</div>
        </div>

        <div className="metric-box alert-box">
          <div style={{ fontWeight: '700', color: 'var(--accent-rose)' }}>2. Always Apply Permutation & CI Controls</div>
          <div className="metric-val-sub">Never report raw point-estimate cutoff lists without permutation FDRs and strict bootstrap CI gating.</div>
        </div>

        <div className="metric-box">
          <div style={{ fontWeight: '700', color: 'var(--accent-purple)' }}>3. Implement Upstream Fit-Quality Filters</div>
          <div className="metric-val-sub">Require minimum response span (|Emax| &gt; 15%) before computing EC50 to prevent flat-curve noise explosion.</div>
        </div>
      </div>
    )
  }
];

export default function App() {
  const [activeTab, setActiveTab] = useState('simulator');
  const [selectedGene, setSelectedGene] = useState('RB1');
  const [currentSlide, setCurrentSlide] = useState(0);

  // --- SIMULATOR STATE ---
  const [upper, setUpper] = useState(100.0);
  const [lower, setLower] = useState(0.103);
  const [ec50, setEc50] = useState(0.24491);
  const [hill, setHill] = useState(1.0);
  const [cRef, setCRef] = useState(1.0);

  // Slide keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (activeTab !== 'presentation') return;
      if (e.key === 'ArrowRight' || e.key === 'Space') {
        setCurrentSlide((prev) => Math.min(prev + 1, SLIDES.length - 1));
      } else if (e.key === 'ArrowLeft') {
        setCurrentSlide((prev) => Math.max(prev - 1, 0));
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [activeTab]);

  // Apply preset
  const handleApplyPreset = (p) => {
    setUpper(p.upper);
    setLower(p.lower);
    setEc50(p.ec50);
    setHill(p.hill);
    setCRef(p.cRef);
  };

  // Metric Calculations
  const metrics = useMemo(() => {
    const emax = upper - lower;
    const ratio = (emax / ec50) * cRef;
    const sprime = Math.asinh(ratio);

    let ic50 = null;
    if (upper > 50 && lower < 50) {
      const term = (upper - lower) / (50 - lower) - 1;
      if (term > 0) {
        ic50 = ec50 * Math.pow(term, 1 / hill);
      }
    }

    const doses = [0.00061, 0.00244, 0.00977, 0.03906, 0.15625, 0.625, 2.5, 10.0];
    let aucSum = 0;
    for (let i = 0; i < doses.length; i++) {
      const c = doses[i];
      const y = lower + (upper - lower) / (1 + Math.pow(c / ec50, hill));
      aucSum += y;
    }
    const auc = (aucSum / (doses.length * 100));

    return {
      emax,
      ratio,
      sprime,
      ic50,
      auc
    };
  }, [upper, lower, ec50, hill, cRef]);

  // Curve SVG Points Generator
  const curvePoints = useMemo(() => {
    const points = [];
    const minLog = Math.log10(0.0001);
    const maxLog = Math.log10(100);
    const width = 500;
    const height = 240;

    for (let i = 0; i <= 100; i++) {
      const logC = minLog + (i / 100) * (maxLog - minLog);
      const c = Math.pow(10, logC);
      const yVal = lower + (upper - lower) / (1 + Math.pow(c / ec50, hill));
      
      const x = 40 + ((logC - minLog) / (maxLog - minLog)) * (width - 60);
      const y = height - 30 - ((yVal - (-20)) / (140 - (-20))) * (height - 50);
      points.push(`${x.toFixed(1)},${y.toFixed(1)}`);
    }
    return points.join(' ');
  }, [upper, lower, ec50, hill]);

  return (
    <div className="app-container">
      <div className="bg-ambient">
        <div className="ambient-orb-1"></div>
        <div className="ambient-orb-2"></div>
      </div>

      {/* HEADER SECTION */}
      <header className="header-wrapper">
        <div className="header-top">
          <div className="header-title-group">
            <h1>
              <Activity className="text-cyan-400" size={36} />
              S′ Pharmacogenomics Hub
            </h1>
            <p className="header-subtitle">
              Interactive Dose-Response Curve Simulator, Statistical Control Visualizer & Feature Engineering Navigator
            </p>
          </div>
          <div className="badge-tag">
            <ShieldCheck size={14} />
            Verified Seed: 20260811
          </div>
        </div>

        {/* NAVIGATION TABS */}
        <div className="nav-tabs-container">
          <button 
            className={`nav-tab-btn ${activeTab === 'simulator' ? 'active' : ''}`}
            onClick={() => setActiveTab('simulator')}
          >
            <FlaskConical size={16} /> 4PL Curve & S′ Simulator
          </button>
          <button 
            className={`nav-tab-btn ${activeTab === 'controls' ? 'active' : ''}`}
            onClick={() => setActiveTab('controls')}
          >
            <BarChart3 size={16} /> Statistical Control Funnel
          </button>
          <button 
            className={`nav-tab-btn ${activeTab === 'demeter' ? 'active' : ''}`}
            onClick={() => setActiveTab('demeter')}
          >
            <Dna size={16} /> DEMETER2 RNAi Explorer
          </button>
          <button 
            className={`nav-tab-btn ${activeTab === 'hierarchy' ? 'active' : ''}`}
            onClick={() => setActiveTab('hierarchy')}
          >
            <Layers size={16} /> Primitive Feature Hierarchy
          </button>
          <button 
            className={`nav-tab-btn ${activeTab === 'presentation' ? 'active' : ''}`}
            onClick={() => setActiveTab('presentation')}
          >
            <Presentation size={16} /> Presentation Slide Deck
          </button>
          <button 
            className={`nav-tab-btn ${activeTab === 'verification' ? 'active' : ''}`}
            onClick={() => setActiveTab('verification')}
          >
            <CheckCircle2 size={16} /> Verification & Findings
          </button>
        </div>
      </header>

      {/* TAB 1: DOSE-RESPONSE SIMULATOR */}
      {activeTab === 'simulator' && (
        <div className="grid-2col">
          <div className="card">
            <div className="card-header">
              <div className="card-title">
                <Sliders size={20} className="text-cyan-400" />
                4PL Curve Parameter Controls
              </div>
            </div>

            <p className="metric-val-sub" style={{ marginBottom: '1rem' }}>
              Select a pharmacologic preset or adjust sliders to explore metric behavior:
            </p>

            <div className="preset-group">
              {PRESETS.map((p, idx) => (
                <button 
                  key={idx} 
                  className="preset-btn"
                  onClick={() => handleApplyPreset(p)}
                  title={p.desc}
                >
                  {p.name}
                </button>
              ))}
            </div>

            <div className="slider-group">
              <div className="slider-control">
                <div className="slider-label-row">
                  <span className="slider-name">Upper Asymptote (y_max)</span>
                  <span className="slider-val">{upper.toFixed(1)}%</span>
                </div>
                <input 
                  type="range" 
                  min="0" 
                  max="140" 
                  step="0.5"
                  value={upper}
                  onChange={(e) => setUpper(parseFloat(e.target.value))}
                />
              </div>

              <div className="slider-control">
                <div className="slider-label-row">
                  <span className="slider-name">Lower Asymptote (y_min)</span>
                  <span className="slider-val">{lower.toFixed(1)}%</span>
                </div>
                <input 
                  type="range" 
                  min="-20" 
                  max="100" 
                  step="0.5"
                  value={lower}
                  onChange={(e) => setLower(parseFloat(e.target.value))}
                />
              </div>

              <div className="slider-control">
                <div className="slider-label-row">
                  <span className="slider-name">Inflection Potency (EC50)</span>
                  <span className="slider-val">{ec50.toFixed(4)} µM</span>
                </div>
                <input 
                  type="range" 
                  min="0.0005" 
                  max="10.0" 
                  step="0.001"
                  value={ec50}
                  onChange={(e) => setEc50(parseFloat(e.target.value))}
                />
              </div>

              <div className="slider-control">
                <div className="slider-label-row">
                  <span className="slider-name">Hill Slope (h)</span>
                  <span className="slider-val">{hill.toFixed(2)}</span>
                </div>
                <input 
                  type="range" 
                  min="0.2" 
                  max="3.0" 
                  step="0.1"
                  value={hill}
                  onChange={(e) => setHill(parseFloat(e.target.value))}
                />
              </div>

              <div className="slider-control">
                <div className="slider-label-row">
                  <span className="slider-name">Reference Concentration (C_ref)</span>
                  <span className="slider-val">{cRef.toFixed(1)} µM</span>
                </div>
                <input 
                  type="range" 
                  min="0.1" 
                  max="10.0" 
                  step="0.1"
                  value={cRef}
                  onChange={(e) => setCRef(parseFloat(e.target.value))}
                />
              </div>
            </div>
          </div>

          <div className="card">
            <div className="card-header">
              <div className="card-title">
                <Activity size={20} className="text-cyan-400" />
                Dose-Response Curve & Real-Time Metrics
              </div>
            </div>

            <div className="chart-container">
              <svg className="svg-chart" viewBox="0 0 500 240">
                <line x1="40" y1="30" x2="480" y2="30" stroke="#1e293b" strokeDasharray="3,3" />
                <line x1="40" y1="105" x2="480" y2="105" stroke="#1e293b" strokeDasharray="3,3" />
                <line x1="40" y1="180" x2="480" y2="180" stroke="#1e293b" strokeDasharray="3,3" />
                <line x1="40" y1="105" x2="480" y2="105" stroke="rgba(245, 158, 11, 0.4)" strokeDasharray="4,4" />
                <text x="475" y="100" fill="#f59e0b" fontSize="10" textAnchor="end">50% Viability (IC50 threshold)</text>

                <text x="35" y="35" fill="#64748b" fontSize="10" textAnchor="end">120%</text>
                <text x="35" y="108" fill="#64748b" fontSize="10" textAnchor="end">50%</text>
                <text x="35" y="183" fill="#64748b" fontSize="10" textAnchor="end">0%</text>

                <text x="40" y="225" fill="#64748b" fontSize="10" textAnchor="start">0.0001 µM</text>
                <text x="260" y="225" fill="#64748b" fontSize="10" textAnchor="middle">0.1 µM</text>
                <text x="480" y="225" fill="#64748b" fontSize="10" textAnchor="end">100 µM</text>

                <polyline
                  fill="none"
                  stroke="#06b6d4"
                  strokeWidth="3"
                  points={curvePoints}
                />
              </svg>
            </div>

            <div className="metrics-grid">
              <div className="metric-box highlight">
                <div className="metric-lbl">S′ Operational Metric</div>
                <div className="metric-val-main" style={{ color: metrics.sprime < 0 ? '#f43f5e' : '#06b6d4' }}>
                  {metrics.sprime.toFixed(4)}
                </div>
                <div className="metric-val-sub">
                  asinh(({metrics.emax.toFixed(1)}% / {ec50.toFixed(4)}µM) × {cRef}µM)
                </div>
              </div>

              <div className={`metric-box ${metrics.ic50 === null ? 'alert-box' : ''}`}>
                <div className="metric-lbl">Absolute IC50</div>
                <div className="metric-val-main">
                  {metrics.ic50 !== null ? `${metrics.ic50.toFixed(4)} µM` : 'Undefined'}
                </div>
                <div className="metric-val-sub">
                  {metrics.ic50 !== null ? 'Concentration for 50% absolute kill' : 'Emax < 50% (No 50% kill reached)'}
                </div>
              </div>

              <div className="metric-box">
                <div className="metric-lbl">Area Under Curve (AUC)</div>
                <div className="metric-val-main">{metrics.auc.toFixed(3)}</div>
                <div className="metric-val-sub">Normalized integrated response</div>
              </div>

              <div className="metric-box">
                <div className="metric-lbl">Response Span (Emax)</div>
                <div className="metric-val-main">{metrics.emax.toFixed(1)}%</div>
                <div className="metric-val-sub">y_max ({upper.toFixed(1)}%) - y_min ({lower.toFixed(1)}%)</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* TAB 2: STATISTICAL CONTROL FUNNEL */}
      {activeTab === 'controls' && (
        <div className="grid-2col">
          <div className="card">
            <div className="card-header">
              <div className="card-title">
                <BarChart3 size={20} className="text-cyan-400" />
                Candidate Reduction Funnel by Gene
              </div>
              <div style={{ display: 'flex', gap: '0.5rem' }}>
                {Object.keys(GENE_DATA).map((g) => (
                  <button 
                    key={g} 
                    className={`preset-btn ${selectedGene === g ? 'active' : ''}`}
                    onClick={() => setSelectedGene(g)}
                    style={{
                      background: selectedGene === g ? 'var(--accent-cyan)' : '',
                      color: selectedGene === g ? '#000' : '',
                      fontWeight: selectedGene === g ? '700' : ''
                    }}
                  >
                    {g}
                  </button>
                ))}
              </div>
            </div>

            <p className="metric-val-sub" style={{ marginBottom: '1.25rem' }}>
              Showing how candidate hits thin when subjected to statistical controls for <strong>{selectedGene}</strong>:
            </p>

            <div className="funnel-step-list">
              <div className="funnel-step-item">
                <div className="metric-lbl" style={{ width: '130px' }}>1. Point Candidates</div>
                <div className="funnel-bar-wrapper">
                  <div className="funnel-bar-fill" style={{ width: '100%' }}>
                    <span className="funnel-bar-label">Raw Point Candidates (ΔpS′ ≤ −2)</span>
                  </div>
                </div>
                <div className="funnel-count">{GENE_DATA[selectedGene].rawCandidates}</div>
              </div>

              <div className="funnel-step-item">
                <div className="metric-lbl" style={{ width: '130px' }}>2. Exclude Zero</div>
                <div className="funnel-bar-wrapper">
                  <div 
                    className="funnel-bar-fill" 
                    style={{ 
                      width: `${(GENE_DATA[selectedGene].ciExcl0 / GENE_DATA[selectedGene].rawCandidates) * 100}%` 
                    }}
                  >
                    <span className="funnel-bar-label">95% CI Excludes Zero (ci_excl0)</span>
                  </div>
                </div>
                <div className="funnel-count">{GENE_DATA[selectedGene].ciExcl0}</div>
              </div>

              <div className="funnel-step-item">
                <div className="metric-lbl" style={{ width: '130px' }}>3. Strict Gate</div>
                <div className="funnel-bar-wrapper">
                  <div 
                    className="funnel-bar-fill strict" 
                    style={{ 
                      width: `${(GENE_DATA[selectedGene].strictCI / GENE_DATA[selectedGene].rawCandidates) * 100}%` 
                    }}
                  >
                    <span className="funnel-bar-label">Whole 95% CI ≤ −2.0 (strict)</span>
                  </div>
                </div>
                <div className="funnel-count" style={{ color: 'var(--accent-pink)' }}>
                  {GENE_DATA[selectedGene].strictCI}
                </div>
              </div>

              <div className="funnel-step-item">
                <div className="metric-lbl" style={{ width: '130px' }}>4. Line-Centered</div>
                <div className="funnel-bar-wrapper">
                  <div 
                    className="funnel-bar-fill" 
                    style={{ 
                      width: `${(GENE_DATA[selectedGene].centredCandidates / GENE_DATA[selectedGene].rawCandidates) * 100}%`,
                      background: 'var(--accent-amber)'
                    }}
                  >
                    <span className="funnel-bar-label">Line-Centered Candidates</span>
                  </div>
                </div>
                <div className="funnel-count" style={{ color: 'var(--accent-amber)' }}>
                  {GENE_DATA[selectedGene].centredCandidates}
                </div>
              </div>
            </div>

            <div style={{ marginTop: '1.5rem', paddingTop: '1rem', borderTop: '1px solid var(--bg-card-border)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <div className="metric-lbl">Strict Gate Candidate Reduction</div>
                <div className="metric-val-main" style={{ color: 'var(--accent-rose)', fontSize: '1.4rem' }}>
                  {GENE_DATA[selectedGene].pctEliminated} Candidates Eliminated
                </div>
              </div>
              <span className={`pill ${GENE_DATA[selectedGene].statusColor}`}>
                {GENE_DATA[selectedGene].status}
              </span>
            </div>
          </div>

          <div className="card">
            <div className="card-header">
              <div className="card-title">
                <ShieldCheck size={20} className="text-cyan-400" />
                Permutation Null Model & Line-Centering
              </div>
            </div>

            <table className="custom-table">
              <thead>
                <tr>
                  <th>Gene</th>
                  <th>Tested</th>
                  <th>Candidates</th>
                  <th>Null Mean</th>
                  <th>Empirical p</th>
                  <th>Perm FDR</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(GENE_DATA).map(([g, d]) => (
                  <tr key={g} style={{ background: selectedGene === g ? 'rgba(6, 182, 212, 0.1)' : '' }}>
                    <td style={{ fontWeight: '700' }}>{g}</td>
                    <td>{d.tested}</td>
                    <td style={{ fontWeight: '600', color: 'var(--accent-cyan)' }}>{d.rawCandidates}</td>
                    <td>{d.nullMean.toFixed(1)}</td>
                    <td>{d.empP.toFixed(3)}</td>
                    <td>
                      <span className={`pill ${d.permFDR > 0.8 ? 'pill-red' : 'pill-amber'}`}>
                        {d.permFDR.toFixed(2)}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            <div style={{ marginTop: '1.25rem', padding: '0.75rem', background: 'rgba(15, 23, 42, 0.6)', borderRadius: '0.5rem', border: '1px solid var(--bg-card-border)', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              <div style={{ fontWeight: '600', color: 'var(--accent-amber)', marginBottom: '0.25rem', display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                <AlertTriangle size={14} /> Critical Statistical Finding:
              </div>
              Label-permutation tests (2,000 shuffles) prove that PTEN (FDR 1.00), CDKN2A (FDR 0.87), and TP53 (FDR 1.27) candidate lists are indistinguishable from random genotype assignment. Only RB1 (FDR 0.68) exhibits marginal signal.
            </div>
          </div>
        </div>
      )}

      {/* TAB 3: DEMETER2 RNAI EXPLORER */}
      {activeTab === 'demeter' && (
        <div className="card">
          <div className="card-header">
            <div className="card-title">
              <Dna size={20} className="text-cyan-400" />
              DEMETER2 RNAi Genetic Dependency Cross-Check
            </div>
          </div>

          <p className="metric-val-sub" style={{ marginBottom: '1.25rem' }}>
            Orthogonal RNAi knockdown validation results (emitting exact two-sided FDR-corrected q-values):
          </p>

          <table className="custom-table">
            <thead>
              <tr>
                <th>Gene</th>
                <th>Target</th>
                <th>ΔpD Effect Size</th>
                <th>Direction</th>
                <th>Two-Sided q (q_two)</th>
                <th>Validation Status</th>
              </tr>
            </thead>
            <tbody>
              {DEMETER_RNAI.map((r, idx) => (
                <tr key={idx}>
                  <td style={{ fontWeight: '700' }}>{r.gene}</td>
                  <td style={{ fontWeight: '600', color: 'var(--accent-cyan)' }}>{r.target}</td>
                  <td style={{ fontFamily: 'var(--font-mono)' }}>{r.deltaPD > 0 ? `+${r.deltaPD.toFixed(3)}` : r.deltaPD.toFixed(3)}</td>
                  <td>{r.direction}</td>
                  <td style={{ fontFamily: 'var(--font-mono)' }}>{r.qTwo < 0.0001 ? '<0.0001' : r.qTwo.toFixed(4)}</td>
                  <td>
                    {r.isControl && <span className="pill pill-purple">WT-Selective Control</span>}
                    {r.isMutant && <span className="pill pill-green">Mutant-Selective (Validated)</span>}
                    {r.isNS && <span className="pill pill-amber">Non-Significant (q &gt; 0.05)</span>}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          <div style={{ marginTop: '1.5rem', padding: '1rem', background: 'rgba(139, 92, 246, 0.1)', borderRadius: '0.75rem', border: '1px solid rgba(139, 92, 246, 0.3)', fontSize: '0.85rem' }}>
            <h4 style={{ color: 'var(--accent-purple)', marginBottom: '0.35rem', display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
              <Info size={16} /> RB1 Mechanism Resolution (Issue M9):
            </h4>
            DEMETER2 RNAi data confirms mutant-selectivity for the <strong>RB–E2F axis (SKP2, CCNE2, E2F4, AKT1)</strong> and confirms <strong>CDK4/CDK6</strong> as wild-type selective positive controls. It does <em>not</em> support AURKB (q = 0.55) or PLK1.
          </div>
        </div>
      )}

      {/* TAB 4: PRIMITIVE FEATURE HIERARCHY */}
      {activeTab === 'hierarchy' && (
        <div className="card">
          <div className="card-header">
            <div className="card-title">
              <Layers size={20} className="text-cyan-400" />
              Dose-Response Feature Engineering Pipeline
            </div>
          </div>

          <div className="grid-3col">
            <div className="metric-box">
              <div className="metric-lbl" style={{ color: 'var(--accent-cyan)' }}>Tier 1: Raw Primitives</div>
              <ul style={{ fontSize: '0.85rem', color: 'var(--text-muted)', listStyle: 'none', padding: '0.5rem 0' }}>
                <li>• Dose / Concentration (C_k)</li>
                <li>• Raw Readout Signal (I_k)</li>
                <li>• Negative Control (I_DMSO)</li>
                <li>• Positive Control (I_pos)</li>
                <li>• Time Zero Signal (I_t0)</li>
              </ul>
            </div>

            <div className="metric-box">
              <div className="metric-lbl" style={{ color: 'var(--accent-blue)' }}>Tier 2: Fitted 4PL Parameters</div>
              <ul style={{ fontSize: '0.85rem', color: 'var(--text-muted)', listStyle: 'none', padding: '0.5rem 0' }}>
                <li>• Upper Asymptote (y_max)</li>
                <li>• Lower Asymptote (y_min)</li>
                <li>• Inflection Potency (EC50)</li>
                <li>• Hill Slope (h)</li>
                <li>• Response Span (Emax)</li>
              </ul>
            </div>

            <div className="metric-box highlight">
              <div className="metric-lbl" style={{ color: 'var(--accent-purple)' }}>Tier 3 & 4: Operational Metrics</div>
              <ul style={{ fontSize: '0.85rem', color: 'var(--text-muted)', listStyle: 'none', padding: '0.5rem 0' }}>
                <li>• <strong>S′ Index</strong> = asinh((Emax/EC50) × C_ref)</li>
                <li>• Absolute IC50 (requires y_min &lt; 50%)</li>
                <li>• Area Under Curve (AUC)</li>
                <li>• Growth Rate 50 (GR50)</li>
                <li>• Differential Contrast (ΔpS′)</li>
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* TAB 5: PRESENTATION SLIDE DECK */}
      {activeTab === 'presentation' && (
        <div className="card">
          <div className="card-header">
            <div className="card-title">
              <Presentation size={20} className="text-cyan-400" />
              {SLIDES[currentSlide].title}
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <span className="metric-lbl" style={{ margin: 0 }}>
                Slide {currentSlide + 1} of {SLIDES.length}
              </span>
              <button 
                className="preset-btn" 
                disabled={currentSlide === 0}
                onClick={() => setCurrentSlide((prev) => Math.max(prev - 1, 0))}
              >
                <ChevronLeft size={16} /> Prev
              </button>
              <button 
                className="preset-btn" 
                disabled={currentSlide === SLIDES.length - 1}
                onClick={() => setCurrentSlide((prev) => Math.min(prev + 1, SLIDES.length - 1))}
              >
                Next <ChevronRight size={16} />
              </button>
            </div>
          </div>

          <h3 style={{ fontSize: '1rem', color: 'var(--accent-cyan)', marginBottom: '1rem' }}>
            {SLIDES[currentSlide].subtitle}
          </h3>

          <div style={{ minHeight: '300px', padding: '1rem 0' }}>
            {SLIDES[currentSlide].content}
          </div>

          <div style={{ display: 'flex', justifyContent: 'center', gap: '0.35rem', marginTop: '1.5rem' }}>
            {SLIDES.map((_, idx) => (
              <div 
                key={idx}
                onClick={() => setCurrentSlide(idx)}
                style={{
                  width: idx === currentSlide ? '24px' : '8px',
                  height: '8px',
                  borderRadius: '4px',
                  background: idx === currentSlide ? 'var(--accent-cyan)' : 'var(--bg-card-border)',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease'
                }}
              />
            ))}
          </div>
        </div>
      )}

      {/* TAB 6: VERIFICATION & FINDINGS */}
      {activeTab === 'verification' && (
        <div className="card">
          <div className="card-header">
            <div className="card-title">
              <CheckCircle2 size={20} className="text-cyan-400" />
              Repository Verification Status & Review Issues
            </div>
          </div>

          <table className="custom-table">
            <thead>
              <tr>
                <th>Review Issue</th>
                <th>Manuscript Flaw</th>
                <th>Repository Resolution</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td style={{ fontWeight: '700' }}>B1: Circular Benchmark</td>
                <td>100% recovery claim on self-selected data</td>
                <td>Built literature-blind benchmark scaffold in concordance/</td>
                <td><span className="pill pill-green">Code Fix</span></td>
              </tr>
              <tr>
                <td style={{ fontWeight: '700' }}>B2: No Null Model</td>
                <td>Candidate window never tested against noise</td>
                <td>Added 2,000-perm null &amp; strict CI gates (73%–94% eliminated)</td>
                <td><span className="pill pill-green">Code Fix</span></td>
              </tr>
              <tr>
                <td style={{ fontWeight: '700' }}>B3: Sensitivity Confound</td>
                <td>Untested baseline cell line sensitivity</td>
                <td>Implemented line-centering in blocking_analyses.py</td>
                <td><span className="pill pill-green">Code Fix</span></td>
              </tr>
              <tr>
                <td style={{ fontWeight: '700' }}>B4: Worked Example</td>
                <td>Stated S′ = 7.382 (arithmetically wrong)</td>
                <td>Corrected to S′ = 6.7040 &amp; frozen assertion in tests/test_synthetic.py</td>
                <td><span className="pill pill-green">Code Fix</span></td>
              </tr>
              <tr>
                <td style={{ fontWeight: '700' }}>M1: Flat-Curve Fits</td>
                <td>Non-credible hits (aspirin, ranitidine)</td>
                <td>Diagnosed mechanism showing flat curves survive CIs; fit filter must run upstream</td>
                <td><span className="pill pill-amber">Diagnosis / Finding</span></td>
              </tr>
              <tr>
                <td style={{ fontWeight: '700' }}>M9: RNAi Validation</td>
                <td>Cited AURKB as RNAi-validated</td>
                <td>Corrected support to RB–E2F axis (SKP2, CCNE2, E2F4) &amp; CDK4/6 controls</td>
                <td><span className="pill pill-green">Code Fix</span></td>
              </tr>
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
