# FusionPBX Screen / Page List

> Comprehensive inventory of all web UI screens and pages.
> Date: 2026-02-22 | Version: 1.0

---

## Summary

| Category | Screen Count |
|----------|-------------|
| Authentication | 4 |
| Core / Dashboard | 6 |
| User & Group Management | 8 |
| Domain Management | 5 |
| Contacts | 4 |
| Call Management & Routing | 14 |
| IVR & Auto Attendant | 4 |
| Conferencing | 7 |
| Call Center & Queues | 6 |
| Voicemail & Fax | 6 |
| Call Monitoring & Reporting | 7 |
| Devices & Provisioning | 4 |
| SIP & Network | 6 |
| Admin & System | 12 |
| **Total** | **93** |

### Role Legend

| Abbreviation | Role |
|-------------|------|
| SA | Superadmin (global access across all domains) |
| A | Admin (domain-level administrator) |
| U | User (standard end-user) |

---

## 1. Authentication

| # | Screen Name | URL Path | Description | Roles |
|---|-------------|----------|-------------|-------|
| 1 | Login | `/core/authentication/login.php` | User login form with username, password, and optional domain selector | Public |
| 2 | Logout | `/core/authentication/logout.php` | Session termination and redirect to login | SA, A, U |
| 3 | Password Recovery | `/core/authentication/password_reset.php` | Self-service password reset via email | Public |
| 4 | Two-Factor Authentication | `/core/authentication/totp.php` | TOTP-based two-factor authentication challenge | SA, A, U |

---

## 2. Core / Dashboard

| # | Screen Name | URL Path | Description | Roles |
|---|-------------|----------|-------------|-------|
| 5 | Dashboard | `/core/dashboard/dashboard.php` | Main dashboard with configurable widgets (call stats, system info, voicemail) | SA, A, U |
| 6 | Dashboard Widget Config | `/core/dashboard/dashboard_edit.php` | Add, remove, and arrange dashboard widgets | SA, A |
| 7 | Default Settings | `/core/default_settings/default_settings.php` | Global system default settings list | SA |
| 8 | Default Setting Edit | `/core/default_settings/default_setting_edit.php` | Edit a specific default setting value | SA |
| 9 | Email Templates | `/core/email_templates/email_templates.php` | List all email templates | SA, A |
| 10 | Email Template Edit | `/core/email_templates/email_template_edit.php` | Create or edit an email template | SA, A |

---

## 3. User & Group Management

| # | Screen Name | URL Path | Description | Roles |
|---|-------------|----------|-------------|-------|
| 11 | User List | `/core/users/users.php` | List all users in the current domain | SA, A |
| 12 | User Edit | `/core/users/user_edit.php` | Create or edit a user account (username, password, groups, settings) | SA, A |
| 13 | User Import | `/core/users/user_import.php` | Bulk import users from CSV | SA, A |
| 14 | Account Settings | `/core/user_settings/user_dashboard.php` | Current user's own account settings (password, timezone, language) | SA, A, U |
| 15 | Group List | `/core/groups/groups.php` | List all groups (superadmin, admin, user, agent, etc.) | SA, A |
| 16 | Group Edit | `/core/groups/group_edit.php` | Create or edit a group and its members | SA, A |
| 17 | Permission List | `/core/permissions/permissions.php` | View and manage application permissions by group | SA |
| 18 | User Logs | `/core/user_logs/user_logs.php` | User activity and authentication log viewer | SA, A |

---

## 4. Domain Management

| # | Screen Name | URL Path | Description | Roles |
|---|-------------|----------|-------------|-------|
| 19 | Domain List | `/core/domains/domains.php` | List all domains in a multi-tenant deployment | SA |
| 20 | Domain Edit | `/core/domains/domain_edit.php` | Create or edit a domain (name, description, enabled flag) | SA |
| 21 | Domain Settings | `/core/domain_settings/domain_settings.php` | List domain-level settings overrides | SA, A |
| 22 | Domain Setting Edit | `/core/domain_settings/domain_setting_edit.php` | Edit a domain-level setting | SA, A |
| 23 | Domain Limits | `/app/domain_limits/domain_limits.php` | Configure per-domain resource limits (extensions, devices, etc.) | SA |

---

## 5. Contacts

| # | Screen Name | URL Path | Description | Roles |
|---|-------------|----------|-------------|-------|
| 24 | Contact List | `/core/contacts/contacts.php` | Searchable list of all contacts | SA, A, U |
| 25 | Contact Edit | `/core/contacts/contact_edit.php` | Create or edit contact (phones, emails, addresses, notes, URLs) | SA, A, U |
| 26 | Contact Import | `/core/contacts/contact_import.php` | Bulk import contacts from CSV | SA, A |
| 27 | Contact Export | `/core/contacts/contact_export.php` | Export contacts to CSV | SA, A |

---

## 6. Call Management & Routing

