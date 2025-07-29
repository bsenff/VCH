#!/usr/bin/env python3
"""
VCH Common Utilities
Shared functions and classes for VCH analysis modules
"""

import numpy as np
import pandas as pd
from scipy import stats
from astropy.coordinates import SkyCoord
from astropy import units as u
from astropy.cosmology import Planck18
from pathlib import Path
import matplotlib.pyplot as plt

class VCHEnvironmentalClassifier:
    """Shared environmental classification system for all VCH modules"""
    
    def __init__(self, void_threshold_mpc=20.0, cosmology=Planck18):
        self.void_threshold_mpc = void_threshold_mpc
        self.cosmology = cosmology
        
    def cross_match_positions(self, object_coords, void_coords, object_redshifts, void_redshifts, void_radii):
        """Cross-match object positions with void catalog"""
        print(f"Cross-matching {len(object_coords)} objects with {len(void_coords)} voids...")
        
        matches = []
        for i, obj_coord in enumerate(object_coords):
            # Calculate angular separations to all voids
            separations = obj_coord.separation(void_coords)
            
            # Find nearest void
            min_idx = np.argmin(separations)
            min_separation = separations[min_idx]
            
            # Calculate physical distance using redshift
            obj_z = object_redshifts[i]
            void_z = void_redshifts[min_idx]
            avg_z = (obj_z + void_z) / 2
            
            # Convert angular to physical distance (Mpc)
            angular_distance = self.cosmology.angular_diameter_distance(avg_z)
            physical_separation = (min_separation.radian * angular_distance).to(u.Mpc).value
            
            # Void properties
            void_radius = void_radii[min_idx] * 0.67  # Convert h^-1 Mpc to Mpc (h~0.67)
            
            matches.append({
                'object_idx': i,
                'void_idx': min_idx,
                'angular_sep_deg': min_separation.degree,
                'physical_sep_mpc': physical_separation,
                'void_radius_mpc': void_radius,
                'void_redshift': void_z,
                'redshift_diff': abs(obj_z - void_z)
            })
        
        matches_df = pd.DataFrame(matches)
        
        print(f"✅ Cross-matching complete!")
        print(f"   Median angular separation: {matches_df['angular_sep_deg'].median():.2f}°")
        print(f"   Median physical separation: {matches_df['physical_sep_mpc'].median():.1f} Mpc")
        print(f"   Median redshift difference: {matches_df['redshift_diff'].median():.4f}")
        
        return matches_df
    
    def classify_environments(self, matches_df):
        """Classify objects by environment: void/wall/cluster"""
        print(f"🌌 ENVIRONMENTAL CLASSIFICATION")
        print("-" * 40)
        
        # Classification based on distance to nearest void
        inside_void = matches_df['physical_sep_mpc'] < matches_df['void_radius_mpc']
        near_void = (matches_df['physical_sep_mpc'] >= matches_df['void_radius_mpc']) & \
                   (matches_df['physical_sep_mpc'] < (matches_df['void_radius_mpc'] + self.void_threshold_mpc))
        
        # Create environment labels
        environments = np.full(len(matches_df), 'cluster', dtype=object)
        environments[inside_void] = 'void'
        environments[near_void] = 'wall'
        
        # Statistics
        env_counts = pd.Series(environments).value_counts()
        print(f"Environmental classification:")
        for env, count in env_counts.items():
            pct = count / len(environments) * 100
            print(f"   {env.capitalize()}: {count} objects ({pct:.1f}%)")
        
        return environments, env_counts

