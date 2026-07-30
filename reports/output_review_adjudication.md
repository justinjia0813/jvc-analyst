# Output Review Adjudication

This report adjudicates reviewer choices from the blind A/B output review pack against the separate answer key.

- Pairs: `2`
- Judgments: `2`
- Pending: `0`
- Agreement rate: `50.0`
- Invalid decisions: `0`
- Answer keys revealed: `2`
- Pending/invalid answers hidden: `0`
- Reviewer checklist: `2` ready / `2` total
- Reviewer metadata present: `true`
- Blind review attested: `true`
- Raw content excluded: `true`
- Ready for human evidence: `true`

## Case Adjudication

| Case | Reviewer | Expected | Status | Confidence | Reason |
| --- | --- | --- | --- | ---: | --- |
| glass-substrate-public-research-output | B | B | match | 0.7 | 实用性更好 |
| industrial-vision-market-model-output | B | A | disagree | 0.3 | 格式处理更胜一筹 |

## Reviewer Checklist

| Case | Readiness | Answer key | Decision file |
| --- | --- | --- | --- |
| `glass-substrate-public-research-output` | `adjudicated` | `visible` | `/Users/justinjia/Desktop/personal project/vc-analyst/reports/output_review_decisions.json` |
| `industrial-vision-market-model-output` | `adjudicated` | `visible` | `/Users/justinjia/Desktop/personal project/vc-analyst/reports/output_review_decisions.json` |

### glass-substrate-public-research-output

- readiness: `adjudicated`
- blocking reason: Reviewer decision is valid; answer key is revealed for this case.
- answer key visible: `true`
- blind pack: `/Users/justinjia/Desktop/personal project/vc-analyst/reports/output_blind_review_pack.json`
- decisions: `/Users/justinjia/Desktop/personal project/vc-analyst/reports/output_review_decisions.json`

#### Commands

- prepare_review_kit: `python3 scripts/yao.py output-review-kit`
- write_template: `python3 scripts/adjudicate_output_review.py --write-template`
- import_decisions: `python3 scripts/yao.py output-review-import --input <reviewer-decisions.json> --blind-review-attested --run-adjudication`
- adjudicate: `python3 scripts/yao.py output-review`
- refresh_review_studio: `python3 scripts/yao.py review-studio .`

#### Required Fields

- winner_variant: A or B after reading only the blind review pack.
- confidence: Optional number from 0 to 1.
- reason: Required rationale; do not reveal baseline or with-skill labels before adjudication.
- reviewer: Human reviewer name or review group at the decision-file top level.
- reviewed_at: Review date or timestamp at the decision-file top level.
- reviewer_attestation.blind_review_completed_before_answer_key: True only after the reviewer has completed choices before opening the answer key.
- reviewer_attestation.answer_key_not_opened_before_decisions: True only when the answer key was not opened before decisions were recorded.

#### Privacy Contract

- Do not paste raw private user data into the decision reason.
- Do not open the answer key before reviewer choices are recorded.
- Leave winner_variant blank when the reviewer is not ready to decide.

### industrial-vision-market-model-output

- readiness: `adjudicated`
- blocking reason: Reviewer decision is valid; answer key is revealed for this case.
- answer key visible: `true`
- blind pack: `/Users/justinjia/Desktop/personal project/vc-analyst/reports/output_blind_review_pack.json`
- decisions: `/Users/justinjia/Desktop/personal project/vc-analyst/reports/output_review_decisions.json`

#### Commands

- prepare_review_kit: `python3 scripts/yao.py output-review-kit`
- write_template: `python3 scripts/adjudicate_output_review.py --write-template`
- import_decisions: `python3 scripts/yao.py output-review-import --input <reviewer-decisions.json> --blind-review-attested --run-adjudication`
- adjudicate: `python3 scripts/yao.py output-review`
- refresh_review_studio: `python3 scripts/yao.py review-studio .`

#### Required Fields

- winner_variant: A or B after reading only the blind review pack.
- confidence: Optional number from 0 to 1.
- reason: Required rationale; do not reveal baseline or with-skill labels before adjudication.
- reviewer: Human reviewer name or review group at the decision-file top level.
- reviewed_at: Review date or timestamp at the decision-file top level.
- reviewer_attestation.blind_review_completed_before_answer_key: True only after the reviewer has completed choices before opening the answer key.
- reviewer_attestation.answer_key_not_opened_before_decisions: True only when the answer key was not opened before decisions were recorded.

#### Privacy Contract

- Do not paste raw private user data into the decision reason.
- Do not open the answer key before reviewer choices are recorded.
- Leave winner_variant blank when the reviewer is not ready to decide.

## Next Fixes

- Keep the blind review pack separate from the answer key until decisions are recorded.
- Treat disagreement cases as prompts for rubric tuning or output improvement.
- Add model-executed holdout runs after this human adjudication harness is stable.
