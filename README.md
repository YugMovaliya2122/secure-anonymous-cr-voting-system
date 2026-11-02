# Secure Anonymous CR Voting System

A localhost-first academic prototype for a class representative election. This is not certified or suitable for a real institutional election.

## Current phase: authentication foundation

Implemented:
- File-backed identity records, separate from the ballot-box storage directory.
- Password hashes using Werkzeug scrypt; plaintext passwords are not persisted.
- HTTP-only, SameSite=Lax session cookies and CSRF checks.
- Explicit first-admin bootstrap through environment variables.
- Main Admin can provision Faculty Officer accounts scoped to a class.
- Server-side role checks.

Not implemented yet: official roster import/verification, student email OTP, candidate applications, anonymous voting credentials, ballot casting, encryption, receipts, tallying, or publication.

## Run locally (Python 3.11+)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
$env:BOOTSTRAP_ADMIN_EMAIL = "admin@example.edu"
$env:BOOTSTRAP_ADMIN_PASSWORD = "replace-with-a-long-unique-password"
$env:PYTHONPATH = "src"
python -m flask --app voting_system.app:create_app run
```

For macOS/Linux, activate the virtual environment, install the project, then:
```bash
export BOOTSTRAP_ADMIN_EMAIL="admin@example.edu"
export BOOTSTRAP_ADMIN_PASSWORD="replace-with-a-long-unique-password"
export PYTHONPATH=src
python -m flask --app voting_system.app:create_app run
```

The app creates private local data under `instance/data/`, including the identity store and a random session-signing secret. Keep this directory private and out of version control. The first admin is created only when the user store is empty. Bootstrap password length is 12–256 characters.

## Initial API flow

1. `GET /auth/csrf` — obtain a CSRF token.
2. `POST /auth/login` — send JSON email/password with the `X-CSRF-Token` header.
3. `GET /auth/me` — inspect the current account role and class assignment.
4. Main Admin only: `POST /admin/faculty` with email, password, display_name, and class_id, plus the current CSRF header.
5. `POST /auth/logout` — end the session with the current CSRF token.

A frontend has not been added yet.

## Security decisions and limitations

- Identity and ballot records must remain separate; never store student IDs, emails, or session IDs in ballot records.
- The selected policy is independent dual-recipient decryption: Main Admin and Faculty Officer each hold a separate key and can independently decrypt ballots. This is not threshold decryption and does not protect ballot secrecy from either authorized key holder.
- Localhost cannot defend against a fully compromised host or malicious application operator.
- No custom cryptographic primitive will be implemented. Anonymous credentials and ballot encryption require reviewed standards, maintained libraries, documented key lifecycle, and tests.
- Do not use this prototype for a real election.