| # | Screen Name | URL Path | Description | Roles |
|---|-------------|----------|-------------|-------|
| 28 | Extension List | `/app/extensions/extensions.php` | List all SIP extensions in the domain | SA, A |
| 29 | Extension Edit | `/app/extensions/extension_edit.php` | Create or edit an extension (number, password, caller ID, call forward, voicemail) | SA, A |
| 30 | Extension Settings | `/app/extension_settings/extension_settings.php` | Per-extension advanced settings | SA, A |
| 31 | Dialplan Manager | `/app/dialplans/dialplans.php` | List all dialplan entries with context and order | SA, A |
| 32 | Dialplan Edit | `/app/dialplans/dialplan_edit.php` | Create or edit a dialplan with conditions and actions | SA, A |
| 33 | Inbound Routes | `/app/dialplan_inbound/dialplan_inbound.php` | List inbound routing rules | SA, A |
| 34 | Outbound Routes | `/app/dialplan_outbound/dialplan_outbound.php` | List outbound routing rules | SA, A |
| 35 | Destinations | `/app/destinations/destinations.php` | List external destination numbers | SA, A |
| 36 | Destination Edit | `/app/destinations/destination_edit.php` | Create or edit a destination number | SA, A |
| 37 | Gateway List | `/app/gateways/gateways.php` | List SIP gateways / trunk providers | SA, A |
| 38 | Gateway Edit | `/app/gateways/gateway_edit.php` | Create or edit a SIP gateway (server, credentials, codecs) | SA, A |
| 39 | Call Flows | `/app/call_flows/call_flows.php` | List toggle-based call flows (day/night mode) | SA, A |
| 40 | Call Flow Edit | `/app/call_flows/call_flow_edit.php` | Create or edit a call flow | SA, A |
| 41 | Call Block | `/app/call_block/call_block.php` | Manage blocked caller ID numbers | SA, A, U |

---

## 7. IVR & Auto Attendant

| # | Screen Name | URL Path | Description | Roles |
|---|-------------|----------|-------------|-------|
| 42 | IVR Menu List | `/app/ivr_menus/ivr_menus.php` | List all IVR menus | SA, A |
| 43 | IVR Menu Edit | `/app/ivr_menus/ivr_menu_edit.php` | Create or edit an IVR menu (greetings, digit actions, timeouts) | SA, A |
| 44 | Phrases | `/app/phrases/phrases.php` | List phrase macros for IVR prompts | SA, A |
| 45 | Phrase Edit | `/app/phrases/phrase_edit.php` | Create or edit a phrase | SA, A |

---

## 8. Conferencing

| # | Screen Name | URL Path | Description | Roles |
|---|-------------|----------|-------------|-------|
| 46 | Conference Centers | `/app/conference_centers/conference_centers.php` | List conference center rooms | SA, A |
| 47 | Conference Center Edit | `/app/conference_centers/conference_center_edit.php` | Create or edit a conference center | SA, A |
| 48 | Conferences | `/app/conferences/conferences.php` | List conference rooms | SA, A |
| 49 | Conference Edit | `/app/conferences/conference_edit.php` | Create or edit a conference room (name, PIN, profile) | SA, A |
| 50 | Active Conferences | `/app/conferences_active/conferences_active.php` | Real-time view of active conferences and participants | SA, A |
| 51 | Conference Controls | `/app/conference_controls/conference_controls.php` | Manage conference DTMF control mappings | SA |
| 52 | Conference Profiles | `/app/conference_profiles/conference_profiles.php` | Manage conference parameter profiles | SA |

---

## 9. Call Center & Queues

| # | Screen Name | URL Path | Description | Roles |
|---|-------------|----------|-------------|-------|
| 53 | Call Center Queues | `/app/call_centers/call_centers.php` | List call center queues | SA, A |
| 54 | Call Center Queue Edit | `/app/call_centers/call_center_edit.php` | Create or edit a queue (strategy, timeout, agents, tiers) | SA, A |
| 55 | Call Center Active | `/app/call_center_active/call_center_active.php` | Real-time view of active calls and agent status | SA, A |
| 56 | Ring Groups | `/app/ring_groups/ring_groups.php` | List ring groups | SA, A |
| 57 | Ring Group Edit | `/app/ring_groups/ring_group_edit.php` | Create or edit a ring group (strategy, destinations, timeouts) | SA, A |
| 58 | FIFO Queues | `/app/fifo/fifo.php` | List FIFO-based waiting queues | SA, A |

---

## 10. Voicemail & Fax

| # | Screen Name | URL Path | Description | Roles |
|---|-------------|----------|-------------|-------|
| 59 | Voicemail List | `/app/voicemails/voicemails.php` | List voicemail boxes in the domain | SA, A |
| 60 | Voicemail Edit | `/app/voicemails/voicemail_edit.php` | Configure a voicemail box (PIN, greeting, email notification) | SA, A, U |
| 61 | Voicemail Greetings | `/app/voicemail_greetings/voicemail_greetings.php` | Manage voicemail greeting recordings | SA, A, U |
| 62 | Fax Server | `/app/fax/fax.php` | List fax extensions and configuration | SA, A |
| 63 | Fax Edit | `/app/fax/fax_edit.php` | Create or edit a fax extension | SA, A |
| 64 | Fax Queue | `/app/fax_queue/fax_queue.php` | View outbound fax queue status | SA, A |

