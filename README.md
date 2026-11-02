# Secure Anonymous CR Voting System

A localhost-first academic prototype for a class representative election. This is not certified or suitable for a real institutional election.

## Current phase: authentication and roster foundation

Implemented:
- File-backed identity records, separate from the ballot-box storage directory.
- Password hashes using Werkzeug scrypt; plaintext passwords are not persisted.
- HTTP-only, SameSite=Lax session cookies and CSRF checks.
- Explicit first-admin bootstrap through environment variables.
- Main Admin can provision Faculty Officer accounts scoped to a class.
- Main Admin can import a class roster from CSV.
- Roster import validates required fields, duplicate roll numbers/emails, file size and row count.
- Faculty Officers can see the eligible-student count only for their assigned class.

Not implemented yet: student self-registration, institutional email OTP, candidate applications, anonymous voting credentials, ballot casting, encryption, receipts, tallying, or publication.

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

## Importing the official roster

The Main Admin uploads a UTF-8 CSV to:
`POST /admin/classes/{class_id}/roster/import`

Required CSV header columns:
`roll_number,name,email`

Example:
```csv
roll_number,name,email
23CSB0B21,Student One,student1@example.edu
23CSB0B22,Student Two,student2@example.edu
```

The import is limited to 1 MB and 5,000 rows. Roll numbers and email addresses must be unique within the uploaded class roster. A new import replaces the previous roster for that class. Keep the original official roster separately as an institutional record.

The current importer validates email syntax only. It deliberately does not assume a campus email pattern or treat a listed email as proof of ownership. Institutional email format and OTP delivery must be configured before student registration is enabled.

A Faculty Officer can retrieve only the eligible count for their assigned class:
`GET /faculty/classes/{class_id}/roster`

## Initial API flow

1. `GET /auth/csrf` — obtain a CSRF token.
2. `POST /auth/login` — send JSON email/password with the `X-CSRF-Token` header.
3. `GET /auth/me` — inspect the current account role and class assignment.
4. Main Admin only: `POST /admin/faculty` with email, password, display_name, and class_id, plus the current CSRF header.
5. Main Admin only: upload the CSV roster to the endpoint above as multipart form field `file`.
6. `POST /auth/logout` — end the session with the current CSRF token.

A frontend has not been added yet.

## Security decisions and limitations

- Identity and ballot records must remain separate; never store student IDs, emails, or session IDs in ballot records.
- The selected policy is independent dual-recipient decryption: Main Admin and Faculty Officer each hold a separate key and can independently decrypt ballots. This is not threshold decryption and does not protect ballot secrecy from either authorized key holder.
- Localhost cannot defend against a fully compromised host or malicious application operator.
- No custom cryptographic primitive will be implemented. Anonymous credentials and ballot encryption require reviewed standards, maintained libraries, documented key lifecycle, and tests.
- Do not use this prototype for a real election.
