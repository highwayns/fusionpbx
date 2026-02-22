# FusionPBX UAT Test Specification

---

## Metadata

| Field | Value |
|-------|-------|
| Project | FusionPBX |
| Document Type | UAT Test Specification |
| Version | 1.0 |
| Date | 2026-02-22 |
| Status | Ready for Execution |
| Author | UAT Team |

---

## Revision History

| Version | Date | Author | Description |
|---------|------|--------|-------------|
| 0.1 | 2026-02-20 | UAT Team | Initial draft with test case outlines |
| 0.9 | 2026-02-21 | UAT Team | Complete test cases with detailed steps |
| 1.0 | 2026-02-22 | UAT Team | Final review and approval for execution |

---

## 1. UAT Target Scope

### 1.1 Features Under Test

| Category | Feature Count | Reference |
|----------|--------------|-----------|
| Core System Modules | 20 | feature_list.md (Core) |
| Application Modules | 74 | feature_list.md (App) |
| Web UI Screens | 93 | screen_list.md |
| Database Tables | 87 | db_schema.md |
| API / Integration Points | 60 | api_list.md |

### 1.2 In-Scope

- Authentication, authorization, and session management
- All CRUD operations for managed entities
- Role-based access control across superadmin, admin, and user roles
- Multi-tenant domain isolation
- Call management (extensions, dialplans, gateways, call flows)
- Voice features (voicemail, IVR, recordings, conferencing)
- Queue management (call center, ring groups, FIFO)
- Fax operations (send, receive, queue)
- Device provisioning
- CDR access and reporting
- System administration (switch status, modules, SIP profiles, ACLs)

### 1.3 Out-of-Scope

- FreeSWITCH engine-level testing
- SIP protocol packet analysis
- Performance and load testing
- All 13 vendor-specific provisioning templates (sampled coverage only)
- Infrastructure and OS-level hardening

---

## 2. Prerequisites

### 2.1 Test Accounts

| Account | Username | Role | Domain | Password |
|---------|----------|------|--------|----------|
| Superadmin | uat_superadmin | superadmin | (global) | [provided separately] |
| Domain Admin | uat_admin | admin | test.example.com | [provided separately] |
| End User | uat_user | user | test.example.com | [provided separately] |
| Second Admin | uat_admin2 | admin | test2.example.com | [provided separately] |

### 2.2 Test Environment

- FusionPBX instance deployed and accessible via HTTPS
- FreeSWITCH running and connected via Event Socket
- PostgreSQL database initialized with schema
- At least 2 configured domains
- At least 5 extensions pre-created per domain
- At least 1 SIP gateway configured
- At least 2 SIP softphones available for call testing
- Test audio files (WAV format) available for upload
- Test PDF/TIFF file available for fax testing

### 2.3 Test Data

| Data Item | Quantity | Notes |
|-----------|----------|-------|
| Domains | 2+ | test.example.com, test2.example.com |
| Extensions | 5+ per domain | Range: 1001-1005 |
| Contacts | 5+ | With phone, email, and address data |
| Voicemail boxes | 2+ | With at least 1 test message |
| IVR menu | 1+ | With digit routing configured |
| Ring group | 1+ | With 3+ member extensions |
| Conference room | 1+ | With moderator and participant PINs |
| Call center queue | 1+ | With 2+ agents assigned |
| SIP gateway | 1+ | Configured and registered |
| Audio recordings | 2+ | WAV files for IVR/MOH testing |

---

## 3. Acceptance Criteria

### 3.1 Functional

| ID | Criterion |
|----|-----------|
| FA-01 | All features are accessible per assigned role |
| FA-02 | CRUD operations complete successfully for all managed entities |
| FA-03 | Authentication workflows (login, logout, 2FA, password reset) function correctly |
| FA-04 | Role-based access control prevents unauthorized access |
| FA-05 | Multi-tenant data isolation is enforced |
| FA-06 | FreeSWITCH configuration changes are applied on save |
| FA-07 | Error messages are clear and do not expose system internals |

### 3.2 Non-Functional

| ID | Criterion |
|----|-----------|
| NF-01 | All pages load within 3 seconds |
| NF-02 | Sessions expire after configured timeout |
| NF-03 | CSRF tokens are enforced on all POST forms |
| NF-04 | System functions correctly in Chrome, Firefox, and Edge |

---

## 4. Test Cases

### Legend

- **Priority**: H = High, M = Medium, L = Low
- **Roles**: SA = Superadmin, A = Admin, U = User
### 4.1 Authentication (AUTH)

