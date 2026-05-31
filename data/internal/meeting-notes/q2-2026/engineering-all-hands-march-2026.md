# NEXLIFY CORP — ENGINEERING ALL-HANDS MARCH 2026

## Engineering Organization All-Hands Meeting

---

| Field | Value |
|-------|-------|
| **Document Title** | Engineering All-Hands — March 2026 |
| **Document ID** | NEAH-Mar-2026-001 |
| **Version** | 1.0 |
| **Date** | March 18, 2026 |
| **Owner** | David Park, VP Engineering |
| **Classification** | INTERNAL — ALL ENGINEERING |
| **Distribution** | All Engineering, Product, Quality |

---

## 1. Meeting Overview

**Date:** March 18, 2026  
**Time:** 10:00 AM - 2:00 PM CT  
**Location:** Austin HQ, Building A — All Hands Center + Virtual  
**Attendance:** 2,180 engineers (1,820 in-person, 360 virtual)

**Hosts:**
- David Park (VP Engineering) — Chair
- Dr. Amanda Foster (CTO)
- Sarah Chen (VP Product)
- Robert Kim (CISO)

**Agenda:**
| Time | Topic | Presenter |
|------|-------|----------|
| 10:00 | Opening & Announcements | David Park |
| 10:30 | NEXL-X4 Status & Tape-out Readiness | Team Leads |
| 11:15 | Break | — |
| 11:30 | Security Transformation Update | Robert Kim |
| 12:15 | Lunch | — |
| 1:00 | Q&A Panel | Leadership |

---

## 2. Opening Remarks — David Park, VP Engineering

### 2.1 Company State of the Union

David opened with a transparent update on the company's situation:

> "Six months ago, we faced a significant cybersecurity incident. Today, I want to address it directly and talk about where we stand. We contained the breach, notified customers, and are implementing the most comprehensive security transformation in our company's history. Most importantly: we are still building great products."

**Key Points:**
- Q1 revenue tracking to plan ($1.38B target)
- NEXL-X4 development on track for June tape-out
- Attrition reduced from 16% to 13% — approaching target
- Security transformation in progress — 65% complete

### 2.2 Engineering Priorities for 2026

| Priority | Description | Target |
|----------|-------------|--------|
| NEXL-X4 | Next-gen inference accelerator | June tape-out |
| NEXL-SW 4.0 | Unified software platform | Q3 release |
| Security Hardening | Zero Trust, design air-gapping | Q2 completion |
| NEXL-A3 | Training accelerator | Q4 tape-out |
| Automotive | ASIL-D certification | BMW Q2 approval |

### 2.3 Engineering Metrics

| Metric | Q1 2026 | Q4 2025 | Target | Trend |
|--------|---------|---------|--------|-------|
| Headcount | 2,180 | 2,140 | 2,300 | ↑ |
| Attrition | 13% | 16% | 10% | ↓ |
| Productivity Index | 94 | 89 | 100 | ↑ |
| On-time Delivery | 78% | 72% | 90% | ↑ |
| Quality (DPM) | 920 | 980 | 800 | ↑ |

---

## 3. NEXL-X4 Status — Dr. Marcus Lee, Principal AI Architect

### 3.1 Project Status

**Tape-out Date:** June 15, 2026 (89 days away)

| Milestone | Original | Current | Status |
|-----------|----------|---------|--------|
| RTL Complete | Mar 15 | Mar 18 | 🟡 3 days late |
| Timing Closure | Apr 30 | Apr 28 | ✅ 2 days early |
| Tape-out | Jun 15 | Jun 15 | ✅ ON TRACK |

**Current Progress:**
- All major blocks integrated
- DFT coverage 98.5% (target: 98%)
- Power integrity validated
- Signal integrity confirmed
- Physical verification complete

### 3.2 Technical Highlights

**Performance:**
- Inference: 4,350 TOPS (exceeds 4,200 target by 3.5%)
- Memory Bandwidth: 5.7 TB/s (exceeds 5.5 target by 3.6%)
- HBM4: 192 GB (on target)
- TDP: 640W (under 650W target)

**Key Innovations:**
- 3D V-Cache architecture (stacked L3)
- Transformer Engine v2 optimized for LLMs
- Unified Memory Architecture (multi-chip config)
- First HBM4 deployment in industry

### 3.3 What's At Stake

Marcus presented the competitive context:

> "NEXL-X4 is our ticket to reclaiming inference leadership. It delivers 90% of NVIDIA B300 performance at 70% of the price. Tape-out in June, first silicon in September, production in December — we're on track."

**Customer Interest:**
- Amazon evaluating for 2027 deployment
- Google in discussions for TPU alternative
- Microsoft Azure partnership expanding

---

## 4. Security Transformation — Robert Kim, CISO

### 4.1 What Happened (Transparent Update)

Robert gave a detailed, transparent account of the November breach:

**The Facts:**
- October 28, 2025: Breach discovered
- Attack vector: Phishing + service account vulnerability
- Duration: 94 days undetected
- Impact: 2.8TB data, NEXL-X4 design files accessed
- Attribution: APT41 (Chinese state-sponsored) — 90% confidence

**What We Did:**
- Contained within 72 hours
- All passwords reset
- FBI and CISA engaged
- Customer notifications completed
- 47 customers notified

### 4.2 Security Improvements

**Completed:**
- MFA enforced on all 5,200 accounts
- EDR deployed to 1,247 endpoints
- Privileged Access Workstations (340 units)
- Password rotation for all employees
- 47 new detection rules in SIEM
- Micro-segmentation 92% complete

