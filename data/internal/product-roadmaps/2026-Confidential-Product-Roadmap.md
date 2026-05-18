# NEXLIFY CORP - CONFIDENTIAL PRODUCT ROADMAP 2026-2028

## STRICTLY CONFIDENTIAL - COMPETITIVE INTELLIGENCE

---

| Field | Value |
|-------|-------|
| **Document Title** | Product Roadmap 2026-2028 (Confidential) |
| **Document ID** | NCPR-2026-001 |
| **Version** | 1.3 |
| **Date** | May 12, 2025 |
| **Classification** | STRICTLY CONFIDENTIAL — OUTSIDE COMPETITORS |
| **Prepared By** | Dr. Sarah Kim, VP Product Strategy & Planning |
| **Reviewed By** | CEO, CTO, COO |
| **Distribution** | Executive Committee, Product Leadership, Strategic Accounts |

---

## 1. Document Purpose & Confidentiality

This document outlines Nexlify Corp's product roadmap for fiscal years 2026-2028. The information contained herein is **strictly confidential** and constitutes trade secrets under company policy and applicable law.

**Forbidden Actions:**
- ❌ Share with external parties, contractors, or consultants without NDA
- ❌ Discuss with customers or partners outside approved contexts
- ❌ Reference in public presentations, earnings calls, or press releases
- ❌ Store on unsecured systems or cloud services
- ❌ Email to personal accounts

**Authorized Distribution:** Executive Committee, VP-level and above, Product Leadership Team, Strategic Account Managers (read-only)

---

## 2. Executive Summary

### 2.1 Strategic Vision

Nexlify's 2026-2028 roadmap is built on three pillars:

1. **Performance Leadership** — Regain competitive advantage through NEXL-X4 and NEXL-X5
2. **Portfolio Expansion** — Capture edge and automotive markets with differentiated products
3. **Ecosystem Enablement** — Match NVIDIA's software moat through unified developer platform

### 2.2 Key Milestones

| Quarter | Product | Status | Strategic Rationale |
|---------|---------|--------|---------------------|
| Q1 2026 | NEXL-X4 (Tape-out) | ON TRACK | Performance parity with Blackwell |
| Q2 2026 | NEXL-E1 (Volume) | ON TRACK | Edge SoC market entry |
| Q4 2026 | NEXL-X4 (Production) | AT RISK | Awaiting TSMC capacity |
| Q1 2027 | NEXL-A3 (Training) | PLANNING | AI training market re-entry |
| Q2 2027 | NEXL-X5 (Architecture) | PLANNING | Next-gen performance leap |
| Q3 2027 | NEXL-C1 (Automotive) | PLANNING | Dedicated automotive SoC |

### 2.3 Portfolio Overview

```
NEXL Product Portfolio 2026-2028
─────────────────────────────────────────────────────
DATA CENTER
├── Training: NEXL-A3 (Q1 2027) — HBM4, 5nm, 2x A100
├── Inference: NEXL-X4 (Q4 2026) — HBM4, 3nm, 2x X3
└── High-End: NEXL-X5 (Q2 2027) — HBM4e, 2nm class

EDGE/CONSUMER
├── Edge SoC: NEXL-E1 (Q2 2026) — 7W TDP, CV/AI
├── Edge AI: NEXL-E2 (Q3 2027) — 15W TDP, multi-modal
└── IOT: NEXL-I1 (Q4 2027) — 2W TDP, ultra-low power

AUTOMOTIVE
├── ADAS: NEXL-C1 (Q3 2027) — ASIL-D, L3+ autonomous
├── Cockpit: NEXL-C2 (Q2 2028) — IVI, digital cluster
└── Edge: NEXL-C3 (Q4 2028) — V2X, infrastructure
```

---

## 3. Data Center Products

### 3.1 NEXL-X4 — Next Generation Inference Accelerator

**Launch:** Q4 2026 (Production)  
**Process:** TSMC 3nm N3E  
**Target Performance:** 2x NEXL-X3 inference throughput  
**Target Customers:** Hyperscalers, enterprise, edge data centers

**Technical Specifications (Target):**

| Specification | NEXL-X3 | NEXL-X4 | Improvement |
|---------------|---------|---------|-------------|
| Inference Performance | 1,800 TOPS | 4,200 TOPS | +133% |
| Memory Bandwidth | 2.8 TB/s | 5.5 TB/s | +96% |
| HBM Capacity | 80 GB HBM3e | 192 GB HBM4 | +140% |
| TDP | 700W | 650W | -7% |
| Die Size | 820 mm² | 740 mm² | -10% |
| Transistors | 92B | 140B | +52% |
| Price (ASP) | $29,500 | $42,000 | +42% |