| TestCaseID | Category | Scenario | Prerequisites | Steps | InputData | ExpectedResult | Priority |
|------------|----------|----------|---------------|-------|-----------|----------------|----------|
| AUTH-001 | Authentication | Successful login with valid credentials | User account exists and is enabled | 1. Open the FusionPBX login page in browser. 2. Enter username in the Username field. 3. Enter password in the Password field. 4. Select the domain from the domain dropdown (if shown). 5. Click the Login button. | Username: uat_admin, Password: [valid], Domain: test.example.com | Dashboard page loads successfully. User sees the main navigation menu. Welcome message or dashboard widgets are displayed. | H |
| AUTH-002 | Authentication | Failed login with invalid password | User account exists | 1. Open the FusionPBX login page. 2. Enter a valid username. 3. Enter an incorrect password. 4. Click the Login button. | Username: uat_admin, Password: wrongpassword123 | Login fails. An error message "Username or password is incorrect" is displayed. User remains on the login page. No session is created. | H |
| AUTH-003 | Authentication | Failed login with non-existent user | None | 1. Open the FusionPBX login page. 2. Enter a username that does not exist. 3. Enter any password. 4. Click the Login button. | Username: nonexistent_user, Password: anypassword | Login fails. The same generic error message is shown (no user enumeration). User remains on the login page. | H |
| AUTH-004 | Authentication | Successful logout | User is logged in | 1. Log in as uat_admin. 2. Click the Logout link in the top navigation bar. | None | Session is terminated. User is redirected to the login page. Attempting to access a protected page redirects back to login. | H |
| AUTH-005 | Authentication | Session timeout enforcement | User is logged in; session timeout configured to a short value for testing | 1. Log in as uat_admin. 2. Note the current time. 3. Wait for the session timeout period to elapse without any activity. 4. Attempt to navigate to any page. | None | After the timeout period, the session expires. User is redirected to the login page with a session expired message. | H |
| AUTH-006 | Authentication | Two-factor authentication (TOTP) login | 2FA is enabled for the user account; user has TOTP authenticator configured | 1. Open the FusionPBX login page. 2. Enter valid username and password. 3. Click Login. 4. On the 2FA challenge page, enter the current TOTP code from the authenticator app. 5. Click Verify. | Username: uat_admin, Password: [valid], TOTP: [current code] | After entering the correct TOTP code, the dashboard loads successfully. A failed TOTP code shows an error and allows retry. | H |
| AUTH-007 | Authentication | Password change by user | User is logged in | 1. Log in as uat_user. 2. Navigate to Account Settings. 3. Click Change Password. 4. Enter the current password. 5. Enter a new password. 6. Confirm the new password. 7. Click Save. | Current password: [valid], New password: NewSecurePass123\! | Password is changed successfully. A success message is displayed. User can log out and log back in with the new password. | H |
| AUTH-008 | Authentication | Login attempt with empty credentials | None | 1. Open the FusionPBX login page. 2. Leave the username field empty. 3. Leave the password field empty. 4. Click the Login button. | Username: (empty), Password: (empty) | Login fails. Validation error is shown indicating required fields. User remains on the login page. | H |
| AUTH-009 | Authentication | CSRF protection on login form | None | 1. Open the FusionPBX login page. 2. Using browser developer tools, remove or modify the CSRF token hidden field. 3. Submit the login form with valid credentials. | Username: uat_admin, Password: [valid], Token: [tampered] | Login is rejected due to invalid CSRF token. An error message is displayed. | H |
| AUTH-010 | Authentication | Concurrent session handling | User is logged in on one browser | 1. Log in as uat_admin in Browser A. 2. Open a different browser (Browser B). 3. Log in as the same uat_admin user. 4. Verify behavior in both browsers. | Username: uat_admin (both browsers) | Both sessions are functional (or the previous session is invalidated, depending on policy). No data corruption occurs. | M |

### 4.2 Dashboard (DASH)

| TestCaseID | Category | Scenario | Prerequisites | Steps | InputData | ExpectedResult | Priority |
|------------|----------|----------|---------------|-------|-----------|----------------|----------|
| DASH-001 | Dashboard | Dashboard displays after login | User is logged in | 1. Log in as uat_admin. 2. Observe the dashboard page. | None | Dashboard loads within 3 seconds. Widgets are displayed (system status, voicemail, missed calls, etc.). Page renders without errors. | M |
| DASH-002 | Dashboard | Configure dashboard widgets | Logged in as admin | 1. Log in as uat_admin. 2. Navigate to Dashboard. 3. Click the dashboard configuration/edit button. 4. Add a new widget (e.g., System Status). 5. Save the configuration. 6. Return to the dashboard. | Widget: System Status, Position: Column 1 | The new widget appears on the dashboard in the configured position. Configuration is persisted across page refreshes. | M |
| DASH-003 | Dashboard | Remove a dashboard widget | Dashboard has at least 2 widgets configured | 1. Log in as uat_admin. 2. Navigate to Dashboard configuration. 3. Select a widget and remove it. 4. Save the configuration. 5. Return to the dashboard. | Remove widget: System Status | The removed widget no longer appears on the dashboard. Other widgets remain unaffected. | M |
| DASH-004 | Dashboard | Dashboard content varies by role | Three test accounts exist (superadmin, admin, user) | 1. Log in as uat_superadmin and note the visible dashboard widgets. 2. Log out. 3. Log in as uat_admin and note the visible widgets. 4. Log out. 5. Log in as uat_user and note the visible widgets. | None | Each role sees dashboard content appropriate to their permissions. Superadmin sees system-wide stats. Admin sees domain stats. User sees personal stats (voicemail, CDR). | M |
| DASH-005 | Dashboard | Dashboard auto-refresh | Dashboard is displayed | 1. Log in as uat_admin. 2. Navigate to the dashboard. 3. Wait for the auto-refresh interval (if configured). 4. Observe if widget data updates. | None | Dashboard widgets refresh their data without requiring a manual page reload. No JavaScript errors in browser console. | L |

### 4.3 User Management (USER)

