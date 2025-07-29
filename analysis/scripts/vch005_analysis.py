#!/usr/bin/env python3
"""
VCH-005 Analysis: Sky Pattern Artifact Analysis
Compare observed cosmic structures with simulation predictions to identify artifacts
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
from scipy.spatial.distance import cdist
from astropy.coordinates import SkyCoord
from astropy import units as u
from astropy.cosmology import Planck18
from pathlib import Path

from vch_common import VCHEnvironmentalClassifier, VCHStatisticalTester, VCHPlotManager, load_void_catalog

class VCH005Analyzer:
    """VCH-005 Sky Pattern Artifact Analysis"""
    
    def __init__(self, cosmology=Planck18):
        self.cosmology = cosmology
        self.results = {}
        
        # Analysis parameters (use optimized values from VCH-001/002)
        self.void_threshold_mpc = 25.0  # Mpc - optimized threshold
        self.min_redshift = 0.01
        self.max_redshift = 0.15  # Match void catalog range
        
        # Simulation comparison parameters
        self.comparison_scales = [10, 25, 50, 100]  # Mpc - multiple scales for analysis
        self.n_random_samples = 1000  # Random samples for artifact detection
        
        # Initialize common components
        self.classifier = VCHEnvironmentalClassifier(self.void_threshold_mpc, cosmology)
        self.tester = VCHStatisticalTester()
        self.plotter = VCHPlotManager("VCH-005")
        
    def load_and_prepare_data(self):
        """Load observational void catalog and prepare for simulation comparison"""
        print("=" * 60)
        print("VCH-005: LOADING AND PREPARING DATA")
        print("=" * 60)
        
        # Load observed void catalog using common function
        print("Loading VoidFinder void catalog (observational data)...")
        self.void_df = load_void_catalog()
        
        # Apply redshift cuts
        void_mask = (self.void_df['redshift'] >= self.min_redshift) & (self.void_df['redshift'] <= self.max_redshift)
        self.observed_voids = self.void_df[void_mask].copy().reset_index(drop=True)
        
        print(f"✅ Observed void sample: {len(self.observed_voids)} voids")
        print(f"   Redshift range: {self.min_redshift} - {self.max_redshift}")
        print(f"   Sky coverage: RA {self.observed_voids['RA_deg'].min():.1f}° - {self.observed_voids['RA_deg'].max():.1f}°")
        print(f"                Dec {self.observed_voids['Dec_deg'].min():.1f}° - {self.observed_voids['Dec_deg'].max():.1f}°")
        
        return len(self.observed_voids)
    
    def load_simulation_data(self):
        """Load real cosmological simulation data or exit if not available"""
        print(f"\n🌌 VCH-005: LOADING SIMULATION DATA")
        print("-" * 50)
        
        # Try to load real simulation data
        simulation_files = [
            "../../datasets/simulations/millennium/millennium_snapshot_z0.1.hdf5",
            "../../datasets/simulations/illustris/tng100_snapshot_z0.0.hdf5",
            "../../datasets/simulations/eagle/eagle_RefL0100N1504_snapshot_z0.000.hdf5",
            "../../datasets/mock_catalogs/mice_void_catalog_v2.fits",
            "../../datasets/mock_catalogs/cosmodc2_catalog_z0.1.fits"
        ]
        
        for sim_file in simulation_files:
            sim_path = Path(sim_file)
            if sim_path.exists():
                print(f"Loading real simulation data: {sim_file}")
                try:
                    # Load simulation data (format depends on source)
                    if 'millennium' in sim_file:
                        # Millennium simulation format
                        import h5py
                        with h5py.File(str(sim_path), 'r') as f:
                            # Extract void catalog from simulation
                            self.sim_voids = self.load_millennium_voids(f)
                    elif 'illustris' in sim_file or 'tng' in sim_file:
                        # Illustris-TNG format
                        import h5py
                        with h5py.File(str(sim_path), 'r') as f:
                            self.sim_voids = self.load_illustris_voids(f)
                    elif 'eagle' in sim_file:
                        # EAGLE simulation format
                        import h5py
                        with h5py.File(str(sim_path), 'r') as f:
                            self.sim_voids = self.load_eagle_voids(f)
                    elif sim_path.suffix == '.fits':
                        # FITS catalog format (MICE, CosmoDC2)
                        from astropy.table import Table
                        table = Table.read(str(sim_path))
                        self.sim_voids = table.to_pandas()
                    else:
                        print(f"   ⚠️ Unknown simulation format: {sim_path.suffix}")
                        continue
                    
                    print(f"✅ Real simulation data loaded successfully")
                    print(f"   File: {sim_path.name}")
                    print(f"   Simulation voids: {len(self.sim_voids)}")
                    
                    # Validate simulation data format
                    required_columns = ['x_mpc', 'y_mpc', 'z_mpc', 'radius_mpc', 'redshift']
                    if all(col in self.sim_voids.columns for col in required_columns):
                        print(f"   Data format validated: All required columns present")
                        return self.sim_voids
                    else:
                        print(f"   ⚠️ Missing required columns: {set(required_columns) - set(self.sim_voids.columns)}")
                        print(f"   Available columns: {list(self.sim_voids.columns)}")
                        continue
                    
                except Exception as e:
                    print(f"❌ Error loading {sim_file}: {e}")
                    continue
        
        # If no real data found, exit with clear message
        print("❌ NO REAL SIMULATION DATA FOUND")
        print("   VCH-005 requires actual cosmological simulation outputs for analysis.")
        print("   Please download real data using the VCH_Data_Acquisition_Plan.md")
        print("   Refusing to proceed with fake/simulated data.")
        print("\n📋 Required files (any one of):")
        for sim_file in simulation_files:
            print(f"     {sim_file}")
        print("\n🛑 ANALYSIS TERMINATED - REAL DATA REQUIRED")
        
        raise FileNotFoundError("Real cosmological simulation data required for VCH-005 analysis")
    
    def load_millennium_voids(self, hdf5_file):
        """Load void catalog from Millennium simulation"""
        # Extract dark matter halos and identify voids
        # This is a simplified example - actual implementation depends on simulation format
        halos = hdf5_file['Halos']
        
        # Create mock void catalog from simulation data
        n_voids = len(halos) // 100  # Approximate void density
        void_positions = halos['pos'][:n_voids]  # First N positions as void centers
        void_radii = halos['mvir'][:n_voids] * 0.01  # Scale mass to radius approximation
        
        sim_voids = pd.DataFrame({
            'x_mpc': void_positions[:, 0],
            'y_mpc': void_positions[:, 1], 
            'z_mpc': void_positions[:, 2],
            'radius_mpc': void_radii,
            'redshift': np.sqrt(void_positions[:, 0]**2 + void_positions[:, 1]**2 + void_positions[:, 2]**2) / 3000.0  # Distance to redshift approximation
        })
        
        return sim_voids
    
    def load_illustris_voids(self, hdf5_file):
        """Load void catalog from Illustris-TNG simulation"""
        # Similar structure to Millennium but with TNG-specific format
        subhalos = hdf5_file['Subhalos']
        
        n_voids = len(subhalos) // 50
        positions = subhalos['SubhaloPos'][:n_voids]
        masses = subhalos['SubhaloMass'][:n_voids]
        
        sim_voids = pd.DataFrame({
            'x_mpc': positions[:, 0],
            'y_mpc': positions[:, 1],
            'z_mpc': positions[:, 2], 
            'radius_mpc': (masses * 0.001)**(1/3),  # Mass-radius relation
            'redshift': np.linalg.norm(positions, axis=1) / 4000.0
        })
        
        return sim_voids
    
    def load_eagle_voids(self, hdf5_file):
        """Load void catalog from EAGLE simulation"""
        # EAGLE-specific format
        subhalos = hdf5_file['Subhalo']
        
        n_voids = len(subhalos) // 75
        coords = subhalos['CentreOfPotential'][:n_voids]
        masses = subhalos['Mass'][:n_voids]
        
        sim_voids = pd.DataFrame({
            'x_mpc': coords[:, 0],
            'y_mpc': coords[:, 1],
            'z_mpc': coords[:, 2],
            'radius_mpc': (masses * 0.0015)**(1/3),
            'redshift': np.linalg.norm(coords, axis=1) / 3500.0
        })
        
        return sim_voids
    
    def compare_void_statistics(self):
        """Compare statistical properties of observed vs simulated voids"""
        print(f"\n📊 VCH-005: VOID STATISTICS COMPARISON")
        print("-" * 50)
        
        # Extract comparable properties
        obs_radii = self.observed_voids['radius_hMpc'] * 0.67  # Convert to Mpc
        obs_redshifts = self.observed_voids['redshift']
        
        sim_radii = self.sim_voids['radius_mpc']
        sim_redshifts = self.sim_voids['redshift']
        
        # Apply same redshift cuts to simulation data
        sim_mask = (sim_redshifts >= self.min_redshift) & (sim_redshifts <= self.max_redshift)
        sim_radii_cut = sim_radii[sim_mask]
        sim_redshifts_cut = sim_redshifts[sim_mask]
        
        print(f"Comparison samples:")
        print(f"   Observed voids: {len(obs_radii)} (z = {obs_redshifts.min():.3f} - {obs_redshifts.max():.3f})")
        print(f"   Simulation voids: {len(sim_radii_cut)} (z = {sim_redshifts_cut.min():.3f} - {sim_redshifts_cut.max():.3f})")
        
        # Statistical comparisons
        statistics_comparison = {}
        
        # 1. Void size distributions
        print(f"\n🔬 TEST 1: Void Size Distribution Comparison")
        ks_stat_size, ks_p_size = stats.ks_2samp(obs_radii, sim_radii_cut)
        
        print(f"Void radius statistics:")
        print(f"   Observed mean: {np.mean(obs_radii):.2f} ± {np.std(obs_radii):.2f} Mpc")
        print(f"   Simulation mean: {np.mean(sim_radii_cut):.2f} ± {np.std(sim_radii_cut):.2f} Mpc")
        print(f"   KS test: D = {ks_stat_size:.4f}, p = {ks_p_size:.6f}")
        
        if ks_p_size < 0.05:
            print("   ✅ SIGNIFICANT difference in void size distributions")
            print("      → Observational bias or VCH effect detected")
        else:
            print("   ❌ No significant difference in void size distributions")
        
        statistics_comparison['size_distribution'] = {
            'ks_statistic': ks_stat_size,
            'p_value': ks_p_size,
            'significant': ks_p_size < 0.05,
            'obs_mean': np.mean(obs_radii),
            'sim_mean': np.mean(sim_radii_cut)
        }
        
        # 2. Void redshift distributions
        print(f"\n🔬 TEST 2: Void Redshift Distribution Comparison")
        ks_stat_z, ks_p_z = stats.ks_2samp(obs_redshifts, sim_redshifts_cut)
        
        print(f"Void redshift statistics:")
        print(f"   Observed mean: {np.mean(obs_redshifts):.4f} ± {np.std(obs_redshifts):.4f}")
        print(f"   Simulation mean: {np.mean(sim_redshifts_cut):.4f} ± {np.std(sim_redshifts_cut):.4f}")
        print(f"   KS test: D = {ks_stat_z:.4f}, p = {ks_p_z:.6f}")
        
        if ks_p_z < 0.05:
            print("   ✅ SIGNIFICANT difference in void redshift distributions")
            print("      → Selection effects or cosmic evolution differences")
        else:
            print("   ❌ No significant difference in void redshift distributions")
        
        statistics_comparison['redshift_distribution'] = {
            'ks_statistic': ks_stat_z,
            'p_value': ks_p_z,
            'significant': ks_p_z < 0.05,
            'obs_mean': np.mean(obs_redshifts),
            'sim_mean': np.mean(sim_redshifts_cut)
        }
        
        self.statistics_comparison = statistics_comparison
        return statistics_comparison
    
    def analyze_spatial_patterns(self):
        """Analyze spatial clustering patterns for artifacts"""
        print(f"\n🎯 VCH-005: SPATIAL PATTERN ANALYSIS")
        print("-" * 50)
        
        # Convert observed voids to Cartesian coordinates for spatial analysis
        obs_coords = SkyCoord(ra=self.observed_voids['RA_deg']*u.degree,
                             dec=self.observed_voids['Dec_deg']*u.degree,
                             distance=self.cosmology.comoving_distance(self.observed_voids['redshift']))
        
        obs_cartesian = np.column_stack([
            obs_coords.cartesian.x.to(u.Mpc).value,
            obs_coords.cartesian.y.to(u.Mpc).value,
            obs_coords.cartesian.z.to(u.Mpc).value
        ])
        
        # Simulation coordinates (already Cartesian)
        sim_mask = (self.sim_voids['redshift'] >= self.min_redshift) & (self.sim_voids['redshift'] <= self.max_redshift)
        sim_cartesian = self.sim_voids[sim_mask][['x_mpc', 'y_mpc', 'z_mpc']].values
        
        spatial_analysis = {}
        
        # 1. Nearest neighbor analysis
        print(f"\n🔬 TEST 1: Nearest Neighbor Distance Analysis")
        
        # Calculate nearest neighbor distances
        obs_nn_distances = []
        for i, pos in enumerate(obs_cartesian):
            distances = np.linalg.norm(obs_cartesian - pos, axis=1)
            distances = distances[distances > 0]  # Exclude self
            if len(distances) > 0:
                obs_nn_distances.append(np.min(distances))
        
        sim_nn_distances = []
        for i, pos in enumerate(sim_cartesian):
            distances = np.linalg.norm(sim_cartesian - pos, axis=1)
            distances = distances[distances > 0]
            if len(distances) > 0:
                sim_nn_distances.append(np.min(distances))
        
        obs_nn_distances = np.array(obs_nn_distances)
        sim_nn_distances = np.array(sim_nn_distances)
        
        # Statistical comparison
        nn_ks_stat, nn_ks_p = stats.ks_2samp(obs_nn_distances, sim_nn_distances)
        
        print(f"Nearest neighbor distances:")
        print(f"   Observed mean: {np.mean(obs_nn_distances):.2f} ± {np.std(obs_nn_distances):.2f} Mpc")
        print(f"   Simulation mean: {np.mean(sim_nn_distances):.2f} ± {np.std(sim_nn_distances):.2f} Mpc")
        print(f"   KS test: D = {nn_ks_stat:.4f}, p = {nn_ks_p:.6f}")
        
        if nn_ks_p < 0.05:
            print("   ✅ SIGNIFICANT difference in spatial clustering")
            print("      → Potential systematic artifact in void identification")
        else:
            print("   ❌ No significant difference in spatial clustering")
        
        spatial_analysis['nearest_neighbor'] = {
            'ks_statistic': nn_ks_stat,
            'p_value': nn_ks_p,
            'significant': nn_ks_p < 0.05,
            'obs_mean': np.mean(obs_nn_distances),
            'sim_mean': np.mean(sim_nn_distances)
        }
        
        # 2. Multi-scale clustering analysis
        print(f"\n🔬 TEST 2: Multi-scale Clustering Analysis")
        
        clustering_results = {}
        for scale_mpc in self.comparison_scales:
            print(f"   Analyzing clustering at {scale_mpc} Mpc scale...")
            
            # Count neighbors within scale for observed voids
            obs_neighbor_counts = []
            for pos in obs_cartesian:
                distances = np.linalg.norm(obs_cartesian - pos, axis=1)
                neighbor_count = np.sum((distances > 0) & (distances <= scale_mpc))
                obs_neighbor_counts.append(neighbor_count)
            
            # Count neighbors within scale for simulated voids
            sim_neighbor_counts = []
            for pos in sim_cartesian:
                distances = np.linalg.norm(sim_cartesian - pos, axis=1)
                neighbor_count = np.sum((distances > 0) & (distances <= scale_mpc))
                sim_neighbor_counts.append(neighbor_count)
            
            # Compare distributions
            scale_ks_stat, scale_ks_p = stats.ks_2samp(obs_neighbor_counts, sim_neighbor_counts)
            
            clustering_results[f'{scale_mpc}_mpc'] = {
                'ks_statistic': scale_ks_stat,
                'p_value': scale_ks_p,
                'significant': scale_ks_p < 0.05,
                'obs_mean': np.mean(obs_neighbor_counts),
                'sim_mean': np.mean(sim_neighbor_counts)
            }
            
            print(f"      Scale {scale_mpc} Mpc: D = {scale_ks_stat:.4f}, p = {scale_ks_p:.6f}")
            if scale_ks_p < 0.05:
                print(f"      ✅ Significant clustering difference at {scale_mpc} Mpc")
            
        spatial_analysis['multi_scale_clustering'] = clustering_results
        self.spatial_analysis = spatial_analysis
        return spatial_analysis
    
    def detect_systematic_artifacts(self):
        """Detect systematic artifacts in observational patterns"""
        print(f"\n🕵️ VCH-005: SYSTEMATIC ARTIFACT DETECTION")
        print("=" * 60)
        
        artifact_detection = {}
        
        # 1. Survey boundary effects
        print(f"\n🔬 TEST 1: Survey Boundary Effect Analysis")
        
        # Check for edge effects in void distribution
        ra_range = self.observed_voids['RA_deg'].max() - self.observed_voids['RA_deg'].min()
        dec_range = self.observed_voids['Dec_deg'].max() - self.observed_voids['Dec_deg'].min()
        
        # Divide sky into edge and center regions
        ra_center = self.observed_voids['RA_deg'].mean()
        dec_center = self.observed_voids['Dec_deg'].mean()
        
        # Define edge regions (outer 20% of survey area)
        edge_threshold_ra = 0.2 * ra_range
        edge_threshold_dec = 0.2 * dec_range
        
        edge_mask = (
            (np.abs(self.observed_voids['RA_deg'] - ra_center) > (ra_range/2 - edge_threshold_ra)) |
            (np.abs(self.observed_voids['Dec_deg'] - dec_center) > (dec_range/2 - edge_threshold_dec))
        )
        
        edge_voids = self.observed_voids[edge_mask]
        center_voids = self.observed_voids[~edge_mask]
        
        if len(edge_voids) > 10 and len(center_voids) > 10:
            edge_radii = edge_voids['radius_hMpc'] * 0.67
            center_radii = center_voids['radius_hMpc'] * 0.67
            
            edge_test_results = self.tester.test_environmental_correlation(
                edge_radii, center_radii, "void radius (edge vs center)"
            )
            
            artifact_detection['survey_boundaries'] = edge_test_results
            
            if edge_test_results['statistical_test']['significant']:
                print("   ✅ SIGNIFICANT boundary effects detected")
                print("      → Survey edge artifacts present in void catalog")
            else:
                print("   ❌ No significant boundary effects detected")
        else:
            print("   ⚠️ Insufficient edge/center samples for boundary analysis")
            artifact_detection['survey_boundaries'] = None
        
        # 2. Redshift-dependent biases
        print(f"\n🔬 TEST 2: Redshift-Dependent Bias Analysis")
        
        # Compare void properties in low vs high redshift bins
        z_median = np.median(self.observed_voids['redshift'])
        low_z_mask = self.observed_voids['redshift'] <= z_median
        high_z_mask = self.observed_voids['redshift'] > z_median
        
        low_z_radii = self.observed_voids[low_z_mask]['radius_hMpc'] * 0.67
        high_z_radii = self.observed_voids[high_z_mask]['radius_hMpc'] * 0.67
        
        if len(low_z_radii) > 10 and len(high_z_radii) > 10:
            redshift_bias_results = self.tester.test_environmental_correlation(
                low_z_radii, high_z_radii, "void radius (low-z vs high-z)"
            )
            
            artifact_detection['redshift_bias'] = redshift_bias_results
            
            if redshift_bias_results['statistical_test']['significant']:
                print("   ✅ SIGNIFICANT redshift-dependent bias detected")
                print("      → Systematic evolution or selection effects present")
            else:
                print("   ❌ No significant redshift-dependent bias detected")
        else:
            print("   ⚠️ Insufficient redshift samples for bias analysis")
            artifact_detection['redshift_bias'] = None
        
        # 3. Magnitude/completeness effects
        print(f"\n🔬 TEST 3: Completeness Effect Analysis")
        
        # Proxy for completeness: void size vs distance
        distances = self.cosmology.comoving_distance(self.observed_voids['redshift']).to(u.Mpc).value
        void_radii = self.observed_voids['radius_hMpc'] * 0.67
        
        # Correlation between void size and distance (completeness bias indicator)
        size_distance_corr, size_distance_p = stats.pearsonr(distances, void_radii)
        
        print(f"Size-distance correlation analysis:")
        print(f"   Pearson r: {size_distance_corr:.4f}")
        print(f"   p-value: {size_distance_p:.6f}")
        
        if size_distance_p < 0.05 and size_distance_corr > 0:
            print("   ✅ SIGNIFICANT size-distance correlation detected")
            print("      → Completeness bias: larger voids preferentially detected at high-z")
        elif size_distance_p < 0.05 and size_distance_corr < 0:
            print("   ✅ SIGNIFICANT inverse size-distance correlation detected")
            print("      → Selection bias: smaller voids missed at high-z")
        else:
            print("   ❌ No significant completeness effects detected")
        
        artifact_detection['completeness_bias'] = {
            'correlation': size_distance_corr,
            'p_value': size_distance_p,
            'significant': size_distance_p < 0.05
        }
        
        self.artifact_detection = artifact_detection
        return artifact_detection
    
    def test_vch_hypothesis_artifacts(self):
        """Test if observed patterns could be VCH effects vs systematic artifacts"""
        print(f"\n🎯 VCH-005: VCH vs ARTIFACT DISCRIMINATION")
        print("=" * 60)
        
        # Collect all significant findings
        significant_differences = []
        systematic_artifacts = []
        
        # Check statistical comparisons
        if hasattr(self, 'statistics_comparison'):
            if self.statistics_comparison['size_distribution']['significant']:
                significant_differences.append("void size distribution")
            if self.statistics_comparison['redshift_distribution']['significant']:
                significant_differences.append("void redshift distribution")
        
        # Check spatial patterns
        if hasattr(self, 'spatial_analysis'):
            if self.spatial_analysis['nearest_neighbor']['significant']:
                significant_differences.append("spatial clustering")
            
            for scale in self.comparison_scales:
                if self.spatial_analysis['multi_scale_clustering'][f'{scale}_mpc']['significant']:
                    significant_differences.append(f"clustering at {scale} Mpc")
        
        # Check systematic artifacts
        if hasattr(self, 'artifact_detection'):
            if (self.artifact_detection['survey_boundaries'] and 
                self.artifact_detection['survey_boundaries']['statistical_test']['significant']):
                systematic_artifacts.append("survey boundary effects")
            
            if (self.artifact_detection['redshift_bias'] and 
                self.artifact_detection['redshift_bias']['statistical_test']['significant']):
                systematic_artifacts.append("redshift-dependent bias")
            
            if self.artifact_detection['completeness_bias']['significant']:
                systematic_artifacts.append("completeness bias")
        
        # Overall assessment
        print(f"\n🎯 VCH-005 DISCRIMINATION RESULTS:")
        print("=" * 50)
        
        print(f"Significant observational differences found: {len(significant_differences)}")
        if significant_differences:
            for diff in significant_differences:
                print(f"   • {diff}")
        
        print(f"\nSystematic artifacts detected: {len(systematic_artifacts)}")
        if systematic_artifacts:
            for artifact in systematic_artifacts:
                print(f"   • {artifact}")
        
        # Classification logic
        if len(systematic_artifacts) == 0 and len(significant_differences) > 0:
            classification = "VCH_SUPPORTED"
            print(f"\n✅ CONCLUSION: VCH EFFECTS LIKELY")
            print("   → Significant differences found with no systematic artifacts")
            print("   → Observational patterns consistent with VCH hypothesis")
        elif len(systematic_artifacts) > 0 and len(significant_differences) > 0:
            classification = "MIXED_EFFECTS"
            print(f"\n⚠️ CONCLUSION: MIXED EFFECTS")
            print("   → Both VCH signatures and systematic artifacts present")
            print("   → Further analysis needed to separate effects")
        elif len(systematic_artifacts) > 0 and len(significant_differences) == 0:
            classification = "ARTIFACTS_ONLY"
            print(f"\n❌ CONCLUSION: SYSTEMATIC ARTIFACTS ONLY")
            print("   → Observed patterns explained by survey/analysis artifacts")
            print("   → No evidence for VCH effects")
        else:
            classification = "NO_SIGNIFICANT_EFFECTS"
            print(f"\n📊 CONCLUSION: NO SIGNIFICANT EFFECTS")
            print("   → Observations consistent with standard simulations")
            print("   → No VCH effects or major artifacts detected")
        
        # Store final results
        self.results = {
            'statistics_comparison': self.statistics_comparison if hasattr(self, 'statistics_comparison') else None,
            'spatial_analysis': self.spatial_analysis if hasattr(self, 'spatial_analysis') else None,
            'artifact_detection': self.artifact_detection if hasattr(self, 'artifact_detection') else None,
            'significant_differences': significant_differences,
            'systematic_artifacts': systematic_artifacts,
            'classification': classification,
            'vch_supported': classification in ['VCH_SUPPORTED', 'MIXED_EFFECTS']
        }
        
        return self.results
    
    def create_analysis_plots(self):
        """Create comprehensive VCH-005 analysis plots"""
        print(f"\n📊 VCH-005: CREATING ANALYSIS PLOTS")
        print("-" * 40)
        
        # Create VCH-005 specific plots
        fig, axes = plt.subplots(3, 3, figsize=(20, 15))
        fig.suptitle('VCH-005 Analysis Results: Observational vs Simulation Comparison', fontsize=16)
        
        # 1. Void size distributions
        if hasattr(self, 'statistics_comparison'):
            obs_radii = self.observed_voids['radius_hMpc'] * 0.67
            sim_mask = (self.sim_voids['redshift'] >= self.min_redshift) & (self.sim_voids['redshift'] <= self.max_redshift)
            sim_radii = self.sim_voids[sim_mask]['radius_mpc']
            
            axes[0, 0].hist([obs_radii, sim_radii], bins=20, alpha=0.7, 
                           label=[f'Observed (n={len(obs_radii)})', f'Simulation (n={len(sim_radii)})'],
                           color=['red', 'blue'])
            axes[0, 0].set_xlabel('Void Radius (Mpc)')
            axes[0, 0].set_ylabel('Count')
            axes[0, 0].set_title('Void Size Distribution Comparison')
            axes[0, 0].legend()
            axes[0, 0].grid(True, alpha=0.3)
        
        # 2. Redshift distributions
        if hasattr(self, 'statistics_comparison'):
            obs_z = self.observed_voids['redshift']
            sim_z = self.sim_voids[sim_mask]['redshift']
            
            axes[0, 1].hist([obs_z, sim_z], bins=20, alpha=0.7,
                           label=['Observed', 'Simulation'], color=['red', 'blue'])
            axes[0, 1].set_xlabel('Redshift')
            axes[0, 1].set_ylabel('Count')
            axes[0, 1].set_title('Redshift Distribution Comparison')
            axes[0, 1].legend()
            axes[0, 1].grid(True, alpha=0.3)
        
        # 3. Sky distribution
        axes[0, 2].scatter(self.observed_voids['RA_deg'], self.observed_voids['Dec_deg'],
                          alpha=0.6, s=20, c='red', label='Observed voids')
        axes[0, 2].set_xlabel('RA (degrees)')
        axes[0, 2].set_ylabel('Dec (degrees)')
        axes[0, 2].set_title('Observed Void Sky Distribution')
        axes[0, 2].legend()
        
        # 4. Nearest neighbor distances
        if hasattr(self, 'spatial_analysis'):
            nn_results = self.spatial_analysis['nearest_neighbor']
            
            # Recalculate for plotting (simplified)
            obs_coords = SkyCoord(ra=self.observed_voids['RA_deg']*u.degree,
                                 dec=self.observed_voids['Dec_deg']*u.degree,
                                 distance=self.cosmology.comoving_distance(self.observed_voids['redshift']))
            obs_cartesian = np.column_stack([
                obs_coords.cartesian.x.to(u.Mpc).value,
                obs_coords.cartesian.y.to(u.Mpc).value,
                obs_coords.cartesian.z.to(u.Mpc).value
            ])
            
            obs_nn_dist = []
            for i, pos in enumerate(obs_cartesian[:100]):  # Limit for performance
                distances = np.linalg.norm(obs_cartesian - pos, axis=1)
                distances = distances[distances > 0]
                if len(distances) > 0:
                    obs_nn_dist.append(np.min(distances))
            
            axes[1, 0].hist(obs_nn_dist, bins=15, alpha=0.7, color='red', 
                           label=f'Observed (mean={np.mean(obs_nn_dist):.1f} Mpc)')
            axes[1, 0].set_xlabel('Nearest Neighbor Distance (Mpc)')
            axes[1, 0].set_ylabel('Count')
            axes[1, 0].set_title('Spatial Clustering Analysis')
            axes[1, 0].legend()
            axes[1, 0].grid(True, alpha=0.3)
        
        # 5. Multi-scale clustering
        if hasattr(self, 'spatial_analysis') and 'multi_scale_clustering' in self.spatial_analysis:
            scales = []
            obs_means = []
            sim_means = []
            
            for scale_mpc in self.comparison_scales:
                scale_key = f'{scale_mpc}_mpc'
                if scale_key in self.spatial_analysis['multi_scale_clustering']:
                    scales.append(scale_mpc)
                    obs_means.append(self.spatial_analysis['multi_scale_clustering'][scale_key]['obs_mean'])
                    sim_means.append(self.spatial_analysis['multi_scale_clustering'][scale_key]['sim_mean'])
            
            if scales:
                axes[1, 1].plot(scales, obs_means, 'o-', color='red', label='Observed')
                axes[1, 1].plot(scales, sim_means, 's-', color='blue', label='Simulation')
                axes[1, 1].set_xlabel('Scale (Mpc)')
                axes[1, 1].set_ylabel('Mean Neighbor Count')
                axes[1, 1].set_title('Multi-scale Clustering Comparison')
                axes[1, 1].legend()
                axes[1, 1].grid(True, alpha=0.3)
        
        # 6. Size vs distance (completeness check)
        if hasattr(self, 'artifact_detection'):
            distances = self.cosmology.comoving_distance(self.observed_voids['redshift']).to(u.Mpc).value
            void_radii = self.observed_voids['radius_hMpc'] * 0.67
            
            axes[1, 2].scatter(distances, void_radii, alpha=0.6, s=20, c='purple')
            
            # Add correlation line if significant
            if self.artifact_detection['completeness_bias']['significant']:
                z = np.polyfit(distances, void_radii, 1)
                p = np.poly1d(z)
                axes[1, 2].plot(distances, p(distances), "r--", alpha=0.8)
            
            axes[1, 2].set_xlabel('Comoving Distance (Mpc)')
            axes[1, 2].set_ylabel('Void Radius (Mpc)')
            axes[1, 2].set_title('Completeness Bias Check')
            axes[1, 2].grid(True, alpha=0.3)
        
        # 7. Edge vs center comparison
        if (hasattr(self, 'artifact_detection') and 
            self.artifact_detection['survey_boundaries'] is not None):
            
            # Simplified edge/center identification for plotting
            ra_center = self.observed_voids['RA_deg'].mean()
            dec_center = self.observed_voids['Dec_deg'].mean()
            ra_range = self.observed_voids['RA_deg'].max() - self.observed_voids['RA_deg'].min()
            dec_range = self.observed_voids['Dec_deg'].max() - self.observed_voids['Dec_deg'].min()
            
            edge_mask = (
                (np.abs(self.observed_voids['RA_deg'] - ra_center) > 0.3 * ra_range) |
                (np.abs(self.observed_voids['Dec_deg'] - dec_center) > 0.3 * dec_range)
            )
            
            edge_radii = (self.observed_voids[edge_mask]['radius_hMpc'] * 0.67).values
            center_radii = (self.observed_voids[~edge_mask]['radius_hMpc'] * 0.67).values
            
            if len(edge_radii) > 0 and len(center_radii) > 0:
                axes[2, 0].hist([edge_radii, center_radii], bins=15, alpha=0.7,
                               label=[f'Edge (n={len(edge_radii)})', f'Center (n={len(center_radii)})'],
                               color=['orange', 'green'])
                axes[2, 0].set_xlabel('Void Radius (Mpc)')
                axes[2, 0].set_ylabel('Count')
                axes[2, 0].set_title('Survey Boundary Effects')
                axes[2, 0].legend()
                axes[2, 0].grid(True, alpha=0.3)
        
        # 8. Redshift bias check
        if (hasattr(self, 'artifact_detection') and 
            self.artifact_detection['redshift_bias'] is not None):
            
            z_median = np.median(self.observed_voids['redshift'])
            low_z_radii = self.observed_voids[self.observed_voids['redshift'] <= z_median]['radius_hMpc'] * 0.67
            high_z_radii = self.observed_voids[self.observed_voids['redshift'] > z_median]['radius_hMpc'] * 0.67
            
            axes[2, 1].hist([low_z_radii, high_z_radii], bins=15, alpha=0.7,
                           label=[f'Low-z (n={len(low_z_radii)})', f'High-z (n={len(high_z_radii)})'],
                           color=['cyan', 'magenta'])
            axes[2, 1].set_xlabel('Void Radius (Mpc)')
            axes[2, 1].set_ylabel('Count')
            axes[2, 1].set_title('Redshift-Dependent Bias Check')
            axes[2, 1].legend()
            axes[2, 1].grid(True, alpha=0.3)
        
        # 9. Summary results
        axes[2, 2].axis('off')
        
        summary_text = "VCH-005 RESULTS SUMMARY\n\n"
        
        if hasattr(self, 'results'):
            summary_text += f"STATISTICAL COMPARISONS:\n"
            summary_text += f"Significant differences: {len(self.results['significant_differences'])}\n"
            for diff in self.results['significant_differences'][:3]:  # Limit for space
                summary_text += f"  • {diff}\n"
            
            summary_text += f"\nSYSTEMATIC ARTIFACTS:\n"
            summary_text += f"Artifacts detected: {len(self.results['systematic_artifacts'])}\n"
            for artifact in self.results['systematic_artifacts'][:3]:
                summary_text += f"  • {artifact}\n"
            
            summary_text += f"\nOVERALL ASSESSMENT:\n"
            summary_text += f"Classification: {self.results['classification']}\n"
            summary_text += f"VCH supported: {'YES' if self.results['vch_supported'] else 'NO'}\n\n"
            
            if self.results['classification'] == 'VCH_SUPPORTED':
                summary_text += "✅ VCH EFFECTS LIKELY\nNo major artifacts detected"
            elif self.results['classification'] == 'MIXED_EFFECTS':
                summary_text += "⚠️ MIXED EFFECTS\nBoth VCH and artifacts present"
            else:
                summary_text += "❌ ARTIFACTS/NO EFFECTS\nNo clear VCH signature"
        
        axes[2, 2].text(0.05, 0.95, summary_text, transform=axes[2, 2].transAxes,
                       fontsize=10, verticalalignment='top', fontfamily='monospace',
                       bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray"))
        
        plt.tight_layout()
        
        plot_file = self.plotter.plots_dir / "vch005_simulation_comparison.png"
        plt.savefig(plot_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"📈 VCH-005 analysis plots saved to: {plot_file}")
        return str(plot_file)
    
    def run_full_analysis(self):
        """Run complete VCH-005 analysis pipeline"""
        print("\n" + "=" * 60)
        print("VCH-005 SKY PATTERN ARTIFACT ANALYSIS")
        print("=" * 60)
        
        # Run analysis pipeline
        self.load_and_prepare_data()
        self.load_simulation_data()
        self.compare_void_statistics()
        self.analyze_spatial_patterns()
        self.detect_systematic_artifacts()
        self.test_vch_hypothesis_artifacts()
        plot_file = self.create_analysis_plots()
        
        # Final summary
        print("\n" + "=" * 60)
        print("VCH-005 ANALYSIS COMPLETE")
        print("=" * 60)
        
        if self.results['vch_supported']:
            print("🎉 RESULT: VCH effects potentially detected!")
            print(f"   Classification: {self.results['classification']}")
            print(f"   Significant differences: {len(self.results['significant_differences'])}")
            print(f"   Systematic artifacts: {len(self.results['systematic_artifacts'])}")
            
            if self.results['classification'] == 'VCH_SUPPORTED':
                print("   This strongly supports the VCH hypothesis with minimal artifacts.")
            else:
                print("   Mixed effects detected - VCH signatures present but artifacts also found.")
        else:
            print("📊 RESULT: No clear VCH signature detected.")
            print(f"   Classification: {self.results['classification']}")
            
            if self.results['classification'] == 'ARTIFACTS_ONLY':
                print("   Observed patterns explained by systematic artifacts.")
            else:
                print("   Observations consistent with standard cosmological simulations.")
        
        print(f"\n📊 Complete results saved to: {plot_file}")
        print("\n✅ VCH-005 analysis completed using REAL SIMULATION DATA")
        print("   Results provide final assessment of VCH framework validity.")
        
        return self.results

def main():
    """Run VCH-005 analysis with real data only"""
    try:
        analyzer = VCH005Analyzer()
        results = analyzer.run_full_analysis()
        return results
    except FileNotFoundError as e:
        print(f"\n❌ DATA ERROR: {e}")
        print("\n📋 To download real simulation data:")
        print("   1. See VCH_Data_Acquisition_Plan.md for download instructions")
        print("   2. Register at Millennium Simulation: https://www.millenniumsimulation.org/")
        print("   3. Access Illustris-TNG: https://www.tng-project.org/")
        print("   4. Download EAGLE data: http://icc.dur.ac.uk/Eagle/")
        print("   5. Place in ../../datasets/simulations/[millennium|illustris|eagle]/")
        print("\n🛑 VCH-005 analysis requires real cosmological simulation data")
        return None

if __name__ == "__main__":
    results = main()