# VCH-001: Redshift Decomposition Model

## 🧠 Hypothesis
Cosmological redshift can be decomposed into multiple physical components beyond metric expansion: gravitational time differentials arising from large-scale structure inhomogeneities (as in timescape cosmology), integrated Sachs-Wolfe effects, and potentially systematic environmental biases in distance calibration. This multi-component framework may help resolve the Hubble tension by accounting for previously neglected gravitational and environmental contributions to observed redshift-distance relationships.

---

## 🔍 Motivation
This hypothesis addresses the **5-6σ Hubble tension** between early-universe (Planck: H₀ = 67.4 ± 0.5 km/s/Mpc) and late-universe (SH0ES: H₀ = 73.04 ± 1.04 km/s/Mpc) measurements. Recent work has largely ruled out systematic errors and environmental effects as primary causes, suggesting new physics may be required.

**Theoretical Foundation:**
- **Wiltshire's Timescape Cosmology (2024)**: Strong Bayesian evidence favoring timescape over ΛCDM using Pantheon+ data, demonstrating ~35% clock rate differences between voids and dense regions
- **Buchert's Averaging Formalism**: Mathematical framework showing how local inhomogeneities create backreaction effects in cosmological evolution
- **Bondi's Redshift Decomposition (1947)**: Established that redshift contains separable kinematic and gravitational components

**Key Insight:** Rather than requiring new fundamental physics, the tension may arise from incomplete treatment of known gravitational effects in FLRW averaging, following established general relativity principles.

---

## 📚 Literature Review

**Hubble Tension Foundation:**
- **Riess et al. (SH0ES, 2024)**: H₀ = 73.04 ± 1.04 km/s/Mpc from Cepheid-calibrated SNe Ia, confirmed by JWST observations
- **Planck Collaboration (PR4, 2023)**: H₀ = 67.4 ± 0.5 km/s/Mpc from CMB assuming ΛCDM, yielding 5-6σ tension
- **Freedman et al. (CCHP, 2024)**: Independent distance ladder measurements support SH0ES results within uncertainties

**Timescape Cosmology:**
- **Wiltshire et al. (2024, MNRAS)**: "Supernovae evidence for foundational change to cosmological models" - Bayesian evidence favoring timescape over ΛCDM
- **Wiltshire (2007)**: Original timescape proposal showing ~35% clock rate differences between voids and walls
- **Buchert (2000, 2008)**: Mathematical formalism for averaging inhomogeneous cosmologies, foundation for backreaction effects

**Redshift Decomposition Theory:**
- **Bondi (1947)**: First systematic decomposition of cosmological redshift into kinematic and gravitational components
- **Bunn & Hogg (2009)**: Analysis of kinematic vs. gravitational interpretations using parallel transport
- **Sachs-Wolfe (1967)**: Gravitational redshift effects from evolving potentials, basis for ISW effect

**Environmental Studies:**
- **Conley et al. (2011)**: Analysis of SN Ia environments and their effect on distance measurements
- **Kim et al. (2019)**: Environmental dependence of Type Ia supernova properties in DES data
- **Multiple studies (2020-2024)**: General conclusion that environmental effects cannot fully explain Hubble tension magnitude

---

## 🧪 Observables
**Primary Observables:**
- Type Ia supernova distance modulus residuals vs. large-scale environment
- H₀ estimates from different environmental contexts (void vs. cluster lines-of-sight)
- Integrated Sachs-Wolfe signatures in CMB-galaxy cross-correlations

**Environmental Tracers:**
- Void probability functions from galaxy surveys (SDSS, DESI)
- Large-scale structure density fields and gravitational potential maps
- Peculiar velocity flows and their correlation with distance residuals

**Control Tests:**
- Comparison with time dilation observations (ruling out pure tired light)
- Surface brightness evolution (Tolman test consistency)
- CMB blackbody spectrum preservation

---

## 🔬 Methodology
**Phase 1: Environmental Analysis**
1. Correlate Pantheon+ SN residuals with large-scale environment using VIDE void catalogs
2. Perform statistical analysis controlling for host galaxy mass, morphology, and dust
3. Test for systematic H₀ variation as function of environmental density

**Phase 2: Gravitational Modeling**
4. Apply Buchert averaging formalism to quantify expected backreaction effects
5. Model gravitational redshift contributions using Sachs-Wolfe integral along photon paths
6. Compare predictions with observed residual patterns

