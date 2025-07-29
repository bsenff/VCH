# VCH Data Acquisition Plan: Modules 003, 004, 005

**Date:** July 29, 2025  
**Purpose:** Acquire datasets for completing VCH-003, VCH-004, and VCH-005 analyses  
**Status:** VCH-001 ✅ | VCH-002 ✅ | VCH-003 📥 | VCH-004 📥 | VCH-005 📥

---

## VCH-003: CMB Void Entropy Signature Analysis

### **Required Datasets:**

**1. Planck CMB Temperature Maps**
- **Source:** Planck Legacy Archive (PLA) - ESA
- **URL:** https://pla.esac.esa.int/pla/
- **Specific Files Needed:**
  - `COM_CMB_IQU-commander_2048_R3.00_full.fits` (Temperature map)
  - `COM_CMB_IQU-smica_2048_R3.00_full.fits` (Alternative pipeline)
- **Format:** HEALPix FITS files, NSIDE=2048
- **Size:** ~200 MB per map
- **Resolution:** ~1.7 arcmin per pixel

**2. Planck CMB Masks**
- **Files:** `COM_Mask_CMB-confidence_2048_R3.00.fits`
- **Purpose:** Exclude contaminated regions (Galaxy, point sources)
- **Size:** ~50 MB

**3. CMB Power Spectrum (for validation)**
- **File:** `COM_PSM_CMB-spec_R3.01.fits`
- **Purpose:** Cross-validate temperature fluctuation statistics
- **Size:** ~1 MB

### **Download Commands:**
```bash
# Create CMB data directory
mkdir -p ../../datasets/planck_cmb/

# Download Planck temperature maps (using ESA PLA API or direct links)
wget -O ../../datasets/planck_cmb/COM_CMB_IQU-commander_2048_R3.00_full.fits \
  "https://pla.esac.esa.int/pla/aio/product-action?MAP.MAP_ID=COM_CMB_IQU-commander_2048_R3.00_full.fits"

wget -O ../../datasets/planck_cmb/COM_CMB_IQU-smica_2048_R3.00_full.fits \
  "https://pla.esac.esa.int/pla/aio/product-action?MAP.MAP_ID=COM_CMB_IQU-smica_2048_R3.00_full.fits"

# Download masks
wget -O ../../datasets/planck_cmb/COM_Mask_CMB-confidence_2048_R3.00.fits \
  "https://pla.esac.esa.int/pla/aio/product-action?MAP.MAP_ID=COM_Mask_CMB-confidence_2048_R3.00.fits"
```

**Alternative Access Methods:**
- **LAMBDA (NASA):** https://lambda.gsfc.nasa.gov/product/map/current/
- **IRSA (Caltech):** https://irsa.ipac.caltech.edu/Missions/planck.html
- **Direct FTP:** ftp://pla.esac.esa.int/data/PLANCK/

---

## VCH-004: High-z Galaxy Chronology Conflict Analysis

### **Required Datasets:**

**1. JWST High-Redshift Galaxy Catalogs**
- **Source:** MAST (Mikulski Archive for Space Telescopes)
- **URL:** https://mast.stsci.edu/portal/Mashup/Clients/Mast/Portal.html
- **Specific Surveys:**
  - **CEERS** (Cosmic Evolution Early Release Science): z > 8 galaxies
  - **JADES** (JWST Advanced Deep Extragalactic Survey): z > 10 galaxies  
  - **GLASS** (Grism Lens-Amplified Survey from Space): z > 7 galaxies
- **Key Catalogs:**
  - `ceers_nircam_v0.51.fits` (~10,000 galaxies, z = 0.2-15)
  - `jades_nircam_v1.0.fits` (~50,000 galaxies, z = 0.5-13)
- **Data Needed:** RA, Dec, photometric redshift, stellar mass, formation time

**2. HST Legacy High-z Catalogs (for comparison)**
- **Source:** 3D-HST Survey, CANDELS
- **Files:**
  - `3dhst_master.phot.v4.1.cat` (HST photometric catalog)
  - `candels_goodss_v1.0.fits` (CANDELS GOODS-South)
- **Purpose:** Pre-JWST high-z galaxy sample for comparison
- **Redshift Range:** z = 1-8 (HST limit)

