# Nexlify Corp Security Clearance Levels Guide

**Version:** 4.0  
**Owner:** Information Security / People Operations  
**Last Updated:** 2026-05-10  
**Classification:** Internal

---

## 1. Purpose

This guide outlines the security clearance level system at Nexlify Corp. Access to company information, systems, and facilities is controlled based on job responsibilities and data sensitivity. All employees are assigned a clearance level that determines what information they can access.

## 2. Overview of Access Levels

Nexlify Corp uses a four-tier access level system:

| Level | Name | Authentication Requirements |
|-------|------|----------------------------|
| 1 | Public | Basic authentication |
| 2 | Internal | Standard SSO |
| 3 | Confidential | MFA required (Okta) |
| 4 | Strictly Confidential | Hardware key (YubiKey FIPS) |

## 3. Access Level Definitions

### 3.1 Level 1: Public

**Description:** Information intended for public consumption or that has been publicly disclosed.

**Examples:**
- Marketing materials and public website content
- Press releases
- Job postings
- Publicly filed SEC documents
- Content approved for public release

**Access Requirements:**
- Standard employee account
- No additional authentication beyond basic login credentials

### 3.2 Level 2: Internal

**Description:** General business information intended for internal employees only. This is the default level for most employees.

**Examples:**
- Internal policies and procedures
- General company announcements
- Team project documentation in **Linear**
- Employee handbook content
- Non-sensitive meeting notes and communications

**Access Requirements:**
- Authentication via **Okta** SSO (single sign-on)
- Standard company credentials

**Access via:** Tailscale VPN recommended but not required for internal content.

### 3.3 Level 3: Confidential

**Description:** Sensitive business information that could harm the company or its customers if disclosed improperly. Access requires additional verification.

**Examples:**
- Unreleased financial results
- Employee personal information (PII)
- Customer contracts and pricing
- Product roadmaps and strategy
- Security incident details
- Legal matters and litigation
- M&A discussions and sensitive negotiations

**Access Requirements:**
- Authentication via **Okta** SSO
- **Multi-factor authentication (MFA)** required
- MFA must be configured on the employee's **Okta** account before access is granted
- Access logged and monitored

**Access via:** Tailscale VPN required for all Confidential-level content.

**Additional Controls:**
- Access reviews quarterly
- Data loss prevention (DLP) policies active
- No external sharing without encryption

### 3.4 Level 4: Strictly Confidential

**Description:** Highly sensitive information requiring the highest level of protection. Access is limited to specifically authorized individuals and involves hardware-based authentication.

**Examples:**
- Executive leadership communications
- Board materials and minutes
- Security architecture and penetration test results
- Highly classified business strategies
- Authentication systems and credentials
- Crisis response plans

**Access Requirements:**
- Authentication via **Okta** SSO
- **YubiKey FIPS hardware key** required for access
- YubiKey must be registered with the employee's **Okta** account
- Access granted only after physical YubiKey enrollment verified by IT Security
- Approved by Department Head and CISO

**Access via:** Tailscale VPN required. Connections are logged and subject to audit.

**Additional Controls:**
- Access reviews monthly
- Zero-trust architecture
- Behavioral anomaly detection active
- No printing or downloading without explicit approval
- Escort required in physical spaces containing Level 4 materials

## 4. Identity and Access Management

### 4.1 Identity Provider
Nexlify Corp uses **Okta** as the central identity provider for all access decisions. All employees must maintain an active Okta account for the duration of their employment.

### 4.2 SSO Requirements
Single Sign-On (SSO) is required for all company systems, including:
- **Slack**
- **Linear**
- **Notion**
- **Workday**
- **Expensify**

Direct login to these services (bypassing Okta) is prohibited except for service accounts with documented business justification.

### 4.3 VPN Access
**Tailscale** is the approved VPN solution for remote access to company resources. All employees working remotely must connect via Tailscale when accessing:
- Confidential (Level 3) information
- Strictly Confidential (Level 4) information
- Internal systems from non-office networks

Tailscale should be active during all working hours for remote employees.

## 5. Physical Security

### 5.1 Badge Access
Physical access to Nexlify Corp offices is managed through badge systems integrated with **Okta** identity. Badge access levels correspond to areas of the office:
- General office: All employees
- Server rooms and secure areas: Level 3+ employees only
- Executive floor: Invitation only, Level 4 clearance or executive assistant with documented approval

### 5.2 Visitor Management
All visitors must sign in at reception and be escorted by an employee at all times. Visitors are not granted access to Level 3 or Level 4 information or systems.

## 6. Obtaining Higher Access

### 6.1 Request Process
Employees who believe they need a higher access level should:
1. Discuss with their manager to confirm business justification
2. Submit access request through **Workday** (IT Security → Access Request)
3. Obtain manager approval (documented in request)
4. Obtain Department Head approval for Level 3 or Level 4
5. Complete any required training (especially for Level 4)
6. For Level 4, complete YubiKey enrollment with IT Security

### 6.2 Approval Requirements
| Level | Manager | Department Head | CISO | Other |
|-------|---------|----------------|------|-------|
| Level 2 | Required | — | — | — |
| Level 3 | Required | Required | — | — |
| Level 4 | Required | Required | Required | Executive approval |

## 7. Access Reviews

### 7.1 Quarterly Reviews
Access to Level 3 information is reviewed quarterly by department managers and People Operations to ensure continued business justification.

### 7.2 Monthly Reviews
Access to Level 4 information is reviewed monthly by the CISO and relevant executive sponsors.

### 7.3 Termination Reviews
All access is automatically revoked upon termination of employment.IT Security conducts a review within 24 hours of termination to confirm revocation.

### 7.4 Transfer Reviews
When an employee transfers between departments, their access is reviewed and adjusted as needed based on new role requirements. Previous access that is no longer needed is revoked.

## 8. Compliance

Violations of access level requirements may result in:
- Immediate suspension of access pending investigation
- Disciplinary action up to and including termination
- Legal action if criminal activity is suspected

All employees are required to report suspected access violations or security incidents to IT Security immediately. Reports can be made anonymously via the Ethics Hotline or directly to IT Security via Slack (#security) or security@nexlifycorp.com.

## 9. Training

All employees must complete the following security training:
- **Initial onboarding:** Security fundamentals within first 5 days
- **Annual:** Comprehensive security awareness training
- **Level 3+:** Additional data handling training
- **Level 4:** Advanced threat awareness and YubiKey usage training

Training completion is tracked in **Workday**.

---

**Related Documents:**
- Remote Work Policy
- Code of Conduct
- Equipment Provisioning Policy
