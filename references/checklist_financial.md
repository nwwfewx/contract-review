# Financial Mode Checklist

## Core Product Checks
1. Verify product type and apply strictest matching compliance template.
2. Validate term/rate/use-of-funds consistency across all versions.
3. Validate repayment source clarity and monitorability.

## Governance and Regulatory Checks
1. Verify shareholder/board approvals and special requirements from SASAC/finance authorities.
2. If listed entities are involved, check disclosure, related-party procedures, and fund-occupation risk.
3. If financial/quasi-financial entities are involved, check regulatory confirmations and asset segregation boundaries.

## Security and Enhancement Checks
1. Identify full security mix: guarantee, mortgage, pledge, off-balance support, other credit enhancement.
2. Verify legal enforceability and disposal path of collateral/pledge assets.

## Funds Use and Monitoring
1. Check fund path one-to-one mapping against agreed用途.
2. Treat归集、挪用、pooling without traceability as red flags.

## _AltsReview Linkage Rule
1. First load通用字段模板, then stack product-specific template.
2. For mixed attributes, follow stricter regulatory bucket.
3. Use interface mapping in `interface_altsreview.md`.

## Custody Agreement Overlay Rule
1. If contract text is托管协议/托管合同, stack `references/checklist_custody_agreement_2026.md`.
2. Keep this checklist as base; custody checklist only adds托管职责边界、账户/估值/监督/信披等专项核查。
