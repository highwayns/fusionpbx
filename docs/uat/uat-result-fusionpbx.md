# FusionPBX UAT Test Result Record

---

## Metadata

| Field | Value |
|-------|-------|
| Project | FusionPBX |
| Document Type | UAT Test Result Record |
| Spec Reference | uat-spec-fusionpbx.md v1.0 |
| Version | 1.0 |
| Date Created | 2026-02-22 |

---

## 1. Execution Overview

| Field | Value |
|-------|-------|
| Execution Date | __________________ |
| Executor(s) | __________________ |
| Environment URL | __________________ |
| FusionPBX Version | __________________ |
| FreeSWITCH Version | __________________ |
| Database | PostgreSQL __.__ / SQLite |
| Browser(s) Used | __________________ |
| SIP Devices Used | __________________ |

---

## 2. Test Results

### Instructions

For each test case, record:
- **Actual Result**: What actually happened (describe briefly)
- **Pass/Fail**: Mark P (Pass), F (Fail), B (Blocked), or S (Skipped)
- **Execution Date**: Date this specific test was executed
- **Executor**: Person who ran this test
- **Remarks**: Any notes, defect IDs, or observations

### 2.1 Authentication (AUTH)

| TestNo | Procedure | Condition | ExpectedResult | ActualResult | Pass/Fail | ExecutionDate | Executor | Remarks |
|--------|-----------|-----------|----------------|--------------|-----------|---------------|----------|---------|
| AUTH-001 | Successful login with valid credentials | Login page accessible; valid user account exists | See spec | | | | | |
| AUTH-002 | Failed login with invalid password | Valid user account exists | See spec | | | | | |
| AUTH-003 | Failed login with non-existent user | None | See spec | | | | | |
| AUTH-004 | Successful logout | User is logged in | See spec | | | | | |
| AUTH-005 | Session timeout enforcement | User is logged in; short timeout configured | See spec | | | | | |
| AUTH-006 | Two-factor authentication (TOTP) login | 2FA enabled for user; authenticator app configured | See spec | | | | | |
| AUTH-007 | Password change by user | User is logged in | See spec | | | | | |
| AUTH-008 | Login with empty credentials | None | See spec | | | | | |
| AUTH-009 | CSRF protection on login form | None | See spec | | | | | |
| AUTH-010 | Concurrent session handling | User logged in on one browser | See spec | | | | | |

### 2.2 Dashboard (DASH)

| TestNo | Procedure | Condition | ExpectedResult | ActualResult | Pass/Fail | ExecutionDate | Executor | Remarks |
|--------|-----------|-----------|----------------|--------------|-----------|---------------|----------|---------|
| DASH-001 | Dashboard displays after login | User is logged in | See spec | | | | | |
| DASH-002 | Configure dashboard widgets | Logged in as admin | See spec | | | | | |
| DASH-003 | Remove a dashboard widget | Dashboard has widgets | See spec | | | | | |
| DASH-004 | Dashboard content varies by role | Three role accounts exist | See spec | | | | | |
| DASH-005 | Dashboard auto-refresh | Dashboard is displayed | See spec | | | | | |

### 2.3 User Management (USER)

| TestNo | Procedure | Condition | ExpectedResult | ActualResult | Pass/Fail | ExecutionDate | Executor | Remarks |
|--------|-----------|-----------|----------------|--------------|-----------|---------------|----------|---------|
| USER-001 | Create a new user | Logged in as admin | See spec | | | | | |
| USER-002 | Edit an existing user | User exists | See spec | | | | | |
| USER-003 | Delete a user | User exists | See spec | | | | | |
| USER-004 | Assign user to a group | User exists without group | See spec | | | | | |
| USER-005 | Remove user from a group | User has group assignment | See spec | | | | | |
| USER-006 | Create user with duplicate username | Duplicate username exists | See spec | | | | | |
| USER-007 | Bulk import users from CSV | CSV file prepared | See spec | | | | | |
| USER-008 | Admin cannot see users in other domains | Two domains with users | See spec | | | | | |
| USER-009 | User account disable | User exists and is enabled | See spec | | | | | |
| USER-010 | User changes own account settings | Logged in as end user | See spec | | | | | |

### 2.4 Domain Management (DOMAIN)

