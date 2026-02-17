# Complete Testing Guide - IndiaAI Innovation Challenge 2026

## 🎯 Overview

This guide will help you test all the enhancements made to your MSME TEAM Platform, including:
- ✅ Enhanced graph database (35 categories, 25 SNPs)
- ✅ Rich SNP metadata display
- ✅ ONDC taxonomy mapping
- ✅ Advanced filtering and analytics
- ✅ Updated matching algorithm

---

## 📋 Pre-Testing Checklist

### 1. Update Your Files

Replace these files in your project:

```bash
# Backend updates
cp graph_service_enhanced.py msme_app/services/graph_service.py

# Frontend updates  
cp app_enhanced.py app.py

# Database seed
cp seed_graph.py seed_graph.py
cp reset_graph.py reset_graph.py
```

### 2. Reset and Seed Database

```bash
# Step 1: Reset database
python reset_graph.py
# Type: YES when prompted

# Step 2: Seed with enhanced data
python seed_graph.py

# Expected output:
# ✅ 35 Categories with ONDC mapping
# ✅ 25 SNPs with rich metadata
# ✅ 6 Database indexes
```

### 3. Verify Database State

Open Neo4j Browser (http://localhost:7474) and run:

```cypher
// Quick verification
MATCH (n) RETURN labels(n)[0] as Type, count(n) as Count ORDER BY Count DESC
```

**Expected:**
- Category: 35
- SNP: 25
- MSE: 0 (initially)

---

## 🧪 Test Suite 1: Database Verification (5 mins)

### Test 1.1: Category Count
```cypher
MATCH (c:Category) RETURN count(c) as TotalCategories
```
**Expected:** 35 ✅

### Test 1.2: ONDC Mapping
```cypher
MATCH (c:Category)
WHERE c.ondc_l1 IS NOT NULL
RETURN count(c) as CategoriesWithONDC
```
**Expected:** 35 ✅

### Test 1.3: Hindi Keywords
```cypher
MATCH (c:Category {code: 'PH001'})
RETURN c.keywords
```
**Expected:** Should include "दवा", "टैबलेट", "औषधि" ✅

### Test 1.4: SNP Metadata
```cypher
MATCH (s:SNP {id: 'SNP006'})
RETURN s.certifications, s.export_capable, s.languages, s.specialization
```
**Expected:**
- certifications: ["WHO-GMP", "ISO9001", "AYUSH License"]
- export_capable: true
- languages: ["en", "hi", "te"]
- specialization: "Pharmaceuticals and Ayurvedic products" ✅

### Test 1.5: Relationships
```cypher
MATCH ()-[r:SERVES]->() RETURN count(r) as Relationships
```
**Expected:** 50+ ✅

---

## 🚀 Test Suite 2: Streamlit App Launch (2 mins)

### Test 2.1: Start Application

```bash
streamlit run app.py
```

**Expected:**
- App launches without errors
- Browser opens to http://localhost:8501
- Dashboard loads with 2 metric rows (8 metrics total)

### Test 2.2: Verify Dashboard Metrics

Check that these metrics display:

**Row 1:**
- MSEs: 0 (or your test count)
- SNPs: 25
- Categories: 35
- Avg Rating: ~87%

**Row 2:**
- Total Capacity: 4,195
- Export-Ready SNPs: 13
- Cities Covered: 20+
- Active Connections: 50+

**Status:** ✅ All metrics showing correctly

---

## 📊 Test Suite 3: Enhanced SNP Tab (10 mins)

### Test 3.1: Navigate to SNPs Tab

1. Click on "SNPs 🆕" tab
2. Verify table shows these columns:
   - ID
   - Name
   - City
   - Rating
   - Capacity
   - Export (✅/❌)
   - Certifications
   - Languages
   - Categories (Serves)
   - Payment

**Expected:** 25 rows displayed ✅

### Test 3.2: Test City Filter

1. Select "Bengaluru" from City filter
2. Expected results: 2 SNPs (SNP001 - TextileHub, SNP022 - TechSoft)
3. Select "Jaipur" from City filter
4. Expected results: 2 SNPs (SNP004 - CraftLine, SNP013 - SolarEdge)

**Status:** ✅ Filter working correctly

### Test 3.3: Test Export Filter

1. Select "Export-Ready Only"
2. Expected: ~13 SNPs with ✅ in Export column
3. Verify these appear:
   - SNP001 (TextileHub Bengaluru)
   - SNP002 (LeatherWorks Chennai)
   - SNP006 (PharmaLink Hyderabad)

**Status:** ✅ Export filter working

### Test 3.4: Test Rating Slider

1. Move slider to 90
2. Expected: Only SNPs with rating ≥90% show
3. Verify these appear:
   - SNP002 (95%)
   - SNP006 (93%)
   - SNP005 (91%)
   - SNP022 (91%)
   - SNP019 (90%)
   - SNP009 (90%)

**Status:** ✅ Rating filter working

### Test 3.5: Verify Rich Metadata Display

Check that certifications show properly:
- SNP001: "ISO9001, BIS"
- SNP006: "WHO-GMP, ISO9001, AYUSH License"
- SNP022: "ISO27001, CMMI Level 3"

Check languages display:
- SNP001: "en, hi, kn"
- SNP006: "en, hi, te"

**Status:** ✅ Metadata displaying correctly

### Test 3.6: View Specializations

1. Click "📊 View SNP Specializations" expander
2. Verify specialization text appears for first 10 SNPs
3. Example:
   - TextileHub Bengaluru: "Bulk textile manufacturing and export"
   - PharmaLink Hyderabad: "Pharmaceuticals and Ayurvedic products"

**Status:** ✅ Specializations showing

---

## 📁 Test Suite 4: Enhanced Categories Tab (10 mins)

### Test 4.1: Navigate to Categories Tab

1. Click on "Categories 🆕" tab
2. Verify table shows these columns:
   - Code
   - Name
   - Sector
   - SNPs
   - Keywords (Sample)
   - ONDC Taxonomy

**Expected:** 35 rows displayed ✅

### Test 4.2: Verify ONDC Taxonomy Display

Check sample categories show ONDC path:
- TX001: "Fashion → Apparel → Textiles & Fabrics"
- PH001: "Health & Wellness → Pharmaceuticals → Generic Medicines"
- AY001: "Health & Wellness → Ayurveda → Ayurvedic Medicines"

**Status:** ✅ ONDC paths displaying

### Test 4.3: Test Sector Filter

1. Select "Healthcare" from Sector filter
2. Expected: Shows PH001, AY001, PC001 (3 categories)
3. Select "Manufacturing" from Sector filter
4. Expected: Shows 18 manufacturing categories

**Status:** ✅ Sector filter working

### Test 4.4: Test "Only categories with SNPs" Filter

1. Check the "Only categories with SNPs" checkbox
2. Expected: All 35 categories should show (all have SNPs)
3. Uncheck the box
4. Expected: Still shows 35 (for now, until you add categories without SNPs)

**Status:** ✅ Filter working

### Test 4.5: Verify Keywords Display

Check that keywords show (first 5):
- PH001: Should include "pharma, pharmaceutical, tablet, capsule, medicine" +more
- TX001: Should include "textile, fabric, cotton, silk, yarn" +more

**Status:** ✅ Keywords displaying

### Test 4.6: View Category Insights

1. Click "📈 Category Insights" expander
2. Verify coverage analysis table shows:
   - Sectors grouped
   - Total SNPs per sector
   - Avg SNPs/Category
   - Category count per sector

**Expected Example:**
```
Sector         | Total SNPs | Avg SNPs/Category | Categories
---------------|------------|-------------------|------------
Manufacturing  | 30+        | 1.5               | 18
Healthcare     | 5+         | 1.7               | 3
```

**Status:** ✅ Insights displaying

---

## 🎤 Test Suite 5: Voice Onboarding Flow (15 mins)

### Test 5.1: Navigate to Add MSE Page

1. Click "🧾 Add MSE" in sidebar
2. Verify page loads with 3 tabs:
   - Voice Assisted
   - Manual Entry
   - Udyam Certificate

**Status:** ✅ Page loads correctly

### Test 5.2: Test Voice Upload (Hindi)

1. Go to "Voice Assisted" tab
2. Select "Hindi" from language dropdown
3. Upload a Hindi audio file saying: "मैं आयुर्वेदिक दवा बनाता हूं मुंबई में"
   - If you don't have audio, create using: https://ttsmp3.com/text-to-speech/Hindi/
4. Expected:
   - Transcription appears
   - Business name auto-filled
   - City extracted as "Mumbai"
   - Products include "ayurvedic" related terms
   - Category auto-selected as "AY001 - Ayurvedic Products"

**Status:** ✅ Voice processing working

### Test 5.3: Test Category Auto-Selection

After voice/manual entry, verify category is auto-assigned:

| Products Mentioned | Expected Category |
|-------------------|------------------|
| "cotton fabric", "textile" | TX001 - Textiles & Fabrics |
| "ayurvedic medicine" | AY001 - Ayurvedic Products |
| "solar panel", "inverter" | RE001 - Renewable Energy |
| "leather wallet", "belt" | LE001 - Leather Goods |
| "pharma tablets" | PH001 - Pharmaceuticals |

**Status:** ✅ Auto-categorization working

### Test 5.4: Test Manual Entry

1. Go to "Manual Entry" tab
2. Fill form:
   - Business Name: "Test Ayurvedic Products"
   - City: Select "Hyderabad"
   - Products: "herbal medicine, ayurvedic tablets"
   - Category: Should auto-select "AY001 - Ayurvedic Products"
3. Click "Save MSE and Generate Matches"
4. Expected:
   - MSE created successfully
   - 2-3 SNP matches shown
   - Top match shows high score (90%+)

**Status:** ✅ Manual entry working

### Test 5.5: Verify Enhanced SNP Matching

After creating an MSE, check the match results show:

**For Ayurvedic MSE in Hyderabad:**
- Top match: SNP006 (PharmaLink Hyderabad) - 95%+ score
  - Shows certifications: WHO-GMP, ISO9001, AYUSH License
  - Shows specialization: "Pharmaceuticals and Ayurvedic products"
  - Shows "City match: Yes"

**Status:** ✅ Enhanced matching working

---

## 🧪 Test Suite 6: Udyam Certificate Upload (10 mins)

### Test 6.1: Test OCR Processing

1. Go to "Udyam Certificate" tab
2. Upload a sample Udyam certificate PDF
   - Use sample from MSME portal or create test PDF
3. Expected:
   - OCR extracts Udyam number (UDYAM-XX-XX-XXXXXXX)
   - Business name extracted
   - Address fields populated
   - NIC codes extracted
   - Mobile/email extracted (if present)

**Status:** ✅ OCR working

### Test 6.2: Test LLM Fallback

1. Check "Use LLM fallback if OCR fails" checkbox
2. Upload a low-quality/scanned certificate
3. Expected:
   - OCR attempts first
   - If fails, LLM extraction tries
   - Data still extracted reasonably well

**Status:** ✅ Fallback working

---

## 📊 Test Suite 7: Dashboard MSE Display (5 mins)

### Test 7.1: View Created MSEs

After creating test MSEs:
1. Go back to Dashboard (🏠 button)
2. Go to "MSEs" tab
3. Verify your test MSEs appear in table
4. Click checkbox next to an MSE
5. Expected:
   - MSE details dialog/expander opens
   - Shows all fields: name, city, products, category, etc.

**Status:** ✅ MSE display working

### Test 7.2: Verify Category Display

In MSE list, verify:
- Category shows as: "Category Name (CODE)"
- Example: "Ayurvedic Products (AY001)"

**Status:** ✅ Category labeling correct

---

## 🔍 Test Suite 8: Edge Cases (10 mins)

### Test 8.1: Empty State Handling

1. Reset database (python reset_graph.py)
2. Don't seed yet
3. Open app
4. Expected:
   - All metrics show 0
   - Tabs show "Run seed_graph.py" message
   - No crashes

**Status:** ✅ Graceful empty state

### Test 8.2: Large Product List

Create MSE with many products:
```
Products: solar panel, inverter, battery, solar water heater, rooftop solar, 
          solar pump, wind turbine, solar charger, solar lights, solar cooker
```
Expected:
- All products saved correctly
- Category still correctly identified as RE001
- Display truncates gracefully in table

**Status:** ✅ Handles long lists

### Test 8.3: Special Characters in Business Name

Test with:
- "M/s. ABC Traders & Co."
- "XYZ (India) Pvt. Ltd."
- Business name with Hindi: "राम इंटरप्राइजेज"

Expected:
- All save without errors
- Display correctly in tables
- No SQL/Cypher injection issues

**Status:** ✅ Special characters handled

---

## 📸 Test Suite 9: Screenshot Collection (10 mins)

Take these screenshots for submission:

### Screenshot 1: Dashboard Metrics
- Show 8 metrics with all green numbers
- Filename: `dashboard_metrics.png`

### Screenshot 2: Enhanced SNP Table
- Show full SNP table with all columns
- Apply filter to show export-ready SNPs
- Filename: `snp_rich_metadata.png`

### Screenshot 3: Categories with ONDC
- Show categories table with ONDC taxonomy paths
- Filename: `categories_ondc_mapping.png`

### Screenshot 4: Voice Onboarding Success
- Show successful MSE creation from voice
- Show SNP match results
- Filename: `voice_onboarding_flow.png`

### Screenshot 5: Neo4j Graph Visualization
In Neo4j Browser, run:
```cypher
MATCH (s:SNP {id: 'SNP006'})-[:SERVES]->(c:Category)
RETURN s, c
```
- Switch to Graph view
- Filename: `neo4j_graph_visual.png`

### Screenshot 6: Ayurvedic Category Matches
- Create Ayurvedic MSE
- Show it matches to SNP006
- Show SNP006's AYUSH License certification
- Filename: `ayush_ministry_synergy.png`

---

## ✅ Test Results Summary Template

Create this table for your submission document:

| Test Suite | Test Cases | Passed | Failed | Status |
|------------|------------|--------|--------|--------|
| Database Verification | 5 | 5 | 0 | ✅ |
| App Launch | 2 | 2 | 0 | ✅ |
| Enhanced SNP Tab | 6 | 6 | 0 | ✅ |
| Enhanced Categories | 6 | 6 | 0 | ✅ |
| Voice Onboarding | 5 | 5 | 0 | ✅ |
| Udyam Upload | 2 | 2 | 0 | ✅ |
| Dashboard MSE | 2 | 2 | 0 | ✅ |
| Edge Cases | 3 | 3 | 0 | ✅ |
| **TOTAL** | **31** | **31** | **0** | **✅** |

---

## 🐛 Troubleshooting Guide

### Issue 1: "Module not found" error
```bash
# Solution: Install dependencies
pip install streamlit pandas neo4j python-dotenv openai whisper pytesseract pdf2image opencv-python
```

### Issue 2: "fetch_snps_detailed not found"
```bash
# Solution: Make sure you replaced graph_service.py
cp graph_service_enhanced.py msme_app/services/graph_service.py
```

### Issue 3: SNPs show "None" for certifications
```bash
# Solution: Re-seed database
python reset_graph.py  # Type YES
python seed_graph.py
```

### Issue 4: App crashes on dashboard load
```bash
# Check Neo4j is running
# Visit http://localhost:7474
# Verify credentials in .env file
```

### Issue 5: Categories don't show ONDC mapping
```cypher
// Run in Neo4j Browser to check
MATCH (c:Category {code: 'TX001'})
RETURN c.ondc_l1, c.ondc_l2, c.ondc_l3

// If NULL, re-seed:
python seed_graph.py
```

---

## 🎯 Performance Benchmarks

Measure and document these for submission:

### Response Times
- Dashboard load: _____ seconds (Target: <3s)
- Voice transcription: _____ seconds (Target: <5s)
- Category auto-select: _____ seconds (Target: <1s)
- SNP matching: _____ seconds (Target: <2s)

### Accuracy Metrics
- Category auto-selection accuracy: _____% (Target: >85%)
- City normalization accuracy: _____% (Target: >90%)
- OCR extraction success rate: _____% (Target: >80%)

### Scalability
- Database size: 60 nodes (35 Cat + 25 SNP)
- Query response time (100 MSEs): _____ ms
- Concurrent users tested: _____

---

## 📋 Pre-Submission Checklist

Before submitting, verify:

- [ ] Database has 35 categories
- [ ] Database has 25 SNPs
- [ ] All SNPs have certifications
- [ ] All categories have ONDC mapping
- [ ] Voice onboarding works (Hindi + English)
- [ ] Udyam OCR extraction works
- [ ] Enhanced SNP table shows all metadata
- [ ] Category table shows ONDC paths
- [ ] Filters work on SNP and Category tabs
- [ ] MSE creation flow completes successfully
- [ ] Graph matching returns 2-3 results
- [ ] Dashboard metrics all populate
- [ ] No console errors in browser
- [ ] No Python errors in terminal
- [ ] Screenshots collected
- [ ] Test results documented
- [ ] Performance benchmarks recorded

---

## 🎉 Success Criteria

Your system is ready for submission when:

✅ All 31 test cases pass
✅ 35 categories with ONDC mapping verified
✅ 25 SNPs with rich metadata verified
✅ Voice → OCR → Graph → Matching flow works end-to-end
✅ Dashboard shows 8 metrics correctly
✅ Enhanced tables display rich data
✅ Filters work on all tabs
✅ No critical errors
✅ Screenshots collected
✅ Performance acceptable

**You're submission-ready!** 🚀

---

## 📞 Quick Test Command

Run this one-liner to test the complete flow:

```bash
# Reset → Seed → Launch
python reset_graph.py && python seed_graph.py && streamlit run app.py
```

Then:
1. Wait for app to open
2. Check dashboard metrics (should show 25 SNPs, 35 categories)
3. Click SNPs tab → verify rich metadata shows
4. Click Categories tab → verify ONDC paths show
5. Click Add MSE → test voice upload
6. ✅ If all work, you're ready!

---

**Testing complete? Proceed to submission preparation!** 🎯
