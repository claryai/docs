# Mintlify Configuration Guide

This document provides guidance on configuring Mintlify for the Clary AI documentation.

## Configuration Files

Mintlify uses two main configuration files:

1. `mint.json` - The primary configuration file
2. `docs.json` - An alternative configuration file (used by some Mintlify installations)

## Schema

The schema URL should be set to:

```json
"$schema": "https://mintlify.com/docs.json"
```

Previously, we were using:

```json
"$schema": "https://mintlify.com/schema.json"
```

## Theme

The theme property must be one of the following values:

- mint
- maple
- palm
- willow
- linden
- almond

Example:

```json
"theme": "mint"
```

## Common Issues

### Invalid discriminator value

If you encounter this error:

```
Invalid docs.json: #.theme: Invalid discriminator value. Expected 'mint' | 'maple' | 'palm' | 'willow' | 'linden' | 'almond'
```

Make sure:

1. The `theme` property is present in your configuration files
2. The value is one of the allowed values
3. The `$schema` URL is correct
4. There are no duplicate properties in your JSON files

## Deployment

After making changes to the configuration files, commit and push them to the repository. Mintlify will automatically deploy the updated documentation.
