#!/usr/bin/env python3
"""
VCH-001 Data Loader
Loads and validates datasets for redshift decomposition analysis
"""

import numpy as np
import pandas as pd
from pathlib import Path
import warnings

class VCH001DataLoader:
    """Load and validate VCH-001 datasets"""
    
    def __init__(self, data_root="../../datasets"):
        self.data_root = Path(data_root)
        self.pantheon_path = self.data_root / "pantheon"
        self.vide_path = self.data_root / "vide"
        self.processed_path = self.data_root / "processed"
        
        # Ensure processed directory exists
        self.processed_path.mkdir(parents=True, exist_ok=True)
    
    def load_pantheon(self):
        """Load Pantheon+ supernova catalog"""
        print("Loading Pantheon+ catalog...")
        
        # Try DataRelease structure first (correct path)
        pantheon_file = self.pantheon_path / "DataRelease/Pantheon+_Data/4_DISTANCES_AND_COVAR/Pantheon+SH0ES.dat"
        if not pantheon_file.exists():
            # Try direct download
            pantheon_file = self.pantheon_path / "Pantheon+SH0ES.dat" 
            
        if not pantheon_file.exists():
            raise FileNotFoundError(f"Pantheon+ catalog not found. Expected at {pantheon_file}")
        
        # Load with appropriate column names (based on Pantheon+ documentation)
        try:
            df = pd.read_csv(pantheon_file, sep=r'\s+', comment='#')
            print(f"Loaded {len(df)} supernovae from Pantheon+")
            
            # Basic validation - adjust for actual Pantheon+ column names
            required_cols = ['CID', 'zCMB', 'MU_SH0ES', 'MU_SH0ES_ERR_DIAG']
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                print(f"Warning: Missing expected columns: {missing_cols}")
                print(f"Available columns: {list(df.columns)}")
            else:
                print("✅ All required columns present")
            
            return df
            
        except Exception as e:
            print(f"Error loading Pantheon+ data: {e}")
            # Try to read first few lines to diagnose format
            with open(pantheon_file, 'r') as f:
                print("First 5 lines of file:")
                for i, line in enumerate(f):
                    if i < 5:
                        print(f"  {line.strip()}")
                    else:
                        break
            raise
    
    def load_vide_voids(self):
        """Load VIDE void catalog"""
        print("Loading VIDE void catalog...")
        
        # Try multiple void catalog sources (real catalogs first)
        void_files = [
            self.vide_path / "table1.dat",  # VoidFinder maximal spheres (Douglass+ 2023)
            self.vide_path / "table3.dat",  # V2/VIDE voids (Douglass+ 2023)
            self.vide_path / "test_voids.dat",  # Test catalog for development
            self.vide_path / "VIDE_voids_SDSSdr12.dat"
        ]
        
        void_file = None
        for vf in void_files:
            if vf.exists():
                void_file = vf
                break
                
        if void_file is None:
            raise FileNotFoundError(f"No void catalog found. Tried: {[str(vf) for vf in void_files]}")
        
        print(f"Using void catalog: {void_file}")
        try:
            # Handle different catalog formats
            if 'table1.dat' in str(void_file):
                # VoidFinder maximal spheres format (Douglass+ 2023)
                # Based on ReadMe: Cosmo x y z Rad void edge s RAdeg DEdeg Reff
                column_names = ['Cosmology', 'x_hMpc', 'y_hMpc', 'z_hMpc', 'radius_hMpc', 
                               'void_id', 'edge_flag', 'comoving_dist_hMpc', 'RA_deg', 'Dec_deg', 'Reff_hMpc']
                df = pd.read_csv(void_file, sep=r'\s+', names=column_names, comment='#')
                # Filter for Planck2018 cosmology and valid voids
                df = df[df['Cosmology'] == 'Planck2018'].copy()
                
                # Convert comoving distance to redshift (approximate for low z)
                # Using Hubble's law: d = c*z/H0, assuming H0 = 100 h km/s/Mpc
                # So z ≈ d * 100 h / c = d_hMpc * 100 / 299792.458 
                c_km_s = 299792.458  # km/s
                df['redshift'] = df['comoving_dist_hMpc'] * 100 / c_km_s
                
                print(f"Loaded {len(df)} VoidFinder voids (Planck2018 cosmology)")
                
            elif 'table3.dat' in str(void_file):
                # V2/VIDE format - more complex, would need ReadMe for exact format
                df = pd.read_csv(void_file, sep=r'\s+', comment='#')
                print(f"Loaded {len(df)} V2/VIDE voids")
                
            elif 'csv' in str(void_file) or 'tsv' in str(void_file):
                # TSV/CSV format with tab separator
                df = pd.read_csv(void_file, sep='\t', comment='#', skiprows=20)
                print(f"Loaded {len(df)} voids from TSV catalog")
                
            else:
                # Standard whitespace-separated format (test catalog)
                df = pd.read_csv(void_file, sep=r'\s+', comment='#')
                print(f"Loaded {len(df)} voids from standard catalog")
            
            print(f"Columns: {list(df.columns)}")
            return df
            
        except Exception as e:
            print(f"Error loading VIDE data: {e}")
            # Diagnose format
            with open(void_file, 'r') as f:
                print("First 5 lines of void catalog:")
                for i, line in enumerate(f):
                    if i < 5:
                        print(f"  {line.strip()}")
                    else:
                        break
            raise
    
    def validate_datasets(self):
        """Validate loaded datasets and report statistics"""
        print("\n" + "="*50)
        print("DATASET VALIDATION REPORT")
        print("="*50)
        
        try:
            # Load datasets
            sn_df = self.load_pantheon()
            void_df = self.load_vide_voids()
            
            # Pantheon+ validation
            print(f"\nPANTHEON+ CATALOG:")
            print(f"  Total supernovae: {len(sn_df)}")
            if 'zCMB' in sn_df.columns:
                print(f"  Redshift range: {sn_df['zCMB'].min():.3f} - {sn_df['zCMB'].max():.3f}")
                print(f"  SNe in analysis range (0.01 < z < 0.15): {len(sn_df[(sn_df['zCMB'] > 0.01) & (sn_df['zCMB'] < 0.15)])}")
            
            # Check for coordinates
            coord_cols = ['RA', 'DEC', 'ra', 'dec']
            has_coords = any(col in sn_df.columns for col in coord_cols)
            print(f"  Has coordinates: {has_coords}")
            
            # VIDE validation  
            print(f"\nVIDE VOID CATALOG:")
            print(f"  Total voids: {len(void_df)}")
            
            # Try to identify coordinate columns
            possible_coords = [col for col in void_df.columns if any(x in col.lower() for x in ['ra', 'dec', 'x', 'y', 'z'])]
            print(f"  Possible coordinate columns: {possible_coords}")
            
            # Summary
            print(f"\n✅ Data loading successful!")
            return True
            
        except Exception as e:
            print(f"\n❌ Data validation failed: {e}")
            return False

if __name__ == "__main__":
    # Run validation
    loader = VCH001DataLoader()
    success = loader.validate_datasets()
    
    if success:
        print(f"\n🎉 Ready to proceed with VCH-001 analysis!")
    else:
        print(f"\n⚠️  Please check data downloads and try again.")