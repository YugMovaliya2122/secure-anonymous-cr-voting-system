# Requirement-to-test mapping

| Requirement | Current feature | Test evidence | Status |
| --- | --- | --- | --- |
| Separate identity and ballot storage roots | `Settings` layout | App startup test | Complete |
| Atomic locked state transition | `AtomicJsonStore` | `test_transaction_persists_json_atomically` | Complete |
| Tamper-evident administrative audit | SHA-256 linked events | `test_hash_chain_detects_tampering` | Foundation only; external checkpoint required |
| Role definitions | `Role` enum | Authentication and role tests | Complete |
| Local session authentication | Scrypt hashes, HTTP-only SameSite cookie, CSRF | `tests/test_auth.py` | Implemented; hardening pending |
| Main Admin bootstrap | Environment-configured first admin | `test_bootstrap_admin_can_login_and_view_session` | Implemented |
| Faculty provisioning | Admin creates class-scoped Faculty Officer | `test_admin_can_create_class_scoped_faculty` | Implemented |
| Official roster import | Admin-only CSV import with duplicate, size and row validation | `tests/test_roster.py` | Implemented; institution-specific email rule pending |
| Faculty class isolation | Faculty sees only own class roster count | `test_faculty_cannot_read_other_class_roster` | Implemented |
| Student email ownership verification | Not implemented | OTP and rate-limit tests required | Pending |
| Roster-based student registration | Not implemented | Must match official roll/email pair | Pending |
| Anonymous credential | Not implemented | Protocol approval and vetted library required | Pending |
| One vote / atomic nullifier | Not implemented | Concurrency tests required | Pending |
| Dual-recipient ballot encryption | Not implemented | Reviewed crypto library and key tests required | Pending |
| Candidate workflow | Not implemented | Planned | Pending |
| Manifest freeze | Not implemented | Planned | Pending |
| Tally and publication | Not implemented | End-to-end tests required | Pending |

This remains a localhost academic prototype. Do not expose it publicly. Production hardening, independent security review and operational key management remain necessary.
