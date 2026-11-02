# Requirement-to-test mapping

| Requirement | Current feature | Test evidence | Status |
| --- | --- | --- | --- |
| Separate identity and ballot storage roots | `Settings` storage layout | Application startup creates all three roots | Complete |
| Atomic, locked state transition | `AtomicJsonStore` | `test_transaction_persists_json_atomically` | Complete |
| Tamper-evident administrative audit | SHA-256 linked events | `test_hash_chain_detects_tampering` | Foundation only; external checkpoint still required |
| Role definitions | `Role` domain type | Authentication and role-gate tests | Complete |
| Local session authentication | Scrypt password hashes, HTTP-only SameSite session cookie, CSRF checks | `tests/test_auth.py` | Implemented; rate limiting and production hardening pending |
| Main Admin bootstrap | Explicit environment-configured first-admin creation | `test_bootstrap_admin_can_login_and_view_session` | Implemented |
| Faculty provisioning | Main Admin creates class-scoped Faculty Officer accounts | `test_admin_can_create_class_scoped_faculty` | Implemented |
| Roster eligibility | Not yet implemented | Planned | Pending |
| Anonymous credential | Not yet implemented | Protocol approval and vetted library required | Pending |
| One vote / atomic nullifier | Not yet implemented | Protocol approval and concurrency tests required | Pending |
| Dual-recipient ballot encryption | Not yet implemented | Protocol/library decision and crypto tests required | Pending |
| Candidate workflow | Not yet implemented | Planned | Pending |
| Manifest freeze | Not yet implemented | Planned | Pending |
| Tally and publication | Not yet implemented | Protocol approval and end-to-end tests required | Pending |

Authentication is an initial local prototype, not a production identity provider. Do not expose it to the public internet. Before a real deployment, add rate limiting, secure HTTPS cookies, account recovery policy, security review, and operational key management.
