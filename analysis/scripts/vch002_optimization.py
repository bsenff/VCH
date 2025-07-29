#!/usr/bin/env python3
"""
VCH-002 Parameter Optimization
Test different thresholds to optimize redshift correlation significance
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from vch002_analysis import VCH002Analyzer

class VCH002Optimizer:
    """Optimize VCH-002 analysis parameters for maximum significance"""
    
    def __init__(self):
        self.results_history = []
        
    def run_parameter_sweep(self):
        """Test different parameter combinations for VCH-002"""
        print("=" * 60)
        print("VCH-002 PARAMETER OPTIMIZATION")
        print("=" * 60)
        
        # Parameter ranges to test (using lessons from VCH-001)
        void_thresholds = [15.0, 20.0, 25.0, 30.0, 35.0]  # Mpc
        redshift_maxes = [0.12, 0.13, 0.14, 0.15, 0.16]
        
        results = []
        
        total_runs = len(void_thresholds) * len(redshift_maxes)
        run_count = 0
        
        for void_thresh in void_thresholds:
            for z_max in redshift_maxes:
                run_count += 1
                print(f"\\n--- Run {run_count}/{total_runs} ---")
                print(f"Parameters: void_thresh={void_thresh} Mpc, z_max={z_max}")
                
                try:
                    result = self.run_single_analysis(void_thresh, z_max)
                    results.append(result)
                    
                    # Print quick summary for all three tests
                    print(f"   Redshift Residuals: p={result.get('residuals_p', 'N/A'):.4f}")
                    print(f"   Raw Redshift: p={result.get('raw_z_p', 'N/A'):.4f}")
                    print(f"   Implied Redshift: p={result.get('implied_z_p', 'N/A'):.4f}")
                    print(f"   Best p-value: {result.get('best_p', 'N/A'):.4f}")
                    
                except Exception as e:
                    print(f"   Error: {e}")
                    
        self.results_df = pd.DataFrame(results)
        return self.results_df
    
    def run_single_analysis(self, void_threshold_mpc, max_redshift):
        """Run single VCH-002 analysis with specified parameters"""
        
        # Create analyzer with custom parameters
        analyzer = VCH002Analyzer()
        analyzer.void_threshold_mpc = void_threshold_mpc
        analyzer.max_redshift = max_redshift
        analyzer.classifier.void_threshold_mpc = void_threshold_mpc  # Update classifier too
        
        # Load data
        analyzer.load_and_prepare_data()
        
        # Run analysis (suppress most output)
        import io
        import sys
        from contextlib import redirect_stdout
        
        with redirect_stdout(io.StringIO()):
            analyzer.cross_match_positions()
            analyzer.classify_environments()
            analyzer.calculate_redshift_residuals()
            analysis_results = analyzer.test_environmental_correlation()
        
        # Extract key results
        env_counts = analyzer.sn_analysis['environment'].value_counts()
        
        result = {
            'void_threshold_mpc': void_threshold_mpc,
            'max_redshift': max_redshift,
            'n_total': len(analyzer.sn_analysis),
            'n_void': env_counts.get('void', 0),
            'n_wall': env_counts.get('wall', 0), 
            'n_cluster': env_counts.get('cluster', 0),
            'median_void_distance': analyzer.sn_analysis['nearest_void_distance_mpc'].median(),
            'median_angular_sep': analyzer.matches_df['angular_sep_deg'].median(),
        }
        
        # Extract results for all three tests
        test_results = {}
        test_names = ['redshift_residuals', 'raw_redshift', 'implied_redshift']
        
        for test_name in test_names:
            if test_name in analysis_results and analysis_results[test_name]:
                test = analysis_results[test_name]['statistical_test']
                test_results[f'{test_name}_p'] = test['p_value']
                test_results[f'{test_name}_d'] = test['cohens_d']
                test_results[f'{test_name}_sig'] = test['significant']
                test_results[f'{test_name}_mean_diff'] = test['mean_difference']
            else:
                test_results[f'{test_name}_p'] = np.nan
                test_results[f'{test_name}_d'] = np.nan
                test_results[f'{test_name}_sig'] = False
                test_results[f'{test_name}_mean_diff'] = np.nan
        
        # Add test results to main result
        result.update(test_results)
        
        # Find best (most significant) p-value across all tests
        p_values = [result.get(f'{test}_p', np.nan) for test in test_names]
        valid_p_values = [p for p in p_values if not np.isnan(p)]
        
        if valid_p_values:
            result['best_p'] = min(valid_p_values)
            result['best_test'] = test_names[np.nanargmin(p_values)]
            result['any_significant'] = any(result.get(f'{test}_sig', False) for test in test_names)
        else:
            result['best_p'] = np.nan
            result['best_test'] = None
            result['any_significant'] = False
        
        # Short names for main results
        result['residuals_p'] = result.get('redshift_residuals_p', np.nan)
        result['raw_z_p'] = result.get('raw_redshift_p', np.nan)
        result['implied_z_p'] = result.get('implied_redshift_p', np.nan)
        
        return result
    
    def find_optimal_parameters(self):
        """Find parameter combination with best significance"""
        print(f"\\n🎯 VCH-002 OPTIMIZATION RESULTS")
        print("=" * 60)
        
        # Filter to valid results only
        valid_results = self.results_df[
            (self.results_df['n_void'] >= 20) & 
            (self.results_df['n_cluster'] >= 50) &
            (~self.results_df['best_p'].isna())
        ].copy()
        
        if len(valid_results) == 0:
            print("❌ No valid results found with sufficient sample sizes")
            return None
        
        # Sort by best p-value (most significant first)
        valid_results = valid_results.sort_values('best_p')
        
        print(f"Valid parameter combinations: {len(valid_results)}")
        print(f"\\nTop 5 most significant results:")
        print("-" * 100)
        
        cols = ['void_threshold_mpc', 'max_redshift', 'n_void', 'n_cluster', 
                'best_p', 'best_test', 'any_significant']
        
        top_results = valid_results[cols].head()
        for i, (idx, row) in enumerate(top_results.iterrows()):
            sig_str = "***" if row['best_p'] < 0.001 else "**" if row['best_p'] < 0.01 else "*" if row['best_p'] < 0.05 else "ns"
            print(f"{i+1}. void_thresh={row['void_threshold_mpc']:4.1f} z_max={row['max_redshift']:.2f} | "
                  f"n_void={row['n_void']:3.0f} n_cluster={row['n_cluster']:3.0f} | "
                  f"best_p={row['best_p']:.4f} {sig_str} ({row['best_test']})")
        
        # Get best result
        best_result = valid_results.iloc[0]
        
        print(f"\\n🏆 OPTIMAL PARAMETERS:")
        print(f"   Void threshold: {best_result['void_threshold_mpc']} Mpc")
        print(f"   Max redshift: {best_result['max_redshift']}")
        print(f"   Sample sizes: {best_result['n_void']:.0f} void, {best_result['n_cluster']:.0f} cluster")
        print(f"   Best significance: p = {best_result['best_p']:.4f} ({best_result['best_test']})")
        print(f"   Any test significant: {best_result['any_significant']}")
        
        # Show all test results for best configuration
        print(f"\\n📊 ALL TEST RESULTS FOR OPTIMAL PARAMETERS:")
        test_names = ['redshift_residuals', 'raw_redshift', 'implied_redshift']
        for test in test_names:
            p_val = best_result.get(f'{test}_p', np.nan)
            sig = best_result.get(f'{test}_sig', False)
            if not np.isnan(p_val):
                sig_str = "✅" if sig else "❌"
                print(f"   {test}: p = {p_val:.4f} {sig_str}")
        
        return best_result
    
    def create_optimization_plots(self):
        """Create plots showing VCH-002 parameter optimization results"""
        print(f"\\n📊 Creating VCH-002 optimization plots...")
        
        plots_dir = Path("../plots")
        plots_dir.mkdir(exist_ok=True)
        
        # Filter valid results
        valid_results = self.results_df[
            (self.results_df['n_void'] >= 20) & 
            (self.results_df['n_cluster'] >= 50) &
            (~self.results_df['best_p'].isna())
        ].copy()
        
        if len(valid_results) == 0:
            print("❌ No valid results to plot")
            return None
        
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle('VCH-002 Parameter Optimization Results', fontsize=16)
        
        # 1. Best p-value vs void threshold
        axes[0, 0].scatter(valid_results['void_threshold_mpc'], valid_results['best_p'], alpha=0.7)
        axes[0, 0].axhline(0.05, color='red', linestyle='--', label='p = 0.05')
        axes[0, 0].set_xlabel('Void Threshold (Mpc)')
        axes[0, 0].set_ylabel('Best p-value')
        axes[0, 0].set_title('Best Significance vs Void Threshold')
        axes[0, 0].legend()
        axes[0, 0].set_yscale('log')
        
        # 2. Best p-value vs max redshift
        axes[0, 1].scatter(valid_results['max_redshift'], valid_results['best_p'], alpha=0.7)
        axes[0, 1].axhline(0.05, color='red', linestyle='--', label='p = 0.05')
        axes[0, 1].set_xlabel('Max Redshift')
        axes[0, 1].set_ylabel('Best p-value')
        axes[0, 1].set_title('Best Significance vs Redshift Range')
        axes[0, 1].legend()
        axes[0, 1].set_yscale('log')
        
        # 3. Individual test results comparison
        test_colors = {'redshift_residuals': 'blue', 'raw_redshift': 'green', 'implied_redshift': 'red'}
        for test, color in test_colors.items():
            p_col = f'{test}_p'
            if p_col in valid_results.columns:
                mask = ~valid_results[p_col].isna()
                axes[0, 2].scatter(valid_results[mask]['void_threshold_mpc'], 
                                 valid_results[mask][p_col],
                                 label=test.replace('_', ' ').title(), 
                                 alpha=0.7, color=color)
        
        axes[0, 2].axhline(0.05, color='red', linestyle='--', label='p = 0.05')
        axes[0, 2].set_xlabel('Void Threshold (Mpc)')
        axes[0, 2].set_ylabel('p-value')
        axes[0, 2].set_title('Individual Test Results')
        axes[0, 2].legend()
        axes[0, 2].set_yscale('log')
        
        # 4. Sample size vs significance
        axes[1, 0].scatter(valid_results['n_void'], valid_results['best_p'], alpha=0.7)
        axes[1, 0].axhline(0.05, color='red', linestyle='--', label='p = 0.05')
        axes[1, 0].set_xlabel('Void Sample Size')
        axes[1, 0].set_ylabel('Best p-value')
        axes[1, 0].set_title('Significance vs Sample Size')
        axes[1, 0].legend()
        axes[1, 0].set_yscale('log')
        
        # 5. Parameter space heatmap (best p-values)
        try:
            pivot = valid_results.pivot_table(values='best_p', 
                                            index='void_threshold_mpc', 
                                            columns='max_redshift', 
                                            aggfunc='mean')
            im = axes[1, 1].imshow(pivot.values, aspect='auto', cmap='RdYlBu_r', 
                                  extent=[pivot.columns.min(), pivot.columns.max(),
                                         pivot.index.min(), pivot.index.max()],
                                  origin='lower')
            axes[1, 1].set_xlabel('Max Redshift')
            axes[1, 1].set_ylabel('Void Threshold (Mpc)')
            axes[1, 1].set_title('Best p-value Heatmap')
            plt.colorbar(im, ax=axes[1, 1], label='Best p-value')
        except:
            axes[1, 1].text(0.5, 0.5, 'Heatmap\\ngeneration\\nerror', 
                           ha='center', va='center', transform=axes[1, 1].transAxes)
        
        # 6. Summary statistics
        axes[1, 2].axis('off')
        
        # Best result summary
        best_idx = valid_results['best_p'].idxmin()
        best = valid_results.loc[best_idx]
        
        summary_text = f"""VCH-002 OPTIMIZATION SUMMARY

