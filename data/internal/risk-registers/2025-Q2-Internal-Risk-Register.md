# NEXLIFY CORP - INTERNAL RISK REGISTER

## CONFIDENTIAL - INTERNAL USE ONLY

---

| Field | Value |
|-------|-------|
| **Document Title** | Q2 2025 Internal Risk Register |
| **Document ID** | NCR-2025-Q2-001 |
| **Version** | 2.1 (Final) |
| **Date** | May 17, 2025 |
| **Classification** | CONFIDENTIAL - BOARD LEVEL |
| **Prepared By** | Enterprise Risk Management Team |
| **Reviewed By** | CFO, COO, General Counsel |
| **Next Review** | August 15, 2025 |

---

## 1. Executive Summary

This document presents the comprehensive risk register for Nexlify Corp as of Q2 2025. The risk landscape has evolved significantly since Q1, with **geopolitical tensions in the Taiwan Strait** now rated as the highest-probability, highest-impact risk facing the company. Supply chain vulnerabilities, AI chip competition, and regulatory pressures have intensified, requiring immediate strategic attention.

**Key Changes from Q1 2025:**
- Taiwan geopolitical risk elevated from **HIGH** to **CRITICAL**
- AI chip competition risk elevated from **MEDIUM** to **HIGH**
- New entry: Data center cooling infrastructure risk (HIGH)
- Customer concentration risk downgraded from HIGH to MEDIUM (partial mitigation via new automotive contracts)

**Overall Enterprise Risk Posture:** ELEVATED

---

## 2. Risk Summary Dashboard

| Risk ID | Risk Category | Risk Title | Current Rating | Trend |
|---------|---------------|------------|----------------|-------|
| R-001 | Strategic | Taiwan Geopolitical Instability | 🔴 CRITICAL | ↑ |
| R-002 | Operational | Advanced Packaging Capacity Constraints | 🔴 HIGH | → |
| R-003 | Competitive | NVIDIA Blackwell Dominance | 🟠 HIGH | ↑ |
| R-004 | Financial | Customer Concentration (Hyperscaler Dependency) | 🟡 MEDIUM | ↓ |
| R-005 | Regulatory | US Export Controls (China Market) | 🔴 HIGH | → |
| R-006 | Operational | Talent Retention & AI Engineer Competition | 🟠 HIGH | → |
| R-007 | Strategic | Automotive OEM Qualification Delays | 🟡 MEDIUM | ↓ |
| R-008 | Technology | AI Inference Chip Architecture Shift | 🟠 HIGH | ↑ |
| R-009 | Financial | Margin Pressure from CoWoS Costs | 🟠 HIGH | → |
| R-010 | Operational | Data Center Cooling Limitations | 🟠 HIGH | NEW |
| R-011 | Strategic | Enterprise Customer Budget Constraints | 🟡 MEDIUM | → |
| R-012 | Compliance | AI Safety Regulations (EU AI Act) | 🟡 MEDIUM | ↑ |

---

## 3. Detailed Risk Profiles

### R-001: Taiwan Geopolitical Instability

**Category:** Strategic  
**Probability:** HIGH (45-55%)  
**Impact:** CATASTROPHIC  
**Risk Score:** 9.0/10  

**Description:**

Taiwan Strait tensions represent an existential threat to Nexlify's supply chain. Approximately **78% of our advanced packaging (CoWoS)** and **92% of our HBM memory** supply flows through TSMC and SK Hynix facilities in Taiwan and South Korea respectively. Any military conflict or blockade would halt production within 6-8 weeks.

**Current Exposure:**

| Component | Taiwan Dependency | Alternative Capacity | Lead Time to Diversify |
|-----------|-------------------|----------------------|-----------------------|
| CoWoS Packaging | 78% | Limited (Intel, Amkor in US) | 18-24 months |
| HBM Memory | 65% (SK Taiwan) | Samsung (Korea), Micron (US) | 12-18 months |
| Advanced Logic | 45% (TSMC) | Samsung, Intel Foundry | 24-36 months |