**3. Theoretical Galaxy Formation Models**
- **Source:** Illustris-TNG, EAGLE, Millennium simulations
- **Files:** 
  - `illustris_galaxies_z8-15.hdf5` (galaxy formation predictions)
  - `eagle_public_galaxy_catalog.fits`
- **Purpose:** Compare observed vs predicted galaxy formation timing

### **Download Commands:**
```bash
# Create high-z galaxy directory
mkdir -p ../../datasets/high_z_galaxies/jwst/
mkdir -p ../../datasets/high_z_galaxies/hst/
mkdir -p ../../datasets/high_z_galaxies/simulations/

# JWST data (requires MAST authentication)
# Note: Large files, use astroquery for efficient download
python -c "
from astroquery.mast import Observations
obs = Observations.query_criteria(obs_collection='JWST', project='CEERS')
Observations.download_products(obs[:10], download_dir='../../datasets/high_z_galaxies/jwst/')
"

# HST legacy data
wget -O ../../datasets/high_z_galaxies/hst/3dhst_master.phot.v4.1.cat \
  "https://3dhst.research.yale.edu/Data/3dhst_master.phot.v4.1.cat"

# Simulation data (example - actual access varies by simulation)
wget -O ../../datasets/high_z_galaxies/simulations/illustris_sample.hdf5 \
  "https://www.illustris-project.org/api/IllustrisTNG/TNG100-1/snapshots/z8/subhalos/"
```

---

## VCH-005: Sky Pattern Artifact Analysis

### **Required Datasets:**

**1. Cosmological Simulation Outputs**
- **Source:** Millennium Simulation Database, Illustris-TNG
- **Files:**
  - `millennium_snapshot_z0.1.hdf5` (Local universe structure)
  - `tng100_snapshot_z0.0.hdf5` (TNG100 simulation at present)
  - `eagle_RefL0100N1504_snapshot_z0.000.hdf5` (EAGLE reference model)
- **Data Needed:** Dark matter halos, void catalog, galaxy positions
- **Purpose:** Compare simulated vs observed large-scale structure

**2. Observational Survey Footprints**
- **SDSS DR17 Footprint:**
  - `sdss_dr17_survey_geometry.fits`
  - **Purpose:** Define observational selection functions
- **Planck Survey Mask:**
  - `planck_survey_footprint.fits` 
  - **Purpose:** CMB observation boundaries
- **Future Survey Footprints:**
  - `euclid_survey_footprint.fits` (Euclid mission)
  - `roman_survey_footprint.fits` (Roman Space Telescope)

**3. Mock Catalog Generators**
- **Source:** CosmoDC2, MICE, Flagship simulations
- **Files:**
  - `cosmodc2_catalog_z0.1.fits` (Mock galaxy catalog)
  - `mice_void_catalog_v2.fits` (Mock void catalog)
- **Purpose:** Generate synthetic observations for comparison

### **Download Commands:**
```bash
# Create simulation analysis directory
mkdir -p ../../datasets/simulations/millennium/
mkdir -p ../../datasets/simulations/illustris/
mkdir -p ../../datasets/simulations/eagle/
mkdir -p ../../datasets/survey_footprints/
mkdir -p ../../datasets/mock_catalogs/

# Millennium simulation (via SQL query)
# Note: Requires registration at https://www.millenniumsimulation.org/
python -c "
import requests
# Example query - actual implementation needs authentication
query = 'SELECT x, y, z, mass FROM millimil..DarkHalo WHERE snapnum=63'
# Download would be via Millennium Database API
"

# Survey footprints
wget -O ../../datasets/survey_footprints/sdss_dr17_geometry.fits \
  "https://data.sdss.org/sas/dr17/eboss/lss/catalogs/DR16/geometry/sdss_dr17_survey_geometry.fits"

# Mock catalogs (example from MICE collaboration)
wget -O ../../datasets/mock_catalogs/mice_catalog_sample.fits \
  "https://www.ice.csic.es/research/cosmological_simulations/MICE/MICE_catalog_sample.fits"
```

---

## Data Storage Structure

### **Recommended Directory Organization:**
```
analysis/
├── datasets/
│   ├── pantheon/                    # ✅ Already acquired
│   ├── vide/                        # ✅ Already acquired  
│   ├── planck_cmb/                  # 📥 VCH-003 data
│   │   ├── temperature_maps/
│   │   ├── masks/
│   │   └── power_spectra/
│   ├── high_z_galaxies/             # 📥 VCH-004 data
│   │   ├── jwst/
│   │   ├── hst/
│   │   └── simulations/
│   ├── simulations/                 # 📥 VCH-005 data
│   │   ├── millennium/
│   │   ├── illustris/
│   │   └── eagle/
│   ├── survey_footprints/           # 📥 VCH-005 masks
│   └── mock_catalogs/               # 📥 VCH-005 validation
```