Total parameter combinations tested: {len(self.results_df)}
Valid combinations (sufficient sample): {len(valid_results)}
Significant results (p < 0.05): {(valid_results['best_p'] < 0.05).sum()}
Any test significant: {valid_results['any_significant'].sum()}

BEST RESULT:
  Void threshold: {best['void_threshold_mpc']:.1f} Mpc
  Max redshift: {best['max_redshift']:.2f}
  
  Sample: {best['n_void']:.0f} void, {best['n_cluster']:.0f} cluster
  Best p-value: {best['best_p']:.4f}
  Best test: {best['best_test']}
  
INDIVIDUAL TEST RESULTS:
  Redshift residuals: {best.get('residuals_p', np.nan):.4f}
  Raw redshift: {best.get('raw_z_p', np.nan):.4f}
  Implied redshift: {best.get('implied_z_p', np.nan):.4f}
"""
        
        axes[1, 2].text(0.05, 0.95, summary_text, transform=axes[1, 2].transAxes,
                       fontsize=9, verticalalignment='top', fontfamily='monospace',
                       bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray"))
        
        plt.tight_layout()
        
        plot_file = plots_dir / "vch002_parameter_optimization.png"
        plt.savefig(plot_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"📈 VCH-002 optimization plots saved to: {plot_file}")
        return str(plot_file)

def main():
    """Run VCH-002 parameter optimization"""
    optimizer = VCH002Optimizer()
    
    # Run parameter sweep
    results_df = optimizer.run_parameter_sweep()
    
    # Find optimal parameters
    best_params = optimizer.find_optimal_parameters()
    
    # Create plots
    plot_file = optimizer.create_optimization_plots()
    
    # Save results
    results_file = Path("../results/vch002_optimization_results.csv")
    results_file.parent.mkdir(exist_ok=True)
    results_df.to_csv(results_file, index=False)
    
    print(f"\\n💾 VCH-002 results saved to: {results_file}")
    print(f"📊 Plots saved to: {plot_file}")
    
    return best_params, results_df

if __name__ == "__main__":
    best_params, results_df = main()