**Mitigation Status:**
- ✅ LOI signed with Amkor for US-based advanced packaging (Arizona facility)
- ✅ Design changes in progress for dual-sourcing HBM (Samsung/Micron qualification)
- ⚠️ TSMC Arizona capacity negotiations stalled (pricing dispute ongoing)
- ❌ No viable alternative for cutting-edge logic (< 3nm)

**Recommended Actions:**
1. Accelerate TSMC Arizona negotiations — accept 15% premium to secure 2026 capacity
2. Establish strategic HBM buffer inventory (target: 90 days)
3. Engage US Commerce Department for priority access to domestic packaging
4. Commission scenario planning for Taiwan conflict (3-week, 3-month, 6-month scenarios)

**Owner:** Marcus Chen, VP Supply Chain  
**Escalation Level:** CEO + Board

---

### R-002: Advanced Packaging Capacity Constraints

**Category:** Operational  
**Probability:** HIGH (60-70%)  
**Impact:** HIGH  
**Risk Score:** 8.5/10  

**Description:**

The global shortage in advanced packaging (CoWoS, SoIC) continues to constrain Nexlify's ability to scale AI accelerator production. NVIDIA's dominance in securing TSMC CoWoS capacity leaves competitors with limited options. Our current lead times for packaging have extended to **26-30 weeks**, up from 16 weeks in Q4 2024.

**Financial Impact:**

- Lost revenue opportunity: ~$340M (Q1-Q2 2025)
- Customer delivery delays: 12-18 weeks average
- Expediting costs: $18M (Q1-Q2 cumulative)

**Mitigation Status:**
- ✅ Secondary sourcing qualification with ASE Group ( Malaysia)
- ✅ Internal yield improvement initiative (+8% throughput)
- ⚠️ CoWoS-L variant development on hold (waiting for TSMC agreement)
- ❌ Insufficient packaging capacity remains primary bottleneck

**Recommended Actions:**
1. Prepay for 2026 packaging capacity (strategic inventory financing)
2. Evaluate acquisition of small advanced packaging firm
3. Launch customer communication program for delivery transparency

**Owner:** Patricia Okonkwo, VP Operations  
**Escalation Level:** COO

---

### R-003: NVIDIA Blackwell Dominance

**Category:** Competitive  
**Probability:** VERY HIGH (75-85%)  
**Impact:** HIGH  
**Risk Score:** 7.5/10  

**Description:**

NVIDIA's Blackwell Ultra architecture (B200/B300) has significantly widened the performance gap in AI training. Microsoft, Google, and Meta have committed **$47B+ combined** to Blackwell infrastructure in 2025, leaving limited greenfield capacity for alternative vendors. Our NEXL-X3 inference chips face increasing competition even in our strongest market segment.

**Competitive Positioning:**

| Metric | NEXL-X3 | NVIDIA B200 | Gap |
|--------|---------|------------|-----|
| Inference FLOPS/Watt | 3.2 | 4.8 | -33% |
| Memory Bandwidth | 2.8 TB/s | 8.0 TB/s | -65% |
| Software Ecosystem | Moderate | Best-in-class | Significant |
| Pricing | $28K | $35-40K | Competitive |

**Market Share Impact:**
- Inference market share: 18% (Q2 2025) vs 24% (Q2 2024)
- New design wins: 3 (down from 11 in Q2 2024)
- Enterprise customers evaluating alternative: 7 of top 20

**Mitigation Status:**
- ✅ NEXL-X4 architecture (post-hopper) on track for Q4 2025
- ✅ Software stack 3.0 (unified API) releasing September 2025
- ⚠️ Performance parity预计 2026才能实现

**Recommended Actions:**
1. Accelerate NEXL-X4 tape-out (move from March 2026 to December 2025)
2. Intensify software ecosystem partnerships
3. Target cost-sensitive markets (emerging economies, edge inference)

