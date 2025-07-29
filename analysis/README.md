# VCH-001 Analysis Framework

This directory contains the analysis framework for testing the VCH-001 Redshift Decomposition hypothesis.

## Directory Structure

```
analysis/
├── scripts/          # Python analysis scripts
│   ├── data_loader.py    # Load and validate datasets
│   └── requirements.txt  # Python dependencies
├── notebooks/        # Jupyter notebooks for exploration
├── results/          # Analysis outputs and tables
└── plots/           # Generated figures and visualizations
```

## Quick Start

### 1. Install Dependencies
```bash
cd analysis/scripts
pip install -r requirements.txt
```

### 2. Validate Data
```bash
python data_loader.py
```

### 3. Expected Output
```
==================================================
DATASET VALIDATION REPORT
==================================================

PANTHEON+ CATALOG:
  Total supernovae: 1701
  Redshift range: 0.001 - 2.260
  SNe in analysis range (0.01 < z < 0.15): ~800
  Has coordinates: True

VIDE VOID CATALOG:
  Total voids: 10643
  Possible coordinate columns: ['ra', 'dec', 'x', 'y', 'z']

✅ Data loading successful!
🎉 Ready to proceed with VCH-001 analysis!
```

## Analysis Workflow

### Phase 1: Data Preparation
1. **Load datasets** using `data_loader.py`
2. **Cross-match** supernova positions with void catalog
3. **Environmental classification** (void/wall/cluster)
4. **Quality control** and sample selection

### Phase 2: Statistical Analysis
1. **Distance residual calculation** vs. ΛCDM predictions
2. **Environmental correlation** testing
3. **Systematic error analysis** 
4. **Statistical significance** assessment

### Phase 3: Results
1. **H₀ variation** measurement across environments
2. **Hubble tension** mitigation assessment
3. **Model comparison** with standard cosmology

## Expected Results

If VCH-001 is correct, we expect:
- **2-4 km/s/Mpc H₀ variation** between void and cluster lines-of-sight
- **5-10% distance bias** in void supernovae (appear more distant)
- **3σ statistical significance** in environment-distance correlation
- **Reduced Hubble tension** when environmental effects included

## Key Files

- `data_loader.py` - Main data loading and validation
- `cross_match.py` - Coordinate matching between catalogs  
- `environmental_analysis.py` - Statistical testing framework
- `hubble_analysis.py` - H₀ measurement and comparison

## Data Requirements

### Downloaded Datasets
- **Pantheon+**: `../datasets/pantheon/DataRelease/4_DISTANCES_AND_COVAR/Pantheon+SH0ES.dat`
- **VIDE Voids**: `../datasets/vide/VIDE_voids_SDSSdr12.dat`

### Sample Sizes
- **Total SNe**: 1,701 (Pantheon+)
- **Analysis redshift range**: 0.01 < z < 0.15 (~800 SNe)
- **Environmental classification**: ~600 SNe with robust void/cluster assignment

---

*Next: Run `python data_loader.py` to validate your downloaded datasets*