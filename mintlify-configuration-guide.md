# Mintlify Configuration Guide

This document provides guidance on configuring Mintlify for the Clary AI documentation.

## Configuration Files

Mintlify has moved from using `mint.json` to `docs.json` as their primary configuration file:

- `docs.json` - The new recommended configuration file
- `mint.json` - The legacy configuration file (still supported but being phased out)

## Schema

The correct schema URL for Mintlify configuration is:

```json
"$schema": "https://mintlify.com/docs.json"
```

## Theme Property

The theme property must be one of the following values:

- `mint` - Classic documentation theme with time-tested layouts
- `maple` - Modern, clean aesthetics for AI and SaaS products
- `palm` - Sophisticated fintech theme for enterprise documentation
- `willow` - Stripped-back essentials for distraction-free documentation
- `linden` - Retro terminal vibes with monospace fonts
- `almond` - Card-based organization with minimalist design

## Navigation Structure

Mintlify has completely redesigned their navigation structure in the new format. The key differences are:

1. Navigation is now a nested structure with tabs, groups, and pages
2. Properties like `tabs` now use `tab` instead of `name` and `href` instead of `url`
3. The structure is more intuitive and easier to maintain

## Common Issues

### Invalid discriminator value

If you encounter this error:

```
Invalid docs.json: #.theme: Invalid discriminator value. Expected 'mint' | 'maple' | 'palm' | 'willow' | 'linden' | 'almond'
```

Make sure:

1. The `theme` property is present in your configuration file
2. The value is one of the allowed values listed above
3. The `$schema` URL is correct
4. There are no duplicate properties in your JSON file

### Navigation structure issues

If you encounter navigation-related errors, make sure:

1. You're using the correct property names (`tab` instead of `name`, `href` instead of `url`)
2. Your navigation structure follows the new nested format
3. All referenced pages exist in your repository

## Deployment Best Practices

1. Use a single configuration file (`docs.json`) to avoid conflicts
2. Validate your JSON configuration before deployment
3. Follow Mintlify's example configurations for best practices
4. Regularly check Mintlify's documentation for schema changes

## References

- [Mintlify Settings Documentation](https://mintlify.com/docs/settings)
- [Mintlify Navigation Documentation](https://mintlify.com/docs/navigation)
- [Mintlify Themes Documentation](https://mintlify.com/docs/themes)
