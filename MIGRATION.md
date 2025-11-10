# Migration Guide - Multi-Market Structure

This document explains the changes from the previous single-market structure to the new multi-market structure.

## Summary of Changes

The codebase has been restructured to support multiple markets (India and Australia) while maintaining backwards compatibility with existing workflows.

## What Changed

### 1. File Organization

**Before:**
```
src/
├── main.py
├── config.py
├── data_fetcher.py
├── btst_scanner.py
├── swing_scanner.py
└── notifier.py
```

**After:**
```
src/
├── config/
│   ├── base_config.py (shared)
│   ├── india_config.py (India-specific)
│   └── australia_config.py (Australia-specific)
├── shared/
│   ├── data_fetcher.py (multi-market support)
│   └── notifier.py (shared)
├── markets/
│   ├── india/
│   │   ├── btst_scanner.py
│   │   └── swing_scanner.py
│   └── australia/
│       └── swing_scanner.py
├── main_india.py (new)
├── main_australia.py (new)
└── main.py (deprecated, redirects to main_india.py)
```

### 2. Import Changes

**Before:**
```python
from config import Config
from data_fetcher import DataFetcher
from btst_scanner import BTSTScanner
```

**After:**
```python
from config.india_config import IndiaConfig
from shared.data_fetcher import DataFetcher
from markets.india.btst_scanner import BTSTScanner
```

### 3. Configuration Changes

**Before:**
```python
config = Config()
fetcher = DataFetcher()
```

**After:**
```python
config = IndiaConfig()  # or AustraliaConfig()
fetcher = DataFetcher(config, market="india")
```

## Backwards Compatibility

The old `src/main.py` still works and automatically redirects to `src/main_india.py`. This ensures:
- Existing GitHub Actions workflows continue to work
- Local scripts using `python src/main.py` still function
- No immediate migration required

However, `src/main.py` is **deprecated** and will be removed in a future version. Please update to `src/main_india.py`.

## Migration Steps

### For GitHub Actions

**Old workflow:**
```yaml
run: python src/main.py
```

**New workflow (recommended):**
```yaml
run: python src/main_india.py
```

### For Local Scripts

**Old:**
```bash
python src/main.py --test
```

**New:**
```bash
python src/main_india.py --test
```

### For Custom Integrations

If you have custom scripts importing from the scanner:

**Old:**
```python
from src.config import Config
from src.btst_scanner import BTSTScanner
```

**New:**
```python
from src.config.india_config import IndiaConfig
from src.markets.india.btst_scanner import BTSTScanner
```

## What You Need to Do

### Immediate (Optional)
1. Update workflow file from `src/main.py` to `src/main_india.py`
2. Test that scans still work correctly

### Before Next Release (Required)
1. Update all references from `main.py` to `main_india.py`
2. Update any custom scripts to use new import paths
3. Prepare for removal of deprecated files in next major version

## Testing Your Migration

1. **Test Indian scanner:**
   ```bash
   python src/main_india.py --test
   ```

2. **Test Australian scanner (if using):**
   ```bash
   python src/main_australia.py --test
   ```

3. **Test backwards compatibility:**
   ```bash
   python src/main.py --test  # Should show deprecation warning
   ```

## Benefits of New Structure

1. **Cleaner organization**: Market-specific code is separated
2. **Easier maintenance**: Changes to one market don't affect others
3. **Scalability**: Easy to add new markets (e.g., US, Europe)
4. **Shared code**: Common functionality in `shared/` reduces duplication
5. **Better testing**: Each market can be tested independently

## Removed Files

The following files are now redundant but kept for backwards compatibility:
- `src/config.py` (use `config/india_config.py` instead)
- `src/data_fetcher.py` (use `shared/data_fetcher.py` instead)
- `src/btst_scanner.py` (use `markets/india/btst_scanner.py` instead)
- `src/swing_scanner.py` (use `markets/india/swing_scanner.py` instead)
- `src/notifier.py` (use `shared/notifier.py` instead)

These files will be removed in version 2.0.

## Australian Market

If you want to enable Australian market scanning:

1. Review `README-AUSTRALIA.md`
2. Enable the workflow `.github/workflows/daily_scan_australia.yml`
3. The scanner will run automatically at 4:15 PM AEST

## Questions or Issues?

If you encounter any issues during migration:
1. Check that all files are in the correct locations
2. Verify Python path includes `src/` directory
3. Test with `--test` flag first
4. Review error messages for import path issues

## Rollback

If you need to rollback to the old structure:
1. Checkout the previous commit before the migration
2. The old single-market structure will be restored
3. Report any issues you encountered

## Future Plans

- Version 2.0: Remove all deprecated files
- Version 2.1: Add US market support
- Version 2.2: Cross-market correlation analysis
