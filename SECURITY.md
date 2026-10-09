# Security Policy

AGP treats unpublished research, account credentials, Editorial access and Trust Vault records as sensitive.

## Reporting
Do not open a public GitHub issue for a suspected vulnerability. Use the AGP Contact page with **Security report** as the subject. Never include passwords, recovery codes, API keys or another person's private manuscript.

## Production boundaries
- Reader/Researcher sign-in uses password plus email OTP.
- Editorial/Super Admin uses dedicated Editorial Access plus TOTP MFA.
- Editorial identities are separated from public researcher identities.
- Private manuscripts are stored outside the public web root.
- Trust Vault access and editorial actions are audit-recorded.
- Only unsubmitted private drafts can be deleted through the ordinary author delete flow.
- Production state-changing browser requests use origin/site checks in addition to SameSite cookies.
- Secrets belong in deployment environment variables and must never be committed.

## Release gate
Run backend compile/pip checks, frontend production build, production dependency audit, verify Render/Netlify commit parity, `/health`, all four role boundaries, private manuscript upload/download and disabled production API docs.
