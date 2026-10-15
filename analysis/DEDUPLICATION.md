# Vulnerability count verification

Verified against the syntax-corrected AI scan and the human scan on 14 October 2026.

Deduplication counts one underlying issue at a source location within each implementation. The overlapping Python S2068/S6779 findings on the same secret assignment are merged. The two JavaScript S6437 findings in AI sample 6 both trace to the same JWT_SECRET assignment at line 8 and are merged. Distinct issues within an implementation, and issues in different implementations, remain separate. This is not merely grouping by rule or by sample.

| Measure | AI | Human |
|---|---:|---:|
| Raw vulnerability findings | 16 | 9 |
| BLOCKER classifications | 16 | 9 |
| Deduplicated issues | 11 | 7 |
| Implementations with findings | 11 | 6 |
| Hardcoded-secret issues | 7 | 4 |
| All-interface binding issues | 4 | 2 |
| Database password-protection issues | 0 | 1 |

AI merges: samples 1, 2, 3 and 18 each have two rules for one secret assignment; sample 6 has two uses of one hardcoded JWT secret. Thus 16 − 5 = 11.

Human merges: samples 1 and 3 each have two rules for one secret assignment. Thus 9 − 2 = 7. Human sample 3 has two distinct issues (secret and interface binding), explaining seven issues across six implementations.

Affected AI samples: 1, 2, 3, 6, 9, 11, 17, 18, 19, 24, 26.
Affected human samples: 1, 2, 3, 11, 18, 20.

The CSV maps each underlying issue to its raw SonarQube finding IDs and source location. This audit verifies counts and duplicate relationships, not manual-review outcomes or exploitability. User-reported review decisions remain separate from these scanner-based counts. No scan records or review decisions were changed.