class VCHStatisticalTester:
    """Shared statistical testing framework for all VCH modules"""
    
    @staticmethod
    def test_environmental_correlation(void_values, cluster_values, metric_name="values"):
        """Test correlation between environment and measured values"""
        print(f"📊 STATISTICAL CORRELATION ANALYSIS ({metric_name})")
        print("-" * 50)
        
        if len(void_values) == 0 or len(cluster_values) == 0:
            print("❌ Insufficient sample sizes for statistical testing")
            return None
        
        # Basic statistics
        void_mean = np.mean(void_values)
        void_std = np.std(void_values)
        void_sem = void_std / np.sqrt(len(void_values))
        
        cluster_mean = np.mean(cluster_values)
        cluster_std = np.std(cluster_values)
        cluster_sem = cluster_std / np.sqrt(len(cluster_values))
        
        print(f"Environmental {metric_name} statistics:")
        print(f"   Void: {void_mean:.4f} ± {void_sem:.4f} ({len(void_values)} objects)")
        print(f"   Cluster: {cluster_mean:.4f} ± {cluster_sem:.4f} ({len(cluster_values)} objects)")
        
        # Two-sample t-test
        t_stat, p_value = stats.ttest_ind(void_values, cluster_values)
        
        # Effect size (Cohen's d)
        pooled_std = np.sqrt(((len(void_values)-1)*void_std**2 + 
                             (len(cluster_values)-1)*cluster_std**2) / 
                            (len(void_values) + len(cluster_values) - 2))
        cohens_d = abs(void_mean - cluster_mean) / pooled_std
        
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
        print(f"   Mean difference: {void_mean - cluster_mean:.4f}")
        print(f"   t-statistic: {t_stat:.3f}")
        print(f"   p-value: {p_value:.6f} {sig_str}")
        print(f"   Effect size (Cohen's d): {cohens_d:.3f}")
        
        # Interpretation
        if p_value < 0.05:
            print(f"   ✅ SIGNIFICANT environmental correlation detected!")
            if void_mean > cluster_mean:
                print(f"      → Void objects show HIGHER {metric_name}")
            else:
                print(f"      → Void objects show LOWER {metric_name}")
        else:
            print(f"   ❌ No significant environmental correlation found")
            
        return {
            'void': {
                'count': len(void_values),
                'mean': void_mean,
                'std': void_std,
                'sem': void_sem
            },
            'cluster': {
                'count': len(cluster_values), 
                'mean': cluster_mean,
                'std': cluster_std,
                'sem': cluster_sem
            },
            'statistical_test': {
                't_statistic': t_stat,
                'p_value': p_value,
                'cohens_d': cohens_d,
                'significant': p_value < 0.05,
                'mean_difference': void_mean - cluster_mean
            }
        }