---

## Data Validation Requirements

### **VCH-003 Validation Targets:**
- **CMB temperature RMS:** ~100 μK (expected from Planck)
- **Map resolution:** NSIDE=2048 (1.7 arcmin pixels)
- **Sky coverage:** >80% (after masking)
- **Coordinate system:** Galactic coordinates (standard for CMB)

### **VCH-004 Validation Targets:**
- **Galaxy sample size:** >1,000 galaxies at z > 8
- **Redshift accuracy:** δz/(1+z) < 0.1 for photometric redshifts
- **Sky overlap:** Intersection with SDSS void catalog footprint
- **Stellar mass range:** 10⁸ - 10¹² M☉

### **VCH-005 Validation Targets:**
- **Simulation box size:** >500 Mpc/h (cosmological volume)
- **Mass resolution:** <10⁸ M☉/h (resolve void-forming halos)
- **Redshift range:** z = 0.0 - 0.2 (match observational data)
- **Cosmology consistency:** Planck18 parameters

---

## Data Access Credentials Required

### **Accounts Needed:**
1. **ESA Planck Legacy Archive:** Free registration at https://pla.esac.esa.int/
2. **MAST Archive (JWST):** Free registration at https://archive.stsci.edu/
3. **Millennium Simulation:** Registration at https://www.millenniumsimulation.org/
4. **ASTROQUERY:** Python package for automated downloads

### **Authentication Setup:**
```bash
# Install astroquery for automated data access
pip install astroquery

# Set up MAST authentication
python -c "
from astroquery.mast import Mast
Mast.login()  # Follow prompts for MAST token
"
```

---

## Expected Data Volumes

| Module | Dataset | Size | Download Time (100 Mbps) |
|--------|---------|------|---------------------------|
| **VCH-003** | Planck CMB maps | ~500 MB | 45 seconds |
| **VCH-003** | CMB masks/spectra | ~100 MB | 10 seconds |
| **VCH-004** | JWST catalogs | ~1 GB | 1.5 minutes |
| **VCH-004** | HST legacy | ~200 MB | 20 seconds |
| **VCH-005** | Simulation data | ~2-5 GB | 3-7 minutes |
| **VCH-005** | Mock catalogs | ~500 MB | 45 seconds |
| **TOTAL** | All datasets | ~4-7 GB | 6-10 minutes |

---

## Data Download Priority

### **Immediate Priority (VCH-003):**
1. **Planck CMB temperature maps** - Core analysis data
2. **CMB confidence masks** - Essential for contamination removal
3. **Power spectrum** - Validation and normalization

### **Medium Priority (VCH-004):**
1. **JWST CEERS catalog** - Most complete high-z sample
2. **3D-HST comparison data** - Establish pre-JWST baseline
3. **Theoretical models** - Framework validation

### **Lower Priority (VCH-005):**
1. **Millennium simulation** - Well-established reference
2. **Survey footprints** - Selection function modeling
3. **Mock catalogs** - Statistical validation

---

## Next Steps

### **Immediate Actions:**
1. **Create dataset directory structure**
2. **Set up data access credentials** (ESA, MAST accounts)
3. **Download VCH-003 CMB data** (highest priority)
4. **Validate VCH-003 with real Planck maps**
5. **Proceed to VCH-004 galaxy data acquisition**

### **Success Criteria:**
- All datasets successfully downloaded and validated
- Integration with existing VCH analysis framework
- Real data analysis producing scientifically meaningful results
- Complete documentation of data provenance and quality

---

**Status Summary:**
- **VCH-001:** ✅ Data complete (Pantheon+ SNe, VoidFinder voids)
- **VCH-002:** ✅ Data complete (Same as VCH-001)
- **VCH-003:** 📥 Ready to download (Planck CMB maps)
- **VCH-004:** 📥 Ready to download (JWST high-z galaxies)
- **VCH-005:** 📥 Ready to download (Cosmological simulations)

**Total estimated download time: 6-10 minutes for all remaining datasets**