# Output Risk Profile

| Risk | Required prevention | Release evidence |
| --- | --- | --- |
| Direct ledger edit | Fingerprint chain and core-only writes | Tamper self-check |
| Partial batch append | Validate full batch before atomic replace | Batch rollback self-check |
| Concurrent append loss | Exclusive single-writer lock | Lock-contention self-check |
| Same-origin triangulation | Distinct class, independence key, publisher, location, and packet fingerprint | Conflicting-source fixture |
| Company claim promoted to fact | Claim-kind audit rule | Blocked fixture |
| Counterevidence hidden | Counter-query and counter-source checks | Public research fixture |
| Premature search stop | Two stable search rounds per high-priority public-research question | Audit self-check |
| Stale completion claim | Relevance-aware tail invalidation plus ledger-prefix and artifact fingerprints | Tail-append and ready-after-correction stale-audit self-check |
| Stale runtime or profile | Core and profile fingerprints | Stale-audit self-check |
| Invalid upstream evidence | Claim lineage and recursive audit bindings | Cross-skill audit self-check |
| Waiver produces ready | Status floor at partial | Waiver self-check |
| Hidden runtime missing | No prompt-only fallback | Install simulation |
| Unsupported public claim | Real end-to-end run plus blind human review | Release report |