**Owner:** Dr. Sarah Kim, VP Product Strategy  
**Escalation Level:** CEO

---

### R-004: Customer Concentration (Hyperscaler Dependency)

**Category:** Financial  
**Probability:** MEDIUM (30-40%)  
**Impact:** HIGH  
**Risk Score:** 6.0/10  

**Description:**

Revenue concentration remains elevated but has improved. Our top 3 hyperscale customers (Microsoft, Amazon, Google) represent **52% of 2024 revenue**, down from 61% in 2023. New contracts in automotive and edge computing provide partial mitigation.

**Customer Concentration Analysis (2024):**

| Customer | Revenue Share | Contract Status | Risk |
|----------|--------------|------------------|------|
| Microsoft | 24% | Multi-year (2025-2027) | MEDIUM |
| Amazon | 16% | Annual renewal | HIGH |
| Google | 12% | 18-month | MEDIUM |
| Meta | 8% | Spot + quarterly | HIGH |
| Automotive (new) | 9% | Multi-year (2026-2029) | LOW |
| Edge/Other | 31% | Mixed | LOW |

**Mitigation Status:**
- ✅ New automotive contracts (BMW, Toyota) totaling $420M over 3 years
- ✅ Edge inference deals (retail, healthcare) growing 45% YoY
- ⚠️ Amazon renewal negotiations ongoing (price pressure expected)
- ❌ Concentration still above target (target: <40% for top 3)

**Recommended Actions:**
1. Prioritize Microsoft enterprise expansion (target: +5% share in FY26)
2. Qualify second source for Amazon business (reduce single-point dependency)
3. Accelerate edge/automotive pipeline (current pipeline: $680M)

**Owner:** James Rodriguez, VP Sales  
**Escalation Level:** CFO

---

### R-005: US Export Controls (China Market)

**Category:** Regulatory  
**Probability:** HIGH (55-65%)  
**Impact:** HIGH  
**Risk Score:** 7.0/10  

**Description:**

US-China technology tensions continue to escalate. Proposed expansion of export controls to additional AI chips (NEXL-A100 equivalent and above) would directly impact our $890M China market exposure. BIS is expected to finalize new rules by Q3 2025.

**China Revenue Exposure:**

| Region | FY2024 Revenue | % of Total | Export Control Risk |
|--------|---------------|-----------|---------------------|
| China (Mainland) | $620M | 11% | HIGH |
| Hong Kong | $180M | 3% | HIGH |
| Taiwan (local) | $90M | 2% | MEDIUM |
| ROW | $4.6B | 84% | LOW |

**Scenario Analysis:**

| Scenario | Probability | Revenue Impact | Mitigation |
|----------|------------|----------------|------------|
| Expanded controls (all >A100) | 40% | -$780M annually | Redirect to other markets |
| Targeted restrictions (NEXL-X3+) | 25% | -$420M annually | License applications |
| Status quo | 35% | Minimal | N/A |

**Mitigation Status:**
- ✅ Investment in non-China market development (+$180M in Europe/SEA)
- ✅ China local entity restructuring (reduce HQ exposure)
- ⚠️ Indirect sales monitoring program (incomplete)
- ❌ China revenue cannot be fully replaced in short term

**Recommended Actions:**
1. Establish dedicated China compliance team (hire 3 FTEs by Q3)
2. Accelerate India/SEA market development (invest $50M marketing)
3. Prepare litigation reserve ($45M) in case control expansion
4. Engage via trade associations for BIS rule-making input

**Owner:** Elena Vasquez, General Counsel  
**Escalation Level:** Board

---

### R-006: Talent Retention & AI Engineer Competition

**Category:** Operational  
**Probability:** HIGH (65-75%)  
**Impact:** MEDIUM  
**Risk Score:** 6.5/10  

**Description:**

