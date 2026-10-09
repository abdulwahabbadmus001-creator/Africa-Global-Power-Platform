# AGP Launch Validation Checklist

Use this checklist on the live production URL before sharing AGP with mentors or publishing the launch announcement.

## Public / Guest
- [ ] Home loads on desktop and mobile.
- [ ] Research lists only published research.
- [ ] Publication detail opens and manuscript download works where a public file exists.
- [ ] Researchers directory shows only Researcher / Contributor accounts.
- [ ] Reader and Editorial accounts do not appear in Researchers.
- [ ] Africa, Opportunities, Data Lab, Policy Tracker and Trust Centre load.
- [ ] Opportunity filters work: All, Fellowship, Grant, Collaboration, Call for Papers, Internship, Scholarship, Conference, Research.
- [ ] Closed opportunities show as closed.
- [ ] About, Privacy, Terms, Editorial Policy, Research Integrity and Contact load.
- [ ] Help & Guide loads and the AGP User Guide PDF downloads.

## Reader
- [ ] Reader registration is distinct from Researcher registration.
- [ ] Registration OTP and login OTP work.
- [ ] Reader lands on Reader Workspace.
- [ ] Save / unsave research works.
- [ ] Follow / unfollow researcher works.
- [ ] Notifications load.
- [ ] Messaging an opted-in researcher works.
- [ ] Account Settings works.
- [ ] Reader cannot access New Publication, Edit Public Profile, Editorial or System Administration.

## Researcher / Contributor
- [ ] Researcher registration collects professional fields.
- [ ] Registration OTP and login OTP work.
- [ ] Researcher lands on Researcher Portal.
- [ ] Edit Public Profile works and public profile renders.
- [ ] Featured Works works.
- [ ] New Publication opens.
- [ ] Draft and submission / Trust Vault workflow work.
- [ ] Submitted work locks until revision is requested.
- [ ] Messages, Research Rooms, Analytics and Amplification work.
- [ ] Researcher cannot access Editorial or System Administration.

## Editorial
- [ ] Public login rejects Editorial credentials.
- [ ] Editorial Access + TOTP MFA works.
- [ ] Reviewer / Editor / Senior Editor / Managing Editor lands on Editorial Review Desk.
- [ ] Editorial account does not see Researcher Portal.
- [ ] Editorial cannot access New Publication or Edit Public Profile.
- [ ] Submission queue loads.
- [ ] Claim review works.
- [ ] Confidentiality and conflict gates work.
- [ ] Recusal works.
- [ ] Secure manuscript access works after trust gates.
- [ ] Revision, source check, approval, scheduling and publication transitions work.
- [ ] Editorial activity/history is visible.
- [ ] Editorial account is absent from public Researchers.

## Super Admin
- [ ] Super Admin uses Editorial Access + MFA.
- [ ] Super Admin lands on the Control Centre.
- [ ] Overview metrics and Users load.
- [ ] Role changes and account activation controls work.
- [ ] Self-disable protection works.
- [ ] Opportunity Edit / Publish / Unpublish / Close / Reopen / Delete works.
- [ ] Policy Edit / Publish / Unpublish / Delete works.
- [ ] Data Lab Edit / Publish / Unpublish / Delete works.
- [ ] Editorial Review Desk, Content Studio and Amplification Desk are accessible from Tools.
- [ ] Super Admin does not see the Researcher author workspace as the dashboard.

## Responsive
Test approximately 320, 360, 375, 390, 430, 768, 1024 and 1440 px.
- [ ] Mobile menu works.
- [ ] No horizontal overflow.
- [ ] Forms and tables remain usable.
- [ ] Buttons are not clipped.
- [ ] Footer is readable.

## Production
- [ ] Netlify production deploy references the latest Git commit.
- [ ] Render production deploy references the latest Git commit.
- [ ] Render /health is healthy.
- [ ] Frontend API proxy works.
- [ ] Brevo OTP email arrives.
- [ ] Private manuscript storage remains private.
- [ ] No secrets are committed.
- [ ] Production API docs remain disabled if intended.

## Mentor Review
- [ ] Send the live production URL to the professional mentor for usability, product clarity and professional positioning.
- [ ] Send it to the academic mentor for research credibility, editorial policy, integrity and researcher workflow.
- [ ] Record feedback for post-launch improvements rather than changing the launch build impulsively.

## Launch-Freeze Hardening
- [ ] Researcher can delete an unsubmitted private draft from Dashboard and Publication Workspace.
- [ ] Sealed/previously submitted Trust Vault history cannot be deleted as an ordinary draft.
- [ ] Failed manuscript upload cleanup does not leave a new empty draft when cleanup succeeds.
- [ ] Upload-only research cannot be sealed for Editorial without a 40+ character public abstract.
- [ ] Approved research can be returned to Revision Requested.
- [ ] Editorial transition failures display their backend reason.
- [ ] Oversized manuscript reads are bounded.
- [ ] Invalid Supabase/S3 endpoints return controlled storage errors.
- [ ] Repeated public password failures are throttled.
- [ ] Cross-site state-changing production requests are blocked.
- [ ] Authenticated API responses use no-store caching.
- [ ] Netlify serves CSP/HSTS/framing/MIME/referrer/permissions protections.
- [ ] `npm audit --omit=dev --audit-level=high` passes.
- [ ] `pip check` passes.
- [ ] No real `.env` file is tracked by Git.
