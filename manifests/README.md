# Repository integrity manifests

- `REPOSITORY_FILE_MANIFEST.csv` lists each packaged repository file except the manifest files themselves, with byte size and SHA-256 digest.
- `SHA256SUMS.txt` lists SHA-256 digests for every file present when the checksum list was generated, except `SHA256SUMS.txt` itself. It includes `REPOSITORY_FILE_MANIFEST.csv`.

The full 80-file local target archive is intentionally not part of this GitHub package. See `docs/DATA_QUALITY_AUDIT_NOTES.md` and run the provided copy/audit scripts on the owner's machine.