**Competitive Position:**
- vs NVIDIA B200: 85% of B200 inference performance
- vs NVIDIA B300 (2026): 90% of B300 performance
- vs AMD MI350: 35% performance lead

**Key Features:**
1. **HBM4 Memory** — First to market with HBM4 (beating NVIDIA B300)
2. **3D V-Cache Architecture** — Stacked L3 cache for transformer models
3. **Transformer Engine v2** — Optimized for LLM inference
4. **Unified Memory Architecture** — Shared HBM across multi-chip config

**Challenges:**
- TSMC 3nm capacity constraints (may limit supply in 2026)
- Thermal design complexity (3D stacking)
- Software optimization (competing with mature CUDA ecosystem)

**Revenue Projections:**

| Year | Units | ASP | Revenue |
|------|-------|-----|---------|
| 2026 | 150,000 | $45,000 | $6.75B |
| 2027 | 450,000 | $40,000 | $18.0B |
| 2028 | 600,000 | $38,000 | $22.8B |

### 3.2 NEXL-X5 — Next-Next Generation

**Target Launch:** Q2 2027  
**Process:** TSMC 2nm N2  
**Architecture:** Chiplet-based, 3D stacking

**Target Specifications:**

| Specification | Target |
|---------------|--------|
| Performance | 4x NEXL-X4 |
| Process | TSMC 2nm N2P |
| Transistors | 280B |
| Memory | HBM4e, 512 GB |
| Bandwidth | 12 TB/s |
| TDP | 600W |
| Architecture | 4-chip chiplet, 3D stacking |

**Strategic Rationale:**
- Reclaim performance leadership from NVIDIA
- Demonstrate 2nm capability ahead of competition
- Chiplet architecture enables flexible configurations

**Status:** Architecture definition, RTL in 2026

### 3.3 NEXL-A3 — AI Training Accelerator

**Target Launch:** Q1 2027  
**Process:** TSMC 3nm N3P (optimized)  
**Target Performance:** 2x NEXL-A100, competitive with NVIDIA H200

**Technical Targets:**

| Specification | NEXL-A100 | NEXL-A3 | vs NVIDIA H200 |
|---------------|-----------|---------|----------------|
| FP8 Training | 350 TFLOPS | 850 TFLOPS | 95% |
| FP16 Training | 700 TFLOPS | 1.7 PFLOPS | 90% |
| Memory BW | 2.0 TB/s | 5.2 TB/s | 92% |
| HBM | 80 GB | 256 GB HBM4 | 100% |
| NVLink | N/A | 900 GB/s | 80% |
| Price | $42,000 | $55,000 | — |

**Competitive Context:**
- NVIDIA H200 (2024): Dominant training market (85%+ share)
- NVIDIA B200 (2025): Further extended lead
- Our position: Recover training market share (lost to Blackwell)

**Revenue Projections:**

| Year | Units | ASP | Revenue |
|------|-------|-----|---------|
| 2027 | 80,000 | $52,000 | $4.16B |
| 2028 | 200,000 | $48,000 | $9.6B |

---

## 4. Edge & IoT Products

### 4.1 NEXL-E1 — Edge AI SoC (In Production)

**Launch:** Q2 2026 (Volume)  
**Process:** TSMC 5nm  
**Target:** Edge inference, smart cameras, robotics

**Specifications:**

| Specification | Value |
|---------------|-------|
| AI Performance | 60 TOPS |
| CPU | 8x Cortex-A78 |
| GPU | Mali-G710 |
| Neural Engine | Custom NEXL-NE |
| Power | 7W TDP |
| Memory | LPDDR5, 32 GB |
| Interfaces | PCIe 4.0, USB4, MIPI |
| Software | NEXL-SW 3.0 |

**Market Position:**
- vs NVIDIA Jetson AGX Orin: 15% less performance, 30% lower price
- vs Qualcomm QCS8550: 40% better AI performance
- vs Mobileye EyeQ6: 2x AI performance, more flexible

**Target Applications:**
- Smart cameras (retail, city, industrial)
- Autonomous robots (warehouse, logistics)
- Edge servers (branch office, retail)
- Medical imaging (point-of-care)

### 4.2 NEXL-E2 — Advanced Edge Platform

**Target Launch:** Q3 2027  
**Process:** TSMC 3nm  
**Target:** Multi-modal AI, advanced robotics

**Specifications (Target):**

| Specification | Value |
|---------------|-------|
| AI Performance | 180 TOPS |
| Multi-modal | Vision, Audio, Text |
| CPU | 12x Cortex-X4 |
| Vision Engines | 4x dedicated CV |
| Power | 15W TDP |
| Memory | LPDDR6, 64 GB |
| Connectivity | 5G, WiFi 7 |

**Strategic Rationale:**
- Capture emerging multi-modal edge market
- Address next-gen robotics requirements
- Compete with Qualcomm Snapdragon Ride