The war for AI talent remains intense. Our attrition rate for AI/ML engineers reached **18% in Q1 2025**, above the 12% industry benchmark. Counter-offers have increased 45% since 2023, and equity burn rate is unsustainable at current trajectory.

**Talent Metrics (Q1 2025):**

| Metric | Current | Target | Gap |
|--------|---------|--------|-----|
| AI/ML Engineer Attrition | 18% | 10% | +8pp |
| Time to Fill Senior Roles | 94 days | 60 days | +34 days |
| Offer Acceptance Rate | 62% | 75% | -13pp |
| Competitive Offer Premium | +28% | N/A | N/A |

**Key Flight Risks:**
1. Dr. Anthony Wu (Chief AI Architect) — evaluating Google offer
2. 4 senior compiler engineers — rumored Meta interest
3. 12 ML engineers — receiving weekly LinkedIn recruiter contacts

**Mitigation Status:**
- ✅ Retention equity program (RSU refresh for 45 critical employees)
- ✅ Technical career ladder reform (new Principal/Distinguished tracks)
- ✅ Austin campus expansion (improved facilities)
- ⚠️ Compensation still 15% below Google/NVIDIA for senior ICs
- ❌ Base salary compression (need market adjustment)

**Recommended Actions:**
1. Immediate salary adjustment for 200 critical engineers (+12% average)
2. Accelerated Dr. Wu retention package ($2.5M retention bonus)
3. Establish "Nexlify Research Fellowship" (PhD pipeline program)
4. Review competitor retention packages monthly

**Owner:** Michelle Taylor, Chief People Officer  
**Escalation Level:** CEO

---

### R-007: Automotive OEM Qualification Delays

**Category:** Strategic  
**Probability:** MEDIUM (35-45%)  
**Impact:** MEDIUM  
**Risk Score:** 5.5/10  

**Description:**

While automotive contracts provide diversification, qualification timelines have extended. BMW and Toyota programs are 4-6 months behind schedule due to rigorous safety validation requirements and software integration complexity.

**Automotive Pipeline Status:**

| Customer | Contract Value | Original Date | Revised Date | Status |
|----------|---------------|--------------|-------------|---------|
| BMW | $280M | Q3 2025 | Q1 2026 | AT RISK |
| Toyota | $140M | Q4 2025 | Q2 2026 | AT RISK |
| Stellantis | $180M | Q2 2026 | TBD | ON TRACK |
| Hyundai | $95M | Q3 2026 | TBD | ON TRACK |

**Root Causes:**
- Functional safety standards (ISO 26262) more stringent than expected
- In-vehicle integration complexity with legacy automotive E/E architectures
- Software stack customization requirements (AUTOSAR, Android Automotive)

**Mitigation Status:**
- ✅ Dedicated automotive engineering team (42 FTEs, growing to 65)
- ✅ ISO 26262 ASIL-D certification in progress
- ⚠️ BMW timeline slippage ongoing (negotiating milestone adjustments)
- ❌ Toyota software team understaffed (3 open reqs)

**Recommended Actions:**
1. Hire automotive-specific SW integration team (8 engineers, target: July)
2. Negotiate contract milestone extensions with BMW (preserve relationship)
3. Accelerate Stellantis/Hyundai qualification (reduce BMW concentration)
4. Consider strategic partnership with automotive tier-1 (Bosch, Continental)

**Owner:** Robert Martinez, VP Automotive  
**Escalation Level:** COO

---

### R-008: AI Inference Architecture Shift

**Category:** Technology  
**Probability:** HIGH (70-80%)  
**Impact:** HIGH  
**Risk Score:** 7.5/10  

**Description:**

The AI inference market is shifting from discrete accelerators to integrated SoC solutions and custom ASICs. Hyperscalers are increasingly building proprietary inference chips (Google TPU v7, Amazon Inferentia 3), reducing the addressable market for merchant silicon.

