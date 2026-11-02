# Requirement-to-test mapping

| Requirement | Current feature | Test evidence | Status |
| --- | --- | --- | --- |
| Separate identity and ballot storage roots | `Settings` storage layout | Application startup creates all roots | Complete |
| Atomic, locked state transition | `AtomicJsonStore` | `test_transaction_persists_json_atomically` | Complete |
| Tamper-evident administrative audit | SHA-256 linked events | `test_hash_chain_detects_tampering` | Foundation only; external checkpoint still required |
| Role definitions | `Role` domain type | Authentication and authorization tests | Complete |
| Local session authentication | Scrypt password hashes, HTTP-only SameSite session cookie, CSRF checks | `tests/test_auth.py` | Implemented; hardening pending |
| Main Admin bootstrap | Explicit environment-configured first-admin creation | `test_bootstrap_admin_can_login_and_view_session` | Implemented |
| Faculty provisioning | Main Admin creates class-scoped Faculty Officer accounts | `test_admin_can_create_class_scoped_faculty` | Implemented |
| Official roster import | Admin-only UTF-8 CSV import with duplicate, size and row validation | `tests/test_roster.py` | Implemented; exact institution-specific email policy pending |
| Faculty class isolation | Faculty can read only assigned class roster summary | `test_faculty_cannot_read_other_class_roster` | Implemented |
| Student email ownership verification | Not yet implemented | OTP provider and rate-limit tests required | Pending |
| Roster-based student registration | Not yet implemented | Must match official roll number/email pair | Pending |
| Anonymous credential | Not yet implemented | Protocol approval and vetted library required | Pending |
| One vote / atomic nullifier | Not yet implemented | Protocol approval and concurrency tests required | Pending |
| Dual-recipient ballot encryption | Not yet implemented | Protocol/library decision and crypto tests required | Pending |
| Candidate workflow | Not yet implemented | Planned | Pending |
| Manifest freeze | Not yet implemented | Planned | Pending |
| Tally and publication | Not yet implemented | Protocol approval and end-to-end tests required | Pending |

Authentication and roster management are an initial local prototype, not a production identity provider. Do not expose it to the public internet. Before deployment, add rate limiting, secure HTTPS cookies, account recovery policy, security review, and operational key management.
