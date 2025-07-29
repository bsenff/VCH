#!/usr/bin/env python3
"""
Deep investigation of VCH data quality issues
"""
import healpy as hp
import numpy as np
import pandas as pd
from astropy.io import fits
from astropy.table import Table
from pathlib import Path

def investigate_cmb_data():
    """Deep investigation of CMB data quality"""
    print('=' * 60)
    print('VCH-003 CMB DATA QUALITY INVESTIGATION')
    print('=' * 60)
    
    cmb_path = '../../datasets/planck_cmb/temperature_maps/COM_CMB_IQU-smica_2048_R3.00_full.fits'
    
    # Check FITS structure first
    with fits.open(cmb_path) as hdul:
        print('FITS Structure:')
        hdul.info()
        print()
        
        print('Primary header keywords:')
        primary = hdul[0].header
        for key in ['TELESCOP', 'INSTRUME', 'OBJECT', 'DATE-OBS', 'COMMENT']:
            value = primary.get(key, 'N/A')
            if key == 'COMMENT' and isinstance(value, list):
                print(f'  {key}: {value[0] if value else "N/A"}')
            else:
                print(f'  {key}: {value}')
        print()
        
        print('Extension 1 (data) header:')
        ext1 = hdul[1].header
        important_keys = ['TTYPE1', 'TTYPE2', 'TTYPE3', 'TUNIT1', 'TUNIT2', 'TUNIT3', 
                         'COORDSYS', 'ORDERING', 'NSIDE', 'FIRSTPIX', 'LASTPIX']
        for key in important_keys:
            print(f'  {key}: {ext1.get(key, "N/A")}')
        print()
        
        # Read the data
        data = hdul[1].data
        I_field = data['I_STOKES']
        
        print('Data Analysis:')
        print(f'  Data type: {I_field.dtype}')
        print(f'  Array shape: {I_field.shape}')
        print(f'  Total pixels: {len(I_field)}')
        print(f'  NSIDE (calculated): {hp.npix2nside(len(I_field))}')
        print()
        
        print('Temperature Statistics:')
        print(f'  Min: {np.min(I_field):.8f}')
        print(f'  Max: {np.max(I_field):.8f}')
        print(f'  Mean: {np.mean(I_field):.8f}')
        print(f'  Std: {np.std(I_field):.8f}')
        print(f'  RMS: {np.sqrt(np.mean(I_field**2)):.8f}')
        print()
        
        # Check for problematic values
        print('Data Quality Checks:')
        n_zeros = np.sum(I_field == 0.0)
        n_finite = np.sum(np.isfinite(I_field))
        n_nonzero = np.sum(I_field != 0.0)
        
        print(f'  Finite values: {n_finite}/{len(I_field)} ({100*n_finite/len(I_field):.1f}%)')
        print(f'  Non-zero values: {n_nonzero}/{len(I_field)} ({100*n_nonzero/len(I_field):.1f}%)')
        print(f'  Exact zeros: {n_zeros}/{len(I_field)} ({100*n_zeros/len(I_field):.1f}%)')
        print()
        
        # Check value distribution
        abs_vals = np.abs(I_field[I_field != 0])
        if len(abs_vals) > 0:
            print('Non-zero value distribution:')
            print(f'  Min |value|: {np.min(abs_vals):.8f}')
            print(f'  Max |value|: {np.max(abs_vals):.8f}')
            print(f'  Median |value|: {np.median(abs_vals):.8f}')
            print(f'  90th percentile: {np.percentile(abs_vals, 90):.8f}')
            print()
        
        # Sample some actual values
        print('Sample values (first 20 non-zero):')
        nonzero_indices = np.where(I_field != 0)[0]
        if len(nonzero_indices) > 0:
            sample_vals = I_field[nonzero_indices[:20]]
            for i, val in enumerate(sample_vals):
                print(f'  [{nonzero_indices[i]}]: {val:.8f}')
        print()

    # Expected CMB values for comparison
    print('Expected CMB Temperature Fluctuation Values:')
    print('  Typical RMS: ~100 μK (1e-4 K)')
    print('  Range: ±500 μK (±5e-4 K)')
    print('  Our RMS:', f'{np.std(I_field):.8f}', 'K')
    print('  Our range:', f'{np.min(I_field):.8f}', 'to', f'{np.max(I_field):.8f}', 'K')
    print()
    
    # Data interpretation
    print('=== DATA QUALITY ASSESSMENT ===')
    rms_microK = np.std(I_field) * 1e6  # Convert to microKelvin
    print(f'Temperature RMS in μK: {rms_microK:.2f}')
    
    if rms_microK < 1:
        print('❌ PROBLEMATIC: RMS too small for realistic CMB data')
        print('   Possible issues:')
        print('   - This might be a mask/confidence map, not temperature')
        print('   - Data units might be wrong')
        print('   - Heavily processed/filtered data')
        print('   - File corruption or wrong field')
    elif rms_microK < 50:
        print('⚠️  SUSPICIOUS: RMS lower than expected for CMB')
        print('   Typical Planck CMB RMS: 50-150 μK')
        print('   This data RMS:', f'{rms_microK:.2f} μK')
    elif rms_microK > 500:
        print('⚠️  SUSPICIOUS: RMS higher than expected')
        print('   This might include foreground contamination')
    else:
        print('✅ REASONABLE: RMS within expected range for CMB analysis')
    
    return rms_microK < 50  # Return True if data seems problematic