| TestCaseID | Category | Scenario | Prerequisites | Steps | InputData | ExpectedResult | Priority |
|------------|----------|----------|---------------|-------|-----------|----------------|----------|
| USER-001 | User Management | Create a new user | Logged in as admin | 1. Log in as uat_admin. 2. Navigate to Users from the side menu. 3. Click the Add (+) button. 4. Enter the username. 5. Enter a password. 6. Enter the email address. 7. Select a group (e.g., user). 8. Click Save. | Username: testuser01, Password: TestPass123\!, Email: testuser01@test.example.com, Group: user | User is created successfully. Success message is displayed. The new user appears in the user list. | H |
| USER-002 | User Management | Edit an existing user | User testuser01 exists | 1. Log in as uat_admin. 2. Navigate to Users. 3. Click on testuser01 in the list. 4. Change the email address. 5. Click Save. | New email: updated@test.example.com | User email is updated. Success message is displayed. The updated email is visible in the user list. | H |
| USER-003 | User Management | Delete a user | User testuser01 exists | 1. Log in as uat_admin. 2. Navigate to Users. 3. Select the checkbox next to testuser01. 4. Click the Delete button. 5. Confirm the deletion. | None | User is deleted. Success message is displayed. The user no longer appears in the list. | H |
| USER-004 | User Management | Assign user to a group | User exists without group assignment | 1. Log in as uat_admin. 2. Navigate to Users. 3. Click on a user to edit. 4. In the Groups section, select "admin" from the group dropdown. 5. Click Add. 6. Click Save. | Group: admin | User is assigned to the admin group. The group appears in the user detail. The user gains admin-level permissions on next login. | H |
| USER-005 | User Management | Remove user from a group | User has group assignment | 1. Log in as uat_admin. 2. Navigate to Users. 3. Click on a user to edit. 4. In the Groups section, click the delete icon next to the group assignment. 5. Click Save. | None | User is removed from the group. The group no longer appears in user detail. Permissions are revoked on next login. | H |
| USER-006 | User Management | Create user with duplicate username | User with same username exists | 1. Log in as uat_admin. 2. Navigate to Users. 3. Click Add. 4. Enter a username that already exists. 5. Fill in other fields. 6. Click Save. | Username: uat_user (already exists) | Error message is displayed indicating the username is already taken. User is not created. | H |
| USER-007 | User Management | Bulk import users from CSV | CSV file prepared with user data | 1. Log in as uat_admin. 2. Navigate to Users. 3. Click Import. 4. Select the CSV file. 5. Map the columns to the appropriate fields. 6. Click Import. | CSV file with 3 test users | All users from the CSV are imported. Success message shows the count of imported users. Users appear in the list. | M |
| USER-008 | User Management | Admin cannot see users in other domains | Two domains with separate users | 1. Log in as uat_admin (domain: test.example.com). 2. Navigate to Users. 3. Review the user list. | None | Only users belonging to test.example.com are listed. Users from test2.example.com are not visible. | H |
| USER-009 | User Management | User account disable | User exists and is enabled | 1. Log in as uat_admin. 2. Navigate to Users. 3. Click on a user to edit. 4. Set Enabled to False. 5. Click Save. 6. Log out. 7. Attempt to log in as the disabled user. | Enabled: False | User is saved as disabled. When attempting to login as the disabled user, authentication fails with an appropriate message. | H |
| USER-010 | User Management | User changes own account settings | Logged in as end user | 1. Log in as uat_user. 2. Navigate to Account Settings. 3. Change the time zone setting. 4. Click Save. | Time Zone: America/New_York | Setting is saved successfully. Time zone is reflected in timestamps on subsequent pages. | M |

### 4.4 Domain Management (DOMAIN)

| TestCaseID | Category | Scenario | Prerequisites | Steps | InputData | ExpectedResult | Priority |
|------------|----------|----------|---------------|-------|-----------|----------------|----------|
| DOMAIN-001 | Domain Management | Create a new domain | Logged in as superadmin | 1. Log in as uat_superadmin. 2. Navigate to Domains. 3. Click Add. 4. Enter the domain name. 5. Enter a description. 6. Set Enabled to True. 7. Click Save. | Domain: test3.example.com, Description: UAT Test Domain 3, Enabled: True | Domain is created. Success message is displayed. Domain appears in the domain list. | H |
| DOMAIN-002 | Domain Management | Edit domain description | Domain exists | 1. Log in as uat_superadmin. 2. Navigate to Domains. 3. Click on test3.example.com. 4. Change the description. 5. Click Save. | Description: Updated UAT Domain | Domain description is updated. Success message displayed. | M |
| DOMAIN-003 | Domain Management | Disable a domain | Domain exists and is enabled | 1. Log in as uat_superadmin. 2. Navigate to Domains. 3. Click on test3.example.com. 4. Set Enabled to False. 5. Click Save. 6. Attempt to switch to the disabled domain. | Enabled: False | Domain is disabled. Users of that domain cannot log in. Superadmin can still manage it. | H |
| DOMAIN-004 | Domain Management | Configure domain settings | Domain exists | 1. Log in as uat_superadmin. 2. Navigate to Domain Settings for test.example.com. 3. Add a new setting (e.g., theme). 4. Click Save. | Category: theme, Subcategory: name, Value: dark | Setting is saved. The setting overrides the default setting for that domain only. Other domains are unaffected. | M |
| DOMAIN-005 | Domain Management | Admin cannot manage domains | Logged in as admin | 1. Log in as uat_admin. 2. Attempt to navigate to the Domains page directly via URL. | URL: /core/domains/domains.php | Access is denied. User is redirected or shown an access denied message. Domain management is not visible in the menu. | H |
### 4.5 Extensions (EXT)