### 4.3 NEXL-I1 — IoT AI Chip

**Target Launch:** Q4 2027  
**Process:** TSMC 6nm (cost-optimized)  
**Target:** Battery-powered IoT, always-on AI

**Specifications (Target):**

| Specification | Value |
|---------------|-------|
| AI Performance | 8 TOPS |
| Power | 2W TDP (active), 50mW (always-on) |
| Battery Life | 7+ years (coin cell) |
| Wake Word | Local, <2ms |
| Sleep Mode | 100μW |
| Process | TSMC 6nm |

**Applications:**
- Smart home devices
- Wearables
- Industrial sensors
- Healthcare monitors

---

## 5. Automotive Products

### 5.1 NEXL-C1 — Autonomous Driving SoC

**Target Launch:** Q3 2027  
**Process:** TSMC 5nm (automotive-grade)  
**Target:** Level 3+ autonomous systems

**Specifications (Target):**

| Specification | Value |
|---------------|--------|
| AI Performance | 500 TOPS |
| Safety | ASIL-D certified |
| CPU Clusters | 3x lockstep |
| ISP | 8 channels, 8K |
| Neural Engines | 4x dedicated AD |
| Interface | Automotive Ethernet, CAN-FD |
| Temperature | -40°C to +125°C |
| Package | Plastic BGA (automotive) |

**Safety Architecture:**
- Dual-lockstep CPU clusters
- Hardware safety island
- ECC on all memories
- ISO 26262 ASIL-D
- AEC-Q100 Grade 1

**Customer Engagements:**
- BMW (confirmed, 2027-2030)
- Toyota (confirmed, 2028+)
- Stellantis (in discussion, 2028)
- Hyundai (in discussion, 2029)

### 5.2 NEXL-C2 — Cockpit SoC

**Target Launch:** Q2 2028  
**Target:** Digital cluster, IVI, AR-HUD

**Specifications (Target):**

| Specification | Value |
|---------------|-------|
| Display Output | 6x 4K displays |
| GPU Performance | 4 TFLOPS |
| Video Decode | 8K @ 60fps |
| Audio Channels | 32 |
| Safety | ASIL-B |
| Operating System | Android Automotive, QNX |

### 5.3 NEXL-C3 — V2X/Edge Infrastructure

**Target Launch:** Q4 2028  
**Target:** Vehicle-to-everything communication, smart city

---

## 6. Software & Ecosystem

### 6.1 NEXL-SW 4.0 — Unified Developer Platform

**Launch:** Q3 2026 (aligned with NEXL-X4)  
**Target:** Match NVIDIA CUDA ecosystem

**Components:**

| Component | Description | Priority |
|-----------|-------------|----------|
| NEXL-SDK | Core API/SDK | CRITICAL |
| NEXL-Compiler | Custom compiler (LLVM-based) | CRITICAL |
| NEXL-Runtime | Optimized runtime | HIGH |
| NEXL-Profiler | Performance analysis | HIGH |
| NEXL-Docker | Containerized deployment | MEDIUM |
| NEXL-Cloud | Cloud management | MEDIUM |

**Feature Parity Timeline:**

| Capability | CUDA Equivalent | Target Parity |
|------------|------------------|---------------|
| Basic Compute | CUDA C/C++ | Q4 2026 |
| ML Frameworks | cuDNN, cuBLAS | Q1 2027 |
| Advanced Features | TensorRT, CUDA Graphs | Q2 2027 |
| Full Stack | Complete ecosystem | Q4 2027 |

### 6.2 NEXL-SW 3.0 (Current) Status

- ✅ PyTorch 2.4 support
- ✅ TensorFlow 2.17 support
- ✅ ONNX Runtime optimization
- ✅ Basic profiler
- ⏳ MLIR compiler (Q3 2025)
- ⏳ TensorRT-like optimization (Q4 2025)
- ❌ CUDA compatibility layer (2026+)

---

## 7. Technology Roadmap

### 7.1 Process Technology Timeline

| Node | Products | TSMC Node | Status |
|------|----------|-----------|--------|
| 7nm | NEXL-X1, NEXL-A100 | N7 | Mature |
| 5nm | NEXL-X3, NEXL-E1, NEXL-C1 | N5 | Production |
| 3nm | NEXL-X4, NEXL-E2 | N3E | Tape-out Q1 2026 |
| 3nm+ | NEXL-A3 | N3P | Design |
| 2nm | NEXL-X5 | N2 | Architecture |

### 7.2 Packaging Technology

| Technology | Products | Timeline |
|-----------|----------|----------|
| CoWoS (Standard) | NEXL-X3, X4 | NOW → 2027 |
| CoWoS-L | NEXL-X4, A3 | Q4 2026 |
| SoIC (3D Stacking) | NEXL-X5 | Q2 2027 |
| FOWLP | NEXL-E1, E2 | NOW |
| Chiplet | NEXL-X5 | Q2 2027 |

