# flarum/abandoned-extensions

A community-maintained list of abandoned Flarum extensions, with optional replacement suggestions.

This list is fetched weekly by Flarum core versions `1.8.16` and `2.0.0` (and later versions) and surfaced in the admin panel to notify administrators when an installed extension is no longer maintained.

## Format

`abandoned.json` is a JSON object keyed by composer package name. Each entry may optionally include a `replacement` package name.

```json
{
  "vendor/package-name": {
    "replacement": "vendor/replacement-package"
  },
  "vendor/no-replacement-package": {}
}
```

## Contributing

To add an extension to the list, open a pull request editing `abandoned.json`.

Please ensure:
- The package name matches the composer package name exactly (e.g. `vendor/package-name`)
- The extension is genuinely abandoned — no activity, no response to issues, or explicitly marked as such by the author
- If a replacement exists, it provides equivalent or better functionality
- The relevant discussion on `discuss.flarum.org` is also tagged `Abandoned`

**This list is not for forks.** If an extension's original author has abandoned it but a community fork is actively maintained, the original package should not be listed here — users should be pointed to the fork via the `replacement` field only if the fork has taken over the original's role. Do not list an extension simply because a fork exists.
