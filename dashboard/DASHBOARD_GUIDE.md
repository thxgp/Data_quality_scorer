# Power BI Dashboard Enhancement Guide

## Quick Start - Import Theme

1. Open your .pbix file in Power BI Desktop
2. Go to **View** → **Themes** → **Browse for themes**
3. Select `data-quality-theme.json` from this folder
4. Click **Open** - theme applies instantly

---

## Dashboard Layout (Recommended)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  DATA QUALITY MONITOR                                    [Date Slicer     ] │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐                    │
│  │  98.25   │  │  GREEN   │  │    21    │  │   210    │                    │
│  │  Score   │  │  Status  │  │  Checks  │  │ Records  │                    │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘                    │
│                                                                             │
│  ┌────────────────────────────────────────┐  ┌─────────────────────────┐   │
│  │                                        │  │                         │   │
│  │     Quality Score Trend (Line)         │  │   Status Distribution   │   │
│  │     ────────────────────────           │  │      (Donut Chart)      │   │
│  │                                        │  │                         │   │
│  └────────────────────────────────────────┘  └─────────────────────────┘   │
│                                                                             │
│  ┌────────────────────────────────────────┐  ┌─────────────────────────┐   │
│  │                                        │  │                         │   │
│  │     Quality Dimensions (Bar)           │  │    Recent Checks        │   │
│  │     Completeness ████████████ 100%     │  │    (Table)              │   │
│  │     Consistency  ███████████  98%      │  │                         │   │
│  │     Freshness    ████████████ 100%     │  │                         │   │
│  │                                        │  │                         │   │
│  └────────────────────────────────────────┘  └─────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Visual Enhancements

### 1. KPI Cards (Top Row)

**Score Card:**
- Display units: None (show full number)
- Category label: "Current Score"
- Conditional formatting on value:
  - >= 80: `#2E7D32` (green)
  - >= 70: `#F9A825` (amber)  
  - < 70: `#C62828` (red)

**Status Card:**
- Use a Card visual with your `[Current Status]` measure
- Add conditional background color:
  - GREEN: `#E8F5E9` (light green bg)
  - YELLOW: `#FFF8E1` (light amber bg)
  - RED: `#FFEBEE` (light red bg)

### 2. Line Chart - Score Trend

**Visual settings:**
- X-axis: `checked_at` (date)
- Y-axis: `overall_score`
- Add constant line at 80 (threshold):
  - Color: `#C62828` (red)
  - Style: Dashed
  - Transparency: 50%
- Line color: `#1565C0` (primary blue)
- Show data markers: ON
- Area fill: ON with 10% opacity

**Add conditional line color** (Advanced):
- Format → Data colors → fx
- Based on `overall_score`:
  - >= 80: `#2E7D32`
  - >= 70: `#F9A825`
  - < 70: `#C62828`

### 3. Donut Chart - Status Distribution

**Setup:**
- Legend: Status (GREEN/YELLOW/RED)
- Values: Count of checks
- Inner radius: 60% (creates donut)
- Colors:
  - GREEN: `#2E7D32`
  - YELLOW: `#F9A825`
  - RED: `#C62828`

**Polish:**
- Detail labels: Show both category + percentage
- Legend position: Bottom
- Title: "Health Status Distribution"

### 4. Bar Chart - Quality Dimensions

**Setup:**
- Y-axis: Dimension names (Completeness, Consistency, etc.)
- X-axis: Average score (0-100)
- Sort by value descending

**Conditional bar colors:**
- Format → Data colors → fx → Format by: Rules
  - >= 90: `#2E7D32`
  - >= 80: `#66BB6A`
  - >= 70: `#F9A825`
  - < 70: `#C62828`

**Add data labels:**
- Show: ON
- Display units: None
- Position: Inside end

### 5. Table - Recent Checks

**Columns to show:**
- checked_at (format: dd MMM, HH:mm)
- source_name
- overall_score
- health_status
- records_processed

**Styling:**
- Alternating row colors: OFF (cleaner look)
- Grid lines: Horizontal only
- Row padding: 6px

**Conditional formatting on health_status:**
- Background color by rules:
  - GREEN: `#E8F5E9`
  - YELLOW: `#FFF8E1`
  - RED: `#FFEBEE`

---

## Color Reference

| Purpose | Hex | Usage |
|---------|-----|-------|
| Primary Blue | `#1565C0` | Titles, accents, links |
| Success Green | `#2E7D32` | GREEN status, scores >= 80 |
| Warning Amber | `#F9A825` | YELLOW status, scores 70-80 |
| Error Red | `#C62828` | RED status, scores < 70 |
| Text Primary | `#212121` | Main titles |
| Text Secondary | `#616161` | Body text, labels |
| Text Muted | `#9E9E9E` | Captions, hints |
| Background | `#FAFAFA` | Page background |
| Card Background | `#FFFFFF` | Visual backgrounds |
| Border | `#E0E0E0` | Subtle borders |
| Grid Lines | `#EEEEEE` | Chart gridlines |

---

## Typography

- **Titles:** Segoe UI Semibold, 14pt
- **Headers:** Segoe UI Semibold, 12pt
- **Body/Labels:** Segoe UI, 10pt
- **Big Numbers (KPIs):** Segoe UI Light, 36pt

---

## Pro Tips

1. **Whitespace is your friend** - Don't cram visuals together, leave breathing room

2. **Align everything** - Use View → Snap to Grid and align card tops/bottoms

3. **Consistent sizing** - KPI cards should be same size, charts should align

4. **Remove clutter:**
   - Hide axis titles if obvious (Date, Score)
   - Remove chart borders if using shadows
   - Minimize gridlines

5. **Add a header** - Text box at top:
   - "DATA QUALITY MONITOR"
   - Font: Segoe UI Semibold, 20pt
   - Color: `#212121`

6. **Date slicer style:**
   - Use "Between" style (shows date range)
   - Or use relative date (Last 7 days, Last 30 days)

---

## DAX Measures Reference

To ensure your dashboard is dynamic and correctly formatted, use the following DAX measures:

### 1. Current Overall Score
Fetches the score from the most recent check.
```dax
Current Score = 
VAR LatestCheck = MAXX(ALL('quality_metrics'), 'quality_metrics'[measured_at])
RETURN
CALCULATE(
    MAX('quality_metrics'[overall_score]),
    'quality_metrics'[measured_at] = LatestCheck
)
```

### 2. Current Health Status
Returns the status (GREEN/YELLOW/RED) for the latest check.
```dax
Current Status = 
VAR LatestCheck = MAXX(ALL('quality_metrics'), 'quality_metrics'[measured_at])
RETURN
CALCULATE(
    MAX('quality_metrics'[status]),
    'quality_metrics'[measured_at] = LatestCheck
)
```

### 3. Status Color Logic
Use this measure for conditional formatting of background colors or text.
```dax
Status Color = 
SWITCH(
    [Current Status],
    "GREEN", "#2E7D32",
    "YELLOW", "#F9A825",
    "RED", "#C62828",
    "#212121"
)
```

### 4. Dimension Score (Bar Chart)
Ensures dimension scores (0.0-1.0) are displayed as percentages (0-100).
```dax
Dimension Score = AVERAGE('quality_metrics'[overall_score])
```

---

## Export for Portfolio

1. **Screenshot:** File → Export → Export to PDF (or use Snipping Tool for high-res PNG)

2. **If showing live:** 
   - Publish to Power BI Service (need Pro trial)
   - Embed in personal website via iframe

3. **Video demo:**
   - Record with OBS/screen recorder
   - Show filters interacting
   - Hover over data points
