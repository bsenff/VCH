#!/usr/bin/env python3
"""
VCH-002 Analysis: Redshift Decomposition Environmental Correlation Testing
Test whether supernova redshifts show systematic environmental dependence beyond distance effects
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
from astropy.coordinates import SkyCoord
from astropy import units as u
from astropy.cosmology import Planck18
from pathlib import Path

from vch_common import VCHEnvironmentalClassifier, VCHStatisticalTester, VCHPlotManager, load_void_catalog, load_supernova_catalog

class VCH002Analyzer:
    """VCH-002 Redshift Decomposition Analysis"""
    
    def __init__(self, cosmology=Planck18):
        self.cosmology = cosmology
        self.results = {}
        
        # Analysis parameters (use optimized values from VCH-001)
        self.void_threshold_mpc = 25.0  # Mpc - optimized threshold from VCH-001
        self.min_redshift = 0.01
        self.max_redshift = 0.15  # Extended range from VCH-001 optimization
        
        # Initialize common components
        self.classifier = VCHEnvironmentalClassifier(self.void_threshold_mpc, cosmology)
        self.tester = VCHStatisticalTester()
        self.plotter = VCHPlotManager("VCH-002")
        
    def load_and_prepare_data(self):
        """Load and prepare datasets for VCH-002 analysis"""
        print("=" * 60)
        print("VCH-002: LOADING AND PREPARING DATA")
        print("=" * 60)
        
        # Load datasets using common functions
        print("Loading Pantheon+ supernovae...")
        self.sn_df = load_supernova_catalog()
        
        print("Loading VoidFinder void catalog...")
        self.void_df = load_void_catalog()
        
        # Apply redshift cuts
        sn_mask = (self.sn_df['zCMB'] >= self.min_redshift) & (self.sn_df['zCMB'] <= self.max_redshift)
        void_mask = (self.void_df['redshift'] >= self.min_redshift) & (self.void_df['redshift'] <= self.max_redshift)
        
        self.sn_analysis = self.sn_df[sn_mask].copy().reset_index(drop=True)
        self.void_analysis = self.void_df[void_mask].copy().reset_index(drop=True)
        
        print(f"✅ Analysis sample: {len(self.sn_analysis)} SNe, {len(self.void_analysis)} voids")
        print(f"   Redshift range: {self.min_redshift} - {self.max_redshift}")
        
        return len(self.sn_analysis), len(self.void_analysis)
    
    def cross_match_positions(self):
        """Cross-match supernova positions with void catalog"""
        print(f"\\n🎯 VCH-002: CROSS-MATCHING POSITIONS")
        print("-" * 40)
        
        # Create coordinate objects
        sn_coords = SkyCoord(ra=self.sn_analysis['RA'].values*u.degree,
                            dec=self.sn_analysis['DEC'].values*u.degree)
        
        void_coords = SkyCoord(ra=self.void_analysis['RA_deg'].values*u.degree, 
                              dec=self.void_analysis['Dec_deg'].values*u.degree)
        
        # Use common cross-matching function
        self.matches_df = self.classifier.cross_match_positions(
            sn_coords, void_coords, 
            self.sn_analysis['zCMB'].values,
            self.void_analysis['redshift'].values,
            self.void_analysis['radius_hMpc'].values
        )
        
        return self.matches_df
    
    def classify_environments(self):
        """Classify supernovae by environment using common classifier"""
        environments, env_counts = self.classifier.classify_environments(self.matches_df)
        
        # Add classification to supernova dataframe
        self.sn_analysis['environment'] = environments
        
        # Add matching information
        self.sn_analysis['nearest_void_distance_mpc'] = self.matches_df['physical_sep_mpc']
        self.sn_analysis['nearest_void_radius_mpc'] = self.matches_df['void_radius_mpc'] 
        self.sn_analysis['redshift_to_void'] = self.matches_df['redshift_diff']
        self.sn_analysis['void_threshold_mpc'] = self.void_threshold_mpc
        
        return env_counts
    
    def calculate_redshift_residuals(self):
        """Calculate redshift residuals - the core VCH-002 analysis"""
        print(f"\\n📏 VCH-002: CALCULATING REDSHIFT RESIDUALS")
        print("-" * 50)
        
        # Method 1: Distance-implied redshift vs observed redshift
        # Calculate what redshift should be based on observed distance modulus
        observed_mu = self.sn_analysis['MU_SH0ES'].values
        
        # Convert distance modulus to luminosity distance
        # μ = 5*log10(d_L/pc) - 5  =>  d_L = 10^((μ+5)/5) pc
        observed_dl_pc = 10**((observed_mu + 5) / 5)
        observed_dl_mpc = observed_dl_pc / 1e6
        
        # Find redshift that would give this luminosity distance in ΛCDM
        # This is the "distance-implied redshift"
        implied_redshifts = []
        for dl_mpc in observed_dl_mpc:
            # Search for redshift that gives this distance
            z_test = np.linspace(0.001, 0.5, 1000)
            dl_test = self.cosmology.luminosity_distance(z_test).to(u.Mpc).value
            
            # Find closest match
            closest_idx = np.argmin(np.abs(dl_test - dl_mpc))
            implied_z = z_test[closest_idx]
            implied_redshifts.append(implied_z)
        
        implied_redshifts = np.array(implied_redshifts)
        
        # Calculate redshift residual: observed - distance-implied
        observed_z = self.sn_analysis['zCMB'].values
        redshift_residuals = observed_z - implied_redshifts
        
        self.sn_analysis['implied_redshift'] = implied_redshifts
        self.sn_analysis['redshift_residual'] = redshift_residuals
        
        print(f"✅ Redshift residuals calculated")
        print(f"   Mean redshift residual: {np.mean(redshift_residuals):.6f} ± {np.std(redshift_residuals):.6f}")
        print(f"   RMS redshift residual: {np.sqrt(np.mean(redshift_residuals**2)):.6f}")
        print(f"   Residual range: {np.min(redshift_residuals):.6f} to {np.max(redshift_residuals):.6f}")
        
        # Method 2: Direct environmental redshift comparison
        # Also analyze raw redshift differences between environments
        self.sn_analysis['raw_redshift'] = observed_z
        
        return redshift_residuals
    
    def test_environmental_correlation(self):
        """Test correlation between environment and redshift residuals"""
        print(f"\\n📊 VCH-002: ENVIRONMENTAL REDSHIFT CORRELATION TESTING")
        print("=" * 60)
        
        # Test 1: Redshift residuals by environment
        void_residuals = self.sn_analysis[self.sn_analysis['environment'] == 'void']['redshift_residual']
        cluster_residuals = self.sn_analysis[self.sn_analysis['environment'] == 'cluster']['redshift_residual']
        
        print("\\n🔬 TEST 1: Redshift Residuals (Observed - Distance-Implied)")
        residual_results = self.tester.test_environmental_correlation(
            void_residuals, cluster_residuals, "redshift residuals"
        )
        
        # Test 2: Raw redshift comparison by environment
        void_raw_z = self.sn_analysis[self.sn_analysis['environment'] == 'void']['raw_redshift']
        cluster_raw_z = self.sn_analysis[self.sn_analysis['environment'] == 'cluster']['raw_redshift']
        
        print("\\n🔬 TEST 2: Raw Redshift Environmental Comparison")
        raw_z_results = self.tester.test_environmental_correlation(
            void_raw_z, cluster_raw_z, "raw redshift"
        )
        
        # Test 3: Distance-implied redshift by environment
        void_implied_z = self.sn_analysis[self.sn_analysis['environment'] == 'void']['implied_redshift']
        cluster_implied_z = self.sn_analysis[self.sn_analysis['environment'] == 'cluster']['implied_redshift']
        
        print("\\n🔬 TEST 3: Distance-Implied Redshift Environmental Comparison")
        implied_z_results = self.tester.test_environmental_correlation(
            void_implied_z, cluster_implied_z, "distance-implied redshift"
        )
        
        # Store all results
        self.results = {
            'redshift_residuals': residual_results,
            'raw_redshift': raw_z_results,
            'implied_redshift': implied_z_results
        }
        
        # Overall assessment
        print(f"\\n🎯 VCH-002 HYPOTHESIS ASSESSMENT:")
        print("=" * 50)
        
        significant_tests = []
        if residual_results and residual_results['statistical_test']['significant']:
            significant_tests.append("redshift residuals")
        if raw_z_results and raw_z_results['statistical_test']['significant']:
            significant_tests.append("raw redshift")
        if implied_z_results and implied_z_results['statistical_test']['significant']:
            significant_tests.append("implied redshift")
        
        if significant_tests:
            print(f"✅ SIGNIFICANT environmental correlation found in: {', '.join(significant_tests)}")
            print("   This supports VCH-002 hypothesis that redshift has environmental components")
        else:
            print("❌ No significant environmental correlations found")
            print("   VCH-002 hypothesis not supported by current data")
        
        return self.results
    
    def create_analysis_plots(self):
        """Create comprehensive VCH-002 analysis plots"""
        print(f"\\n📊 VCH-002: CREATING ANALYSIS PLOTS")
        print("-" * 40)
        
        # Prepare data for plotting
        self.sn_analysis['redshift'] = self.sn_analysis['zCMB']  # For compatibility
        
        # Create standard environmental analysis plots for redshift residuals
        plot_file = self.plotter.create_environmental_analysis_plots(
            self.sn_analysis, self.matches_df, self.results['redshift_residuals'],
            'redshift_residual', 'Redshift Residual', 'redshift_residual'
        )
        
        # Create additional VCH-002 specific plots
        self.create_vch002_specific_plots()
        
        return plot_file
    
    def create_vch002_specific_plots(self):
        """Create VCH-002 specific analysis plots"""
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle('VCH-002 Redshift Decomposition Analysis: Detailed Results', fontsize=16)
        
        colors = {'void': 'red', 'wall': 'orange', 'cluster': 'blue'}
        
        # 1. Observed vs Distance-Implied Redshift
        for env in ['void', 'wall', 'cluster']:
            mask = self.sn_analysis['environment'] == env
            if mask.sum() > 0:
                axes[0, 0].scatter(self.sn_analysis[mask]['implied_redshift'],
                                 self.sn_analysis[mask]['raw_redshift'],
                                 c=colors[env], label=f'{env.capitalize()} ({mask.sum()})',
                                 alpha=0.7, s=20)
        
        # Add 1:1 line
        z_range = [self.sn_analysis['implied_redshift'].min(), self.sn_analysis['implied_redshift'].max()]
        axes[0, 0].plot(z_range, z_range, 'k--', alpha=0.5, label='1:1 line')
        axes[0, 0].set_xlabel('Distance-Implied Redshift')
        axes[0, 0].set_ylabel('Observed Redshift')
        axes[0, 0].set_title('Observed vs Distance-Implied Redshift')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
        
        # 2. Redshift residuals vs observed redshift
        for env in ['void', 'wall', 'cluster']:
            mask = self.sn_analysis['environment'] == env
            if mask.sum() > 0:
                axes[0, 1].scatter(self.sn_analysis[mask]['raw_redshift'],
                                 self.sn_analysis[mask]['redshift_residual'],
                                 c=colors[env], label=env.capitalize(),
                                 alpha=0.6, s=20)
        axes[0, 1].axhline(0, color='black', linestyle='--', alpha=0.5)
        axes[0, 1].set_xlabel('Observed Redshift')
        axes[0, 1].set_ylabel('Redshift Residual')
        axes[0, 1].set_title('Redshift Residuals vs Observed Redshift')
        axes[0, 1].legend()
        axes[0, 1].grid(True, alpha=0.3)
        
        # 3. Redshift residual distribution by environment
        env_residuals = []
        env_labels = []
        for env in ['void', 'wall', 'cluster']:
            mask = self.sn_analysis['environment'] == env
            if mask.sum() > 0:
                env_residuals.append(self.sn_analysis[mask]['redshift_residual'])
                env_labels.append(f'{env.capitalize()}\\n(n={mask.sum()})')
        
        if env_residuals:
            axes[0, 2].boxplot(env_residuals, labels=env_labels)
            axes[0, 2].axhline(0, color='black', linestyle='--', alpha=0.5)
            axes[0, 2].set_ylabel('Redshift Residual')
            axes[0, 2].set_title('Redshift Residual Distribution')
            axes[0, 2].grid(True, alpha=0.3)
        
        # 4. Raw redshift vs distance modulus colored by environment
        for env in ['void', 'wall', 'cluster']:
            mask = self.sn_analysis['environment'] == env
            if mask.sum() > 0:
                axes[1, 0].scatter(self.sn_analysis[mask]['MU_SH0ES'],
                                 self.sn_analysis[mask]['raw_redshift'],
                                 c=colors[env], label=env.capitalize(),
                                 alpha=0.6, s=20)
        axes[1, 0].set_xlabel('Distance Modulus')
        axes[1, 0].set_ylabel('Observed Redshift')
        axes[1, 0].set_title('Redshift vs Distance Modulus')
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)
        
        # 5. Redshift residuals vs void distance
        axes[1, 1].scatter(self.sn_analysis['nearest_void_distance_mpc'],
                          self.sn_analysis['redshift_residual'], 
                          alpha=0.6, s=20, c='purple')
        axes[1, 1].axhline(0, color='black', linestyle='--', alpha=0.5)
        axes[1, 1].axvline(self.void_threshold_mpc, color='red', linestyle='--', alpha=0.5)
        axes[1, 1].set_xlabel('Distance to Nearest Void (Mpc)')
        axes[1, 1].set_ylabel('Redshift Residual')
        axes[1, 1].set_title('Redshift Residuals vs Void Distance')
        axes[1, 1].grid(True, alpha=0.3)
        
        # 6. Multi-test results summary
        axes[1, 2].axis('off')
        
        summary_text = "VCH-002 MULTI-TEST RESULTS\\n\\n"
        
        test_names = ["Redshift Residuals", "Raw Redshift", "Implied Redshift"]
        test_keys = ["redshift_residuals", "raw_redshift", "implied_redshift"]
        
        for i, (name, key) in enumerate(zip(test_names, test_keys)):
            if key in self.results and self.results[key]:
                test = self.results[key]['statistical_test']
                sig_str = "✅ SIG" if test['significant'] else "❌ NS"
                summary_text += f"{i+1}. {name}:\\n"
                summary_text += f"   p = {test['p_value']:.4f} {sig_str}\\n"
                summary_text += f"   d = {test['cohens_d']:.3f}\\n\\n"
        
        # Overall assessment
        significant_count = sum(1 for key in test_keys 
                              if key in self.results and self.results[key] 
                              and self.results[key]['statistical_test']['significant'])
        
        summary_text += f"OVERALL ASSESSMENT:\\n"
        summary_text += f"Tests significant: {significant_count}/3\\n"
        
        if significant_count >= 1:
            summary_text += "VCH-002: SUPPORTED ✅"
        else:
            summary_text += "VCH-002: NOT SUPPORTED ❌"
        
        axes[1, 2].text(0.05, 0.95, summary_text, transform=axes[1, 2].transAxes,
                       fontsize=10, verticalalignment='top', fontfamily='monospace',
                       bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray"))
        
        plt.tight_layout()
        
        plot_file = self.plotter.plots_dir / "vch002_detailed_analysis.png"
        plt.savefig(plot_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"📈 Detailed VCH-002 plots saved to: {plot_file}")
        return str(plot_file)
    
    def run_full_analysis(self):
        """Run complete VCH-002 analysis pipeline"""
        print("\\n" + "=" * 60)
        print("VCH-002 REDSHIFT DECOMPOSITION ANALYSIS")
        print("=" * 60)
        
        # Run analysis pipeline
        self.load_and_prepare_data()
        self.cross_match_positions()
        self.classify_environments()
        self.calculate_redshift_residuals()
        self.test_environmental_correlation()
        plot_file = self.create_analysis_plots()
        
        # Final summary
        print("\\n" + "=" * 60)
        print("VCH-002 ANALYSIS COMPLETE")
        print("=" * 60)
        
        # Count significant results
        significant_tests = []
        for test_name, result in self.results.items():
            if result and result['statistical_test']['significant']:
                significant_tests.append(test_name)
        
        if significant_tests:
            print("🎉 RESULT: Significant environmental redshift correlations detected!")
            print(f"   Significant tests: {', '.join(significant_tests)}")
            print("   This supports the VCH-002 hypothesis that redshift contains")
            print("   environmental components beyond pure cosmological expansion.")
        else:
            print("📊 RESULT: No significant environmental redshift correlations found.")
            print("   The data does not support the VCH-002 hypothesis at p<0.05.")
            
        print(f"\\n📊 Complete results saved to: {plot_file}")
        print("\\n🔬 Ready for scientific interpretation and comparison with VCH-001!")
        
        return self.results

def main():
    """Run VCH-002 analysis"""
    analyzer = VCH002Analyzer()
    results = analyzer.run_full_analysis()
    return results

if __name__ == "__main__":
    results = main()