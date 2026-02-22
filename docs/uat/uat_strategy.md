# FusionPBX UAT Strategy Document

> User Acceptance Testing strategy for the FusionPBX telecommunications platform.
> Date: 2026-02-22 | Version: 1.0

---

## 1. Document Purpose

This document defines the User Acceptance Testing (UAT) strategy for the FusionPBX system. It establishes the scope, approach, priority criteria, acceptance thresholds, and governance framework that guide all UAT activities. The strategy ensures that the deployed system meets the operational requirements of administrators, end-users, and the organization before production release.

---

## 2. Target Scope

### 2.1 System Under Test

| Attribute | Value |
|-----------|-------|
| System | FusionPBX (multi-tenant PBX web application) |
| Backend | FreeSWITCH telephony engine |
| Database | PostgreSQL (production) / SQLite (development) |
| Web Stack | PHP, Nginx/Apache |
| Protocol | SIP (Session Initiation Protocol) |

### 2.2 Quantitative Coverage

| Asset | Count | Reference Document |
|-------|-------|--------------------|
| Application and Core Features | 94 | feature_list.md |
| Web UI Screens / Pages | 93 | screen_list.md |
| Database Tables (v_* + FS core) | 87 | db_schema.md |
| API and Integration Points | 60 | api_list.md |

### 2.3 In-Scope

- All web-based user interface functionality across all roles (superadmin, admin, user)
- CRUD operations for all managed entities (users, extensions, gateways, IVR, etc.)
- Authentication and authorization workflows (login, logout, 2FA, password reset)
- Dashboard widget display and configuration
- Call management features (extensions, dialplans, call flows, call block, follow-me)
- Voicemail configuration and message management
- IVR menu creation and digit routing
- Conference room management
- Call center queue and agent management
- Ring group configuration
- Fax send, receive, and queue operations
- Device provisioning and registration
- CDR viewing, filtering, and export
- SIP profile and gateway management
- Access control list management
- System status and switch status monitoring
- Module management
- Multi-tenant domain management and domain settings
- Role-based access control enforcement

### 2.4 Out-of-Scope

- FreeSWITCH engine internals and C-level module testing (covered by unit/integration tests)
- Network-layer SIP packet testing (covered by SIPVicious or similar tools)
- Load and performance testing (separate performance test plan)
- Vendor-specific phone provisioning template testing for all 13 vendors (sampled only)
- Database migration and schema upgrade testing (covered by deployment runbook)
- Operating system and infrastructure hardening
- Third-party cloud integration testing (Azure module)

---

## 3. Test Design Policy

### 3.1 Test Perspective

All UAT test cases are designed from the **end-user perspective**. Testers interact with the system exclusively through the web browser and, where applicable, SIP phone devices. No direct database queries, API calls, or command-line operations are included in UAT procedures.

### 3.2 Test Case Categories

Each feature area includes test cases across three categories:

| Category | Description | Example |
|----------|-------------|---------|
| **Normal** | Standard expected usage with valid inputs | Create a new extension with extension number 1001 and valid password |
| **Abnormal** | Invalid input, unauthorized access, error handling | Attempt to create an extension with a duplicate number; login with wrong password |
| **Boundary** | Edge cases and limit conditions | Create extension with maximum-length description; upload recording at max file size |

### 3.3 Test Case Structure

Every test case includes:

1. **TestCaseID** - Unique identifier (e.g., AUTH-001)
2. **Category** - Functional area
3. **Scenario** - Brief description of what is being tested
4. **Prerequisites** - Required state before execution
5. **Steps** - Numbered, step-by-step instructions executable by non-technical users
6. **Input Data** - Specific values to enter
7. **Expected Result** - Observable outcome that constitutes a pass
8. **Priority** - High / Medium / Low

---

## 4. Priority Criteria

### 4.1 Priority Levels

| Priority | Criteria | Areas |
|----------|----------|-------|
| **High** | Core functionality that directly impacts call handling, security, or tenant isolation. Failure blocks production use. | Authentication (login/logout/2FA), Extensions (CRUD, forwarding), Voicemail, Dialplans (inbound/outbound routing), Gateways, Domain management, User/Group/Permission management, CDR access |
| **Medium** | Important features used regularly by administrators. Failure degrades operational efficiency but does not block core telephony. | IVR menus, Ring groups, Call center queues, Conferencing, Call flows, Fax, Dashboard, Recordings, Device provisioning |
| **Low** | Advanced administration, vendor-specific provisioning, and monitoring features. Failure is tolerable in initial deployment. | SIP profile tuning, Access control lists, Module management, Log viewer, System/Switch status, Vendor provisioning templates, Streams, Tones, Music on hold |

### 4.2 Execution Order

1. Execute all **High** priority test cases first
2. Execute **Medium** priority test cases
3. Execute **Low** priority test cases
4. Failed High-priority cases must be resolved before proceeding to Medium

---

## 5. Acceptance Criteria

### 5.1 Functional Acceptance Criteria

