# Requirement-to-test mapping (foundation)

| Requirement | Current feature | Test evidence | Status |
| --- | --- | --- | --- |
| Separate identity and ballot storage roots | `Settings` storage layout | application startup test indirectly exercises root creation | Foundation complete |
| Atomic, locked state transition | `AtomicJsonStore` | `test_transaction_persists_json_atomically` | Foundation complete |
| Tamper-evident administrative audit | SHA-256 linked events | `test_hash_chain_detects_tampering` | Foundation complete, requires independent checkpoint |
| Role definitions | `Role` domain type | Planned | Foundation complete |
| Roster eligibility | Not yet implemented | Planned | Pending |
| Anonymous credential | Not yet implemented | Protocol approval required | Pending |
| One vote / atomic nullifier | Not yet implemented | Protocol approval required | Pending |
| Dual-recipient ballot encryption | Not yet implemented | Protocol approval required | Pending |
| Candidate workflow | Not yet implemented | Planned | Pending |
| Manifest freeze | Not yet implemented | Planned | Pending |
| Tally and publication | Not yet implemented | Protocol approval required | Pending |
