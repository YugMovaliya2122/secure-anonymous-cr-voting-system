# Secure Anonymous CR Voting System

A localhost-first academic prototype for class representative voting. It is not certified or suitable for a real institutional election.

## Current phase: authentication and roster foundation

Implemented:
- File-backed identity records, separate from the ballot-box directory.
- Password hashes using Werkzeug scrypt; plaintext passwords are not persisted.
- HTTP-only, SameSite=Lax sessions and CSRF checks.
- Explicit first-admin bootstrap through environment variables.
- Main Admin can provision class-scoped Faculty Officer accounts.
- Main Admin can import an official class roster from UTF-8 CSV.
- Roster import checks required columns, duplicate roll numbers/emails, file size and row count.
- Faculty Officers can retrieve the eligible-student count only for their assigned class.

Not implemented: student registration, institutional email OTP, candidate applications, anonymous credentials, ballot casting, encryption, receipts, tallying or publication.

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

For macOS/Linux, activate the virtual environment and install the project, then:
```bash
export BOOTSTRAP_ADMIN_EMAIL="admin@example.edu"
export BOOTSTRAP_ADMIN_PASSWORD="replace-with-a-long-unique-password"
export PYTHONPATH=src
python -m flask --app voting_system.app:create_app run
```

Private data is created under `instance/data/`. Keep it out of version control. The first admin is created only if the user store is empty. Bootstrap passwords must be 12–256 characters.

## Official roster import

Main Admin uploads UTF-8 CSV to `POST /admin/classes/{class_id}/roster/import` as multipart field `file`.

Required header:
```csv
roll_number,name,email
23CSB0B21,Student One,student1@example.edu
23CSB0B22,Student Two,student2@example.edu
```

Limits: 1 MB and 5,000 students. Roll numbers and emails must be unique within the file. Import replaces the class's previous roster. Keep the institutional source file separately.

Faculty can read only the eligible count for their assigned class:
`GET /faculty/classes/{class_id}/roster`

The importer currently checks email syntax, not the institution's domain convention or ownership. Email OTP and the exact student email format must be configured before student self-registration is enabled.

## Existing authentication API

- `GET /auth/csrf`: get a CSRF token.
- `POST /auth/login`: JSON email/password plus `X-CSRF-Token`.
- `GET /auth/me`: current account and role.
- `POST /admin/faculty`: Main Admin provisions faculty with email, password, display_name, class_id.
- `POST /auth/logout`: logout with CSRF token.

There is no frontend yet.

## Security decisions and limitations

- Identity and ballot records must remain separate; never place student IDs, emails or session IDs in ballot records.
- Main Admin and Faculty Officer independently hold separate decryption keys and can independently decrypt ballots. This is not threshold decryption and does not protect ballot secrecy from either key holder.
- A localhost app cannot defend against a fully compromised host or malicious application operator.
- No custom cryptographic primitive will be implemented. Anonymous credentials and ballot encryption require reviewed standards, maintained libraries, documented key lifecycle and tests.
- Do not use this prototype for a real election.