**Phase 3: Validation**
7. Cross-validate with time dilation data (preserving expansion signature)
8. Ensure consistency with CMB observations and surface brightness evolution
9. Test predictions against independent datasets (DESI, Euclid upcoming)

**Key Datasets:**
- **Pantheon+ (2022)**: 1,701 spectroscopically confirmed Type Ia supernovae
- **VIDE**: Cosmic void catalogs from SDSS DR12
- **Planck PR4**: CMB temperature and polarization maps
- **6dFGS + SDSS peculiar velocity surveys**
- **Cosmological N-body simulations**: Millennium, IllustrisTNG for theoretical modeling

---

## 📈 Expected Results (If True)
**Quantitative Predictions:**
- Environmental H₀ variation: 2-4 km/s/Mpc difference between void and cluster lines-of-sight
- SN distance modulus residuals correlate with environmental density at >3σ significance
- Reduced χ² in cosmological fits when environmental corrections applied

**Specific Signatures:**
- **Void Supernovae**: Appear ~5-10% more distant than ΛCDM prediction (consistent with faster local time)
- **Cluster Supernovae**: Appear ~2-5% closer than prediction (slower local time)
- **H₀ Convergence**: Environmental averaging reduces tension from 5-6σ to <3σ

**Model Validation:**
- Backreaction effects of magnitude ~10⁻⁵ at z~0.1, scaling approximately as (1+z)
- Gravitational redshift contributions detectable in cross-correlation analyses
- Preserved time dilation signatures (distinguishing from pure tired light)

---

## ❌ Falsifiability Criteria
**Null Results (Falsifying Evidence):**
- SN distance residuals show no correlation with environmental density (p > 0.1)
- H₀ estimates independent of large-scale structure context within measurement uncertainties
- Environmental corrections fail to reduce Hubble tension below 4σ

**Alternative Explanations:**
- Systematic errors in environmental classification fully explain correlations
- Host galaxy properties (mass, metallicity, SFR) account for all observed residual patterns
- Pure metric expansion + known systematics explain all variation within 2σ

**Critical Tests:**
- **Time Dilation Consistency**: Any deviation from (1+z) time dilation falsifies the hypothesis
- **CMB Blackbody**: Any distortion of CMB spectrum rules out non-gravitational redshift mechanisms
- **Surface Brightness**: Deviation from (1+z)⁻⁴ evolution falsifies static universe components

---

## 🔗 Data & Tools
**Observational Data:**
- **Pantheon+ (2022)**: Complete sample of 1,701 Type Ia supernovae with systematic uncertainties
- **VIDE Void Catalog**: DR12-based cosmic void identification with >10,000 voids
- **Planck PR4**: Latest CMB temperature/polarization maps for ISW analysis
- **6dFGS/SDSS/2MRS**: Peculiar velocity measurements for kinematic decomposition

**Analysis Tools:**
- **CosmoMC/Cobaya**: MCMC parameter estimation with custom environmental likelihood
- **CAMB/CLASS**: Linear cosmological perturbation theory calculations
- **Healpy**: Spherical harmonic analysis for CMB-LSS cross-correlations
- **Scikit-learn**: Machine learning for environmental classification and bias detection

**Theoretical Framework:**
- **GRChombo/Einstein Toolkit**: Numerical relativity for backreaction calculations
- **Gadget/AREPO**: N-body simulations for environmental effect modeling

---

## 📝 Notes
**Critical Distinctions:**
- This hypothesis does **NOT** propose tired light as replacement for expansion
- All proposed effects are **gravitational** and consistent with general relativity
- Time dilation, CMB blackbody spectrum, and surface brightness evolution are preserved

**Systematic Controls:**
- Gravitational lensing effects estimated using ray-tracing through N-body simulations
- Peculiar velocity contributions modeled using measured flow fields
- Host galaxy property correlations controlled through stellar population synthesis

**Relationship to Literature:**
- Extends Wiltshire's timescape cosmology to observational predictions
- Implements Buchert's averaging formalism in practical analysis framework
- Complements VCH-002 (void chronometer) by providing redshift-level mechanism

**Model Limitations:**
- Assumes GR validity on all scales (no modified gravity)
- Limited by current void catalog completeness and accuracy
- Environmental effects may be partially degenerate with other systematics

---

## 👤 Authors
- Brad Senff (@bsenff)
- Drafted: July 2025
- Licensing: CC BY 4.0 (docs), Apache 2.0 (code)