| TestCaseID | Category | Scenario | Prerequisites | Steps | InputData | ExpectedResult | Priority |
|------------|----------|----------|---------------|-------|-----------|----------------|----------|
| EXT-001 | Extensions | Create a new extension | Logged in as admin | 1. Log in as uat_admin. 2. Navigate to Extensions from the side menu. 3. Click Add. 4. Enter the extension number. 5. Enter a password. 6. Enter the caller ID name. 7. Enter the caller ID number. 8. Set Enabled to True. 9. Click Save. | Extension: 1010, Password: ext1010pass, CallerID Name: Test Ext 1010, CallerID Number: 1010, Enabled: True | Extension is created. Success message is displayed. Extension appears in the list. FreeSWITCH reloads the XML configuration. | H |
| EXT-002 | Extensions | Edit extension caller ID | Extension 1010 exists | 1. Log in as uat_admin. 2. Navigate to Extensions. 3. Click on extension 1010. 4. Change the Caller ID Name. 5. Click Save. | CallerID Name: Updated Ext 1010 | Caller ID name is updated. Success message displayed. Change is reflected in the extension list. | H |
| EXT-003 | Extensions | Delete an extension | Extension 1010 exists | 1. Log in as uat_admin. 2. Navigate to Extensions. 3. Select the checkbox next to extension 1010. 4. Click Delete. 5. Confirm the deletion. | None | Extension is deleted. It no longer appears in the list. FreeSWITCH configuration is reloaded. | H |
| EXT-004 | Extensions | Set call forwarding on an extension | Extension exists | 1. Log in as uat_admin. 2. Navigate to Extensions. 3. Click on extension 1001. 4. In the Call Forward section, enable call forwarding. 5. Enter the forwarding destination. 6. Click Save. | Forward All Destination: 1002 | Call forwarding is enabled. When 1001 is called, the call forwards to 1002. | H |
| EXT-005 | Extensions | Enable Do Not Disturb on extension | Extension exists | 1. Log in as uat_admin. 2. Navigate to Extensions. 3. Click on extension 1001. 4. Enable Do Not Disturb. 5. Click Save. | DND: True | DND is enabled. Calls to extension 1001 are rejected or sent to voicemail. | H |
| EXT-006 | Extensions | Link extension to voicemail | Extension and voicemail box exist | 1. Log in as uat_admin. 2. Navigate to Extensions. 3. Click on extension 1001. 4. In the Voicemail section, enable voicemail. 5. Set voicemail ID to match the extension. 6. Click Save. | Voicemail Enabled: True, Voicemail ID: 1001 | Voicemail is linked. Unanswered calls to 1001 go to voicemail after the configured timeout. | H |
| EXT-007 | Extensions | Create extension with duplicate number | Extension 1001 exists | 1. Log in as uat_admin. 2. Navigate to Extensions. 3. Click Add. 4. Enter extension number 1001 (already exists). 5. Fill in other required fields. 6. Click Save. | Extension: 1001 | Error message indicates the extension number already exists. Extension is not created. | H |
| EXT-008 | Extensions | Assign extension to a user | Extension and user exist | 1. Log in as uat_admin. 2. Navigate to Extensions. 3. Click on extension 1001. 4. In the User section, select uat_user from the dropdown. 5. Click Save. | User: uat_user | Extension is linked to the user. The user can see their extension details in their account. | M |
| EXT-009 | Extensions | Disable an extension | Extension 1001 exists and is enabled | 1. Log in as uat_admin. 2. Navigate to Extensions. 3. Click on extension 1001. 4. Set Enabled to False. 5. Click Save. | Enabled: False | Extension is disabled. SIP registration for this extension is rejected. FreeSWITCH config is reloaded. | M |
| EXT-010 | Extensions | Extension with maximum-length fields | None | 1. Log in as uat_admin. 2. Navigate to Extensions. 3. Click Add. 4. Enter extension with maximum length caller ID name (64 characters). 5. Enter a description at maximum length. 6. Click Save. | CallerID Name: (64 char string), Description: (255 char string) | Extension is created with long field values. No truncation errors. Data is stored and displayed correctly. | L |

### 4.6 Dialplan Management (DIAL)

| TestCaseID | Category | Scenario | Prerequisites | Steps | InputData | ExpectedResult | Priority |
|------------|----------|----------|---------------|-------|-----------|----------------|----------|
| DIAL-001 | Dialplan | View dialplan entries | Dialplan entries exist | 1. Log in as uat_admin. 2. Navigate to Dialplan Manager. 3. Review the list of dialplan entries. | None | All dialplan entries for the domain are listed with name, context, and order. List is sorted by order. | H |
| DIAL-002 | Dialplan | Create an inbound route | Logged in as admin | 1. Log in as uat_admin. 2. Navigate to Inbound Routes. 3. Click Add. 4. Enter the destination number (DID). 5. Set the action to transfer to extension 1001. 6. Click Save. | DID: 5551234567, Action: Transfer to 1001 | Inbound route is created. Calls to 5551234567 are routed to extension 1001. Entry appears in the inbound route list. | H |
| DIAL-003 | Dialplan | Create an outbound route | Logged in as admin; gateway exists | 1. Log in as uat_admin. 2. Navigate to Outbound Routes. 3. Click Add. 4. Enter a name for the route. 5. Set the dialplan expression pattern. 6. Select the gateway. 7. Click Save. | Name: US Domestic, Pattern: ^1?(\d{10})$, Gateway: primary_gw | Outbound route is created. Calls matching the pattern are sent through the specified gateway. | H |
| DIAL-004 | Dialplan | Edit a dialplan entry | Dialplan entry exists | 1. Log in as uat_admin. 2. Navigate to Dialplan Manager. 3. Click on an existing entry. 4. Modify the order number. 5. Click Save. | Order: 500 (changed from original) | Dialplan order is updated. The entry moves to the new position in the sorted list. FreeSWITCH config is reloaded. | M |
| DIAL-005 | Dialplan | Delete a dialplan entry | Dialplan entry exists | 1. Log in as uat_admin. 2. Navigate to Dialplan Manager. 3. Select the checkbox next to an entry. 4. Click Delete. 5. Confirm the deletion. | None | Dialplan entry is removed. It no longer appears in the list. FreeSWITCH config is reloaded. | M |

### 4.7 Gateways (GW)

| TestCaseID | Category | Scenario | Prerequisites | Steps | InputData | ExpectedResult | Priority |
|------------|----------|----------|---------------|-------|-----------|----------------|----------|
| GW-001 | Gateways | Create a new gateway | Logged in as admin | 1. Log in as uat_admin. 2. Navigate to Gateways. 3. Click Add. 4. Enter the gateway name. 5. Enter the proxy address. 6. Enter username and password for SIP registration. 7. Select the SIP profile. 8. Set Register to True. 9. Click Save. | Gateway: test_gw, Proxy: sip.provider.com, Username: user123, Password: pass123, Profile: external, Register: True | Gateway is created. It appears in the gateway list. Registration attempt is initiated with the SIP provider. | H |
| GW-002 | Gateways | Edit gateway proxy address | Gateway exists | 1. Log in as uat_admin. 2. Navigate to Gateways. 3. Click on test_gw. 4. Change the proxy address. 5. Click Save. | Proxy: sip2.provider.com | Proxy is updated. FreeSWITCH SIP module is reloaded. Gateway re-registers with the new proxy. | H |
| GW-003 | Gateways | Check gateway registration status | Gateway is configured with registration | 1. Log in as uat_superadmin. 2. Navigate to SIP Status. 3. Look for the gateway name in the gateway status section. | None | Gateway registration status is displayed (REGED, NOREG, FAIL_WAIT, etc.). Status reflects the actual connection state. | M |
| GW-004 | Gateways | Delete a gateway | Gateway exists | 1. Log in as uat_admin. 2. Navigate to Gateways. 3. Select the checkbox next to the gateway. 4. Click Delete. 5. Confirm the deletion. | None | Gateway is deleted. It no longer appears in the list. SIP registration is terminated. | M |
| GW-005 | Gateways | Create gateway without required fields | None | 1. Log in as uat_admin. 2. Navigate to Gateways. 3. Click Add. 4. Leave the gateway name empty. 5. Click Save. | Gateway: (empty) | Validation error is displayed. Gateway is not created. Required fields are highlighted. | M |

