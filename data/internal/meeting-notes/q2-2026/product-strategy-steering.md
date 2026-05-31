# NEXLIFY CORP — PRODUCT STRATEGY STEERING MEETING

## Q2 2026 Product Strategy Session

---

| Field | Value |
|-------|-------|
| **Document Title** | Q2 2026 Product Strategy Steering — Minutes |
| **Document ID** | NPSM-Q2-2026-001 |
| **Version** | 1.0 |
| **Date** | May 6, 2026 |
| **Owner** | Sarah Chen, VP Product |
| **Classification** | CONFIDENTIAL — EXECUTIVE |
| **Distribution** | Executive Committee, Product Leadership |

---

## 1. Meeting Overview

**Date:** May 6, 2026  
**Time:** 9:00 AM - 4:00 PM CT  
**Location:** Austin HQ, Innovation Center  
**Attendees:**
- Sarah Chen (VP Product) — Chair
- Michael Richardson (CEO)
- Dr. Amanda Foster (CTO)
- David Park (VP Engineering)
- James Morrison (VP Sales)
- Dr. Marcus Lee (Principal AI Architect)
- Jennifer Wu (VP Security)

**Guests:**
- Dr. James Liu (External Advisor, former NVIDIA)

**Purpose:** Q2 product strategy alignment, NEXL-X4 launch preparation, competitive response to AMD MI350.

---

## 2. Opening — Sarah Chen, VP Product

Sarah opened with the quarterly strategic assessment:

> "Q2 2026 is a pivotal quarter. NEXL-X4 tape-out in June will determine our competitive position for 2027. AMD MI350 is shipping, NVIDIA B300 is coming, and customer requirements are evolving. We need to ensure our roadmap aligns with market realities."

**Agenda:**
1. Competitive landscape update (AMD MI350, NVIDIA B300)
2. NEXL-X4 launch readiness and positioning
3. Software ecosystem strategy (NEXL-SW 4.0)
4. NEXL-A3 training product alignment
5. Edge/automotive portfolio review
6. Q2 priorities and decisions

---

## 3. Competitive Landscape — Dr. James Liu, External Advisor

### 3.1 AMD MI350 Assessment

Dr. Liu presented an independent assessment of AMD's MI350:

**Strengths:**
- Strong inference performance (1,850 TOPS FP8)
- 192 GB HBM3 memory (superior to our 80 GB on X3)
- Aggressive pricing (15-20% below NVIDIA)
- ROCm 6.1 improving (still behind CUDA)

**Weaknesses:**
- Software ecosystem immaturity
- Enterprise trust still building
- Memory bandwidth advantage vs us but not vs NVIDIA B200

**Competitive Impact on Nexlify:**
- Win rate vs AMD: 58% (up from 52%)
- AMD taking share from NVIDIA in inference (12% → 14%)
- Not yet competitive in training

**Recommendation:** Don't engage in spec wars with AMD. Emphasize total value and support.

### 3.2 NVIDIA B300 Assessment

**Launch:** Q4 2025 (B200), Q2 2026 (B300 Ultra)

| Metric | NEXL-X3 | NVIDIA B200 | NVIDIA B300 |
|--------|---------|-------------|-------------|
| FP8 Inference | 2,400 TOPS | 4,000 TOPS | 6,000 TOPS |
| Memory BW | 2.8 TB/s | 8.0 TB/s | 10.0 TB/s |
| HBM | 80 GB | 192 GB | 256 GB |
| Price | $29,500 | $40,000 | $45,000 |

**Our Position:**
- NEXL-X4 (Q4 2026): 90% of B300 inference performance at 70% price
- NEXL-X4 price target: $35,000 (vs B300 $45,000)

### 3.3 Market Dynamics

| Segment | 2026 TAM | Our Share Target | Notes |
|---------|----------|-----------------|-------|
| AI Training | $58B | 5% (vs 8% current) | NEXL-A3 needed |
| AI Inference | $42B | 22% (vs 18%) | X4 launch critical |
| Edge AI | $18B | 35% (vs 26%) | E1 doing well |
| Automotive | $14B | 15% (vs 14%) | BMW/Toyota ramp |

---

## 4. NEXL-X4 Launch Readiness — David Park, VP Engineering

### 4.1 Tape-out Status

**Date:** June 15, 2026 (12 weeks away)

| Milestone | Original | Current | Status |
|-----------|----------|---------|--------|
| RTL Freeze | Mar 15 | Mar 18 | ✅ |
| Timing Closure | Apr 30 | Apr 28 | ✅ |
| Tape-out | Jun 15 | Jun 15 | ✅ ON TRACK |

**Readiness Assessment:**
- All major blocks verified
- DFT coverage 98.5%
- Place and route complete
- Power integrity validated
- Signal integrity confirmed

### 4.2 NEXL-X4 Specification Finalization