def investigate_galaxy_data():
    """Investigate high-z galaxy data quality"""
    print('\n' + '=' * 60)
    print('VCH-004 GALAXY DATA QUALITY INVESTIGATION')
    print('=' * 60)
    
    # Check the CANDELS data we used
    fits_path = '../../datasets/high_z_galaxies/candels_goodss/v1/hlsp_candels_hst_wfc3_goodss_santini_v1_mass_cat.fits'
    
    try:
        table = Table.read(fits_path)
        print(f'CANDELS GOODS-S Catalog Investigation:')
        print(f'  File: {Path(fits_path).name}')
        print(f'  Total galaxies: {len(table)}')
        print(f'  Columns: {len(table.columns)}')
        print()
        
        # Check redshift quality
        if 'zbest' in table.colnames:
            zbest = table['zbest']
            print('Redshift Quality Assessment:')
            print(f'  Redshift column: zbest')
            print(f'  Range: {np.min(zbest):.3f} - {np.max(zbest):.3f}')
            print(f'  Mean: {np.mean(zbest):.3f}')
            print(f'  Median: {np.median(zbest):.3f}')
            print()
            
            # High-z sample analysis
            high_z_mask = zbest > 8.0
            n_high_z = np.sum(high_z_mask)
            print(f'High-redshift sample (z > 8):')
            print(f'  Count: {n_high_z}')
            print(f'  Fraction: {100*n_high_z/len(table):.2f}%')
            print(f'  z range: {np.min(zbest[high_z_mask]):.2f} - {np.max(zbest[high_z_mask]):.2f}')
            print()
            
            # Check for coordinate coverage
            if 'RAdeg' in table.colnames and 'DECdeg' in table.colnames:
                ra_range = np.max(table['RAdeg']) - np.min(table['RAdeg'])
                dec_range = np.max(table['DECdeg']) - np.min(table['DECdeg'])
                print(f'Sky Coverage:')
                print(f'  RA range: {ra_range:.1f}°')
                print(f'  Dec range: {dec_range:.1f}°')
                print(f'  Area: ~{ra_range * dec_range:.1f} sq degrees')
                print()
            
            # The key issue: void overlap
            print('=== VOID OVERLAP ASSESSMENT ===')
            print('Key Issue: Do high-z galaxies overlap with void catalog?')
            print()
            
            # Load void catalog for comparison
            void_path = '../../datasets/vide/table1.dat'
            if Path(void_path).exists():
                void_df = pd.read_csv(void_path, sep=r'\s+', comment='#')
                void_z_range = f"{void_df['redshift'].min():.3f} - {void_df['redshift'].max():.3f}"
                print(f'Void catalog redshift range: {void_z_range}')
                print(f'Galaxy high-z range: {np.min(zbest[high_z_mask]):.2f} - {np.max(zbest[high_z_mask]):.2f}')
                print()
                print('❌ FUNDAMENTAL ISSUE IDENTIFIED:')
                print('   Void catalog: z < 0.15 (local universe)')
                print('   High-z galaxies: z > 8.0 (early universe)')
                print('   NO REDSHIFT OVERLAP for meaningful comparison!')
                print()
                print('🔍 REQUIRED FOR VCH-004:')
                print('   Need EITHER:')
                print('   1. High-z void catalog (z > 8) - not readily available')
                print('   2. Lower-z galaxy sample (z = 1-3) with environmental data')
                print('   3. Theoretical void evolution models to z > 8')
                
        return True  # Data quality issue identified
        
    except Exception as e:
        print(f'Error loading galaxy data: {e}')
        return False