### 4.8 IVR Menus (IVR)

| TestCaseID | Category | Scenario | Prerequisites | Steps | InputData | ExpectedResult | Priority |
|------------|----------|----------|---------------|-------|-----------|----------------|----------|
| IVR-001 | IVR | Create a new IVR menu | Logged in as admin; recording exists | 1. Log in as uat_admin. 2. Navigate to IVR Menus. 3. Click Add. 4. Enter the IVR name. 5. Enter the extension number. 6. Select the greeting recording. 7. Set the timeout. 8. Click Save. | Name: Main Menu, Extension: 5000, Greeting: welcome.wav, Timeout: 5 seconds | IVR menu is created. It appears in the IVR menu list with the configured extension. | M |
| IVR-002 | IVR | Add digit routing to IVR | IVR menu exists | 1. Log in as uat_admin. 2. Navigate to IVR Menus. 3. Click on Main Menu to edit. 4. Add a new option: Digit 1 routes to extension 1001. 5. Add a new option: Digit 2 routes to extension 1002. 6. Add a new option: Digit 0 routes to ring group. 7. Click Save. | Digit 1: transfer 1001, Digit 2: transfer 1002, Digit 0: transfer ring_group | Options are saved. When callers press the configured digits during the IVR, they are routed to the correct destinations. | M |
| IVR-003 | IVR | Set IVR greeting recording | IVR menu exists; audio file available | 1. Log in as uat_admin. 2. Navigate to IVR Menus. 3. Click on Main Menu to edit. 4. Change the Greet Long field to a different recording. 5. Change the Greet Short field. 6. Click Save. | Greet Long: new_greeting.wav, Greet Short: short_greeting.wav | Greeting is updated. Callers hear the new greeting when they reach the IVR. | M |
| IVR-004 | IVR | Configure IVR timeout action | IVR menu exists | 1. Log in as uat_admin. 2. Navigate to IVR Menus. 3. Click on Main Menu. 4. Set the timeout action (what happens when no digit is pressed). 5. Click Save. | Timeout action: Transfer to operator (ext 1001) | When a caller does not press any digit within the timeout period, they are transferred to extension 1001. | M |
| IVR-005 | IVR | Delete an IVR menu | IVR menu exists and is not referenced by active routes | 1. Log in as uat_admin. 2. Navigate to IVR Menus. 3. Select the checkbox next to a menu. 4. Click Delete. 5. Confirm the deletion. | None | IVR menu is deleted. It no longer appears in the list. | L |

### 4.9 Ring Groups (RG)

| TestCaseID | Category | Scenario | Prerequisites | Steps | InputData | ExpectedResult | Priority |
|------------|----------|----------|---------------|-------|-----------|----------------|----------|
| RG-001 | Ring Groups | Create a new ring group | Logged in as admin; extensions exist | 1. Log in as uat_admin. 2. Navigate to Ring Groups. 3. Click Add. 4. Enter the ring group name. 5. Enter the extension number. 6. Select the ring strategy (e.g., simultaneous). 7. Add member extensions (1001, 1002, 1003). 8. Click Save. | Name: Sales Team, Extension: 2001, Strategy: simultaneous, Members: 1001, 1002, 1003 | Ring group is created. It appears in the list. Calls to 2001 ring all three extensions simultaneously. | M |
| RG-002 | Ring Groups | Edit ring group strategy | Ring group exists | 1. Log in as uat_admin. 2. Navigate to Ring Groups. 3. Click on Sales Team. 4. Change the strategy from simultaneous to sequence. 5. Click Save. | Strategy: sequence | Strategy is updated. Calls now ring extensions one after another instead of simultaneously. | M |
| RG-003 | Ring Groups | Configure ring group timeout | Ring group exists | 1. Log in as uat_admin. 2. Navigate to Ring Groups. 3. Click on Sales Team. 4. Set the timeout action (e.g., transfer to voicemail). 5. Set the timeout duration. 6. Click Save. | Timeout: 30 seconds, Timeout Action: voicemail 1001 | If no member answers within 30 seconds, the call is transferred to voicemail for extension 1001. | M |
| RG-004 | Ring Groups | Add member to ring group | Ring group exists | 1. Log in as uat_admin. 2. Navigate to Ring Groups. 3. Click on Sales Team. 4. Add extension 1004 as a new member. 5. Click Save. | New member: 1004, Delay: 0, Timeout: 30 | Extension 1004 is added to the ring group. Calls to the group now include extension 1004. | M |
| RG-005 | Ring Groups | Delete a ring group | Ring group exists | 1. Log in as uat_admin. 2. Navigate to Ring Groups. 3. Select the checkbox next to Sales Team. 4. Click Delete. 5. Confirm. | None | Ring group is deleted. It no longer appears in the list. The extension number is freed. | L |
### 4.10 Call Center (CC)