| Specification | Target | Achieved | Notes |
|---------------|--------|----------|-------|
| Inference Performance | 4,200 TOPS | 4,350 TOPS | +3.5% over target |
| Memory Bandwidth | 5.5 TB/s | 5.7 TB/s | +3.6% over target |
| HBM Capacity | 192 GB HBM4 | 192 GB HBM4 | On spec |
| TDP | 650W | 640W | -1.5% under target |
| Die Size | 740 mm² | 728 mm² | -1.6% smaller |

**Positioning:** "NEXL-X4 delivers 90% of B300 performance at 70% of the price"

### 4.3 Launch Timeline

| Phase | Date | Notes |
|-------|------|-------|
| Tape-out | Jun 15, 2026 | Target |
| First Silicon | Sep 2026 | ~14 weeks |
| Silicon Validation | Oct-Nov 2026 | 8 weeks |
| Production Release | Dec 2026 | Accelerated from Jan 2027 |
| Volume Shipment | Jan 2027 | 50K units target |

### 4.4 Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Tape-out delay | LOW | CRITICAL | 2-week buffer built in |
| Silicon respin | MEDIUM | HIGH | Multi-spin budget allocated |
| TSMC N3 yield | MEDIUM | MEDIUM | Engineering samples in Q3 |
| Software readiness | MEDIUM | HIGH | Parallel development |

---

## 5. Software Ecosystem — NEXL-SW 4.0 — Dr. Amanda Foster, CTO

### 5.1 NEXL-SW 4.0 Status

**Launch:** Q3 2026 (aligned with NEXL-X4)

| Component | Target | Status | Notes |
|-----------|--------|--------|-------|
| NEXL-SDK | Q3 2026 | 85% | Core API complete |
| NEXL-Compiler | Q3 2026 | 70% | LLVM-based, on track |
| NEXL-Runtime | Q3 2026 | 75% | Optimized for X4 |
| NEXL-Profiler | Q4 2026 | 60% | Beta in Q3 |
| PyTorch Support | Q3 2026 | 90% | 2.5 support |
| TensorFlow Support | Q4 2026 | 80% | 2.18 support |

### 5.2 CUDA Compatibility Layer

**Status:** Critical gap identified

**Current Position:**
- Basic CUDA compatibility via translation layer — 60% coverage
- Memory access patterns — 80% coverage
- Compute kernels — 45% coverage (main gap)

**Decision Needed:** Investment in CUDA compatibility vs native optimization

**Discussion:**
- Dr. Liu: "CUDA compatibility is table stakes. You cannot ask customers to rewrite code."
- James Morrison: "Enterprise customers tell us software is the #1 barrier to adoption."
- David Park: "Full CUDA compatibility adds 6 months to timeline and $40M investment."

**Decision:** APPROVE $40M additional investment for CUDA compatibility. Timeline adjusted to Q4 2026 (from Q3).

### 5.3 Developer Ecosystem

| Initiative | Investment | Status |
|-----------|-----------|--------|
| Developer Portal | $5M | Q3 launch |
| SDK Documentation | $3M | In progress |
| Sample Code Library | $2M | 200+ examples |
| Partner Enablement | $8M | 12 partners |
| Academic Program | $4M | 15 universities |

---

## 6. NEXL-A3 Training Product — Dr. Marcus Lee, Principal AI Architect

### 6.1 Product Status

**Target:** Q1 2027 launch

| Milestone | Original | Current | Status |
|-----------|----------|---------|--------|
| Architecture Finalize | Q2 2026 | Q2 2026 | ON TRACK |
| RTL Development | Q3 2026 | Q3 2026 | ON TRACK |
| Tape-out | Q4 2026 | Q4 2026 | ON TRACK |
| First Silicon | Q1 2027 | Q1 2027 | ON TRACK |

### 6.2 Competitive Position

| Specification | NEXL-A100 | NEXL-A3 | vs NVIDIA H200 |
|---------------|-----------|---------|----------------|
| FP8 Training | 350 TFLOPS | 850 TFLOPS | 95% |
| FP16 Training | 700 TFLOPS | 1.7 PFLOPS | 90% |
| Memory BW | 2.0 TB/s | 5.2 TB/s | 92% |
| HBM | 80 GB | 256 GB HBM4 | 100% |
| Price | $42,000 | $52,000 | Competitive |

### 6.3 Market Opportunity

**Training Market Dynamics:**
- NVIDIA dominates (85%+ share)
- Customers seeking alternatives (cost, availability)
- AMD MI300X gaining traction (5% share)
- Our position: "NVIDIA alternative for cost-conscious enterprises"

**Target Customers:**
- Secondary/tertiary GPU clusters
- Academic institutions
- Enterprise AI labs (non-hyperscaler)
- Emerging market AI providers

### 6.4 Concerns Raised

Michael asked about NEXL-A3 given the cybersecurity breach and IP theft:

> "Could the breach give NVIDIA/AMD insight into our A3 architecture?"

