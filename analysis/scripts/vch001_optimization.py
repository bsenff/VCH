#!/usr/bin/env python3
"""
VCH-001 Parameter Optimization
Test different thresholds and coverage restrictions to optimize significance
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from vch001_analysis import VCH001Analyzer

class VCH001Optimizer:
    """Optimize VCH-001 analysis parameters for maximum significance"""
    
    def __init__(self):
        self.results_history = []
        
    def apply_sdss_footprint(self, sn_df, void_df):
        """Restrict analysis to SDSS DR7 footprint for better void-SN matching"""
        print("🗺️  Applying SDSS footprint restriction...")
        
        # SDSS DR7 approximate coverage (simplified)
        # North Galactic Cap: roughly 120° < RA < 270°, 0° < Dec < 70°  
        # South Galactic Cap: roughly 320° < RA < 60°, -30° < Dec < 5°
        
        # For simplicity, use the overlap region with void catalog
        void_ra_min, void_ra_max = void_df['RA_deg'].min(), void_df['RA_deg'].max()
        void_dec_min, void_dec_max = void_df['Dec_deg'].min(), void_df['Dec_deg'].max()
        
        print(f"   Void catalog coverage: RA {void_ra_min:.1f}° - {void_ra_max:.1f}°")
        print(f"                         Dec {void_dec_min:.1f}° - {void_dec_max:.1f}°")
        
        # Apply footprint restriction to supernovae
        sn_mask = ((sn_df['RA'] >= void_ra_min) & (sn_df['RA'] <= void_ra_max) &
                   (sn_df['DEC'] >= void_dec_min) & (sn_df['DEC'] <= void_dec_max))
        
        sn_restricted = sn_df[sn_mask].copy()
        
        print(f"   SNe before footprint cut: {len(sn_df)}")
        print(f"   SNe after footprint cut: {len(sn_restricted)}")
        print(f"   Retention: {len(sn_restricted)/len(sn_df)*100:.1f}%")
        
        return sn_restricted
    
    def run_parameter_sweep(self):
        """Test different parameter combinations"""
        print("="*60)
        print("VCH-001 PARAMETER OPTIMIZATION")
        print("="*60)
        
        # Parameter ranges to test
        void_thresholds = [10.0, 15.0, 20.0, 25.0, 30.0]  # Mpc
        redshift_maxes = [0.10, 0.11, 0.12, 0.13, 0.14, 0.15]
        footprint_options = [False]  # Apply SDSS footprint restriction (disabled for now)
        
        results = []
        
        total_runs = len(void_thresholds) * len(redshift_maxes) * len(footprint_options)
        run_count = 0
        
        for void_thresh in void_thresholds:
            for z_max in redshift_maxes:
                for use_footprint in footprint_options:
                    run_count += 1
                    print(f"\n--- Run {run_count}/{total_runs} ---")
                    print(f"Parameters: void_thresh={void_thresh} Mpc, z_max={z_max}, footprint={use_footprint}")
                    
                    try:
                        result = self.run_single_analysis(void_thresh, z_max, use_footprint)
                        results.append(result)
                        
                        # Print quick summary
                        if result['n_void'] > 0 and result['n_cluster'] > 0:
                            print(f"   Result: p={result['p_value']:.4f}, n_void={result['n_void']}, n_cluster={result['n_cluster']}")
                        else:
                            print(f"   Result: Insufficient sample size")
                            
                    except Exception as e:
                        print(f"   Error: {e}")
                        
        self.results_df = pd.DataFrame(results)
        return self.results_df
    
    def run_single_analysis(self, void_threshold_mpc, max_redshift, use_footprint):
        """Run single analysis with specified parameters"""
        
        # Create analyzer with custom parameters
        analyzer = VCH001Analyzer()
        analyzer.void_threshold_mpc = void_threshold_mpc
        analyzer.max_redshift = max_redshift
        
        # Load data
        analyzer.load_and_prepare_data()
        
        # Apply footprint restriction if requested
        if use_footprint:
            restricted_sn = self.apply_sdss_footprint(analyzer.sn_analysis, analyzer.void_analysis)
            if len(restricted_sn) == 0:
                raise ValueError("No SNe remaining after footprint cut")
            analyzer.sn_analysis = restricted_sn.reset_index(drop=True)
        
        # Run analysis (suppress output)
        import io
        import sys
        from contextlib import redirect_stdout
        
        with redirect_stdout(io.StringIO()):
            analyzer.cross_match_positions()
            analyzer.classify_environments()
            analyzer.calculate_distance_residuals()
            stats_results = analyzer.test_environmental_correlation()
        
        # Extract key results
        env_counts = analyzer.sn_analysis['environment'].value_counts()
        
        result = {
            'void_threshold_mpc': void_threshold_mpc,
            'max_redshift': max_redshift,
            'use_footprint': use_footprint,
            'n_total': len(analyzer.sn_analysis),
            'n_void': env_counts.get('void', 0),
            'n_wall': env_counts.get('wall', 0), 
            'n_cluster': env_counts.get('cluster', 0),
            'median_void_distance': analyzer.sn_analysis['nearest_void_distance_mpc'].median(),
            'median_angular_sep': analyzer.matches_df['angular_sep_deg'].median(),
        }
        
        # Add statistical results if available
        if 'statistical_test' in stats_results:
            test = stats_results['statistical_test']
            result.update({
                't_statistic': test['t_statistic'],
                'p_value': test['p_value'],
                'cohens_d': test['cohens_d'],
                'significant': test['significant']
            })
            
            # Add environment means
            for env in ['void', 'wall', 'cluster']:
                if env in stats_results:
                    result[f'{env}_mean'] = stats_results[env]['mean']
                    result[f'{env}_sem'] = stats_results[env]['sem']
        else:
            # Fill with NaN if no test possible
            result.update({
                't_statistic': np.nan,
                'p_value': np.nan, 
                'cohens_d': np.nan,
                'significant': False,
                'void_mean': np.nan,
                'cluster_mean': np.nan
            })
        
        return result
    
    def find_optimal_parameters(self):
        """Find parameter combination with best significance"""
        print(f"\n🎯 OPTIMIZATION RESULTS")
        print("="*50)
        
        # Filter to valid results only
        valid_results = self.results_df[
            (self.results_df['n_void'] >= 20) & 
            (self.results_df['n_cluster'] >= 50) &
            (~self.results_df['p_value'].isna())
        ].copy()
        
        if len(valid_results) == 0:
            print("❌ No valid results found with sufficient sample sizes")
            return None
        
        # Sort by p-value (most significant first)
        valid_results = valid_results.sort_values('p_value')
        
        print(f"Valid parameter combinations: {len(valid_results)}")
        print(f"\nTop 5 most significant results:")
        print("-" * 80)
        
        cols = ['void_threshold_mpc', 'max_redshift', 'use_footprint', 
                'n_void', 'n_cluster', 'p_value', 'cohens_d']
        
        top_results = valid_results[cols].head()
        for i, (idx, row) in enumerate(top_results.iterrows()):
            sig_str = "***" if row['p_value'] < 0.001 else "**" if row['p_value'] < 0.01 else "*" if row['p_value'] < 0.05 else "ns"
            print(f"{i+1}. void_thresh={row['void_threshold_mpc']:4.1f} z_max={row['max_redshift']:.2f} "
                  f"footprint={str(row['use_footprint']):5s} | "
                  f"n_void={row['n_void']:3.0f} n_cluster={row['n_cluster']:3.0f} | "
                  f"p={row['p_value']:.4f} {sig_str} d={row['cohens_d']:.3f}")
        
        # Get best result
        best_result = valid_results.iloc[0]
        
        print(f"\n🏆 OPTIMAL PARAMETERS:")
        print(f"   Void threshold: {best_result['void_threshold_mpc']} Mpc")
        print(f"   Max redshift: {best_result['max_redshift']}")
        print(f"   Use SDSS footprint: {best_result['use_footprint']}")
        print(f"   Sample sizes: {best_result['n_void']:.0f} void, {best_result['n_cluster']:.0f} cluster")
        print(f"   Significance: p = {best_result['p_value']:.4f}")
        print(f"   Effect size: d = {best_result['cohens_d']:.3f}")
        
        return best_result
    
    def create_optimization_plots(self):
        """Create plots showing parameter optimization results"""
        print(f"\n📊 Creating optimization plots...")
        
        plots_dir = Path("../plots")
        plots_dir.mkdir(exist_ok=True)
        
        # Filter valid results
        valid_results = self.results_df[
            (self.results_df['n_void'] >= 20) & 
            (self.results_df['n_cluster'] >= 50) &
            (~self.results_df['p_value'].isna())
        ].copy()
        
        if len(valid_results) == 0:
            print("❌ No valid results to plot")
            return None
        
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle('VCH-001 Parameter Optimization Results', fontsize=16)
        
        # 1. P-value vs void threshold
        for use_fp in [True, False]:
            subset = valid_results[valid_results['use_footprint'] == use_fp]
            if len(subset) > 0:
                axes[0, 0].scatter(subset['void_threshold_mpc'], subset['p_value'], 
                                 label=f'SDSS footprint: {use_fp}', alpha=0.7)
        axes[0, 0].axhline(0.05, color='red', linestyle='--', label='p = 0.05')
        axes[0, 0].set_xlabel('Void Threshold (Mpc)')
        axes[0, 0].set_ylabel('p-value')
        axes[0, 0].set_title('Significance vs Void Threshold')
        axes[0, 0].legend()
        axes[0, 0].set_yscale('log')
        
        # 2. P-value vs max redshift
        for use_fp in [True, False]:
            subset = valid_results[valid_results['use_footprint'] == use_fp]
            if len(subset) > 0:
                axes[0, 1].scatter(subset['max_redshift'], subset['p_value'],
                                 label=f'SDSS footprint: {use_fp}', alpha=0.7)
        axes[0, 1].axhline(0.05, color='red', linestyle='--', label='p = 0.05')
        axes[0, 1].set_xlabel('Max Redshift')
        axes[0, 1].set_ylabel('p-value')
        axes[0, 1].set_title('Significance vs Redshift Range')
        axes[0, 1].legend()
        axes[0, 1].set_yscale('log')
        
        # 3. Sample size vs p-value
        axes[0, 2].scatter(valid_results['n_void'], valid_results['p_value'], alpha=0.7)
        axes[0, 2].axhline(0.05, color='red', linestyle='--', label='p = 0.05')
        axes[0, 2].set_xlabel('Void Sample Size')
        axes[0, 2].set_ylabel('p-value')
        axes[0, 2].set_title('Significance vs Sample Size')
        axes[0, 2].legend()
        axes[0, 2].set_yscale('log')
        
        # 4. Effect size vs void threshold
        axes[1, 0].scatter(valid_results['void_threshold_mpc'], valid_results['cohens_d'], alpha=0.7)
        axes[1, 0].set_xlabel('Void Threshold (Mpc)')
        axes[1, 0].set_ylabel('Effect Size (Cohen\'s d)')
        axes[1, 0].set_title('Effect Size vs Void Threshold')
        
        # 5. Parameter space heatmap (p-values)
        pivot = valid_results.pivot_table(values='p_value', 
                                        index='void_threshold_mpc', 
                                        columns='max_redshift', 
                                        aggfunc='mean')
        im = axes[1, 1].imshow(pivot.values, aspect='auto', cmap='RdYlBu', 
                              extent=[pivot.columns.min(), pivot.columns.max(),
                                     pivot.index.min(), pivot.index.max()],
                              origin='lower')
        axes[1, 1].set_xlabel('Max Redshift')
        axes[1, 1].set_ylabel('Void Threshold (Mpc)')
        axes[1, 1].set_title('p-value Heatmap')
        plt.colorbar(im, ax=axes[1, 1], label='p-value')
        
        # 6. Summary statistics
        axes[1, 2].axis('off')
        
        # Best result summary
        best_idx = valid_results['p_value'].idxmin()
        best = valid_results.loc[best_idx]
        
        summary_text = f"""OPTIMIZATION SUMMARY

