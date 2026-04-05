# Professional Dashboard Polish Guide

## Theme V2 Changes

Import `data-quality-theme-v2.json` - Key improvements:

| Before | After |
|--------|-------|
| Heavy drop shadows | **No shadows** - flat, modern |
| White on white | Light gray page bg `#F9FAFB` + white cards |
| Harsh borders | Soft gray borders `#E5E7EB` |
| Visual header icons | **Hidden** - cleaner look |
| Default green | Modern emerald `#10B981` |

---

## Color Palette (Tailwind-inspired)

| Purpose | Color | Hex |
|---------|-------|-----|
| Success/GREEN | Emerald | `#10B981` |
| Warning/YELLOW | Amber | `#F59E0B` |
| Error/RED | Red | `#EF4444` |
| Primary accent | Blue | `#3B82F6` |
| Text primary | Gray 900 | `#111827` |
| Text secondary | Gray 500 | `#6B7280` |
| Text muted | Gray 400 | `#9CA3AF` |
| Border | Gray 200 | `#E5E7EB` |
| Card background | White | `#FFFFFF` |
| Page background | Gray 50 | `#F9FAFB` |

---

## Manual Polish Steps

### 1. Title Text Box
- Remove the border/background entirely (theme does this)
- Font: Segoe UI Semibold, 18pt
- Color: `#111827`
- Add subtle subtext: "Real-time data quality monitoring"
  - Font: Segoe UI, 10pt
  - Color: `#9CA3AF`

### 2. KPI Cards - Color the Numbers

**Current Score card:**
- Select card → Format → Callout value → Color → `#111827` (default)
- Add conditional formatting (fx):
  - If value >= 80: `#10B981` (green)
  - If value >= 70: `#F59E0B` (amber)
  - If value < 70: `#EF4444` (red)

**Current Status card:**
- Make "GREEN" text actually green: `#10B981`
- Make "YELLOW" text amber: `#F59E0B`  
- Make "RED" text red: `#EF4444`
- Use conditional formatting based on the Status value

### 3. Line Chart Polish

**Remove Y-axis title:**
- Format → Y-axis → Title → OFF

**Soften gridlines:**
- Format → Y-axis → Gridlines → Color: `#F3F4F6`

**Line styling:**
- Format → Lines → Stroke width: 2px
- Show markers: ON, size 5px

**Threshold line:**
- Analytics pane → Constant line → Value: 80
- Color: `#EF4444` (red)
- Style: Dashed
- Transparency: 50%

### 4. Donut Chart Polish

**Convert pie to donut:**
- Format → Slices → Inner radius: 65%

**Clean up labels:**
- Format → Detail labels → Show: Category + Percent
- Position: Outside

**Colors:**
- Green Count: `#10B981`
- Yellow Count: `#F59E0B`
- Red Count: `#EF4444`

### 5. Bar Chart Polish

**Sort descending:**
- Click chart → More options (...) → Sort by value (descending)

**Clean data labels:**
- Format → Data labels → Position: Inside end
- Color: `#FFFFFF` (white text on green bars)

**Remove axis title:**
- Format → X-axis → Title → OFF

### 6. Slicers Polish

**Date slicer:**
- Use "Between" style with slider
- Or use relative date: "Last 7 days"

**Status filter:**
- Use dropdown style (less space)
- Or use chiclet slicer (horizontal buttons)

---

## Spacing & Alignment

### Enable Helpers
View tab → Enable:
- ✅ Snap to grid
- ✅ Gridlines (temporarily for alignment)
- ✅ Lock objects (after positioning)

### Recommended Spacing
- **Margin from edge**: 16px
- **Gap between cards**: 12px
- **Gap between sections**: 16px

### Card Sizes (suggested)
| Visual | Width | Height |
|--------|-------|--------|
| KPI Cards | 180px | 90px |
| Line Chart | 520px | 200px |
| Donut Chart | 280px | 200px |
| Bar Chart | Full width | 180px |
| Title | Full width | 50px |
| Slicers | 160px each | 80px |

---

## Pro Typography

### Remove Redundant Labels
- Y-axis title "Sum of overall_sc..." → **Delete**
- X-axis title "measured_at" → **Delete** (dates are obvious)
- "Dimension Score" below bar chart → **Delete** (title is enough)

### Title Formatting
All chart titles should be:
- Font: Segoe UI Semibold
- Size: 11pt
- Color: `#374151`
- Alignment: Left

---

## Final Checklist

Before calling it done:

- [ ] Theme V2 imported
- [ ] Page background is light gray (not white)
- [ ] No shadows visible
- [ ] Visual header icons hidden
- [ ] GREEN/YELLOW/RED use correct colors
- [ ] Score card number is color-coded
- [ ] Line chart has red dashed threshold at 80
- [ ] Donut has 65% inner radius
- [ ] Bar chart sorted descending
- [ ] All titles are left-aligned, 11pt
- [ ] Gridlines disabled or very faint
- [ ] Date slicer is horizontal/compact
- [ ] Consistent spacing between visuals
- [ ] No axis titles (unless necessary)

---

## Quick Wins (Biggest Impact)

1. **Import theme V2** - instant improvement
2. **Hide visual headers** - removes clutter icons
3. **Color the score number** - conditional formatting
4. **Add threshold line** - shows the 80 cutoff
5. **Sort bar chart** - highest dimension first

These 5 changes will transform the dashboard from "student project" to "portfolio-ready".