**Market Architecture Trends:**

| Architecture Type | 2024 Share | 2026 Projected | Trend |
|------------------|-----------|----------------|-------|
| Discrete AI Accelerators | 48% | 35% | ↓↓ |
| Integrated SoC (AI on chip) | 28% | 38% | ↑↑ |
| Custom ASICs (hyperscalers) | 18% | 22% | ↑ |
| FPGA/Other | 6% | 5% | → |

**NEXL Position:**
- Current strength: Discrete inference accelerators (75% of revenue)
- Emerging weakness: No integrated SoC offering
- Opportunity: Edge inference (no custom ASIC competition yet)

**Mitigation Status:**
- ✅ NEXL-E1 (edge SoC) on track for Q4 2025
- ⚠️ No hyperscaler custom ASIC strategy defined
- ❌ Integrated datacenter SoC (3+ year gap vs competition)

**Recommended Actions:**
1. Evaluate integrated SoC product line (start architecture study)
2. Double down on edge inference (automotive, IoT, retail)
3. Partner with FPGA vendor (AMD Xilinx) for hybrid solutions
4. Monitor hyperscaler ASIC roadmap closely

**Owner:** Dr. Sarah Kim, VP Product Strategy  
**Escalation Level:** CEO

---

### R-009: Margin Pressure from CoWoS Costs

**Category:** Financial  
**Probability:** HIGH (60-70%)  
**Impact:** HIGH  
**Risk Score:** 7.0/10  

**Description:**

Advanced packaging costs have increased 35% since 2023, compressing gross margins. The combination of CoWoS premiums, HBM price increases, and limited pricing power in a competitive market threatens our 52% gross margin target.

**Margin Impact Analysis:**

| Factor | 2023 | 2024 | 2025 (Projected) | Change |
|--------|------|------|-----------------|--------|
| CoWoS Cost per Unit | $1,200 | $1,580 | $1,720 | +43% |
| HBM Cost per Unit | $800 | $1,100 | $1,280 | +60% |
| Average Selling Price | $28,000 | $29,500 | $30,200 | +8% |
| Gross Margin | 54% | 51% | 48% (target: 52%) | -6pp |

**Break-Even Analysis:**

To maintain 52% gross margin with current cost structure, we need:
- +8% average selling price increase, OR
- -22% packaging cost reduction, OR
- +$420M revenue (economies of scale)

**Mitigation Status:**
- ⚠️ Partial price increase to Microsoft/Amazon (6%, not full 8%)
- ✅ Yield improvement initiatives (+5% throughput)
- ⚠️ CoWoS cost negotiation with TSMC (15% reduction target, stuck at 8%)
- ❌ Insufficient scale for material cost leverage

**Recommended Actions:**
1. Implement price increase for new orders (effective Q3)
2. Expand Amkor/ASE capacity to reduce TSMC dependency (pricing leverage)
3. Consider product redesign for cost optimization (NEXL-X3.5 variant)
4. Negotiate multi-year CoWoS pricing agreement with volume commitment

**Owner:** Michael Thompson, VP Finance  
**Escalation Level:** CFO

---

### R-010: Data Center Cooling Limitations

**Category:** Operational  
**Probability:** MEDIUM (40-50%)  
**Impact:** HIGH  
**Risk Score:** 6.0/10  

**Description:**

NEW RISK — As AI workloads increase power density (NEXL-X3 draws 700W TDP), hyperscaler data centers face thermal management challenges. Several customers report cooling infrastructure limitations constraining AI accelerator deployment density, limiting our growth even where customer demand exists.

**Customer Feedback (Q1 2025 Survey):**
- 8 of 20 enterprise customers cited cooling constraints
- Average deployment density 15% below theoretical maximum
- 3 customers delayed major expansions pending cooling upgrades

**Industry Context:**
- Average AI accelerator power density: 400W → 800W (2024-2026)
- Data center cooling technology lag: 12-18 months
- Liquid cooling adoption: 35% (target: 65% by 2027)

