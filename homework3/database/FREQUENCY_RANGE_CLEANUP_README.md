# Frequency Range Cleanup Script

## Overview

This script removes all DX spots with frequencies outside the range of 7000-54000 kHz. It's designed as a one-time cleanup tool after implementing frequency filtering.

## What It Does

The script performs a cascading delete of frequency-out-of-range records:

1. **spot_grid_squares**: Skipped (table may not exist if migrations not run yet)
2. **dx_spots**: Deletes spot records where frequency < 7000 kHz OR frequency > 54000 kHz
3. **raw_spots**: Deletes orphaned raw spot records (those not referenced by remaining DX spots)

## Frequency Range

**Kept:** 7000 kHz to 54000 kHz (7 MHz to 54 MHz)
- Includes HF bands (40m, 30m, 20m, 17m, 15m, 12m, 10m)
- Includes VHF/UHF bands (6m, 4m, 2m, 70cm, 33cm, 23cm)

**Removed:** Below 7000 kHz or above 54000 kHz
- LF/MF frequencies (< 7 MHz)
- Microwave frequencies (> 54 MHz)

## Safety Features

- **Dry run preview**: Shows count and sample of spots to be deleted
- **Confirmation required**: Asks for explicit "yes" before proceeding
- **Transaction safety**: Uses database transactions - if anything fails, nothing is deleted
- **Verification**: Confirms cleanup was successful after completion

## Usage

```bash
cd homework3/database
python cleanup_frequency_ranges.py
```

## Example Output

```
Frequency Range Cleanup Script
This will permanently remove all DX spots with frequencies < 7000 kHz or > 54000 kHz.

Cleaning up DX spots outside frequency range (7000-54000 kHz)...
Database: dx_analysis
------------------------------------------------------------
Found 1,247 spots outside frequency range

Sample spots to be removed:
  CW: VK2BJ on 3500.0 kHz
  SSB: JA1ABC on 14200.0 kHz
  FT8: W1AW on 144174.0 kHz
  ... and 1,244 more

Delete 1247 out-of-range spots? (yes/no): yes

Starting cleanup...
ℹ Skipping spot_grid_squares cleanup (table may not exist yet)
✓ Deleted 1,247 DX spot records
✓ Deleted 1,013 orphaned raw spot records

Cleanup completed successfully!
Total records removed: 2,260
✓ Verification: No out-of-range frequency spots remaining

🎉 Cleanup completed successfully!
```

## Database Impact

**Tables affected:**
- `dx_spots`: Main spot records removed
- `raw_spots`: Orphaned raw text records removed

**Tables unaffected:**
- `wwv_announcements`: WWV data preserved (if table exists)
- `callsigns`: Callsign statistics preserved (may need separate cleanup if desired)
- `grid_squares`: Coordinate lookup table unchanged

## When to Use

- After implementing server-side frequency filtering
- When you want to clean up historical data outside your operating range
- Before running analytics that should only include your target frequency bands

## Important Notes

- **Backup first**: Always backup your database before running cleanup scripts
- **One-time use**: This script is designed for one-time cleanup, not ongoing filtering
- **Server filtering**: For ongoing filtering, use the DX cluster server configuration
- **Irreversible**: Deleted data cannot be recovered (unless you have a backup)
- **Migration compatibility**: The script works whether you've run migrations or not

## Related Files

- `scrapers/dx_cluster_live_pg.py`: Contains ongoing frequency filtering logic
- Server configuration: DX cluster frequency filter settings