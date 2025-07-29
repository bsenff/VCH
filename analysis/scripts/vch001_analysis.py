#!/usr/bin/env python3
"""
VCH-001 Analysis: Redshift Decomposition Hypothesis Testing
Cross-match supernovae with void catalog and test environmental correlations
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

from data_loader import VCH001DataLoader

class VCH001Analyzer:
    """Main analysis class for VCH-001 hypothesis testing"""
    
    def __init__(self, cosmology=Planck18):
        self.loader = VCH001DataLoader()
        self.cosmology = cosmology
        self.results = {}
        
        # Analysis parameters
        self.void_threshold_mpc = 20.0  # Mpc - distance to classify as "in void"
        self.min_redshift = 0.01
        self.max_redshift = 0.12  # Conservative upper limit for good overlap
        
    def load_and_prepare_data(self):
        """Load and prepare both datasets for analysis"""
        print("="*60)
        print("LOADING AND PREPARING DATA")
        print("="*60)
        
        # Load datasets
        print("Loading Pantheon+ supernovae...")
        self.sn_df = self.loader.load_pantheon()
        
        print("Loading VoidFinder void catalog...")
        self.void_df = self.loader.load_vide_voids() 
        
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
        print(f"\n🎯 CROSS-MATCHING POSITIONS")
        print("-" * 40)
        
        # Create coordinate objects
        sn_coords = SkyCoord(ra=self.sn_analysis['RA'].values*u.degree,
                            dec=self.sn_analysis['DEC'].values*u.degree)
        
        void_coords = SkyCoord(ra=self.void_analysis['RA_deg'].values*u.degree, 
                              dec=self.void_analysis['Dec_deg'].values*u.degree)
        
        print(f"Cross-matching {len(sn_coords)} supernovae with {len(void_coords)} voids...")
        
        # For each supernova, find nearest void and angular separation
        matches = []
        for i, sn_coord in enumerate(sn_coords):
            # Calculate angular separations to all voids
            separations = sn_coord.separation(void_coords)
            
            # Find nearest void
            min_idx = np.argmin(separations)
            min_separation = separations[min_idx]
            
            # Calculate physical distance using redshift
            sn_z = self.sn_analysis.iloc[i]['zCMB']
            void_z = self.void_analysis.iloc[min_idx]['redshift']
            avg_z = (sn_z + void_z) / 2
            
            # Convert angular to physical distance (Mpc)
            angular_distance = self.cosmology.angular_diameter_distance(avg_z)
            physical_separation = (min_separation.radian * angular_distance).to(u.Mpc).value
            
            # Void properties
            void_radius = self.void_analysis.iloc[min_idx]['radius_hMpc'] * 0.67  # Convert h^-1 Mpc to Mpc (h~0.67)
            
            matches.append({
                'sn_idx': i,
                'void_idx': min_idx,
                'angular_sep_deg': min_separation.degree,
                'physical_sep_mpc': physical_separation,
                'void_radius_mpc': void_radius,
                'void_redshift': void_z,
                'redshift_diff': abs(sn_z - void_z)
            })
        
        self.matches_df = pd.DataFrame(matches)
        
        # Summary statistics
        print(f"✅ Cross-matching complete!")
        print(f"   Median angular separation: {self.matches_df['angular_sep_deg'].median():.2f}°")
        print(f"   Median physical separation: {self.matches_df['physical_sep_mpc'].median():.1f} Mpc")
        print(f"   Median redshift difference: {self.matches_df['redshift_diff'].median():.4f}")
        
        return self.matches_df
    
    def classify_environments(self):
        """Classify supernovae by environment: void/wall/cluster"""
        print(f"\n🌌 ENVIRONMENTAL CLASSIFICATION")
        print("-" * 40)
        
        # Classification based on distance to nearest void
        # - Inside void: distance < void_radius
        # - Near void (wall): void_radius < distance < void_radius + threshold
        # - Cluster/field: distance > void_radius + threshold
        
        inside_void = self.matches_df['physical_sep_mpc'] < self.matches_df['void_radius_mpc']
        near_void = (self.matches_df['physical_sep_mpc'] >= self.matches_df['void_radius_mpc']) & \
                   (self.matches_df['physical_sep_mpc'] < (self.matches_df['void_radius_mpc'] + self.void_threshold_mpc))
        
        # Add classification to supernova dataframe
        self.sn_analysis['environment'] = 'cluster'  # Default
        self.sn_analysis.loc[inside_void, 'environment'] = 'void'
        self.sn_analysis.loc[near_void, 'environment'] = 'wall'
        
        # Add matching information
        self.sn_analysis['nearest_void_distance_mpc'] = self.matches_df['physical_sep_mpc']
        self.sn_analysis['nearest_void_radius_mpc'] = self.matches_df['void_radius_mpc'] 
        self.sn_analysis['redshift_to_void'] = self.matches_df['redshift_diff']
        
        # Statistics
        env_counts = self.sn_analysis['environment'].value_counts()
        print(f"Environmental classification:")
        for env, count in env_counts.items():
            pct = count / len(self.sn_analysis) * 100
            print(f"   {env.capitalize()}: {count} SNe ({pct:.1f}%)")
        
        return env_counts
    
    def calculate_distance_residuals(self):
        """Calculate distance residuals vs ΛCDM predictions"""
        print(f"\n📏 CALCULATING DISTANCE RESIDUALS")
        print("-" * 40)
        
        # Calculate theoretical distance modulus using Planck18 cosmology
        z_values = self.sn_analysis['zCMB'].values
        theoretical_dl = self.cosmology.luminosity_distance(z_values)
        theoretical_mu = 5 * np.log10(theoretical_dl.to(u.pc).value) - 5
        
        # Calculate residuals (observed - theoretical)
        observed_mu = self.sn_analysis['MU_SH0ES'].values
        residuals = observed_mu - theoretical_mu
        
        self.sn_analysis['mu_theoretical'] = theoretical_mu
        self.sn_analysis['mu_residual'] = residuals
        
        print(f"✅ Distance residuals calculated")
        print(f"   Mean residual: {np.mean(residuals):.3f} ± {np.std(residuals):.3f}")
        print(f"   RMS residual: {np.sqrt(np.mean(residuals**2)):.3f}")
        
        return residuals
    
    def test_environmental_correlation(self):
        """Test correlation between environment and distance residuals"""
        print(f"\n📊 STATISTICAL CORRELATION ANALYSIS")
        print("-" * 40)
        
        # Group by environment
        env_groups = self.sn_analysis.groupby('environment')
        
        results = {}
        print("Distance residual statistics by environment:")
        
        for env, group in env_groups:
            residuals = group['mu_residual'].values
            mean_res = np.mean(residuals)
            std_res = np.std(residuals)
            sem_res = std_res / np.sqrt(len(residuals))
            
            results[env] = {
                'count': len(residuals),
                'mean': mean_res,
                'std': std_res, 
                'sem': sem_res
            }
            
            print(f"   {env.capitalize()}: {mean_res:.4f} ± {sem_res:.4f} ({len(residuals)} SNe)")
        
        # Statistical tests
        void_residuals = self.sn_analysis[self.sn_analysis['environment'] == 'void']['mu_residual']
        cluster_residuals = self.sn_analysis[self.sn_analysis['environment'] == 'cluster']['mu_residual']
        
        if len(void_residuals) > 0 and len(cluster_residuals) > 0:
            # Two-sample t-test
            t_stat, p_value = stats.ttest_ind(void_residuals, cluster_residuals)
            
            # Effect size (Cohen's d)  
            pooled_std = np.sqrt(((len(void_residuals)-1)*void_residuals.std()**2 + 
                                 (len(cluster_residuals)-1)*cluster_residuals.std()**2) / 
                                (len(void_residuals) + len(cluster_residuals) - 2))
            cohens_d = abs(void_residuals.mean() - cluster_residuals.mean()) / pooled_std
            
            # Significance level
            if p_value < 0.001:
                sig_str = "***"
            elif p_value < 0.01:
                sig_str = "**" 
            elif p_value < 0.05:
                sig_str = "*"
            else:
                sig_str = "ns"
                
            print(f"\n🔬 HYPOTHESIS TEST RESULTS:")
            print(f"   Void vs Cluster comparison:")
            print(f"   Mean difference: {void_residuals.mean() - cluster_residuals.mean():.4f}")
            print(f"   t-statistic: {t_stat:.3f}")
            print(f"   p-value: {p_value:.6f} {sig_str}")
            print(f"   Effect size (Cohen's d): {cohens_d:.3f}")
            
            # Interpretation
            if p_value < 0.05:
                print(f"   ✅ SIGNIFICANT environmental correlation detected!")
                if void_residuals.mean() > cluster_residuals.mean():
                    print(f"      → Void SNe appear MORE DISTANT than ΛCDM prediction")
                else:
                    print(f"      → Void SNe appear CLOSER than ΛCDM prediction")
            else:
                print(f"   ❌ No significant environmental correlation found")
                
            results['statistical_test'] = {
                't_statistic': t_stat,
                'p_value': p_value, 
                'cohens_d': cohens_d,
                'significant': p_value < 0.05
            }
        
        self.results = results
        return results
    
    def create_analysis_plots(self):
        """Create comprehensive analysis plots"""
        print(f"\n📊 CREATING ANALYSIS PLOTS")
        print("-" * 40)
        
        plots_dir = Path("../plots")
        plots_dir.mkdir(exist_ok=True)
        
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle('VCH-001 Analysis Results: Environmental Distance Correlations', fontsize=16)
        
        # 1. Sky distribution by environment
        colors = {'void': 'red', 'wall': 'orange', 'cluster': 'blue'}
        for env in ['void', 'wall', 'cluster']:
            mask = self.sn_analysis['environment'] == env
            if mask.sum() > 0:
                axes[0, 0].scatter(self.sn_analysis[mask]['RA'], 
                                 self.sn_analysis[mask]['DEC'],
                                 c=colors[env], label=f'{env.capitalize()} ({mask.sum()})',
                                 alpha=0.7, s=20)
        axes[0, 0].set_xlabel('RA (degrees)')
        axes[0, 0].set_ylabel('Dec (degrees)')
        axes[0, 0].set_title('Supernova Sky Distribution by Environment')
        axes[0, 0].legend()
        
        # 2. Distance residuals by environment
        env_data = []
        env_labels = []
        for env in ['void', 'wall', 'cluster']:
            mask = self.sn_analysis['environment'] == env
            if mask.sum() > 0:
                env_data.append(self.sn_analysis[mask]['mu_residual'])
                env_labels.append(f'{env.capitalize()}\n(n={mask.sum()})')
        
        axes[0, 1].boxplot(env_data, labels=env_labels)
        axes[0, 1].axhline(0, color='black', linestyle='--', alpha=0.5)
        axes[0, 1].set_ylabel('Distance Modulus Residual')
        axes[0, 1].set_title('Distance Residuals by Environment')
        axes[0, 1].grid(True, alpha=0.3)
        
        # 3. Residuals vs redshift colored by environment
        for env in ['void', 'wall', 'cluster']:
            mask = self.sn_analysis['environment'] == env
            if mask.sum() > 0:
                axes[0, 2].scatter(self.sn_analysis[mask]['zCMB'],
                                 self.sn_analysis[mask]['mu_residual'],
                                 c=colors[env], label=env.capitalize(),
                                 alpha=0.6, s=20)
        axes[0, 2].axhline(0, color='black', linestyle='--', alpha=0.5)
        axes[0, 2].set_xlabel('Redshift')
        axes[0, 2].set_ylabel('Distance Modulus Residual')
        axes[0, 2].set_title('Residuals vs Redshift by Environment')
        axes[0, 2].legend()
        axes[0, 2].grid(True, alpha=0.3)
        
        # 4. Distance to nearest void distribution
        axes[1, 0].hist(self.sn_analysis['nearest_void_distance_mpc'], 
                       bins=30, alpha=0.7, color='green', edgecolor='black')
        axes[1, 0].axvline(self.void_threshold_mpc, color='red', linestyle='--', 
                          label=f'Classification threshold ({self.void_threshold_mpc} Mpc)')
        axes[1, 0].set_xlabel('Distance to Nearest Void (Mpc)')
        axes[1, 0].set_ylabel('Count')
        axes[1, 0].set_title('Distribution of Void Distances')
        axes[1, 0].legend()
        
        # 5. Residuals vs void distance
        axes[1, 1].scatter(self.sn_analysis['nearest_void_distance_mpc'],
                          self.sn_analysis['mu_residual'], 
                          alpha=0.6, s=20, c='purple')
        axes[1, 1].axhline(0, color='black', linestyle='--', alpha=0.5)
        axes[1, 1].axvline(self.void_threshold_mpc, color='red', linestyle='--', alpha=0.5)
        axes[1, 1].set_xlabel('Distance to Nearest Void (Mpc)')
        axes[1, 1].set_ylabel('Distance Modulus Residual')
        axes[1, 1].set_title('Residuals vs Void Distance')
        axes[1, 1].grid(True, alpha=0.3)
        
        # 6. Statistical summary
        axes[1, 2].axis('off')
        
        # Add text summary
        summary_text = "STATISTICAL SUMMARY\n\n"
        for env, stats in self.results.items():
            if isinstance(stats, dict) and 'mean' in stats:
                summary_text += f"{env.upper()}:\n"
                summary_text += f"  Count: {stats['count']}\n"
                summary_text += f"  Mean: {stats['mean']:.4f}\n"
                summary_text += f"  SEM: {stats['sem']:.4f}\n\n"
        
        if 'statistical_test' in self.results:
            test = self.results['statistical_test']
            summary_text += "SIGNIFICANCE TEST:\n"
            summary_text += f"  t-stat: {test['t_statistic']:.3f}\n"
            summary_text += f"  p-value: {test['p_value']:.6f}\n"
            summary_text += f"  Cohen's d: {test['cohens_d']:.3f}\n"
            summary_text += f"  Significant: {'YES' if test['significant'] else 'NO'}"
        
        axes[1, 2].text(0.05, 0.95, summary_text, transform=axes[1, 2].transAxes,
                       fontsize=10, verticalalignment='top', fontfamily='monospace',
                       bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray"))
        
        plt.tight_layout()
        
        plot_file = plots_dir / "vch001_analysis_results.png"
        plt.savefig(plot_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"📈 Analysis plots saved to: {plot_file}")
        return str(plot_file)
    
    def run_full_analysis(self):
        """Run complete VCH-001 analysis pipeline"""
        print("\n" + "="*60)
        print("VCH-001 REDSHIFT DECOMPOSITION ANALYSIS")
        print("="*60)
        
        # Run analysis pipeline
        self.load_and_prepare_data()
        self.cross_match_positions()
        self.classify_environments()
        self.calculate_distance_residuals()
        self.test_environmental_correlation()
        plot_file = self.create_analysis_plots()
        
        # Final summary
        print("\n" + "="*60)
        print("ANALYSIS COMPLETE")
        print("="*60)
        
        if 'statistical_test' in self.results and self.results['statistical_test']['significant']:
            print("🎉 RESULT: Significant environmental correlation detected!")
            print("   This supports the VCH-001 hypothesis that supernova distances")
            print("   vary systematically with large-scale cosmic environment.")
        else:
            print("📊 RESULT: No significant environmental correlation found.")
            print("   The data does not support the VCH-001 hypothesis at p<0.05.")
            
        print(f"\n📊 Complete results saved to: {plot_file}")
        print("\n🔬 Ready for scientific interpretation and discussion!")
        
        return self.results

def main():
    """Run VCH-001 analysis"""
    analyzer = VCH001Analyzer()
    results = analyzer.run_full_analysis()
    return results

if __name__ == "__main__":
    results = main()