| TestNo | Procedure | Condition | ExpectedResult | ActualResult | Pass/Fail | ExecutionDate | Executor | Remarks |
|--------|-----------|-----------|----------------|--------------|-----------|---------------|----------|---------|
| DOMAIN-001 | Create a new domain | Logged in as superadmin | See spec | | | | | |
| DOMAIN-002 | Edit domain description | Domain exists | See spec | | | | | |
| DOMAIN-003 | Disable a domain | Domain exists and is enabled | See spec | | | | | |
| DOMAIN-004 | Configure domain settings | Domain exists | See spec | | | | | |
| DOMAIN-005 | Admin cannot manage domains | Logged in as admin | See spec | | | | | |

### 2.5 Extensions (EXT)

| TestNo | Procedure | Condition | ExpectedResult | ActualResult | Pass/Fail | ExecutionDate | Executor | Remarks |
|--------|-----------|-----------|----------------|--------------|-----------|---------------|----------|---------|
| EXT-001 | Create a new extension | Logged in as admin | See spec | | | | | |
| EXT-002 | Edit extension caller ID | Extension exists | See spec | | | | | |
| EXT-003 | Delete an extension | Extension exists | See spec | | | | | |
| EXT-004 | Set call forwarding on extension | Extension exists | See spec | | | | | |
| EXT-005 | Enable Do Not Disturb | Extension exists | See spec | | | | | |
| EXT-006 | Link extension to voicemail | Extension and voicemail exist | See spec | | | | | |
| EXT-007 | Create extension with duplicate number | Extension 1001 exists | See spec | | | | | |
| EXT-008 | Assign extension to a user | Extension and user exist | See spec | | | | | |
| EXT-009 | Disable an extension | Extension exists | See spec | | | | | |
| EXT-010 | Extension with maximum-length fields | None | See spec | | | | | |

### 2.6 Dialplan Management (DIAL)

| TestNo | Procedure | Condition | ExpectedResult | ActualResult | Pass/Fail | ExecutionDate | Executor | Remarks |
|--------|-----------|-----------|----------------|--------------|-----------|---------------|----------|---------|
| DIAL-001 | View dialplan entries | Dialplan entries exist | See spec | | | | | |
| DIAL-002 | Create an inbound route | Logged in as admin | See spec | | | | | |
| DIAL-003 | Create an outbound route | Gateway exists | See spec | | | | | |
| DIAL-004 | Edit a dialplan entry | Dialplan entry exists | See spec | | | | | |
| DIAL-005 | Delete a dialplan entry | Dialplan entry exists | See spec | | | | | |

### 2.7 Gateways (GW)

| TestNo | Procedure | Condition | ExpectedResult | ActualResult | Pass/Fail | ExecutionDate | Executor | Remarks |
|--------|-----------|-----------|----------------|--------------|-----------|---------------|----------|---------|
| GW-001 | Create a new gateway | Logged in as admin | See spec | | | | | |
| GW-002 | Edit gateway proxy address | Gateway exists | See spec | | | | | |
| GW-003 | Check gateway registration status | Gateway configured | See spec | | | | | |
| GW-004 | Delete a gateway | Gateway exists | See spec | | | | | |
| GW-005 | Create gateway without required fields | None | See spec | | | | | |

### 2.8 IVR Menus (IVR)

| TestNo | Procedure | Condition | ExpectedResult | ActualResult | Pass/Fail | ExecutionDate | Executor | Remarks |
|--------|-----------|-----------|----------------|--------------|-----------|---------------|----------|---------|
| IVR-001 | Create a new IVR menu | Recording exists | See spec | | | | | |
| IVR-002 | Add digit routing to IVR | IVR menu exists | See spec | | | | | |
| IVR-003 | Set IVR greeting recording | IVR menu and audio exist | See spec | | | | | |
| IVR-004 | Configure IVR timeout action | IVR menu exists | See spec | | | | | |
| IVR-005 | Delete an IVR menu | IVR menu exists | See spec | | | | | |

### 2.9 Ring Groups (RG)