| TestCaseID | Category | Scenario | Prerequisites | Steps | InputData | ExpectedResult | Priority |
|------------|----------|----------|---------------|-------|-----------|----------------|----------|
| CC-001 | Call Center | Create a call center queue | Logged in as admin | 1. Log in as uat_admin. 2. Navigate to Call Centers. 3. Click Add. 4. Enter the queue name. 5. Enter the queue extension. 6. Select the strategy (e.g., ring-all). 7. Select music on hold sound. 8. Click Save. | Name: Support Queue, Extension: 3001, Strategy: ring-all, MOH: default | Call center queue is created. It appears in the queue list. | M |
| CC-002 | Call Center | Add agent to queue | Queue and agents exist | 1. Log in as uat_admin. 2. Navigate to Call Centers. 3. Click on Support Queue. 4. In the Agents section, add an agent. 5. Set the tier level and position. 6. Click Save. | Agent: agent_1001, Tier Level: 1, Tier Position: 1 | Agent is added to the queue. Agent appears in the queue agent list with the correct tier. | M |
| CC-003 | Call Center | Configure queue timeout action | Queue exists | 1. Log in as uat_admin. 2. Navigate to Call Centers. 3. Click on Support Queue. 4. Set the max wait time. 5. Set the timeout action (e.g., transfer to voicemail). 6. Click Save. | Max Wait Time: 120 seconds, Timeout Action: transfer to voicemail 3001 | Queue is configured. Callers waiting more than 120 seconds are transferred to voicemail. | M |
| CC-004 | Call Center | View active call center status | Queue is active with calls or agents | 1. Log in as uat_admin. 2. Navigate to Call Center Active. 3. Review the real-time display. | None | Active queue status is displayed showing waiting callers, active agents, and their current state (Available, On Break, Logged Out). | M |
| CC-005 | Call Center | Remove agent from queue | Agent is assigned to queue | 1. Log in as uat_admin. 2. Navigate to Call Centers. 3. Click on Support Queue. 4. In the Agents section, remove an agent by deleting the tier. 5. Click Save. | None | Agent is removed from the queue. They no longer receive calls from this queue. | L |

### 4.11 Voicemail (VM)

| TestCaseID | Category | Scenario | Prerequisites | Steps | InputData | ExpectedResult | Priority |
|------------|----------|----------|---------------|-------|-----------|----------------|----------|
| VM-001 | Voicemail | Configure voicemail box | Logged in as admin; extension exists | 1. Log in as uat_admin. 2. Navigate to Voicemails. 3. Click Add or select an existing voicemail. 4. Enter the voicemail ID (matching extension number). 5. Set the voicemail password (PIN). 6. Enter the email address for notifications. 7. Click Save. | Voicemail ID: 1001, PIN: 1234, Email: user@test.example.com | Voicemail box is configured. PIN and email are saved. Voicemail is linked to the extension. | H |
| VM-002 | Voicemail | Upload voicemail greeting | Voicemail box exists | 1. Log in as uat_admin. 2. Navigate to Voicemail Greetings. 3. Select the voicemail box. 4. Click Upload or Record. 5. Select a WAV audio file. 6. Click Save. | Audio file: greeting.wav (WAV format, under 5MB) | Greeting is uploaded successfully. It is listed in the greetings for this voicemail box. | M |
| VM-003 | Voicemail | Listen to voicemail message | Voicemail box has at least 1 message | 1. Log in as uat_user. 2. Navigate to Voicemails (or dashboard voicemail widget). 3. Click on a voicemail message in the inbox. 4. Click the Play button. | None | Voicemail message plays in the browser audio player. Caller ID and timestamp are displayed. Message duration is shown. | H |
| VM-004 | Voicemail | Delete a voicemail message | Voicemail box has messages | 1. Log in as uat_user. 2. Navigate to Voicemails. 3. Select the checkbox next to a message. 4. Click Delete. 5. Confirm. | None | Message is deleted. It no longer appears in the voicemail inbox. | M |
| VM-005 | Voicemail | Configure voicemail-to-email | Voicemail box exists | 1. Log in as uat_admin. 2. Navigate to Voicemails. 3. Click on a voicemail box. 4. Enable the email notification option. 5. Enter the notification email address. 6. Choose whether to attach the audio file. 7. Click Save. | Email: user@test.example.com, Attach file: Yes | Settings are saved. When a new voicemail is received, an email notification is sent with the audio attachment. | M |

### 4.12 Recordings (REC)

| TestCaseID | Category | Scenario | Prerequisites | Steps | InputData | ExpectedResult | Priority |
|------------|----------|----------|---------------|-------|-----------|----------------|----------|
| REC-001 | Recordings | Upload a recording | Logged in as admin | 1. Log in as uat_admin. 2. Navigate to Recordings. 3. Click Add. 4. Enter a name for the recording. 5. Click the Upload button. 6. Select a WAV audio file from the local computer. 7. Click Save. | Name: Main Greeting, File: main_greeting.wav | Recording is uploaded and saved. It appears in the recordings list. The file can be played back in the browser. | M |
| REC-002 | Recordings | Play back a recording | Recording exists | 1. Log in as uat_admin. 2. Navigate to Recordings. 3. Click the play icon next to a recording. | None | Audio plays in the browser. Playback controls (play, pause, stop) work correctly. | M |
| REC-003 | Recordings | View call recordings | Call recordings exist | 1. Log in as uat_admin. 2. Navigate to Call Recordings. 3. Browse the list of recorded calls. 4. Click on a recording to play it. | None | Call recordings are listed with date, caller, callee, and duration. Playback works in the browser audio player. | M |

### 4.13 Fax (FAX)

| TestCaseID | Category | Scenario | Prerequisites | Steps | InputData | ExpectedResult | Priority |
|------------|----------|----------|---------------|-------|-----------|----------------|----------|
| FAX-001 | Fax | Send a fax | Fax extension configured; gateway available | 1. Log in as uat_admin. 2. Navigate to Fax. 3. Click on the fax extension. 4. Click Send Fax. 5. Enter the destination fax number. 6. Upload or select the document to fax. 7. Click Send. | Destination: 5559876543, Document: test_document.pdf | Fax is queued for sending. It appears in the Fax Queue with status Waiting or Sending. Upon completion, status updates to Sent or Failed. | M |
| FAX-002 | Fax | View received faxes | Fax extension configured; fax has been received | 1. Log in as uat_admin. 2. Navigate to Fax. 3. Click on the fax extension. 4. Browse the list of received faxes. 5. Click on a fax to view it. | None | Received faxes are listed with date, caller ID, and page count. Clicking on a fax opens the document (PDF/TIFF) for viewing or download. | M |
| FAX-003 | Fax | View fax queue status | Faxes have been queued | 1. Log in as uat_admin. 2. Navigate to Fax Queue. 3. Review the queue. | None | Fax queue shows all pending, in-progress, and completed fax jobs with status, retry count, and timestamps. | L |

