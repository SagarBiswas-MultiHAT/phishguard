# Security

## Threat Model

This application stores tasks locally. Threats include unauthorized access to the local data file, accidental data loss, or corrupted storage. Network access is not required, and no telemetry is collected.

## Secure Defaults

- Atomic saves with backup rotation.
- Rotating logs to avoid unbounded disk usage.
- Optional encryption using a password-derived key.

## Encrypted Storage

Encrypted storage uses a per-file salt and PBKDF2-HMAC-SHA256 with strong iterations. The password is never stored. If the password is lost, data cannot be recovered.

## Reporting

For security issues, open a private issue or contact the maintainers.