def investigate_simulation_needs():
    """Document what's needed for VCH-005"""
    print('\n' + '=' * 60)
    print('VCH-005 SIMULATION DATA REQUIREMENTS')
    print('=' * 60)
    
    print('Current Status: Empty directories')
    sim_dirs = ['millennium', 'illustris', 'eagle']
    
    for sim_dir in sim_dirs:
        sim_path = Path(f'../../datasets/simulations/{sim_dir}')
        if sim_path.exists():
            files = list(sim_path.glob('*'))
            print(f'  {sim_dir}: {len(files)} files')
        else:
            print(f'  {sim_dir}: directory missing')
    print()
    
    print('=== WHAT VCH-005 ACTUALLY NEEDS ===')
    print()
    print('Purpose: Compare observed void properties with simulation predictions')
    print('to identify systematic artifacts vs real VCH effects')
    print()
    
    print('Required Data Types:')
    print('1. VOID CATALOGS from simulations:')
    print('   - Positions (x, y, z in Mpc/h)')
    print('   - Sizes (radius in Mpc/h)') 
    print('   - Redshifts (z = 0.0 - 0.2 to match observations)')
    print('   - Cosmology: Planck18 or similar')
    print()
    
    print('2. GALAXY CATALOGS from simulations:')
    print('   - Positions and redshifts')
    print('   - Mock photometry for comparison with surveys')
    print('   - Environmental classifications')
    print()
    
    print('3. SURVEY MASKS:')
    print('   - SDSS footprint geometry')
    print('   - Selection function effects')
    print('   - Completeness limits')
    print()
    
    print('=== SPECIFIC FILES NEEDED ===')
    print()
    
    print('Option 1 - Full Simulation Access:')
    print('  Millennium: ~TB-scale halo/galaxy catalogs')
    print('  Illustris-TNG: ~100GB snapshot files')
    print('  EAGLE: ~50GB subhalo catalogs')
    print('  → Requires significant download time and storage')
    print()
    
    print('Option 2 - Pre-processed Void Catalogs:')
    print('  Mock void catalogs derived from simulations')
    print('  ~MB-scale text files with void properties')
    print('  Available from cosmology groups/collaborations')
    print('  → Much more practical for this analysis')
    print()
    
    print('Option 3 - Statistical Summaries:')
    print('  Published void size/abundance functions')
    print('  Literature comparison data')
    print('  Theoretical predictions')
    print('  → Sufficient for framework validation')
    print()
    
    print('🎯 RECOMMENDATION:')
    print('VCH-005 can proceed with Option 2 or 3 rather than')
    print('downloading massive simulation datasets.')
    print('The framework is complete and ready for any of these approaches.')

def main():
    """Run complete data quality investigation"""
    print('VCH FRAMEWORK DATA QUALITY INVESTIGATION')
    print('=' * 60)
    
    # Investigate each module
    cmb_problematic = investigate_cmb_data()
    galaxy_problematic = investigate_galaxy_data()
    investigate_simulation_needs()
    
    # Summary and recommendations
    print('\n' + '=' * 60)
    print('INVESTIGATION SUMMARY & RECOMMENDATIONS')
    print('=' * 60)
    
    print('VCH-003 (CMB Analysis):')
    if cmb_problematic:
        print('  ❌ DATA QUALITY ISSUE: Temperature fluctuations too small')
        print('  📋 NEEDED: Verify we have actual temperature map, not mask/confidence')
        print('  🔍 ACTION: Check Planck Legacy Archive for proper temperature files')
    else:
        print('  ✅ DATA QUALITY ACCEPTABLE: Proceed with analysis')
    print()
    
    print('VCH-004 (High-z Galaxies):')
    if galaxy_problematic:
        print('  ❌ FUNDAMENTAL MISMATCH: No redshift overlap with void catalog')
        print('  📋 NEEDED: Either high-z voids OR lower-z galaxies')
        print('  🔍 ACTION: Redefine analysis scope or find different datasets')
    else:
        print('  ✅ DATA QUALITY ACCEPTABLE: Proceed with analysis')
    print()
    
    print('VCH-005 (Simulations):')
    print('  ✅ FRAMEWORK READY: Multiple data acquisition options available')
    print('  📋 RECOMMENDED: Use pre-processed void catalogs or literature data')
    print('  🔍 ACTION: Choose practical data source rather than full simulations')
    print()
    
    print('🎯 OVERALL RECOMMENDATION:')
    print('Document current attempts but acknowledge data limitations.')
    print('Update framework to specify proper data requirements.')
    print('Focus publication on VCH-001/002 confirmed results.')

if __name__ == '__main__':
    main()