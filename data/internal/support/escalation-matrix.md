# Nexlify Corp — Support Escalation Matrix

**Document Version:** 3.2
**Effective Date:** February 1, 2026
**Owner:** Customer Success Operations
**Classification:** INTERNAL — LEVEL 2 CONFIDENTIAL
**Review Cycle:** Quarterly

---

## Document Control

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | Jun 15, 2025 | Maria Santos | Initial release |
| 2.0 | Aug 22, 2025 | Maria Santos | Added Enterprise tier |
| 2.5 | Oct 10, 2025 | Maria Santos | Updated PagerDuty integration |
| 3.0 | Nov 20, 2025 | Maria Santos | Post-breach protocol updates |
| 3.1 | Dec 15, 2025 | Maria Santos | Added Sentinel escalation |
| 3.2 | Feb 1, 2026 | Maria Santos | Q1 2026 update |

---

## 1. Overview

This document defines Nexlify Corp's support escalation framework, establishing clear protocols for tier-based support, severity classification, response time SLAs, and escalation pathways.

**Escalation Objectives:**
- Ensure timely resolution of customer issues
- Provide clear guidance for support personnel
- Define accountability at each escalation level
- Minimize customer effort during issue resolution

**Key Definitions:**
- **L1 (Tier 1):** Initial response and basic troubleshooting
- **L2 (Tier 2):** Technical specialists and advanced troubleshooting
- **L3 (Tier 3):** Engineering and product development experts
- **SLA:** Service Level Agreement — committed response and resolution times

---

## 2. Support Tier Architecture

### 2.1 Tier Definitions

| Tier | Name | Role | Team Size | Primary Responsibility |
|------|------|------|-----------|----------------------|
| L1 | First Response | Customer Support | 12 FTE | Initial triage, common issues, documentation |
| L2 | Technical Support | Solutions Engineers | 8 FTE | Advanced troubleshooting, configuration |
| L3 | Engineering | Product Engineering | Varies | Root cause resolution, bug fixes |

### 2.2 Shift Coverage

| Support Channel | Hours | On-Call Rotation |
|-----------------|-------|------------------|
| Email/Chat | 24/5 (Mon-Fri PST) | Yes (after hours) |
| Phone (Pro/Enterprise) | 24/5 (Mon-Fri PST) | Yes (24/7 for Enterprise) |
| Slack (Enterprise) | 24/7 | Yes |
| PagerDuty | 24/7 | Yes |

---

## 3. Severity Classification

### 3.1 Severity Levels

| Severity | Definition | Business Impact | Examples |
|----------|------------|----------------|----------|
| **SEV-1** | Critical | Complete service outage or major business impact | Platform down, all inference failing, security breach |
| **SEV-2** | High | Major feature unavailable or significant degradation | Single endpoint down, >50% error rate |
| **SEV-3** | Medium | Minor feature impaired, workaround available | Dashboard slow, intermittent errors |
| **SEV-4** | Low | Cosmetic issue, minimal impact | UI typo, non-critical documentation error |

### 3.2 Severity Assessment Guidelines

**SEV-1 Criteria (Any one of):**
- Platform completely unavailable (100% error rate)
- Security incident or data breach suspected
- Customer production environment down
- SLA violation imminent or occurring

**SEV-2 Criteria (Any one of):**
- Single critical endpoint failing
- Error rate >10% for >5 minutes
- Latency 5x above SLA for >10 minutes
- Data integrity concern
- Customer-facing revenue impact

**SEV-3 Criteria (Any one of):**
- Non-critical feature unavailable
- Performance degradation without business impact
- Configuration issues with workaround available
- API returning incorrect but non-critical data

**SEV-4 Criteria (All of):**
- No functional impact
- Cosmetic or documentation issues
- Feature requests
- How-to questions

---

## 4. SLA Commitments by Tier

### 4.1 Response Time SLAs