### 4.14 Conferencing (CONF)

| TestCaseID | Category | Scenario | Prerequisites | Steps | InputData | ExpectedResult | Priority |
|------------|----------|----------|---------------|-------|-----------|----------------|----------|
| CONF-001 | Conferencing | Create a conference room | Logged in as admin | 1. Log in as uat_admin. 2. Navigate to Conferences or Conference Centers. 3. Click Add. 4. Enter the conference name. 5. Enter the extension number. 6. Set the moderator PIN. 7. Set the participant PIN. 8. Click Save. | Name: Team Standup, Extension: 4001, Moderator PIN: 9999, Participant PIN: 1111 | Conference room is created. It appears in the conference list. The extension is registered for dial-in. | M |
| CONF-002 | Conferencing | Configure conference PIN | Conference room exists | 1. Log in as uat_admin. 2. Navigate to Conference Centers. 3. Click on Team Standup. 4. Change the participant PIN. 5. Click Save. | Participant PIN: 2222 | PIN is updated. Participants must use the new PIN to join. Old PIN no longer works. | M |
| CONF-003 | Conferencing | View active conference participants | Conference is active with participants | 1. Log in as uat_admin. 2. Navigate to Active Conferences. 3. Click on the active conference room. 4. Review the participant list. | None | Active participants are listed with their caller ID, join time, and mute status. Moderator controls (mute, kick) are available. | M |

### 4.15 Devices (DEV)

| TestCaseID | Category | Scenario | Prerequisites | Steps | InputData | ExpectedResult | Priority |
|------------|----------|----------|---------------|-------|-----------|----------------|----------|
| DEV-001 | Devices | Register a new device | Logged in as admin | 1. Log in as uat_admin. 2. Navigate to Devices. 3. Click Add. 4. Enter the MAC address of the phone. 5. Select the device template (vendor/model). 6. Add a line assignment (extension, server, credentials). 7. Click Save. | MAC: 001122334455, Template: yealink/t46u, Line 1: Extension 1001 | Device is registered. It appears in the device list. Provisioning file is generated for the device. | M |
| DEV-002 | Devices | Edit device line assignment | Device exists | 1. Log in as uat_admin. 2. Navigate to Devices. 3. Click on the device. 4. Change the line 1 extension to a different extension. 5. Click Save. | Line 1: Extension 1002 (changed from 1001) | Line assignment is updated. The provisioning file is regenerated. The phone will pick up the new extension on next reboot. | M |
| DEV-003 | Devices | Provision a device | Device is registered; phone is on the network | 1. Log in as uat_admin. 2. Navigate to Devices. 3. Verify the device is listed. 4. Reboot or trigger provisioning on the physical/softphone device. 5. Verify the phone registers with the correct extension. | None | The phone requests its provisioning file from FusionPBX. The phone boots with the correct extension, display name, and server settings. SIP registration succeeds. | L |

### 4.16 Access Controls (ACL)

| TestCaseID | Category | Scenario | Prerequisites | Steps | InputData | ExpectedResult | Priority |
|------------|----------|----------|---------------|-------|-----------|----------------|----------|
| ACL-001 | Access Controls | View access control lists | Logged in as superadmin | 1. Log in as uat_superadmin. 2. Navigate to Access Controls. 3. Review the list of ACLs. | None | Access control lists are displayed (e.g., domains, lan, wan). Each ACL shows its default policy (allow/deny) and description. | L |
| ACL-002 | Access Controls | Add a node to an ACL | ACL exists | 1. Log in as uat_superadmin. 2. Navigate to Access Controls. 3. Click on an ACL (e.g., lan). 4. Add a new node with type Allow and CIDR. 5. Click Save. | Type: allow, CIDR: 10.0.0.0/8, Description: Internal network | Node is added to the ACL. FreeSWITCH ACL is reloaded. The IP range is now permitted. | L |
| ACL-003 | Access Controls | Delete an ACL node | ACL has nodes | 1. Log in as uat_superadmin. 2. Navigate to Access Controls. 3. Click on an ACL. 4. Select a node and delete it. 5. Click Save. | None | Node is removed from the ACL. FreeSWITCH ACL is reloaded. | L |

### 4.17 Call Detail Records (CDR)

| TestCaseID | Category | Scenario | Prerequisites | Steps | InputData | ExpectedResult | Priority |
|------------|----------|----------|---------------|-------|-----------|----------------|----------|
| CDR-001 | CDR | View call detail records | CDR data exists from test calls | 1. Log in as uat_admin. 2. Navigate to CDR (XML CDR). 3. Review the list of call records. | None | CDR list is displayed with columns: date/time, caller, destination, duration, and hangup cause. Records are sorted by date (newest first). | H |
| CDR-002 | CDR | Filter CDR by date range | CDR data exists | 1. Log in as uat_admin. 2. Navigate to CDR. 3. Set the start date filter. 4. Set the end date filter. 5. Click Search/Filter. | Start: 2026-02-01, End: 2026-02-22 | Only CDR records within the specified date range are displayed. Records outside the range are excluded. | M |
| CDR-003 | CDR | Export CDR to CSV | CDR data exists | 1. Log in as uat_admin. 2. Navigate to CDR. 3. Apply desired filters. 4. Click the Export or Download button. | None | A CSV file is downloaded containing the filtered CDR records with all fields (date, caller, destination, duration, hangup cause, etc.). | M |

### 4.18 System Administration (SYS)