| TestNo | Procedure | Condition | ExpectedResult | ActualResult | Pass/Fail | ExecutionDate | Executor | Remarks |
|--------|-----------|-----------|----------------|--------------|-----------|---------------|----------|---------|
| RG-001 | Create a new ring group | Extensions exist | See spec | | | | | |
| RG-002 | Edit ring group strategy | Ring group exists | See spec | | | | | |
| RG-003 | Configure ring group timeout | Ring group exists | See spec | | | | | |
| RG-004 | Add member to ring group | Ring group exists | See spec | | | | | |
| RG-005 | Delete a ring group | Ring group exists | See spec | | | | | |

### 2.10 Call Center (CC)

| TestNo | Procedure | Condition | ExpectedResult | ActualResult | Pass/Fail | ExecutionDate | Executor | Remarks |
|--------|-----------|-----------|----------------|--------------|-----------|---------------|----------|---------|
| CC-001 | Create a call center queue | Logged in as admin | See spec | | | | | |
| CC-002 | Add agent to queue | Queue and agents exist | See spec | | | | | |
| CC-003 | Configure queue timeout action | Queue exists | See spec | | | | | |
| CC-004 | View active call center status | Queue is active | See spec | | | | | |
| CC-005 | Remove agent from queue | Agent assigned to queue | See spec | | | | | |

### 2.11 Voicemail (VM)

| TestNo | Procedure | Condition | ExpectedResult | ActualResult | Pass/Fail | ExecutionDate | Executor | Remarks |
|--------|-----------|-----------|----------------|--------------|-----------|---------------|----------|---------|
| VM-001 | Configure voicemail box | Extension exists | See spec | | | | | |
| VM-002 | Upload voicemail greeting | Voicemail box exists | See spec | | | | | |
| VM-003 | Listen to voicemail message | Messages exist | See spec | | | | | |
| VM-004 | Delete a voicemail message | Messages exist | See spec | | | | | |
| VM-005 | Configure voicemail-to-email | Voicemail box exists | See spec | | | | | |

### 2.12 Recordings (REC)

| TestNo | Procedure | Condition | ExpectedResult | ActualResult | Pass/Fail | ExecutionDate | Executor | Remarks |
|--------|-----------|-----------|----------------|--------------|-----------|---------------|----------|---------|
| REC-001 | Upload a recording | Logged in as admin | See spec | | | | | |
| REC-002 | Play back a recording | Recording exists | See spec | | | | | |
| REC-003 | View call recordings | Call recordings exist | See spec | | | | | |

### 2.13 Fax (FAX)

| TestNo | Procedure | Condition | ExpectedResult | ActualResult | Pass/Fail | ExecutionDate | Executor | Remarks |
|--------|-----------|-----------|----------------|--------------|-----------|---------------|----------|---------|
| FAX-001 | Send a fax | Fax extension and gateway configured | See spec | | | | | |
| FAX-002 | View received faxes | Fax received | See spec | | | | | |
| FAX-003 | View fax queue status | Faxes have been queued | See spec | | | | | |

### 2.14 Conferencing (CONF)

| TestNo | Procedure | Condition | ExpectedResult | ActualResult | Pass/Fail | ExecutionDate | Executor | Remarks |
|--------|-----------|-----------|----------------|--------------|-----------|---------------|----------|---------|
| CONF-001 | Create a conference room | Logged in as admin | See spec | | | | | |
| CONF-002 | Configure conference PIN | Conference room exists | See spec | | | | | |
| CONF-003 | View active conference participants | Conference is active | See spec | | | | | |

### 2.15 Devices (DEV)

| TestNo | Procedure | Condition | ExpectedResult | ActualResult | Pass/Fail | ExecutionDate | Executor | Remarks |
|--------|-----------|-----------|----------------|--------------|-----------|---------------|----------|---------|
| DEV-001 | Register a new device | Logged in as admin | See spec | | | | | |
| DEV-002 | Edit device line assignment | Device exists | See spec | | | | | |
| DEV-003 | Provision a device | Device registered; phone on network | See spec | | | | | |

### 2.16 Access Controls (ACL)

| TestNo | Procedure | Condition | ExpectedResult | ActualResult | Pass/Fail | ExecutionDate | Executor | Remarks |
|--------|-----------|-----------|----------------|--------------|-----------|---------------|----------|---------|
| ACL-001 | View access control lists | Logged in as superadmin | See spec | | | | | |
| ACL-002 | Add a node to an ACL | ACL exists | See spec | | | | | |
| ACL-003 | Delete an ACL node | ACL has nodes | See spec | | | | | |

