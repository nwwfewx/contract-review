# Standardized Investment Checklist

Use for `asset_mgmt:investment:standardized` (债券/股票/ETF 等标准化品种)。

## Scope
- Investment-side contract review only
- Focus on suitability, execution terms, and regulatory boundary alignment
- Do not reuse alternative-product due-diligence wording directly

## Mandatory Checks
1. Investor suitability and mandate match
2. Product scope and prohibited-asset boundary
3. Pricing/fees/spread disclosure completeness
4. Settlement and custody path clarity
5. Trigger/termination/default clauses and fallback mechanics
6. Related-party transaction disclosure and approval path
7. Information disclosure cadence and breach remedies
8. Dispute resolution, governing law, and evidence retention obligations

## Output Contract
- Main risk table follows the skill's fixed schema
- Each finding must include clause anchor and consequence
- Uncertain legal basis must be marked `【需人工复核】`

## Custody Agreement Overlay Rule
1. If standardized-product documents include standalone托管协议, stack `references/checklist_custody_agreement_2026.md`.
2. Do not weaken standardized-investment baseline checks when custody overlay is enabled.