**In Progress:**
- Zero Trust Architecture (65% complete)
- Design Network Air-gapping (80% complete)
- Security Operations Center enhancement
- Penetration testing (quarterly)

### 4.3 What This Means for Engineering

Robert addressed the engineering team's concerns directly:

**Impact on Engineering:**
- USB devices restricted on design network
- Additional authentication for sensitive repos
- Enhanced logging on all development systems
- Security training mandatory (annual)

**What's NOT Changing:**
- Access to design tools and systems
- Development workflows (with added security)
- Collaboration tools and processes

**What IS Changing:**
- Privileged Access Workstations required for sensitive work
- Enhanced access logging (for everyone's protection)
- Design repository access requires additional authentication

> "These changes protect you and protect the company. I know they're inconvenient, but they're necessary. We learn from what happened and we move forward stronger."

### 4.4 Security Best Practices Reminder

| Practice | Status | Requirement |
|----------|--------|-------------|
| Password复杂度 | Required | 14+ chars, quarterly rotation |
| MFA | Required | All systems, no exceptions |
| Phishing Reporting | Required | Report to security@nexlify.com |
| USB Devices | Restricted | No unauthorized USB on design network |
| Laptop Encryption | Required | FileVault/BitLocker enabled |

---

## 5. NEXL-SW 4.0 Update — Dr. Amanda Foster, CTO

### 5.1 Software Vision

Amanda presented the unified software platform vision:

> "Our software is the competitive moat — or it should be. NEXL-SW 4.0 will be the platform that makes NEXL-X4 the obvious choice. We're investing $40M in CUDA compatibility to ensure customers can migrate without rewriting code."

### 5.2 Component Status

| Component | Status | Target |
|-----------|--------|--------|
| NEXL-SDK (Core API) | 85% | Q3 2026 |
| NEXL-Compiler | 70% | Q3 2026 |
| NEXL-Runtime | 75% | Q3 2026 |
| NEXL-Profiler | 60% | Q4 2026 |
| PyTorch 2.5 Support | 90% | Q3 2026 |
| TensorFlow 2.18 Support | 80% | Q4 2026 |

### 5.3 CUDA Compatibility

**Decision:** $40M additional investment for CUDA compatibility layer

**Why:**
- Enterprise customers demand CUDA compatibility
- Top request in customer surveys
- Table stakes for competition
- Reduces customer migration cost

**Timeline:**
- Q3 2026: Basic compatibility (60% coverage)
- Q4 2026: Full compatibility (85% coverage)
- 2027: Parity with CUDA features

---

## 6. Break & Networking (11:15 AM - 11:30 AM)

---

## 7. Employee Q&A Session (Panel)

### 7.1 Panel Members

- David Park (VP Engineering)
- Dr. Amanda Foster (CTO)
- Sarah Chen (VP Product)
- Robert Kim (CISO)
- Lisa Thompson (VP HR)

### 7.2 Top Questions

**Q: "The breach exposed NEXL-X4 design. Does this mean competitors have our technology?"**

Robert Kim: "Our forensic analysis indicates the attackers accessed design files — approximately 850 GB. We assume this information could benefit competitors. That's why we're accelerating NEXL-X4 production to December 2026 and adding security hardening to NEXL-A3. The competitive impact is estimated at 3-6 months of advantage loss. We're taking steps to mitigate."

**Q: "Is our work on NEXL-A3 compromised?"**

Dr. Amanda Foster: "Architecture documents for NEXL-A3 were accessed (~120 GB). We've accelerated A3 development and added additional security features. We expect 3-6 month competitive impact. The team is motivated to deliver an even better product."

**Q: "Will the security changes slow down our development?"**

Robert Kim: "Some processes will take longer — additional authentication adds 30-60 seconds. But the alternative is unacceptable. We need to protect our work. Security is everyone's responsibility."

**Q: "Why did we lose Dr. Wu and how are we preventing more departures?"**

Lisa Thompson: "Dr. Wu left for Google in November — compensation gap was a factor. We've implemented retention equity ($2.5M for critical employees), salary adjustments for 200 engineers (+12%), and new career ladders (Principal/Distinguished tracks). Attrition is down from 16% to 13% and approaching our 10% target."

**Q: "What's the timeline for returning to normal work?"**

David Park: "Security transformation is 65% complete. By end of Q2, we'll be at 90%. After that, we return to a new normal — more secure, with some additional steps. The goal is to make security invisible once we've built the foundation."

**Q: "What can we do to help?"**

Dr. Amanda Foster: "Stay vigilant. Report phishing. Follow security protocols. Help colleagues who are struggling. We're all in this together."

---

## 8. Closing Remarks — David Park

> "I'm proud of how this team has responded to adversity. Six months ago, we faced a breach that could have broken us. Instead, we contained it, learned from it, and kept building. NEXL-X4 is on track. Our security is transforming. Our products are getting better.

> I believe in this team. I believe in what we're building. And I believe the best is yet to come."

**Next All-Hands:** June 2026 (Post-Tape-out celebration)

---

## 9. Appendix: Resources

| Resource | Description | Access |
|----------|-------------|--------|
| Security Training | Annual mandatory | LMS |
| NEXL-X4 Specs | Detailed documentation | Engineering Portal |
| NEXL-SW 4.0 | SDK documentation | Developer Portal |
| HR Policies | Benefits, career | HR Intranet |
| Incident Response | Reporting procedures | Security Portal |

---

**Meeting Minutes Prepared by:**  
Tom Rodriguez, Engineering Operations

**Approved by:**  
David Park, VP Engineering

---

*NEAH-Mar-2026-001 v1.0*  
*March 18, 2026*