| Customer Tier | SEV-1 | SEV-2 | SEV-3 | SEV-4 |
|--------------|-------|-------|-------|-------|
| Free | N/A | N/A | N/A | N/A |
| Starter | N/A | < 4 hours | < 24 hours | < 72 hours |
| Platform | < 8 hours | < 4 hours | < 8 hours | < 48 hours |
| Pro | < 1 hour | < 1 hour | < 4 hours | < 24 hours |
| Enterprise | < 15 min | < 30 min | < 2 hours | < 8 hours |

*Response time = Time from ticket creation to first meaningful response*

### 4.2 Resolution Time Targets

| Customer Tier | SEV-1 | SEV-2 | SEV-3 | SEV-4 |
|--------------|-------|-------|-------|-------|
| Free | N/A | N/A | < 5 days | < 10 days |
| Starter | N/A | < 24 hours | < 3 days | < 7 days |
| Platform | < 4 hours | < 8 hours | < 48 hours | < 5 days |
| Pro | < 2 hours | < 4 hours | < 24 hours | < 3 days |
| Enterprise | < 30 min | < 2 hours | < 8 hours | < 24 hours |

*Resolution time = Time from ticket creation to issue resolved or workaround provided*

### 4.3 Uptime SLAs

| Customer Tier | Monthly Uptime | Max Downtime/Month |
|--------------|---------------|-------------------|
| Free | 99.0% | 7h 12m |
| Starter | 99.5% | 3h 36m |
| Platform | 99.9% | 43.8 min |
| Pro | 99.95% | 21.6 min |
| Enterprise | 99.99% | 4.3 min |

---

## 5. Escalation Pathways

### 5.1 Standard Escalation Flow

```
Customer
    │
    ▼
[L1: Tier 1 Support]
    │  (First Response)
    │  - Validate issue
    │  - Gather information
    │  - Apply known solutions
    │
    ├─[Resolved]──────────────────────────────► Close
    │
    ▼ (if unresolved after initial response)
[L2: Tier 2 Technical Support]
    │  (Advanced Troubleshooting)
    │  - Deep dive analysis
    │  - Configuration review
    │  - Escalate to vendor if needed
    │
    ├─[Resolved]──────────────────────────────► Close
    │
    ▼ (if unresolved, SEV-1/SEV-2, or L2 blocked)
[L3: Engineering]
    │  (Root Cause Resolution)
    │  - Code-level investigation
    │  - Hotfix deployment
    │  - Product change required
    │
    ├─[Resolved]──────────────────────────────► Close
    │
    ▼ (if customer requires executive engagement)
[Executive Escalation]
    │  (Customer Success VP)
    │  - Strategic communication
    │  - Resource authorization
    │  - Business impact mitigation
    │
    └────────────────────────────────────────► Resolve & Close
```

### 5.2 Escalation Triggers

**L1 → L2 Escalation (Automatic):**
- Issue not resolved within 2x initial response SLA
- Customer explicitly requests technical lead
- Issue requires configuration changes beyond L1 scope
- SEV-1 or SEV-2 classification assigned
- Multiple L1 attempts have not identified root cause

**L2 → L3 Escalation (Automatic):**
- Issue not resolved within resolution target time
- Issue requires code change or hotfix
- Bug identified in production system
- SEV-1 with no workaround available
- Customer is Enterprise with critical business impact

**L2 → L3 Escalation (Discretionary):**
- Issue requires >8 hours of L2 engineer time
- Issue has potential to affect multiple customers
- Customer requests L3 involvement (Enterprise only)

### 5.3 Escalation Contacts

**Slack Channels:**

| Channel | Purpose | Monitoring |
|---------|---------|------------|
| #support-tier-1 | L1 ticket queue | 24/5 |
| #support-tier-2 | L2 ticket queue | 24/5 |
| #support-tier-3 | L3/Engineering | 24/7 |
| #support-escalations | Urgent escalations | 24/7 |
| #support-enterprise | Enterprise urgent | 24/7 |
| #security-alerts | Security incidents | 24/7 |

**PagerDuty Escalation Paths:**

| Severity | Primary | Secondary | Tertiary |
|----------|---------|-----------|----------|
| SEV-1 (Enterprise) | On-call L3 Engineer | L2 Manager | VP Engineering |
| SEV-1 (Pro) | On-call L2 Engineer | L2 Manager | L3 On-call |
| SEV-2 | L2 Engineer | L2 Manager | — |