### 2.17 Call Detail Records (CDR)

| TestNo | Procedure | Condition | ExpectedResult | ActualResult | Pass/Fail | ExecutionDate | Executor | Remarks |
|--------|-----------|-----------|----------------|--------------|-----------|---------------|----------|---------|
| CDR-001 | View call detail records | CDR data exists | See spec | | | | | |
| CDR-002 | Filter CDR by date range | CDR data exists | See spec | | | | | |
| CDR-003 | Export CDR to CSV | CDR data exists | See spec | | | | | |

### 2.18 System Administration (SYS)

| TestNo | Procedure | Condition | ExpectedResult | ActualResult | Pass/Fail | ExecutionDate | Executor | Remarks |
|--------|-----------|-----------|----------------|--------------|-----------|---------------|----------|---------|
| SYS-001 | View system status | Logged in as superadmin | See spec | | | | | |
| SYS-002 | View switch status | Logged in as superadmin | See spec | | | | | |
| SYS-003 | Enable/disable a module | Logged in as superadmin | See spec | | | | | |
| SYS-004 | View FreeSWITCH logs | Logged in as superadmin | See spec | | | | | |
| SYS-005 | Manage switch variables | Logged in as superadmin | See spec | | | | | |

---

## 3. Execution Summary

| Metric | Count |
|--------|-------|
| Total Test Cases | 93 |
| Executed | ____ |
| Passed | ____ |
| Failed | ____ |
| Blocked | ____ |
| Skipped | ____ |
| **Pass Rate** | **____%** |

### By Priority

| Priority | Total | Executed | Passed | Failed | Pass Rate |
|----------|-------|----------|--------|--------|-----------|
| High | 31 | ____ | ____ | ____ | ____% |
| Medium | 42 | ____ | ____ | ____ | ____% |
| Low | 20 | ____ | ____ | ____ | ____% |

### By Category

| Category | Total | Passed | Failed | Blocked | Pass Rate |
|----------|-------|--------|--------|---------|-----------|
| Authentication | 10 | ____ | ____ | ____ | ____% |
| Dashboard | 5 | ____ | ____ | ____ | ____% |
| User Management | 10 | ____ | ____ | ____ | ____% |
| Domain Management | 5 | ____ | ____ | ____ | ____% |
| Extensions | 10 | ____ | ____ | ____ | ____% |
| Dialplan | 5 | ____ | ____ | ____ | ____% |
| Gateways | 5 | ____ | ____ | ____ | ____% |
| IVR Menus | 5 | ____ | ____ | ____ | ____% |
| Ring Groups | 5 | ____ | ____ | ____ | ____% |
| Call Center | 5 | ____ | ____ | ____ | ____% |
| Voicemail | 5 | ____ | ____ | ____ | ____% |
| Recordings | 3 | ____ | ____ | ____ | ____% |
| Fax | 3 | ____ | ____ | ____ | ____% |
| Conferencing | 3 | ____ | ____ | ____ | ____% |
| Devices | 3 | ____ | ____ | ____ | ____% |
| Access Controls | 3 | ____ | ____ | ____ | ____% |
| CDR | 3 | ____ | ____ | ____ | ____% |
| System Admin | 5 | ____ | ____ | ____ | ____% |

---

## 4. Defects Found

| Defect ID | Test Case | Severity | Summary | Status | Assigned To | Resolution Date |
|-----------|-----------|----------|---------|--------|-------------|-----------------|
| | | | | | | |
| | | | | | | |
| | | | | | | |

---

## 5. Remarks

### General Observations

_[Record any general observations, environmental issues, or patterns noticed during testing.]_



### Recommendations

_[Record any recommendations for the product team based on UAT findings.]_



### Blockers Encountered

_[Record any blockers that prevented test execution and how they were resolved.]_



---

## 6. Sign-Off

| Role | Name | Signature | Date |
|------|------|-----------|------|
| UAT Lead | __________________ | __________________ | __________ |
| Product Owner | __________________ | __________________ | __________ |
| Project Manager | __________________ | __________________ | __________ |

**UAT Outcome**: [ ] ACCEPTED / [ ] ACCEPTED WITH CONDITIONS / [ ] REJECTED

**Conditions (if applicable)**:

_[List any conditions that must be met before production release.]_
