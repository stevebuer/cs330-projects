# FT4/FT8 Cleanup Script

## Overview

This script removes all existing FT4 and FT8 mode DX spots from the database. It's designed as a one-time cleanup tool after implementing server-side filtering.

## What It Does

The script performs a cascading delete of FT4/FT8 related records:

1. **spot_grid_squares**: Skipped (table may not exist if migrations not run yet)
2. **dx_spots**: Deletes the main spot records where mode is FT4 or FT8
3. **raw_spots**: Deletes orphaned raw spot records (those not referenced by remaining DX spots)

## Safety Features

- **Dry run preview**: Shows count and sample of spots to be deleted
- **Confirmation required**: Asks for explicit "yes" before proceeding
- **Transaction safety**: Uses database transactions - if anything fails, nothing is deleted
- **Verification**: Confirms cleanup was successful after completion

## Usage

```bash
cd homework3/database
python cleanup_ft4_ft8.py
```

## Example Output

```
FT4/FT8 Spot Cleanup Script
This will permanently remove all FT4 and FT8 mode spots from the database.

Cleaning up FT4 and FT8 spots from database...
Database: dx_analysis
--------------------------------------------------
Found 1,247 FT4/FT8 spots to remove

Sample spots to be removed:
  FT8: VK2BJ on 7074.0 kHz
  FT4: JA1ABC on 3573.0 kHz
  FT8: W1AW on 14074.0 kHz
  ... and 1,244 more

Delete 1247 FT4/FT8 spots? (yes/no): yes

Starting cleanup...
✓ Deleted 234 grid square records
✓ Deleted 1,247 DX spot records
✓ Deleted 1,013 orphaned raw spot records

Cleanup completed successfully!
Total records removed: 2,494
✓ Verification: No FT4/FT8 spots remaining

🎉 Cleanup completed successfully!
```

## Database Impact

**Tables affected:**
- `spot_grid_squares`: Grid coordinate data removed
- `dx_spots`: Main spot records removed
- `raw_spots`: Orphaned raw text records removed

**Tables unaffected:**
- `wwv_announcements`: WWV data preserved
- `callsigns`: Callsign statistics preserved (may need separate cleanup if desired)
- `grid_squares`: Coordinate lookup table unchanged

## When to Use

- After implementing server-side FT4/FT8 filtering
- When you want to clean up historical data
- Before running analytics that shouldn't include weak-signal digital modes

## Important Notes

- **Backup first**: Always backup your database before running cleanup scripts
- **One-time use**: This script is designed for one-time cleanup, not ongoing filtering
- **Server filtering**: For ongoing filtering, use the DX cluster server configuration
- **Irreversible**: Deleted data cannot be recovered (unless you have a backup)
- **Migration compatibility**: The script works whether you've run the `spot_grid_squares` migration or not. If the table doesn't exist yet, it will skip that cleanup step.

## Related Files

- `scrapers/dx_cluster_live_pg.py`: Contains ongoing FT4/FT8 filtering logic
- Server configuration: DX cluster filter settings