---

## 6. Response Protocols by Severity

### 6.1 SEV-1 Response Protocol

**When:** Critical service outage or major business impact

**L1 Actions (< 15 minutes):**
1. Acknowledge ticket immediately
2. Post in #support-escalations: "SEV-1: [Customer] - [Brief Description]"
3. Check status.nexlify.com for ongoing incidents
4. Verify customer account status and tier
5. Create bridge link for real-time communication
6. Set customer expectations: "Investigating, update in 30 minutes"

**L2 Actions (< 1 hour):**
1. Join bridge call with L1 and customer
2. Gather technical details:
   - API error logs
   - Request traces
   - Rate limit status
   - Recent configuration changes
3. Check internal monitoring dashboards
4. Determine if issue is platform-wide or customer-specific
5. If platform-wide, activate PagerDuty for L3

**L3 Actions (As needed):**
1. Investigate root cause
2. Deploy emergency fix if available
3. Provide status updates every 30 minutes
4. Document incident in post-mortem

**Communication Template:**
> "We are actively investigating the issue affecting your [service]. Our engineering team is engaged. We will provide updates every [30 min] until resolved. Next update at [time]."

---

### 6.2 SEV-2 Response Protocol

**When:** Major feature unavailable or significant degradation

**L1 Actions (< 4 hours):**
1. Acknowledge within SLA window
2. Gather initial information:
   - Endpoint(s) affected
   - Error messages
   - Time since issue started
   - Recent changes (deployments, config, etc.)
3. Apply known solutions from knowledge base
4. If unresolved after 2 attempts, escalate to L2

**L2 Actions (< 4 hours):**
1. Review customer-specific configuration
2. Analyze API logs and metrics
3. Check for rate limit issues
4. Verify model deployment status
5. If issue requires L3:
   - Document findings
   - Escalate with specific hypothesis
   - Continue L2 investigation in parallel

**L3 Actions (As needed):**
1. Code-level debugging
2. Database/log inspection
3. Deploy patch or workaround
4. Test fix before customer deployment

---

### 6.3 SEV-3 Response Protocol

**When:** Minor feature impaired with workaround available

**L1 Actions:**
1. Acknowledge within SLA window
2. Provide documented workaround
3. If workaround not acceptable, escalate to L2
4. Schedule permanent fix if identified

**L2 Actions:**
1. Investigate underlying cause
2. Document permanent fix path
3. Coordinate with engineering for release

---

### 6.4 SEV-4 Response Protocol

**When:** Cosmetic issue or non-critical request

**L1 Actions:**
1. Acknowledge within SLA window
2. Address directly if within L1 scope
3. For feature requests, route to Product team via Salesforce case type "Feature Request"
4. For documentation issues, route to Technical Writing team

---

## 7. Special Escalation Scenarios

### 7.1 Security Incident Escalation

**Trigger:** Customer reports or suspects security breach

**Immediate Actions:**
1. Do NOT attempt to investigate compromised systems
2. Escalate immediately to VP Security: Jennifer Wu (PagerDuty: SECURITY-ONCALL)
3. Post in #security-alerts with customer identifier
4. Document all actions taken
5. Do NOT communicate with customer until cleared by Security team

**Escalation Path:**
```
L1 → L2 Security Lead → CISO → VP Engineering → CEO (if severe)
```

**Customer Communication (Security Team Only):**
- Initial acknowledgment within 1 hour
- Detailed status within 4 hours
- FBI/CISA notification if nation-state suspected (per November 2025 incident protocol)

---

### 7.2 SLA Violation Imminent

**Trigger:** Response or resolution SLA about to be breached

**Actions:**
1. L1/L2 lead reviews queue every 2 hours
2. If SLA at risk:
   - Notify next escalation level
   - Consider emergency resource allocation
   - Customer Success Manager notified for Enterprise
3. Document reason for breach in ticket
4. Process SLA credit automatically for Enterprise customers

---

### 7.3 Customer Threatening Churn

**Trigger:** Customer indicates intent to cancel or escalate to executive