**Mitigation Status:**
- ✅ Partnership with liquid cooling vendors (Green Revolution Cooling, ZutaCore)
- ⚠️ NEXL-X4 thermal design review (targeting 20% improvement)
- ❌ No direct cooling product offering
- ❌ Limited influence on customer infrastructure decisions

**Recommended Actions:**
1. Develop "thermal advisory" services for customers
2. Co-develop liquid cooling solutions with data center operators
3. Design NEXL-X4 for both air and liquid cooling flexibility
4. Partner with infrastructure vendors (Schneider, Vertiv) for bundled solutions

**Owner:** Patricia Okonkwo, VP Operations  
**Escalation Level:** COO

---

### R-011: Enterprise Customer Budget Constraints

**Category:** Strategic  
**Probability:** MEDIUM (45-55%)  
**Impact:** MEDIUM  
**Risk Score:** 5.5/10  

**Description:**

Enterprise IT budgets remain tight amid macroeconomic uncertainty. Several customers have reduced AI infrastructure spending forecasts for 2025, with some shifting from CapEx to OpEx models (cloud rental vs. on-prem purchase).

**Budget Trend Analysis:**

| Segment | Q4 2024 Budget | Q1 2025 Budget | Change |
|---------|----------------|----------------|--------|
| Fortune 500 | $2.1B (pipeline) | $1.7B (revised) | -19% |
| Mid-Market | $890M | $920M | +3% |
| Government | $420M | $480M | +14% |
| SMB | $180M | $160M | -11% |

**Customer Feedback Themes:**
- "Waiting for Blackwell pricing to stabilize before committing"
- "Shifting to cloud (AWS SageMaker) for flexibility"
- "Evaluating total cost of ownership vs. initial price"
- "Delaying upgrade cycles from older NEXL-X1 to X3"

**Mitigation Status:**
- ✅ Flexible financing program (NEXL Capital) launched
- ✅ Cloud-adjacent product (NEXL-CloudEdge) in development
- ⚠️ Pricing flexibility limited by margin targets
- ❌ No immediate response to cloud shift

**Recommended Actions:**
1. Accelerate NEXL Capital financing program (target: $200M in Q3)
2. Launch "Right-Size" product bundle (X1 upgrade trade-in program)
3. Develop TCO calculator tools for customer presentations
4. Partner with cloud providers for hybrid solutions

**Owner:** James Rodriguez, VP Sales  
**Escalation Level:** CFO

---

### R-012: AI Safety Regulations (EU AI Act)

**Category:** Compliance  
**Probability:** MEDIUM (35-45%)  
**Impact:** MEDIUM  
**Risk Score:** 5.0/10  

**Description:**

The EU AI Act enters force in phases through 2026-2027. While Nexlify's products are primarily in B2B contexts (not consumer-facing), certain automotive and medical applications may trigger "high-risk" classification with associated compliance requirements.

**EU AI Act Impact Assessment:**

| Product Category | Risk Level | Compliance Requirements | Estimated Cost |
|------------------|-----------|------------------------|---------------|
| AI Accelerators (general) | Low | Basic transparency | $2M |
| Automotive (BMW/Toyota) | HIGH | Full conformity assessment | $8M |
| Medical/Healthcare | HIGH | Strict conformity + audits | $15M |
| Financial Services | Limited | Transparency + record keeping | $4M |

**Compliance Timeline:**
- August 2025: Prohibited AI practices rules apply
- August 2026: High-risk AI systems requirements apply
- August 2027: General product requirements apply

**Mitigation Status:**
- ✅ Legal review of EU AI Act requirements completed
- ⚠️ Automotive product audit in progress (target: Q4 2025)
- ❌ Medical/healthcare compliance team not yet formed
- ❌ No formal conformity assessment process

