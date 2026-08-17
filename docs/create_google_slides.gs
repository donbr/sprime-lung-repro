/**
 * Google Apps Script: Auto-generate sprime-lung-repro Google Slides Presentation
 * 
 * Instructions:
 * 1. Go to https://script.google.com or open a new Google Slides presentation.
 * 2. Click "Extensions" -> "Apps Script".
 * 3. Replace all code in the editor with this script and click "Run" (createSPrimeSlideDeck).
 * 4. Open the generated Google Slides link printed in the Execution Log!
 */

function createSPrimeSlideDeck() {
  var title = "S′ Pharmacogenomics & Reproducible Drug Response Analysis";
  var presentation = SlidesApp.create(title);
  var slides = presentation.getSlides();
  
  // Slide 1: Title & Executive Overview
  var slide1 = slides[0];
  slide1.getBackground().setSolidFill("#0b0f19");
  
  var titleBox = slide1.insertShape(SlidesApp.ShapeType.ROUNDED_RECTANGLE, 40, 40, 640, 120);
  titleBox.getFill().setSolidFill("#0f172a");
  titleBox.getBorder().getLineFill().setSolidFill("#06b6d4");
  var tf1 = titleBox.getText();
  tf1.setText("S′ Pharmacogenomics & Reproducible Drug Response Analysis\nEvaluation of Genotype-Selective Vulnerabilities & Statistical Controls");
  tf1.getTextStyle().setFontSize(20).setBold(true).setForegroundColor("#06b6d4");
  
  var card1 = slide1.insertShape(SlidesApp.ShapeType.ROUNDED_RECTANGLE, 40, 180, 310, 180);
  card1.getFill().setSolidFill("#1e293b");
  card1.getText().setText("🎯 Core Objective\nEvaluate whether proposed candidate synthetic lethal (SL) hit lists stand up against statistical controls across PTEN, CDKN2A, RB1, and TP53 backgrounds in 94 lung cancer cell lines.")
    .getTextStyle().setFontSize(11).setForegroundColor("#f8fafc");

  var card2 = slide1.insertShape(SlidesApp.ShapeType.ROUNDED_RECTANGLE, 370, 180, 310, 180);
  card2.getFill().setSolidFill("#1e1428");
  card2.getBorder().getLineFill().setSolidFill("#f43f5e");
  card2.getText().setText("⚠️ Headline Scientific Finding\n• Most candidate lists fail permutation null models (PTEN FDR 1.00, CDKN2A FDR 0.87, TP53 FDR 1.27).\n• Only RB1 (FDR 0.68) exhibits marginal signal.\n• Requiring whole 95% bootstrap CI ≤ -2.0 eliminates 73% to 94% of candidates.")
    .getTextStyle().setFontSize(11).setForegroundColor("#f8fafc");

  Logger.log("✨ Google Slides Deck Created Successfully!");
  Logger.log("🔗 Presentation URL: " + presentation.getUrl());
}