**Actions:**
1. Do NOT promise anything beyond your authority
2. Immediately notify:
   - Customer Success Manager
   - Account Executive
3. For Enterprise:
   - VP Customer Success paged via Slack
   - Consider executive-to-executive call
4. Document in Salesforce with "Churn Risk" tag

---

### 7.4 Media Inquiry

**Trigger:** Customer or journalist contacts support about public issue

**Actions:**
1. Do NOT provide any information
2. Immediately transfer to Communications:
   - Slack: #comms-team
   - Email: press@nexlify.com
3. Document the inquiry in Salesforce
4. Do not confirm or deny any information

---

### 7.5 Legal/Hearing Aid Request

**Trigger:** Subpoena, litigation hold, or regulatory inquiry

**Actions:**
1. Do NOT respond directly
2. Immediately transfer to Legal:
   - Slack: #legal-team
   - Email: legal@nexlify.com
3. Document request details
4. Do not acknowledge receipt without Legal guidance

---

## 8. Escalation Metrics

### 8.1 Key Performance Indicators

| Metric | Target | Alert Threshold |
|--------|--------|----------------|
| Average First Response Time | < 2 hours | > 4 hours |
| SEV-1 Average Resolution | < 2 hours | > 4 hours |
| SEV-2 Average Resolution | < 8 hours | > 24 hours |
| Escalation Accuracy (L1→L2) | > 80% | < 70% |
| Customer Satisfaction (CSAT) | > 4.5/5 | < 4.0/5 |
| Escalation to L3 Rate | < 10% | > 15% |

### 8.2 Escalation Review Cadence

| Review | Frequency | Attendees |
|--------|-----------|-----------|
| Daily Queue Review | Daily (9 AM PST) | L1 Lead, L2 Lead |
| Weekly Escalation Report | Weekly (Monday) | Support Management |
| Monthly Deep Dive | Monthly | VP Customer Success, Support Leads |
| Quarterly Post-Mortem | Quarterly | All Support Tiers |

---

## 9. Escalation Authority Matrix

### 9.1 L1 (Tier 1) Authority

| Action | Authority Level |
|--------|----------------|
| Refund under $50 | Approved |
| Extend trial by 7 days | Approved |
| Apply standard discount (up to 10%) | Approved |
| Reset API key | Approved |
| Provide documented workaround | Approved |
| Refund over $50 | Escalate to L2 |
| Subscription downgrade | Escalate to L2 |
| Custom pricing | Escalate to Sales |
| Legal/Emergency requests | Escalate to L2 Manager |

### 9.2 L2 (Tier 2) Authority

| Action | Authority Level |
|--------|----------------|
| Refund up to $500 | Approved |
| Extend trial by 30 days | Approved |
| Apply standard discount (up to 20%) | Approved |
| Credits for SLA violations | Approved |
| Temporary API limit increase | Approved (max 48 hours) |
| Custom integration assistance | Approved |
| Refund over $500 | Escalate to Finance |
| Permanent rate limit changes | Escalate to Product |
| Custom SLA terms | Escalate to Sales |

### 9.3 L3 (Tier 3) Authority

| Action | Authority Level |
|--------|----------------|
| Deploy emergency hotfix | Approved |
| Modify production configuration | Approved |
| Grant temporary elevated access | Approved (with documentation) |
| Authorize customer data access | Escalate to Security |
| Production system changes | Approved (with change management) |

---

## 10. Escalation Documentation Requirements

### 10.1 Required Ticket Fields

All escalations must include:

| Field | Description |
|-------|-------------|
| Customer ID | Account identifier |
| Severity | SEV-1 through SEV-4 |
| Business Impact | Description of customer impact |
| Symptoms | Technical details and error messages |
| Actions Taken | What L1/L2 has already attempted |
| Customer Expectations | What resolution looks like to customer |
| Time Sensitivity | Any deadlines or SLA concerns |

### 10.2 Escalation Email Template

**To:** escalation@nexlify.com
**Subject:** ESCALATION [SEV-X]: [Customer Name] - [Brief Issue]

