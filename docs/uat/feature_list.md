# FusionPBX Feature & Module List

> Auto-generated codebase analysis of FusionPBX modules.
> Date: 2026-02-22

---

## Summary

| Area | Module Count |
|------|-------------|
| **app/** (Application Modules) | 74 |
| **core/** (Core System Modules) | 20 |
| **Total** | **94** |

---

## Core Modules (`core/`)

Core modules provide the foundational infrastructure that all application modules depend on.

| # | Directory | Module Name | Description | Category |
|---|-----------|-------------|-------------|----------|
| 1 | `authentication` | Authentication | Provides an authentication framework with plugins to check if a user is authorized to login. | Core |
| 2 | `contacts` | Contacts | Provides a place to store contact information for individuals and organizations. | CRM |
| 3 | `dashboard` | Dashboard | System dashboard. | System |
| 4 | `databases` | Databases | Stored database connection information. | Core |
| 5 | `default_settings` | Default Settings | Default settings that apply to all domains. | Core |
| 6 | `domain_settings` | Domain Settings | Settings assigned to a particular domain. | Core |
| 7 | `domains` | Domains | Manage a single domain or multiple domains for multi-tenant. | Core |
| 8 | `email_templates` | Email Templates | Email template management. | Core |
| 9 | `events` | Events | Event handling subsystem. | Core |
| 10 | `groups` | Group Manager | Manage user groups and permissions. | Core |
| 11 | `install` | Install | Install the FusionPBX system or add new switches. | Core |
| 12 | `menu` | Menu Manager | The menu can be customized using this tool. | Core |
| 13 | `notifications` | Notifications | Configure notification preferences. | Switch |
| 14 | `permissions` | Permissions | Permission management. | Core |
| 15 | `software` | Software | Software management. | Core |
| 16 | `upgrade` | Upgrade | Update or restore various system settings. | Core |
| 17 | `user_logs` | User Logs | User activity logging. | System |
| 18 | `user_settings` | Account Settings | User account settings can be changed by the user. | Switch |
| 19 | `users` | User Manager | Add, edit, delete, and search for users. | Core |
| 20 | `websockets` | WebSockets | WebSocket subsystem. | Core |

---

## Application Modules (`app/`)

### Call Management & Routing

| # | Directory | Module Name | Description |
|---|-----------|-------------|-------------|
| 1 | `extensions` | Extensions | Used to configure SIP extensions. |
| 2 | `extension_settings` | Extension Settings | Settings for individual extensions. |
| 3 | `dialplans` | Dialplan Manager | Setup call destinations based on conditions and context. Send calls to gateways, auto attendants, external numbers, scripts, or any destination. |
| 4 | `dialplan_inbound` | Inbound Routes | Route incoming calls to destinations based on one or more conditions and context. |
| 5 | `dialplan_outbound` | Outbound Routes | Route outgoing calls to gateways when conditions are matched. |
| 6 | `destinations` | Destinations | Used to define external destination numbers. |
| 7 | `gateways` | Gateways | Provide access into other voice networks. These can be voice providers or other systems that require SIP registration. |
| 8 | `bridges` | Bridges | Bridge connections between endpoints. |
| 9 | `call_flows` | Call Flows | Direct calls between two destinations by calling a feature code. |
| 10 | `call_forward` | Call Forward | Call Forward, Follow Me, and Do Not Disturb. |
| 11 | `follow_me` | Follow Me | Define alternate inbound call handling for extensions. |
| 12 | `time_conditions` | Time Conditions | Direct calls based on the time of day. |
| 13 | `number_translations` | Number Translation | Manage mod_translation. |
| 14 | `call_block` | Call Block | A tool to block incoming numbers. |

### IVR & Auto Attendant

| # | Directory | Module Name | Description |
|---|-----------|-------------|-------------|
| 1 | `ivr_menus` | IVR Menus | Plays a recording or phrase that presents the caller with options. Destinations can be extensions, voicemail, IVR menus, hunt groups, FAX extensions, and more. |
| 2 | `phrases` | Phrases | Manage phrases primarily used with an IVR. |
| 3 | `recordings` | Recordings | Manage recordings primarily used with an IVR. |

### Conferencing

| # | Directory | Module Name | Description |
|---|-----------|-------------|-------------|
| 1 | `conference_centers` | Conference Center | One or more audio and video conference rooms. |
| 2 | `conferences` | Conferences | Setup conference rooms with a name, description, and optional PIN number. |
| 3 | `conferences_active` | Conferences Active | AJAX tool to view and manage all active callers in a conference room. |
| 4 | `active_conferences` | Conferences Active | Real-time active conference viewer and moderator tool. |
| 5 | `conference_controls` | Conference Controls | Assign digits to actions (mute, unmute, etc.) during a conference call. |
| 6 | `conference_profiles` | Conference Profiles | A group of conference parameters saved together as a profile. |

### Call Center & Queues

| # | Directory | Module Name | Description |
|---|-----------|-------------|-------------|
| 1 | `call_centers` | Call Center | Queues for managing inbound calls and routing to available agents. |
| 2 | `call_center_active` | Call Center Active | Shows active calls and agents in the call center queue. |
| 3 | `fifo` | FIFO | Queues (FIFO) for waiting lines for callers. |
| 4 | `fifo_list` | FIFO List | List all queues currently active with one or more callers. |
| 5 | `ring_groups` | Ring Groups | A tool to call multiple extensions simultaneously. |

### Voicemail & Fax

| # | Directory | Module Name | Description |
|---|-----------|-------------|-------------|
| 1 | `voicemails` | Voicemail | Manage voicemail mailboxes. |
| 2 | `voicemail_greetings` | Voicemail Greetings | Manage voicemail greetings for extensions. |
| 3 | `fax` | Fax | Receive FAX by setting up a fax extension. Direct incoming FAX with a dedicated number or detect the FAX tone. |
| 4 | `fax_queue` | FAX Queue | FAX queuing system. |

### Call Monitoring & Reporting

| # | Directory | Module Name | Description |
|---|-----------|-------------|-------------|
| 1 | `active_calls` | Active Calls | Realtime view of active calls. |
| 2 | `calls_active` | Active Calls | Active channels on the system. |
| 3 | `xml_cdr` | XML CDR | Call Detail Records with all information about the call. |
| 4 | `call_recordings` | Call Recordings | Call recording management. |
| 5 | `call_broadcast` | Call Broadcast | Schedule to immediately make multiple calls to extensions, IVR Menus, Conference Rooms, or any other number. |
| 6 | `basic_operator_panel` | Operator Panel | Operator panel shows the status. |
| 7 | `click_to_call` | Click to Call | Originate calls with a URL. |

### Phone Provisioning - Vendor Modules

| # | Directory | Module Name | Vendor |
|---|-----------|-------------|--------|
| 1 | `aastra` | Aastra | Aastra |
| 2 | `algo` | Algo | Algo |
| 3 | `avaya` | Avaya | Avaya |
| 4 | `cisco` | Cisco | Cisco |
| 5 | `fanvil` | Fanvil | Fanvil |
| 6 | `flyingvoice` | Flyingvoice | Flyingvoice |
| 7 | `grandstream` | Grandstream | Grandstream |
| 8 | `htek` | Htek | Htek |
| 9 | `poly` | Poly | Poly |
| 10 | `polycom` | Polycom | Polycom |
| 11 | `snom` | Snom | Snom |
| 12 | `swissvoice` | Swissvoice | Swissvoice |
| 13 | `yealink` | Yealink | Yealink |

### Provisioning & Devices

| # | Directory | Module Name | Description |
|---|-----------|-------------|-------------|
| 1 | `provision` | Provision | Writes provisioning files from templates. |
| 2 | `devices` | Devices | Devices for provisioning. |

### Switch & System Administration

| # | Directory | Module Name | Description |
|---|-----------|-------------|-------------|
| 1 | `switch` | Switch | Switch details such as version, uptime, channels, and registrations. |
| 2 | `system` | System | Displays information for CPU, HDD, RAM, and more. |
| 3 | `modules` | Modules | Modules extend the features of the system. Enable or disable modules. |
| 4 | `vars` | Variables | Define variables used by the switch, provisioning, and more. |
| 5 | `sip_profiles` | SIP Profiles | Manage settings for the SIP profiles. |
| 6 | `sip_status` | SIP Status | Displays system information such as RAM, CPU, and Hard Drive information. |
| 7 | `sofia_global_settings` | Sofia Global Settings | Global SIP (Sofia) settings. |
| 8 | `registrations` | Registrations | Displays registrations from endpoints. |
| 9 | `log_viewer` | Log Viewer | Display the switch logs. |
| 10 | `access_controls` | Access Controls | Manage access control lists. |
| 11 | `streams` | Streams | Audio stream management. |
| 12 | `tones` | Tones | Manage tones. |
| 13 | `music_on_hold` | Music on Hold | Add, delete, or play music on hold files. |
| 14 | `pin_numbers` | PIN Numbers | Manage PIN numbers and account codes. |
| 15 | `domain_limits` | Domain Limits | Domain-level limit configuration. |
| 16 | `email_queue` | Email Queue | Email queuing system. |
| 17 | `database_transactions` | Database Transactions | Track database transactions. |
| 18 | `emergency` | Emergency Logs | Emergency call logging. |
| 19 | `event_guard` | Event Guard Logs | Event guard logging. |

### Cloud & Integration

| # | Directory | Module Name | Description |
|---|-----------|-------------|-------------|
| 1 | `azure` | Azure | Azure cloud integration. |

---

## Feature Categories Overview

| Category | Count | Examples |
|----------|-------|---------|
| Call Management & Routing | 14 | Extensions, Dialplans, Inbound/Outbound Routes, Gateways |
| IVR & Auto Attendant | 3 | IVR Menus, Phrases, Recordings |
| Conferencing | 6 | Conference Centers, Active Conferences, Controls, Profiles |
| Call Center & Queues | 5 | Call Center, FIFO Queues, Ring Groups |
| Voicemail & Fax | 4 | Voicemail, Voicemail Greetings, Fax, Fax Queue |
| Call Monitoring & Reporting | 7 | Active Calls, CDR, Call Recordings, Operator Panel |
| Phone Provisioning (Vendors) | 13 | Aastra, Cisco, Grandstream, Polycom, Yealink, etc. |
| Provisioning & Devices | 2 | Provision, Devices |
| Switch & System Administration | 19 | Switch, System, Modules, SIP Profiles, Logs, ACLs |
| Cloud & Integration | 1 | Azure |
| Core System | 20 | Authentication, Users, Groups, Domains, Dashboard |
| **Total** | **94** | |
