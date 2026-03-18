# Business Units — KPI Dashboard Framework

## Overview

Centralized KPI tracking for the 4 business units of VCF Group ecosystem.

| Business Unit | Location | Core Operations |
|---------------|----------|----------------|
| **VCF Group** | Thailand | Pig farming + feed production (4 feedmills) |
| **VC Meat Processing** | Thailand | Slaughterhouse, carcass processing, export (HK/SG/MY) |
| **VC Meat Distribution** | Thailand | 24 butcher shop branches, retail |
| **GT21 Myanmar** | Myanmar | Feedmill, pig farms, seed company, ethanol plant |

## Structure

Each BU folder contains:
- `kpi-definitions.yaml` — KPI metrics, targets, thresholds, units
- `README.md` — Business unit overview and KPI summary
- `data/` — CSV/Excel data files for actual KPI values

## How to Use

### 1. Manual KPI Entry
Place CSV files in `{BU}/data/` with columns matching KPI metric names.

### 2. Generate Dashboard
```bash
python3 main.py "Generate KPI dashboard for VCF-Group period 2026-03"
```

### 3. Generate Executive Summary (All BUs)
```bash
python3 main.py "Generate executive KPI summary for all business units"
```

## KPI Categories

All BUs track metrics across these standard categories:
- **Production/Operations** — Volume, efficiency, quality
- **Financial** — Revenue, costs, margins
- **Growth/Strategic** — Expansion, compliance, market metrics
- **People/HR** — Headcount, productivity

## Traffic Light System

| Status | Meaning | Threshold |
|--------|---------|-----------|
| GREEN | On/above target | >= 90% of target |
| YELLOW | Needs attention | 70-89% of target |
| RED | Critical | < 70% of target |

## Review Cadence

- **Weekly**: Operational KPIs (production, sales, inventory)
- **Monthly**: Financial KPIs + full dashboard generation
- **Quarterly**: Strategic KPIs + trend analysis
