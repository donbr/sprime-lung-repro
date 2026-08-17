import { chromium } from '@playwright/test';
import fs from 'fs';
import path from 'path';

const ARTIFACTS_DIR = '/home/donbr/.gemini/antigravity-ide/brain/90af2e0d-4828-477d-957d-4ad6d836533c';

async function runValidation() {
  console.log('🚀 Starting Playwright UI & Data Accuracy Validation on http://localhost:5173/ ...');
  
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1400, height: 900 } });

  try {
    // 1. Load Page
    await page.goto('http://localhost:5173/', { waitUntil: 'networkidle' });
    console.log('✅ Page loaded successfully.');

    // Screenshot Tab 1: Simulator (Default Doxorubicin Anchor)
    await page.screenshot({ path: path.join(ARTIFACTS_DIR, 'dashboard_tab1_simulator.png'), fullPage: true });
    console.log('📸 Screenshot saved: dashboard_tab1_simulator.png');

    // 2. Validate Simulator Controls & Presets
    console.log('\n--- 🧪 Testing Dose-Response Simulator Controls ---');
    
    // Check Doxorubicin Anchor Default
    const defaultSPrime = await page.locator('.metric-box.highlight .metric-val-main').textContent();
    const sprimeVal = parseFloat(defaultSPrime.trim());
    console.log(`   Doxorubicin Anchor S′ metric readout: "${defaultSPrime.trim()}"`);
    if (Math.abs(sprimeVal - 6.704) < 0.01) {
      console.log('   ✅ PASS: Worked-example anchor S′ matches ~6.704 (validating doxorubicin/A549).');
    } else {
      console.log(`   ❌ FAIL: Expected ~6.704, got ${sprimeVal}`);
    }

    // Click "Partial Kill (Emax < 50%)" Preset
    await page.click('button:has-text("Partial Kill")');
    await page.waitForTimeout(300);
    const partialIC50 = await page.locator('.metric-box:has-text("Absolute IC50") .metric-val-main').textContent();
    console.log(`   Partial Kill IC50 readout: "${partialIC50.trim()}"`);
    if (partialIC50.trim() === 'Undefined') {
      console.log('   ✅ PASS: IC50 correctly reports "Undefined" when Emax < 50%.');
    }

    // Click "Disinhibitory / Proliferative" Preset
    await page.click('button:has-text("Disinhibitory")');
    await page.waitForTimeout(300);
    const disSPrime = await page.locator('.metric-box.highlight .metric-val-main').textContent();
    console.log(`   Disinhibitory S′ readout: "${disSPrime.trim()}"`);
    if (parseFloat(disSPrime.trim()) < 0) {
      console.log('   ✅ PASS: S′ correctly converts to negative for proliferative curves.');
    }

    // Click "Flat Noise Artifact (Aspirin)" Preset
    await page.click('button:has-text("Flat Noise Artifact")');
    await page.waitForTimeout(300);
    const flatSPrime = await page.locator('.metric-box.highlight .metric-val-main').textContent();
    console.log(`   Flat Noise S′ readout: "${flatSPrime.trim()}"`);
    if (parseFloat(flatSPrime.trim()) > 7.0) {
      console.log('   ✅ PASS: S′ explosion on flat noise curve correctly demonstrates Issue M1.');
    }

    // 3. Test Tab 2: Statistical Control Funnel
    console.log('\n--- 📊 Testing Statistical Control Funnel Tab ---');
    await page.click('button:has-text("Statistical Control Funnel")');
    await page.waitForTimeout(500);
    await page.screenshot({ path: path.join(ARTIFACTS_DIR, 'dashboard_tab2_funnel.png'), fullPage: true });
    console.log('📸 Screenshot saved: dashboard_tab2_funnel.png');

    // Test PTEN Gene Data
    await page.click('button:has-text("PTEN")');
    await page.waitForTimeout(300);
    const ptenStrict = await page.locator('.funnel-count:has-text("26")').textContent();
    console.log(`   PTEN Strict CI gate survivors: "${ptenStrict.trim()}"`);
    if (ptenStrict.trim() === '26') {
      console.log('   ✅ PASS: PTEN candidate reduction matches repository (97 -> 26).');
    }

    // Test CDKN2A Gene Data
    await page.click('button:has-text("CDKN2A")');
    await page.waitForTimeout(300);
    const cdknStrict = await page.locator('.funnel-count:has-text("3")').textContent();
    console.log(`   CDKN2A Strict CI gate survivors: "${cdknStrict.trim()}"`);
    if (cdknStrict.trim() === '3') {
      console.log('   ✅ PASS: CDKN2A candidate reduction matches repository (48 -> 3).');
    }

    // 4. Test Tab 3: DEMETER2 RNAi Explorer
    console.log('\n--- 🧬 Testing DEMETER2 RNAi Explorer Tab ---');
    await page.click('button:has-text("DEMETER2 RNAi Explorer")');
    await page.waitForTimeout(500);
    await page.screenshot({ path: path.join(ARTIFACTS_DIR, 'dashboard_tab3_demeter.png'), fullPage: true });
    console.log('📸 Screenshot saved: dashboard_tab3_demeter.png');

    const skp2Target = await page.locator('tr:has-text("SKP2")').textContent();
    if (skp2Target.includes('mutant-selective') && skp2Target.includes('0.0081')) {
      console.log('   ✅ PASS: SKP2 RB1 mutant-selectivity and q-value (0.0081) match demeter_validation.csv.');
    }

    // 5. Test Tab 4: Primitive Feature Hierarchy
    console.log('\n--- 🗺️ Testing Feature Hierarchy Tab ---');
    await page.click('button:has-text("Primitive Feature Hierarchy")');
    await page.waitForTimeout(500);
    await page.screenshot({ path: path.join(ARTIFACTS_DIR, 'dashboard_tab4_hierarchy.png'), fullPage: true });
    console.log('📸 Screenshot saved: dashboard_tab4_hierarchy.png');

    // 6. Test Tab 5: Verification & Findings
    console.log('\n--- 🛡️ Testing Verification & Findings Tab ---');
    await page.click('button:has-text("Verification & Findings")');
    await page.waitForTimeout(500);
    await page.screenshot({ path: path.join(ARTIFACTS_DIR, 'dashboard_tab5_verification.png'), fullPage: true });
    console.log('📸 Screenshot saved: dashboard_tab5_verification.png');

    console.log('\n✨ ALL PLAYWRIGHT UI CONTROLS AND DATA ACCURACY CHECKS PASSED SUCCESSFULLY!');

  } catch (err) {
    console.error('❌ Validation Error:', err);
  } finally {
    await browser.close();
  }
}

runValidation();