| ID | Criterion | Threshold |
|----|-----------|-----------|
| FA-01 | All features accessible per role assignment | 100% of screens load without error for authorized roles |
| FA-02 | CRUD operations complete successfully | Create, read, update, and delete work for all managed entities |
| FA-03 | Authentication and session management | Login, logout, 2FA, session timeout all function correctly |
| FA-04 | Role-based access control | Unauthorized users cannot access restricted screens or perform restricted operations |
| FA-05 | Data integrity across tenants | Actions in one domain do not affect another domain |
| FA-06 | FreeSWITCH integration | Configuration changes (extensions, dialplans, gateways) are applied to FreeSWITCH via reloadxml |
| FA-07 | Error handling | Invalid inputs produce clear error messages without stack traces or system information disclosure |

### 5.2 Non-Functional Acceptance Criteria

| ID | Criterion | Threshold |
|----|-----------|-----------|
| NF-01 | Page load time | All pages load within 3 seconds under normal conditions |
| NF-02 | Session security | Sessions expire after configured timeout; CSRF tokens are enforced on all POST operations |
| NF-03 | Browser compatibility | Full functionality in Chrome (latest), Firefox (latest), and Edge (latest) |
| NF-04 | Concurrent users | System supports at least 10 concurrent admin sessions without degradation |
| NF-05 | Data validation | All user input is validated; SQL injection and XSS payloads are rejected |

### 5.3 Pass/Fail Thresholds

| Priority | Required Pass Rate | Notes |
|----------|-------------------|-------|
| High | 100% | All high-priority test cases must pass |
| Medium | 95% | Up to 5% may fail with documented workarounds |
| Low | 90% | Up to 10% may fail with documented workarounds |
| Overall | 95% | Combined pass rate across all priorities |

---

## 6. Test Environment

### 6.1 Environment Requirements

| Component | Specification |
|-----------|--------------|
| FusionPBX | Current release version under test |
| FreeSWITCH | Matching version as required by FusionPBX |
| Database | PostgreSQL 13+ |
| Web Server | Nginx or Apache with PHP 8.0+ |
| Browser | Chrome, Firefox, or Edge (latest stable) |
| SIP Devices | At least 2 SIP softphones for call testing |
| Network | LAN connectivity between all components |

### 6.2 Test Accounts

| Account | Role | Domain | Purpose |
|---------|------|--------|---------|
| uat_superadmin | superadmin | (global) | Test superadmin-only features and multi-domain management |
| uat_admin | admin | test.example.com | Test domain-level administration features |
| uat_user | user | test.example.com | Test end-user features (voicemail, CDR, contacts) |
| uat_admin2 | admin | test2.example.com | Test multi-tenant isolation |

### 6.3 Test Data

The following test data must be pre-provisioned before UAT execution:

- At least 2 domains configured
- At least 5 extensions per domain
- At least 1 SIP gateway configured
- At least 1 IVR menu with digit routing
- At least 1 ring group with 3+ members
- At least 1 voicemail box with a test message
- At least 1 conference room
- At least 5 contacts
- At least 1 call center queue with agents

---

## 7. Roles and Responsibilities

| Role | Responsibility |
|------|---------------|
| UAT Lead | Owns the UAT plan, coordinates execution, tracks results, escalates blockers |
| Testers | Execute test cases, record results, report defects |
| Development Team | Triage and fix defects found during UAT |
| Product Owner | Reviews UAT results, provides final sign-off for production release |
| System Administrator | Prepares and maintains the UAT environment |

---

## 8. Defect Management

| Severity | Definition | Response SLA |
|----------|-----------|--------------|
| Critical | Core telephony or authentication feature is broken | Fix within 24 hours; UAT paused for affected area |
| Major | Feature works incorrectly but has a workaround | Fix within 48 hours; UAT continues |
| Minor | Cosmetic issue or minor inconvenience | Tracked for next release; does not block UAT |

---

## 9. Artifact References

| Document | File | Description |
|----------|------|-------------|
| Feature List | docs/uat/feature_list.md | Complete module and feature inventory (94 items) |
| Screen List | docs/uat/screen_list.md | All web UI screens with URL paths and role access (93 screens) |
| API List | docs/uat/api_list.md | JSON endpoints, form patterns, PHP classes, ESL commands (60 points) |
| Database Schema | docs/uat/db_schema.md | All database tables organized by category (87 tables) |
| UAT Test Specification | docs/uat/uat-spec-fusionpbx.md | Complete test cases with steps and expected results |
| UAT Result Template | docs/uat/uat-result-fusionpbx.md | Execution recording template |

---

## 10. Schedule and Milestones

| Milestone | Target | Owner |
|-----------|--------|-------|
| UAT environment ready | T-5 business days | System Administrator |
| Test data provisioned | T-3 business days | UAT Lead |
| High-priority test execution | T to T+3 days | Testers |
| Medium-priority test execution | T+3 to T+5 days | Testers |
| Low-priority test execution | T+5 to T+7 days | Testers |
| Defect resolution window | T+7 to T+10 days | Development Team |
| Re-test failed cases | T+10 to T+12 days | Testers |
| UAT sign-off | T+12 days | Product Owner |

---

## 11. Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| FreeSWITCH service instability during testing | Call-related tests cannot be executed | Dedicated UAT FreeSWITCH instance; restart procedures documented |
| Insufficient SIP devices for call testing | Cannot verify end-to-end call scenarios | Use softphones (Okt8 Okt8 Okt8 Okt8 Okt8 Okt8) as backup |
| Multi-tenant data leakage | Security vulnerability | Dedicated test domains with clearly marked test data |
| Tester unavailability | Schedule slippage | Cross-train at least 2 testers on all test areas |