| TestCaseID | Category | Scenario | Prerequisites | Steps | InputData | ExpectedResult | Priority |
|------------|----------|----------|---------------|-------|-----------|----------------|----------|
| SYS-001 | System | View system status | Logged in as superadmin | 1. Log in as uat_superadmin. 2. Navigate to System from the menu. 3. Review the system status page. | None | System status page displays CPU usage, RAM usage, disk space, and uptime. All values are current and reasonable. | L |
| SYS-002 | System | View switch status | Logged in as superadmin | 1. Log in as uat_superadmin. 2. Navigate to Switch from the menu. 3. Review the FreeSWITCH status. | None | Switch status displays FreeSWITCH version, uptime, current sessions, sessions per second, and memory usage. | L |
| SYS-003 | System | Enable/disable a module | Logged in as superadmin | 1. Log in as uat_superadmin. 2. Navigate to Modules. 3. Find a module (e.g., Call Broadcast). 4. Toggle its enabled status. 5. Click Save. | Module: Call Broadcast, Status: Toggle | Module status is changed. If disabled, the module is no longer accessible in the menu. If enabled, it reappears. | L |
| SYS-004 | System | View FreeSWITCH logs | Logged in as superadmin | 1. Log in as uat_superadmin. 2. Navigate to Log Viewer. 3. Review the log output. 4. Optionally filter by log level. | None | FreeSWITCH log entries are displayed in real-time or near-real-time. Log entries show timestamp, level, and message. | L |
| SYS-005 | System | Manage switch variables | Logged in as superadmin | 1. Log in as uat_superadmin. 2. Navigate to Variables. 3. Click on an existing variable. 4. Change its value. 5. Click Save. 6. Verify the change is applied. | Variable: default_language, Value: en | Variable is updated. The change is reflected in FreeSWITCH configuration after reloadxml. | L |

---

## 5. Test Case Summary

| Category | ID Range | Count | Priority Breakdown |
|----------|----------|-------|-------------------|
| Authentication | AUTH-001 to AUTH-010 | 10 | 9 High, 1 Medium |
| Dashboard | DASH-001 to DASH-005 | 5 | 4 Medium, 1 Low |
| User Management | USER-001 to USER-010 | 10 | 8 High, 2 Medium |
| Domain Management | DOMAIN-001 to DOMAIN-005 | 5 | 3 High, 2 Medium |
| Extensions | EXT-001 to EXT-010 | 10 | 7 High, 2 Medium, 1 Low |
| Dialplan | DIAL-001 to DIAL-005 | 5 | 2 High, 3 Medium |
| Gateways | GW-001 to GW-005 | 5 | 2 High, 3 Medium |
| IVR Menus | IVR-001 to IVR-005 | 5 | 4 Medium, 1 Low |
| Ring Groups | RG-001 to RG-005 | 5 | 4 Medium, 1 Low |
| Call Center | CC-001 to CC-005 | 5 | 4 Medium, 1 Low |
| Voicemail | VM-001 to VM-005 | 5 | 2 High, 3 Medium |
| Recordings | REC-001 to REC-003 | 3 | 3 Medium |
| Fax | FAX-001 to FAX-003 | 3 | 2 Medium, 1 Low |
| Conferencing | CONF-001 to CONF-003 | 3 | 3 Medium |
| Devices | DEV-001 to DEV-003 | 3 | 2 Medium, 1 Low |
| Access Controls | ACL-001 to ACL-003 | 3 | 3 Low |
| CDR | CDR-001 to CDR-003 | 3 | 1 High, 2 Medium |
| System Admin | SYS-001 to SYS-005 | 5 | 5 Low |
| **Total** | | **93** | **31 High, 42 Medium, 20 Low** |

---

## 6. Traceability Matrix

| Test Area | Feature List Ref | Screen List Ref | DB Schema Ref | API List Ref |
|-----------|-----------------|-----------------|---------------|--------------|
| Authentication | core/authentication | Screens 1-4 | v_users, v_user_logs | authentication class |
| Dashboard | core/dashboard | Screens 5-6 | v_dashboards, v_dashboard_widgets | dashboard_config_json.php |
| User Management | core/users, core/groups | Screens 11-18 | v_users, v_groups, v_user_groups, v_permissions | user_json.php |
| Domain Management | core/domains | Screens 19-23 | v_domains, v_domain_settings | domain_json.php |
| Extensions | app/extensions | Screens 28-30 | v_extensions, v_extension_users | extension_json.php, reloadxml |
| Dialplan | app/dialplans | Screens 31-34 | v_dialplans, v_dialplan_details | reloadxml |
| Gateways | app/gateways | Screens 37-38 | v_gateways | gateway_json.php, sofia status |
| IVR | app/ivr_menus | Screens 42-43 | v_ivr_menus, v_ivr_menu_options | reloadxml |
| Ring Groups | app/ring_groups | Screens 56-57 | v_ring_groups, v_ring_group_destinations | reloadxml |
| Call Center | app/call_centers | Screens 53-55 | v_call_center_queues, v_call_center_agents, v_call_center_tiers | reload mod_callcenter |
| Voicemail | app/voicemails | Screens 59-61 | v_voicemails, v_voicemail_messages, v_voicemail_greetings | voicemail_json.php |
| Recordings | app/recordings | Screens 69-70 | v_recordings, v_call_recordings | file upload |
| Fax | app/fax | Screens 62-64 | v_fax, v_fax_files, v_fax_queue | fax queue processing |
| Conferencing | app/conferences | Screens 46-52 | v_conference_centers, v_conference_rooms | conference ESL commands |
| Devices | app/devices | Screens 72-75 | v_devices, v_device_lines, v_device_keys | provisioning endpoint |
| Access Controls | app/access_controls | Screens 79-80 | v_access_controls, v_access_control_nodes | reloadacl |
| CDR | app/xml_cdr | Screens 66-67 | v_xml_cdr | xml_cdr_json.php |
| System Admin | app/system, app/switch | Screens 82-93 | v_software | show channels, status |