**Recommended Actions:**
1. Hire EU AI Act compliance lead (dedicated role)
2. Begin automotive conformity assessment (priority)
3. Establish AI risk management framework (aligned with ISO 42001)
4. Review all customer contracts for EU AI Act risk allocation

**Owner:** Elena Vasquez, General Counsel  
**Escalation Level:** Board

---

## 4. Risk Mitigation Tracking

### High-Priority Actions (Next 90 Days)

| Action | Owner | Due Date | Status | Impact |
|--------|-------|----------|--------|--------|
| Secure TSMC Arizona pricing agreement | Marcus Chen | Jun 30 | IN PROGRESS | CRITICAL |
| Retention package for Dr. Wu | Michelle Taylor | May 30 | URGENT | CRITICAL |
| Salary adjustment for 200 critical engineers | Michelle Taylor | Jun 15 | APPROVED | HIGH |
| Price increase for new orders | Michael Thompson | Jul 1 | PENDING | HIGH |
| Amkor capacity expansion agreement | Marcus Chen | Jun 30 | IN PROGRESS | HIGH |
| BMW milestone negotiation | Robert Martinez | May 31 | IN PROGRESS | MEDIUM |
| EU AI Act compliance lead hire | Elena Vasquez | Jul 15 | IN PROGRESS | MEDIUM |

---

## 5. Emerging Risks (Watch List)

The following risks are not yet material but warrant monitoring:

| Risk | Probability | Impact | Notes |
|------|------------|--------|-------|
| Quantum computing threat to encryption | LOW | HIGH | Monitor 2027+ |
| Climate-related manufacturing disruption | MEDIUM | MEDIUM | Taiwan drought risk |
| AI chip commodity market shift | MEDIUM | HIGH | Price war scenario |
| Acquisition of competitor by hyperscaler | MEDIUM | HIGH | Potential market consolidation |
|人才流失风险 (talent outflow to China) | LOW | MEDIUM | Restrictive covenants under review |

---

## 6. Appendix: Risk Rating Methodology

### Probability Ratings

| Rating | Probability Range | Description |
|--------|------------------|-------------|
| VERY LOW | <10% | Highly unlikely event |
| LOW | 10-25% | Unlikely but possible |
| MEDIUM | 25-50% | Reasonable possibility |
| HIGH | 50-75% | More likely than not |
| VERY HIGH | >75% | Expected to occur |

### Impact Ratings

| Rating | Financial Impact | Operational Impact |
|--------|-----------------|-------------------|
| LOW | <$50M | Minimal disruption |
| MEDIUM | $50-250M | Manageable impact |
| HIGH | $250-500M | Significant disruption |
| CATASTROPHIC | >$500M | Existential threat |

### Risk Score Matrix

|  | LOW Impact | MEDIUM Impact | HIGH Impact | CATASTROPHIC |
|--|------------|--------------|-------------|--------------|
| VERY LOW | 1 | 2 | 3 | 4 |
| LOW | 2 | 3 | 4 | 5 |
| MEDIUM | 3 | 4 | 6 | 7 |
| HIGH | 4 | 6 | 8 | 9 |
| VERY HIGH | 5 | 7 | 9 | 10 |

---

## 7. Document Control

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | Apr 1, 2025 | Risk Team | Initial draft |
| 1.1 | Apr 15, 2025 | CFO Review | Financial adjustments |
| 2.0 | May 1, 2025 | Risk Team | Q2 review complete |
| 2.1 | May 17, 2025 | Legal Review | Final classification updates |

**Approved by:** James Morrison, Chief Financial Officer  
**Date:** May 17, 2025

**Distribution:**
- CEO (Final)
- COO (Final)
- CFO (Final)
- General Counsel (Final)
- Board Risk Committee (Summary only)

---

*This document contains confidential information. Unauthorized distribution is prohibited.*
*Classification: CONFIDENTIAL - BOARD LEVEL*
*NCR-2025-Q2-001 v2.1*