```
Severity: SEV-[X]
Customer: [Name] ([Account ID])
Tier: [Starter/Platform/Pro/Enterprise]

Issue Summary:
[Brief description of the issue]

Business Impact:
[How this affects customer operations]

Technical Details:
- Error messages: [list]
- Affected endpoints: [list]
- Time started: [timestamp]
- Rate limit status: [if applicable]

Actions Taken:
1. [What L1/L2 tried #1]
2. [What L1/L2 tried #2]

Customer Expectation:
[What resolution they're expecting]

Time Sensitivity:
[Any deadlines or SLA concerns]

Contact:
[Primary customer contact name]
[Customer contact Slack/phone]
```

---

## 11. Escalation Contacts Directory

### 11.1 Internal Escalation Contacts

| Role | Name | Slack | PagerDuty |
|------|------|-------|-----------|
| L1 Support Lead | Maria Santos | @maria.santos | SUPPORT-L1-LEAD |
| L2 Support Lead | James Chen | @james.chen | SUPPORT-L2-LEAD |
| L3 On-Call Engineer | Rotating | @oncall-engineering | ENGINEERING-ONCALL |
| VP Engineering | Robert Kim | @robert.kim | ENG-VP |
| VP Customer Success | Patricia Wong | @patricia.wong | CS-VP |
| VP Security | Jennifer Wu | @jennifer.wu | SECURITY-ONCALL |
| VP Sales | James Rodriguez | @james.rodriguez | SALES-VP |

### 11.2 On-Call Schedules

| Rotation | Coverage | Contact Method |
|----------|---------|----------------|
| L1 Weekday | Mon-Fri 6AM-8PM PST | Slack #support-tier-1 |
| L1 Weekend | Sat-Sun limited | Email (48hr response) |
| L2 On-Call | 24/7 rotation | PagerDuty |
| L3 On-Call | 24/7 rotation | PagerDuty |
| Security On-Call | 24/7 rotation | PagerDuty |

---

## 12. Post-Escalation Procedures

### 12.1 Escalation Closure

**L1 Closure Requirements:**
- Customer confirmed resolution
- Documentation complete
- CSAT survey sent (if applicable)

**L2 Closure Requirements:**
- All L1 requirements met
- Technical root cause documented
- Knowledge base article created or updated
- Handoff to L1 if customer follow-up needed

**L3 Closure Requirements:**
- All L2 requirements met
- Incident report filed (if SEV-1)
- Bug ticket created (if applicable)
- Permanent fix scheduled (if needed)

### 12.2 Escalation Post-Mortem

**SEV-1 incidents require post-mortem within 5 business days:**

| Section | Content |
|---------|---------|
| Summary | What happened, impact, duration |
| Timeline | Minute-by-minute breakdown |
| Root Cause | Technical root cause |
| Contributing Factors | What allowed it to happen |
| Resolution | How it was fixed |
| Action Items | Prevention measures |
| Lessons Learned | What to do differently |

**Post-Mortem Distribution:**
- #support-escalations (internal)
- Customer-facing summary (approved by CS VP)

---

## Appendix A: Escalation Quick Reference Card

**Emergency Contacts (24/7):**

| Scenario | Contact | Method |
|----------|---------|--------|
| SEV-1 (Enterprise) | PagerDuty: ENGINEERING-ONCALL | Phone/SMS |
| Security Incident | PagerDuty: SECURITY-ONCALL | Phone/SMS |
| Media Inquiry | #comms-team | Slack |
| Legal Request | legal@nexlify.com | Email |
| Executive Escalation | VP Customer Success | Slack DM |

**Slack Channels:**
- #support-tier-1 — L1 queue
- #support-tier-2 — L2 queue
- #support-tier-3 — L3 queue
- #support-escalations — Urgent issues
- #support-enterprise — Enterprise issues

**Salesforce Case Types:**
- Technical Issue
- Billing Inquiry
- SLA Credit Request
- Security - Confidential
- Feature Request

---

*Document Owner: Customer Success Operations*
*Last Updated: February 1, 2026*
*Next Review: May 1, 2026*
*Classification: INTERNAL — LEVEL 2 CONFIDENTIAL*
