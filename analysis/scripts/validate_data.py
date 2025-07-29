#!/usr/bin/env python3
"""
Data validation script for VCH framework
"""
import healpy as hp
import numpy as np
import pandas as pd
from pathlib import Path
from astropy.table import Table

def validate_cmb_data():
    """Validate VCH-003 CMB data"""
    print("=" * 50)
    print("VCH-003 CMB DATA VALIDATION")
    print("=" * 50)
    
    cmb_files = [
        "../../datasets/planck_cmb/temperature_maps/COM_CMB_IQU-commander_2048_R3.00_full.fits",
        "../../datasets/planck_cmb/temperature_maps/COM_CMB_IQU-smica_2048_R3.00_full.fits"
    ]
    
    valid_cmb = False
    
    for cmb_file in cmb_files:
        cmb_path = Path(cmb_file)
        print(f"\nChecking: {cmb_path.name}")
        
        if not cmb_path.exists():
            print("  ❌ File does not exist")
            continue
            
        size_mb = cmb_path.stat().st_size / (1024**2)
        print(f"  📁 File size: {size_mb:.1f} MB")
        
        if size_mb < 1:
            print("  ❌ File too small (likely empty/failed download)")
            continue
            
        try:
            # Try to read the CMB map
            data = hp.read_map(str(cmb_path), field=None)
            
            if isinstance(data, list):
                print(f"  📊 Multi-field FITS: {len(data)} fields")
                T_cmb = data[0]  # Temperature field
                print(f"  🌡️ Temperature field statistics:")
            else:
                print(f"  📊 Single field FITS")
                T_cmb = data
                
            nside = hp.npix2nside(len(T_cmb))
            print(f"     NSIDE = {nside}")
            print(f"     Min: {np.min(T_cmb):.6f}")
            print(f"     Max: {np.max(T_cmb):.6f}")
            print(f"     Mean: {np.mean(T_cmb):.6f}")
            print(f"     RMS: {np.std(T_cmb):.6f}")
            
            nonzero_count = np.sum(np.abs(T_cmb) > 1e-10)
            print(f"     Non-zero pixels: {nonzero_count}/{len(T_cmb)}")
            
            if np.std(T_cmb) > 1e-6 and nonzero_count > len(T_cmb)//2:
                print("  ✅ Valid CMB temperature data detected!")
                valid_cmb = True
                break
            else:
                print("  ⚠️ Suspicious data (might be mask or confidence map)")
                
        except Exception as e:
            print(f"  ❌ Error reading file: {e}")
            
    return valid_cmb

def validate_high_z_data():
    """Validate VCH-004 high-redshift galaxy data"""
    print("\n" + "=" * 50)
    print("VCH-004 HIGH-Z GALAXY DATA VALIDATION")
    print("=" * 50)
    
    # Check HST data
    hst_file = "../../datasets/high_z_galaxies/hst/3dhst_master.phot.v4.1.cat"
    hst_path = Path(hst_file)
    
    print(f"\nChecking HST data: {hst_path.name}")
    if hst_path.exists():
        size_kb = hst_path.stat().st_size / 1024
        print(f"  📁 File size: {size_kb:.1f} KB")
        
        if size_kb > 10:
            try:
                # Try to read as ASCII catalog
                df = pd.read_csv(str(hst_path), sep=r'\s+', comment='#', nrows=10)
                print(f"  ✅ Valid ASCII catalog")
                print(f"  📊 Columns: {list(df.columns)}")
                print(f"  📊 Sample data shape: {df.shape}")
            except Exception as e:
                print(f"  ❌ Error reading: {e}")
        else:
            print("  ❌ File too small")
    else:
        print("  ❌ File does not exist")
    
    # Check CANDELS data
    print(f"\nChecking CANDELS data:")
    candels_dir = Path("../../datasets/high_z_galaxies/candels_goodss")
    
    if candels_dir.exists():
        fits_files = list(candels_dir.rglob("*.fits"))
        print(f"  📁 Found {len(fits_files)} FITS files")
        
        for fits_file in fits_files[:3]:  # Check first 3 files
            try:
                size_mb = fits_file.stat().st_size / (1024**2)
                print(f"  📄 {fits_file.name}: {size_mb:.1f} MB")
                
                if size_mb > 1:
                    # Try to read FITS table
                    table = Table.read(str(fits_file))
                    print(f"     ✅ Valid FITS table ({len(table)} rows, {len(table.columns)} columns)")
                    
                    # Look for redshift columns
                    z_cols = [col for col in table.columns if 'z' in col.lower() or 'redshift' in col.lower()]
                    if z_cols:
                        print(f"     🔍 Redshift columns found: {z_cols[:3]}")
                        
            except Exception as e:
                print(f"     ❌ Error reading: {e}")
    else:
        print("  ❌ CANDELS directory does not exist")

def validate_simulation_data():
    """Validate VCH-005 simulation data"""
    print("\n" + "=" * 50)
    print("VCH-005 SIMULATION DATA VALIDATION")
    print("=" * 50)
    
    sim_dirs = [
        "../../datasets/simulations/millennium",
        "../../datasets/simulations/illustris", 
        "../../datasets/simulations/eagle"
    ]
    
    for sim_dir in sim_dirs:
        sim_path = Path(sim_dir)
        print(f"\nChecking: {sim_path.name}")
        
        if sim_path.exists():
            files = list(sim_path.glob("*"))
            print(f"  📁 Directory exists with {len(files)} files")
            
            if len(files) == 0:
                print("  ❌ Directory is empty")
            else:
                for file in files[:3]:  # Check first 3 files
                    size_mb = file.stat().st_size / (1024**2)
                    print(f"  📄 {file.name}: {size_mb:.1f} MB")
        else:
            print("  ❌ Directory does not exist")

def main():
    """Run complete data validation"""
    print("VCH FRAMEWORK DATA VALIDATION")
    print("=" * 60)
    
    # Validate all datasets
    cmb_valid = validate_cmb_data()
    validate_high_z_data()
    validate_simulation_data()
    
    # Summary
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    
    print(f"VCH-003 CMB data: {'✅ READY' if cmb_valid else '❌ NEEDS ATTENTION'}")
    print(f"VCH-004 Galaxy data: ⚠️ PARTIAL (needs validation)")
    print(f"VCH-005 Simulation data: ❌ MISSING")
    
    if cmb_valid:
        print("\n🎉 At least VCH-003 can proceed with real CMB data!")
    
if __name__ == "__main__":
    main()