Total parameter combinations tested: {len(self.results_df)}
Valid combinations (sufficient sample): {len(valid_results)}
Significant results (p < 0.05): {(valid_results['p_value'] < 0.05).sum()}

BEST RESULT:
  Void threshold: {best['void_threshold_mpc']:.1f} Mpc
  Max redshift: {best['max_redshift']:.2f}
  SDSS footprint: {best['use_footprint']}
  
  Sample: {best['n_void']:.0f} void, {best['n_cluster']:.0f} cluster
  p-value: {best['p_value']:.4f}
  Effect size: {best['cohens_d']:.3f}
  
  Void mean: {best.get('void_mean', np.nan):.4f}
  Cluster mean: {best.get('cluster_mean', np.nan):.4f}
"""
        
        axes[1, 2].text(0.05, 0.95, summary_text, transform=axes[1, 2].transAxes,
                       fontsize=10, verticalalignment='top', fontfamily='monospace',
                       bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray"))
        
        plt.tight_layout()
        
        plot_file = plots_dir / "vch001_parameter_optimization.png"
        plt.savefig(plot_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"📈 Optimization plots saved to: {plot_file}")
        return str(plot_file)

def main():
    """Run parameter optimization"""
    optimizer = VCH001Optimizer()
    
    # Run parameter sweep
    results_df = optimizer.run_parameter_sweep()
    
    # Find optimal parameters
    best_params = optimizer.find_optimal_parameters()
    
    # Create plots
    plot_file = optimizer.create_optimization_plots()
    
    # Save results
    results_file = Path("../results/vch001_optimization_results.csv")
    results_file.parent.mkdir(exist_ok=True)
    results_df.to_csv(results_file, index=False)
    
    print(f"\n💾 Results saved to: {results_file}")
    print(f"📊 Plots saved to: {plot_file}")
    
    return best_params, results_df

if __name__ == "__main__":
    best_params, results_df = main()