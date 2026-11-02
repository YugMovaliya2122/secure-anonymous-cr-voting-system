# Architecture and cryptographic decision gate

## Foundation architecture

The prototype has three local storage roots:

| Area | Stores | Must never store |
| --- | --- | --- |
| Identity | roster, authentication state, candidate applications, credential-issued state | vote choice, ballot ID, nullifier |
| Ballot box | encrypted ballots, nullifiers, receipt values, commitments | names, email addresses, roll numbers, login sessions |
| Audit | administrative events and integrity checkpoints | vote choices, passwords, OTPs |

Every role check will be performed server-side. The UI is not an access-control boundary.

## Approved policy decision

The project owner selected **dual-recipient decryption**. Both the Main Administrator and Faculty Election Officer are intended to decrypt a ballot independently. This conflicts with the stronger administrator-resistance goal in the original specification. The project will disclose this limitation in the user interface, code comments, tests, and final documentation.

## Protocol proposal - approval required before implementation

No cryptographic voting module is implemented yet. The proposed construction is:

1. **Anonymous credential:** RFC 9474 RSA blind signatures using the randomized preparation variant, election-bound credential messages, and an election-scoped nullifier. A maintained implementation must be selected; no low-level RSA or blind-signature arithmetic will be written in this repository.
2. **Ballot encryption:** each ballot receives a fresh symmetric data-encryption key and nonce. The plaintext ballot is authenticated and encrypted with a vetted AEAD. The data key is independently wrapped for the Main Administrator and Faculty Officer using a standards-compliant HPKE implementation (RFC 9180) with election ID and frozen manifest digest as authenticated context.
3. **Manifest and audit signatures:** Ed25519 signatures from keys kept outside version control; SHA-256 for commitments and audit checkpoints.
4. **Tally:** either authorized recipient may decrypt the ballot set after election close. The tally counts only accepted, valid ballots and produces an aggregate result package. This is not threshold decryption.

Before code is added, the selected Python libraries, exact algorithm suite, key lifecycle, serialization format, validation rules, and tests must be documented and approved. The RFCs define protocols, but they do not by themselves make a web voting system safe.

## Deployment limit

The first release is localhost-only. A compromised host can alter the program, inspect memory, or collect timing metadata. It must not be used for a real election.
