# VCH-001 Data Acquisition Plan

## Overview
This document outlines the practical steps to acquire and prepare data for testing the VCH-001 Redshift Decomposition hypothesis. The goal is to test whether Type Ia supernova distance residuals correlate with large-scale cosmic environment.

---

## Phase 1: Core Dataset Acquisition

### 1. Pantheon+ Supernova Catalog ⭐ **PRIORITY 1**
**What:** 1,701 Type Ia supernovae with standardized distance measurements  
**Why:** Primary observable for testing environmental distance variations

**Steps:**
```bash
# Download from GitHub
git clone https://github.com/PantheonPlusSH0ES/DataRelease.git
cd DataRelease/4_DISTANCES_AND_COVAR/
```

**Key Files:**
- `Pantheon+SH0ES.dat` - Main supernova catalog
- `Pantheon+SH0ES_STAT+SYS.cov` - Full covariance matrix
- Documentation in `README.md`

**Critical Columns:**
- CID (identifier), zCMB (redshift), MU (distance modulus)
- mB, x1, c (SALT2 parameters)
- RA, DEC (coordinates for environmental matching)
- MU_SYS_ERR, MU_STAT_ERR (uncertainties)

---

### 2. VIDE Void Catalog ⭐ **PRIORITY 2**
**What:** 10,643 cosmic voids from SDSS DR12  
**Why:** Environmental classification (void vs. cluster)

**Steps:**
```bash
# Download VIDE public catalog
wget http://www.cosmicvoids.net/data/VIDE_voids_SDSSdr12.dat
# Or use VIDE toolkit
git clone https://bitbucket.org/cosmicvoids/vide_public.git
```

**Key Files:**
- Void positions, effective radii, central densities
- Void membership catalogs
- Environmental density fields

**Quality Cut:** Use voids with 20-100 Mpc/h effective radii (1,228 voids)

---

### 3. SDSS DR12 Galaxy Data ⭐ **PRIORITY 3**
**What:** Galaxy positions and redshifts for environmental context  
**Why:** Large-scale structure mapping and density field reconstruction

**Access Methods:**
1. **SkyServer SQL:** https://skyserver.sdss.org/dr12/
2. **CasJobs:** For large queries (>500MB)
3. **Astro Data Lab:** https://datalab.noirlab.edu/data/sdss

**SQL Query Example:**
```sql
SELECT objID, ra, dec, z, petroMag_r, petroMagErr_r
FROM SpecObj 
WHERE z BETWEEN 0.01 AND 0.15 
  AND zWarning = 0 
  AND petroMag_r BETWEEN 14 AND 18
```

---

## Phase 2: Supplementary Data

### 4. Peculiar Velocity Corrections
**Options:**
- **6dFGS:** http://www-wfau.roe.ac.uk/6dFGS/vfield/
- **Cosmicflows-3:** https://projets.ip2i.in2p3.fr/cosmicflows/

**Purpose:** Correct for non-Hubble flow systematic effects

### 5. Environmental Density Fields
**Options:**
- Pre-computed from SDSS DR12
- Generate using galaxy number density smoothing
- Use existing MPA-JHU environment catalogs

---

## Phase 3: Data Preparation Workflow

### Step 1: Data Download and Validation
```bash
# Create data directory structure
mkdir -p datasets/{pantheon,vide,sdss,velocity}

# Download core datasets
cd datasets/pantheon/
git clone https://github.com/PantheonPlusSH0ES/DataRelease.git

cd ../vide/
wget http://www.cosmicvoids.net/data/VIDE_voids_SDSSdr12.dat

# Validate file integrity and formats
python validate_datasets.py
```

### Step 2: Cross-Matching
```python
# Coordinate-based matching between:
# 1. Pantheon+ SNe positions -> SDSS galaxy field
# 2. SN lines-of-sight -> Void catalog
# 3. Environmental density assignment

import astropy.coordinates as coords
from astropy import units as u

# Match SNe to nearest voids within search radius
# Classify environment: void, wall, cluster
```

### Step 3: Quality Control
- Remove SNe with poor photometry (x1, c outliers)
- Exclude regions with incomplete galaxy coverage
- Apply redshift cuts consistent across datasets (0.01 < z < 0.15)

---

## Expected Data Products

### Primary Analysis File:
**`vch001_analysis_sample.csv`**
```
Columns:
- sn_id: Pantheon+ identifier
- ra, dec: Coordinates  
- z_cmb: CMB-frame redshift
- mu_obs: Observed distance modulus
- mu_err: Total uncertainty
- env_class: void/wall/cluster
- void_distance: Distance to nearest void center
- env_density: Local galaxy density
- peculiar_v: Peculiar velocity correction
```

### Sample Size Estimates:
- **Total Pantheon+ SNe:** 1,701
- **SDSS footprint overlap:** ~1,400 SNe
- **Quality cuts:** ~1,200 SNe
- **Environmental classification:** ~1,000 SNe with robust void/cluster assignment

---

## Technical Requirements

### Software Dependencies:
```python
# Core analysis
numpy, pandas, matplotlib, scipy
astropy, healpy  # Astronomical calculations
scikit-learn     # Statistical analysis

# Cosmology-specific
colossus         # Cosmological calculations  
emcee, corner    # MCMC analysis
camb             # Theoretical predictions
```

### Computational Resources:
- **Storage:** ~5GB for all datasets
- **Memory:** 8GB RAM sufficient for analysis
- **Processing:** Standard laptop adequate

---

## Success Metrics

### Data Quality Targets:
- ✅ >1,000 SNe with environmental classification
- ✅ <10% missing data in key columns  
- ✅ Void/cluster samples with >100 SNe each
- ✅ Redshift range coverage 0.01 < z < 0.15

### Analysis Readiness:
- ✅ All datasets cross-matched and validated
- ✅ Environmental classifications assigned
- ✅ Systematic corrections applied
- ✅ Statistical framework established

---

## Timeline Estimate

- **Week 1:** Download and validate core datasets
- **Week 2:** Cross-matching and environmental classification  
- **Week 3:** Quality control and sample selection
- **Week 4:** Statistical analysis framework setup

**Total:** ~1 month to analysis-ready dataset

---

## Risk Mitigation

### Potential Issues:
1. **Incomplete overlap:** Pantheon+ SNe outside SDSS footprint
2. **Environmental degeneracy:** Ambiguous void/cluster classification
3. **Systematic errors:** Uncontrolled selection effects

### Mitigation Strategies:
1. Use multiple void catalogs for robustness
2. Implement probabilistic environmental classification
3. Extensive systematic testing with mock catalogs

---

*Next Step: Begin Phase 1 data acquisition starting with Pantheon+ catalog.*