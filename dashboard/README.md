# S′ Pharmacogenomics Interactive Web Dashboard

An interactive React + Vite web dashboard and automated Playwright UI verification suite for simulating dose-response curves ($S'$, $\text{IC}_{50}$, $\text{AUC}$, $\text{GR}_{50}$), visualizing statistical control candidate funnels, exploring DEMETER2 RNAi targets, and presenting the scientific slide deck.

---

## 🚀 Quickstart & Loading the Web UI

### 1. Development Mode (Hot Module Replacement)
Run the Vite development server locally:

```bash
cd dashboard
npm install                  # install dependencies if not already done
npm run dev                  # serves on http://localhost:5173/
```

Open **`http://localhost:5173/`** in any web browser.

### 2. Automated Playwright UI Verification
To execute automated headless browser tests that step through all UI controls, presets, candidate reduction funnels, and DEMETER2 RNAi target rows while verifying numerical accuracy against the pipeline CSVs:

```bash
cd dashboard
node verify_ui.js
```

### 3. Production Build & Static Preview
To build the minified production bundle and preview it locally:

```bash
cd dashboard
npm run build                # builds static bundle into dist/
npm run preview              # serves production bundle locally
```

---

## 📊 Dashboard Modules & Features

1. **🧪 4PL Dose-Response Simulator**: Interactive sliders for $y_{\max}$, $y_{\min}$, $\text{EC}_{50}$, $h$, $C_{\text{ref}}$, and real-time SVG curve rendering. Includes presets for *Doxorubicin / A549 Anchor* ($S' = 6.7040$), *Partial Kill* ($E_{\max} < 50\%$), *Disinhibitory* ($y_{\max} > 100\%$), and *Flat Noise Artifacts* (Issue M1 fit-quality gap).
2. **📊 Statistical Control Funnel**: Candidate reduction funnels ($PTEN$, $CDKN2A$, $RB1$, $TP53$), label-permutation null FDRs, and line-centering sensitivity offsets.
3. **🧬 DEMETER2 RNAi Explorer**: Interactive table of $\Delta pD$ effect sizes, two-sided $q$-values ($q_{\text{two}}$), $RB1$ $E2F$-axis targets ($SKP2$, $CCNE2$, $E2F4$, $AKT1$), and $CDK4/CDK6$ WT controls.
4. **🗺️ Primitive Feature Hierarchy**: Visual 4-tier pipeline mapping raw experimental readouts $\to$ 4PL fits $\to$ operational metrics $\to$ genotype selectivity.
5. **🖥️ Presentation Slide Deck Player**: Interactive 11-slide presentation deck with slide counter, navigation buttons, and keyboard arrow key listeners (Left/Right arrows).
6. **🛡️ Verification & Findings Checklist**: Status table mapping referee review issues B1–B4, M1, and M9 to code resolutions.

---

## 🛠️ Architecture & Tech Stack

* **Framework**: React 19 + Vite 8
* **Styling**: Vanilla CSS (`src/index.css`) with custom CSS variables, dark mode theme, glassmorphism cards, and Google Fonts (`Outfit`, `Inter`, `JetBrains Mono`).
* **Icons**: `lucide-react`
* **Automation & Testing**: `@playwright/test`