**Response from Dr. Lee:**
- NEXL-A3 architecture was accessed (confirmed in breach report)
- 120 GB of architecture documents exfiltrated
- Mitigation: Accelerating A3 development to reduce window
- Competitive impact: 3-6 month advantage loss estimated
- Action: Adding additional security features to differentiate

**Decision:** Add $15M for security hardening (anti-tamering, watermarking).

---

## 7. Edge/Automotive Portfolio Review

### 7.1 NEXL-E1 Edge SoC

**Status:** Volume production (ahead of schedule)

| Metric | Target | Actual | Notes |
|--------|--------|--------|-------|
| Q1 Shipments | 60K | 85K | Ahead of schedule |
| Q2 Target | 80K | — | On track |
| Design Wins | 15 | 18 | Exceeded |
| Revenue (Q1) | $48M | $52M | +8% |

**Success Factors:**
- Retail smart cart wins (Walmart, Target)
- Industrial automation (Fanuc)
- Medical imaging (GE Healthcare)

### 7.2 NEXL-E2 Advanced Edge

**Target:** Q3 2027 launch

**Spec Update:**
- AI Performance: 180 TOPS → 200 TOPS (revised up)
- Multi-modal: Vision, Audio, Text, Sensor fusion
- Power: 15W TDP (maintained)

### 7.3 Automotive Products

**NEXL-C1 (ADAS SoC):**
- BMW qualification: ON TRACK for Q2 sample approval
- Toyota qualification: ON TRACK for Q3
- Production: Q3 2027

**Concern:** ISO 26262 ASIL-D certification taking longer than expected.

**Decision:** Add 10 engineers to automotive SW integration team ($2.5M incremental).

---

## 8. Competitive Response Strategy

### 8.1 Pricing Strategy

| Product | Current Price | X4 Launch Price | Rationale |
|---------|--------------|-----------------|-----------|
| NEXL-X3 | $29,500 | $24,500 (EOL) | Make way for X4 |
| NEXL-X4 | — | $42,000 | Premium performance |
| NEXL-E1 | $14,200 | $13,500 | Volume competition |
| NEXL-A3 | — | $52,000 | Training market entry |

### 8.2 Customer targeting

| Customer | Target | Approach |
|----------|--------|----------|
| Amazon | NEXL-X4 evaluation | Multi-year agreement |
| Microsoft | NEXL-X4 preferred | Azure integration |
| Google | NEXL-X4 pilot | TPU differentiation |
| BMW | NEXL-C1 qualification | ASIL-D support |
| Toyota | NEXL-C1 qualification | Safety partnership |

---

## 9. Q2 Priorities

### 9.1 Critical Path Items

| Priority | Owner | Due Date | Success Metric |
|----------|-------|----------|----------------|
| NEXL-X4 Tape-out | David Park | Jun 15 | On-time tape-out |
| NEXL-SW 4.0 SDK | Amanda Foster | Jul 15 | 90% feature complete |
| BMW Sample Approval | James Morrison | Jun 30 | Qualification letter |
| CUDA Compatibility | Amanda Foster | Jul 30 | $40M investment approved |
| E1 Volume Ramp | Patricia Okonkwo | Jun 30 | 80K Q2 shipments |

### 9.2 Resource Decisions

| Decision | Investment | Recommendation |
|----------|-----------|----------------|
| CUDA compatibility | $40M | APPROVE |
| A3 security hardening | $15M | APPROVE |
| Automotive SW team | $2.5M | APPROVE |
| Developer ecosystem | $22M | APPROVE |

**Total Additional Investment:** $79.5M

**Source:** Reallocate from contingency funds and delay non-critical initiatives.

---

## 10. Key Decisions Made

1. **APPROVE:** NEXL-X4 price at $42,000 (vs B300 $45,000)

2. **APPROVE:** $40M CUDA compatibility investment

3. **APPROVE:** $15M NEXL-A3 security hardening

4. **APPROVE:** 10 additional automotive SW engineers ($2.5M)

5. **APPROVE:** NEXL-X4 production acceleration to December 2026

6. **DEFER:** NEXL-X5 architecture kickoff (pending X4 first silicon)

---

## 11. Next Steps

| Action | Owner | Due Date |
|--------|-------|----------|
| Finalize X4 pricing with Finance | Sarah Chen | May 15 |
| Execute CUDA compatibility contract | Amanda Foster | May 20 |
| BMW sample qualification letter | James Morrison | Jun 30 |
| Developer portal launch | Amanda Foster | Aug 1 |
| X4 first silicon briefing | David Park | Sep 15 |

---

## 12. Appendix: Competitive Analysis Reference

For detailed competitive analysis, see:
- NCCA-2025-Q2-003 (NVIDIA & AMD Competitor Analysis)
- NCPR-2026-001 (Confidential Product Roadmap 2026-2028)

---

**Minutes Prepared by:**  
Rachel Kim, Product Operations

**Approved by:**  
Sarah Chen, VP Product

---

*NPSM-Q2-2026-001 v1.0*  
*May 6, 2026*