### 7.3 Memory Roadmap

| Memory | Products | Status |
|--------|----------|--------|
| HBM3e | NEXL-X4 | In development |
| HBM4 | NEXL-X4, A3 | 2026 |
| HBM4e | NEXL-X5 | 2027 |
| LPDDR5 | NEXL-E1 | NOW |
| LPDDR6 | NEXL-E2 | 2027 |

---

## 8. Competitive Analysis

### 8.1 NVIDIA Competitive Timeline

| Product | NVIDIA | Our Counter | Gap |
|---------|--------|------------|-----|
| Current | B200, B300 | NEXL-X3 | Performance gap |
| 2026 | B300 Ultra | NEXL-X4 | Parity |
| 2027 | B400 | NEXL-X5 | Leadership |
| Training | H200, B200 | NEXL-A3 | Partial parity |
| Edge | Orin NX, Thor | NEXL-E1, E2 | Competing |

### 8.2 AMD Competitive Timeline

| Product | AMD | Our Position | Gap |
|---------|-----|-------------|-----|
| Inference | MI300X, MI350 | NEXL-X3, X4 | Lead |
| Training | MI300X | NEXL-A3 | Competitive |
| Edge | Versal | NEXL-E1, E2 | Lead |

### 8.3 Competitive Response Strategy

**vs NVIDIA:**
- Performance parity: NEXL-X4 (Q4 2026)
- Training recovery: NEXL-A3 (Q1 2027)
- Software parity: NEXL-SW 4.0 (Q3 2026-Q4 2027)
- Price competition: Aggressive on inference

**vs AMD:**
- Maintain lead in inference
- Compete on software ecosystem
- Target AMD's customer base

---

## 9. Revenue Projections by Product Line

### 9.1 Consolidated Revenue Forecast

| Product Line | FY2026 | FY2027 | FY2028 |
|--------------|--------|--------|--------|
| Data Center (X4, A3) | $4.8B | $12.4B | $19.2B |
| Edge (E1, E2) | $380M | $1.2B | $2.4B |
| Automotive (C1) | $0 | $180M | $720M |
| Services | $140M | $200M | $280M |
| **Total** | **$5.32B** | **$13.98B** | **$22.6B** |

### 9.2 Portfolio Mix Evolution

| Category | FY2025 | FY2026 | FY2027 | FY2028 |
|----------|--------|--------|--------|--------|
| Data Center | 80% | 90% | 89% | 85% |
| Edge | 12% | 7% | 9% | 11% |
| Automotive | 4% | 0% | 1% | 3% |
| Services | 4% | 3% | 1% | 1% |

---

## 10. Risk Assessment

### 10.1 Product Launch Risks

| Product | Top Risk | Mitigation |
|---------|---------|------------|
| NEXL-X4 | TSMC capacity | Multi-source packaging, inventory buffer |
| NEXL-A3 | Software readiness | Earlier engagement, parallel development |
| NEXL-E1 | Customer adoption | Reference designs, ecosystem partnerships |
| NEXL-C1 | Qualification delays | Additional engineering resources, BMW partnership |

### 10.2 Technology Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| 3nm yield issues | MEDIUM | HIGH | TSMC partnership, multiple spins |
| HBM4 qualification delay | MEDIUM | HIGH | Early engagement with SK Hynix |
| CoWoS-L capacity | HIGH | HIGH | Alternative packaging, inventory |
| Chiplet integration | MEDIUM | MEDIUM | Pre-silicon verification, emulation |

---

## 11. Appendix: Canceled Products

### 11.1 NEXL-X3.5 — Canceled

**Reason:** Performance gap vs B200 insufficient to justify development  
**Decision Date:** March 2025  
**Redirected Resources:** NEXL-X4 acceleration

### 11.2 NEXL-E1 Pro — Postponed

**Reason:** NEXL-E2 roadmap absorbed capability  
**New Target:** Merge E1 Pro features into E2

---

## 12. Document Control

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 0.1 | Jan 15, 2025 | Initial draft | Sarah Kim |
| 0.5 | Feb 28, 2025 | Added E2, C1 details | Sarah Kim |
| 1.0 | Apr 15, 2025 | Executive review | Product Council |
| 1.3 | May 12, 2025 | Revenue updates, X5 specs | Sarah Kim |

**Classification:** This document is STRICTLY CONFIDENTIAL. Handle with highest care.

**Destruction:** This document must be destroyed after review. Do not retain electronic copies on personal devices.

---

*Prepared by Dr. Sarah Kim, VP Product Strategy & Planning*  
*May 12, 2025*

*NCPR-2026-001 v1.3*