class VCHPlotManager:
    """Shared plotting utilities for all VCH modules"""
    
    def __init__(self, module_name="VCH"):
        self.module_name = module_name
        self.plots_dir = Path("../plots")
        self.plots_dir.mkdir(exist_ok=True)
        
    def create_environmental_analysis_plots(self, object_data, matches_df, analysis_results, 
                                          primary_metric, primary_label, file_suffix="analysis"):
        """Create standardized 6-panel environmental analysis plots"""
        print(f"📊 Creating {self.module_name} analysis plots...")
        
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle(f'{self.module_name} Analysis Results: Environmental {primary_label} Correlations', fontsize=16)
        
        # Color scheme
        colors = {'void': 'red', 'wall': 'orange', 'cluster': 'blue'}
        
        # 1. Sky distribution by environment
        for env in ['void', 'wall', 'cluster']:
            mask = object_data['environment'] == env
            if mask.sum() > 0:
                axes[0, 0].scatter(object_data[mask]['RA'], 
                                 object_data[mask]['DEC'],
                                 c=colors[env], label=f'{env.capitalize()} ({mask.sum()})',
                                 alpha=0.7, s=20)
        axes[0, 0].set_xlabel('RA (degrees)')
        axes[0, 0].set_ylabel('Dec (degrees)')
        axes[0, 0].set_title(f'Object Sky Distribution by Environment')
        axes[0, 0].legend()
        
        # 2. Primary metric by environment
        env_data = []
        env_labels = []
        for env in ['void', 'wall', 'cluster']:
            mask = object_data['environment'] == env
            if mask.sum() > 0:
                env_data.append(object_data[mask][primary_metric])
                env_labels.append(f'{env.capitalize()}\n(n={mask.sum()})')
        
        if env_data:
            axes[0, 1].boxplot(env_data, labels=env_labels)
            axes[0, 1].axhline(0, color='black', linestyle='--', alpha=0.5)
            axes[0, 1].set_ylabel(primary_label)
            axes[0, 1].set_title(f'{primary_label} by Environment')
            axes[0, 1].grid(True, alpha=0.3)
        
        # 3. Primary metric vs redshift colored by environment
        for env in ['void', 'wall', 'cluster']:
            mask = object_data['environment'] == env
            if mask.sum() > 0:
                axes[0, 2].scatter(object_data[mask]['redshift'],
                                 object_data[mask][primary_metric],
                                 c=colors[env], label=env.capitalize(),
                                 alpha=0.6, s=20)
        axes[0, 2].axhline(0, color='black', linestyle='--', alpha=0.5)
        axes[0, 2].set_xlabel('Redshift')
        axes[0, 2].set_ylabel(primary_label)
        axes[0, 2].set_title(f'{primary_label} vs Redshift by Environment')
        axes[0, 2].legend()
        axes[0, 2].grid(True, alpha=0.3)
        
        # 4. Distance to nearest void distribution
        axes[1, 0].hist(object_data['nearest_void_distance_mpc'], 
                       bins=30, alpha=0.7, color='green', edgecolor='black')
        axes[1, 0].axvline(object_data['void_threshold_mpc'].iloc[0], color='red', linestyle='--', 
                          label=f'Classification threshold')
        axes[1, 0].set_xlabel('Distance to Nearest Void (Mpc)')
        axes[1, 0].set_ylabel('Count')
        axes[1, 0].set_title('Distribution of Void Distances')
        axes[1, 0].legend()
        
        # 5. Primary metric vs void distance
        axes[1, 1].scatter(object_data['nearest_void_distance_mpc'],
                          object_data[primary_metric], 
                          alpha=0.6, s=20, c='purple')
        axes[1, 1].axhline(0, color='black', linestyle='--', alpha=0.5)
        axes[1, 1].axvline(object_data['void_threshold_mpc'].iloc[0], color='red', linestyle='--', alpha=0.5)
        axes[1, 1].set_xlabel('Distance to Nearest Void (Mpc)')
        axes[1, 1].set_ylabel(primary_label)
        axes[1, 1].set_title(f'{primary_label} vs Void Distance')
        axes[1, 1].grid(True, alpha=0.3)
        
        # 6. Statistical summary
        axes[1, 2].axis('off')
        
        # Add text summary
        summary_text = f"STATISTICAL SUMMARY\\n\\n"
        for env, stats in analysis_results.items():
            if isinstance(stats, dict) and 'mean' in stats:
                summary_text += f"{env.upper()}:\\n"
                summary_text += f"  Count: {stats['count']}\\n"
                summary_text += f"  Mean: {stats['mean']:.4f}\\n"
                summary_text += f"  SEM: {stats['sem']:.4f}\\n\\n"
        
        if 'statistical_test' in analysis_results:
            test = analysis_results['statistical_test']
            summary_text += "SIGNIFICANCE TEST:\\n"
            summary_text += f"  t-stat: {test['t_statistic']:.3f}\\n"
            summary_text += f"  p-value: {test['p_value']:.6f}\\n"
            summary_text += f"  Cohen's d: {test['cohens_d']:.3f}\\n"
            summary_text += f"  Significant: {'YES' if test['significant'] else 'NO'}"
        
        axes[1, 2].text(0.05, 0.95, summary_text, transform=axes[1, 2].transAxes,
                       fontsize=10, verticalalignment='top', fontfamily='monospace',
                       bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray"))
        
        plt.tight_layout()
        
        plot_file = self.plots_dir / f"{self.module_name.lower()}_{file_suffix}_results.png"
        plt.savefig(plot_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"📈 Analysis plots saved to: {plot_file}")
        return str(plot_file)

def load_void_catalog():
    """Shared void catalog loading function"""
    from data_loader import VCH001DataLoader
    loader = VCH001DataLoader()
    return loader.load_vide_voids()

def load_supernova_catalog():
    """Shared supernova catalog loading function"""  
    from data_loader import VCH001DataLoader
    loader = VCH001DataLoader()
    return loader.load_pantheon()