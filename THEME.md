# Mintlify Theme Configuration

This document explains the theme configuration for the Clary AI documentation.

## Theme Property

The `theme` property in the configuration files (`mint.json` and `docs.json`) is set to "mint", which is one of the allowed values:

- mint
- maple
- palm
- willow
- linden
- almond

## Error Resolution

If you encounter an error like:

```
Invalid docs.json: #.theme: Invalid discriminator value. Expected 'mint' | 'maple' | 'palm' | 'willow' | 'linden' | 'almond'
```

Make sure that:

1. The `theme` property is present in both `mint.json` and `docs.json`
2. The value is one of the allowed values listed above
3. There are no duplicate properties in the JSON files

## Configuration Files

The main configuration files are:

- `mint.json` - The primary configuration file used by Mintlify
- `docs.json` - A copy of the configuration for compatibility

Both files should have the same structure and content to avoid inconsistencies.
