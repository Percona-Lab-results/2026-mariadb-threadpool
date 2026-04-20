# Project Instructions for Claude

## Report Workflow

When making any report change, always do all of these in sequence without being asked:
1. Regenerate interactive report (`./visuals/make_custom_mariadb.sh`)
2. Generate test-report.html out of REPORT.md
3. Update the Google Doc in-place via `gws drive files update --params '{"fileId":"1e3DXhFsyfJS2K9XsjOEFlkbvlbFkcNGunENTMfsKrzA"}' --upload test-report.html --upload-content-type "text/html"`