---

## 11. Call Monitoring & Reporting

| # | Screen Name | URL Path | Description | Roles |
|---|-------------|----------|-------------|-------|
| 65 | Active Calls | `/app/calls_active/calls_active.php` | Real-time view of active channels on the system | SA, A |
| 66 | CDR (Call Detail Records) | `/app/xml_cdr/xml_cdr.php` | Search, filter, and export call detail records | SA, A, U |
| 67 | CDR View | `/app/xml_cdr/xml_cdr_edit.php` | Detailed view of a single CDR with call timeline | SA, A, U |
| 68 | Call Recordings | `/app/call_recordings/call_recordings.php` | List and playback call recordings | SA, A |
| 69 | Recordings (Media) | `/app/recordings/recordings.php` | Manage audio recordings (IVR greetings, MOH, prompts) | SA, A |
| 70 | Recording Edit | `/app/recordings/recording_edit.php` | Upload or record a new audio file | SA, A |
| 71 | Operator Panel | `/app/basic_operator_panel/basic_operator_panel.php` | Visual extension status panel for receptionist use | SA, A, U |

---

## 12. Devices & Provisioning

| # | Screen Name | URL Path | Description | Roles |
|---|-------------|----------|-------------|-------|
| 72 | Device List | `/app/devices/devices.php` | List provisioned devices (phones) | SA, A |
| 73 | Device Edit | `/app/devices/device_edit.php` | Create or edit a device (MAC, template, lines, keys) | SA, A |
| 74 | Device Profiles | `/app/devices/device_profile_edit.php` | Manage device provisioning profiles | SA, A |
| 75 | Provision | `/app/provision/provision.php` | Provisioning template management | SA |

---

## 13. SIP & Network

| # | Screen Name | URL Path | Description | Roles |
|---|-------------|----------|-------------|-------|
| 76 | SIP Profiles | `/app/sip_profiles/sip_profiles.php` | List SIP profiles (internal, external) | SA |
| 77 | SIP Profile Edit | `/app/sip_profiles/sip_profile_edit.php` | Edit SIP profile parameters | SA |
| 78 | SIP Status | `/app/sip_status/sip_status.php` | Display Sofia/SIP stack status and registration info | SA |
| 79 | Access Controls | `/app/access_controls/access_controls.php` | Manage IP-based access control lists | SA |
| 80 | Access Control Edit | `/app/access_controls/access_control_edit.php` | Create or edit ACL rules (allow/deny CIDR) | SA |
| 81 | Registrations | `/app/registrations/registrations.php` | View active SIP endpoint registrations | SA, A |

---

## 14. Admin & System

| # | Screen Name | URL Path | Description | Roles |
|---|-------------|----------|-------------|-------|
| 82 | System Status | `/app/system/system.php` | CPU, RAM, disk, and process information | SA |
| 83 | Switch Status | `/app/switch/switch.php` | FreeSWITCH version, uptime, channels, and memory | SA |
| 84 | Modules | `/app/modules/modules.php` | Enable or disable FreeSWITCH and FusionPBX modules | SA |
| 85 | Variables | `/app/vars/vars.php` | View and edit switch variables | SA |
| 86 | Variable Edit | `/app/vars/var_edit.php` | Create or edit a switch variable | SA |
| 87 | Menu Manager | `/core/menu/menu.php` | Manage navigation menu structure | SA |
| 88 | Menu Edit | `/core/menu/menu_edit.php` | Create or edit a menu item | SA |
| 89 | Log Viewer | `/app/log_viewer/log_viewer.php` | Browse FreeSWITCH console/file logs | SA |
| 90 | Music on Hold | `/app/music_on_hold/music_on_hold.php` | Manage music-on-hold files and streams | SA, A |
| 91 | Streams | `/app/streams/streams.php` | Manage audio streams | SA |
| 92 | Upgrade | `/core/upgrade/upgrade.php` | Schema upgrades, menu defaults, permission defaults | SA |
| 93 | Database Transactions | `/app/database_transactions/database_transactions.php` | View database transaction audit log | SA |

---

## Navigation Notes

- All URL paths are relative to the FusionPBX installation root (e.g., `https://pbx.example.com/`).
- Screens marked **SA** are visible only when logged in as a superadmin user.
- Screens marked **A** are visible to domain administrators.
- Screens marked **U** are visible to standard end-users.
- Role visibility is controlled by the permission system (`core/permissions`) and group membership (`core/groups`).
- The menu structure can be customized per domain via the Menu Manager.
