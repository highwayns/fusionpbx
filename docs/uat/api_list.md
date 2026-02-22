# FusionPBX API & Integration Endpoint List

> Inventory of all JSON/AJAX endpoints, form processing patterns, internal PHP classes, and FreeSWITCH ESL integration points.
> Date: 2026-02-22 | Version: 1.0

---

## Summary

| Category | Count |
|----------|-------|
| JSON / AJAX Endpoints | 12 |
| Form Processing Patterns (POST/DELETE) | 18 |
| Internal PHP Service Classes | 14 |
| FreeSWITCH ESL Commands | 16 |
| **Total Integration Points** | **60** |

---

## 1. JSON / AJAX Endpoints

These endpoints return JSON data and are consumed by the FusionPBX web UI for dynamic content loading (search, autocomplete, dashboard widgets, list filtering).

| # | Endpoint | HTTP Method | Description | Auth Required | Roles |
|---|----------|-------------|-------------|---------------|-------|
| 1 | `/core/contacts/contact_json.php` | GET | Returns contacts as JSON for autocomplete and search widgets | Yes | SA, A, U |
| 2 | `/core/users/user_json.php` | GET | Returns user list as JSON for user selection dropdowns | Yes | SA, A |
| 3 | `/core/domains/domain_json.php` | GET | Returns domain list as JSON for domain switching | Yes | SA |
| 4 | `/core/dashboard/dashboard_config_json.php` | GET | Returns dashboard widget configuration for the current user | Yes | SA, A, U |
| 5 | `/app/extensions/extension_json.php` | GET | Returns extensions as JSON for extension pickers | Yes | SA, A |
| 6 | `/app/gateways/gateway_json.php` | GET | Returns gateway list as JSON | Yes | SA, A |
| 7 | `/app/calls_active/calls_active_json.php` | GET | Returns real-time active call data for live display | Yes | SA, A |
| 8 | `/app/call_center_active/call_center_active_json.php` | GET | Returns live call center queue and agent status | Yes | SA, A |
| 9 | `/app/conferences_active/conferences_active_json.php` | GET | Returns active conference participant data | Yes | SA, A |
| 10 | `/app/voicemails/voicemail_json.php` | GET | Returns voicemail messages as JSON for inbox display | Yes | SA, A, U |
| 11 | `/app/xml_cdr/xml_cdr_json.php` | GET | Returns CDR records as JSON for filtered list display | Yes | SA, A, U |
| 12 | `/app/registrations/registrations_json.php` | GET | Returns SIP registration data as JSON | Yes | SA, A |

### Common Query Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `search` | string | Free-text search filter |
| `order_by` | string | Column name to sort by |
| `order` | string | Sort direction: `asc` or `desc` |
| `limit` | int | Maximum number of results to return |
| `offset` | int | Pagination offset |
| `domain_uuid` | UUID | Filter by domain (superadmin only) |

---

## 2. Form Processing Patterns

FusionPBX uses a consistent pattern for form-based CRUD operations. Each module follows the `_edit.php` (POST for create/update) and list `.php` (POST/DELETE for bulk operations) convention.

### 2.1 Create / Update (POST to _edit.php)

| # | Endpoint | Entity | Key Fields | Description |
|---|----------|--------|------------|-------------|
| 1 | `POST /core/users/user_edit.php` | User | username, password, user_email, group_uuid | Create or update a user account |
| 2 | `POST /core/domains/domain_edit.php` | Domain | domain_name, domain_description, domain_enabled | Create or update a domain |
| 3 | `POST /core/groups/group_edit.php` | Group | group_name, group_description | Create or update a user group |
| 4 | `POST /core/contacts/contact_edit.php` | Contact | contact_name_given, contact_name_family, contact_organization | Create or update a contact |
| 5 | `POST /app/extensions/extension_edit.php` | Extension | extension, password, caller_id_name, caller_id_number | Create or update a SIP extension |
| 6 | `POST /app/gateways/gateway_edit.php` | Gateway | gateway, proxy, username, password, register, profile | Create or update a SIP gateway |
| 7 | `POST /app/dialplans/dialplan_edit.php` | Dialplan | dialplan_name, dialplan_context, dialplan_order | Create or update a dialplan entry |
| 8 | `POST /app/ivr_menus/ivr_menu_edit.php` | IVR Menu | ivr_menu_name, ivr_menu_greet_long, ivr_menu_options[] | Create or update an IVR menu |
| 9 | `POST /app/ring_groups/ring_group_edit.php` | Ring Group | ring_group_name, ring_group_extension, ring_group_strategy | Create or update a ring group |
| 10 | `POST /app/call_centers/call_center_edit.php` | Call Center Queue | queue_name, queue_strategy, queue_moh_sound | Create or update a call center queue |
| 11 | `POST /app/voicemails/voicemail_edit.php` | Voicemail | voicemail_id, voicemail_password, voicemail_mail_to | Create or update a voicemail box |
| 12 | `POST /app/conferences/conference_edit.php` | Conference | conference_name, conference_extension, conference_pin | Create or update a conference room |
| 13 | `POST /app/devices/device_edit.php` | Device | device_mac_address, device_template, device_lines[] | Create or update a provisioned device |
| 14 | `POST /app/fax/fax_edit.php` | Fax | fax_extension, fax_name, fax_email | Create or update a fax extension |
| 15 | `POST /app/destinations/destination_edit.php` | Destination | destination_number, destination_action | Create or update a destination |
| 16 | `POST /app/access_controls/access_control_edit.php` | ACL | access_control_name, access_control_default, nodes[] | Create or update an access control list |
| 17 | `POST /app/sip_profiles/sip_profile_edit.php` | SIP Profile | sip_profile_name, sip_profile_settings[] | Create or update a SIP profile |
| 18 | `POST /app/recordings/recording_edit.php` | Recording | recording_name, recording_filename (multipart upload) | Upload or update an audio recording |

### 2.2 Delete (POST with action=delete)

All list pages support bulk deletion via POST with the following pattern:

```
POST /app/{module}/{module}.php
Content-Type: application/x-www-form-urlencoded

action=delete&checked[]={uuid1}&checked[]={uuid2}
```

The `action` field determines the operation. Common values: `delete`, `toggle` (enable/disable).

### 2.3 CSRF Protection

All POST operations include a CSRF token:
- Token field name: `token`
- Token is generated per session and validated on every POST
- Missing or invalid tokens result in HTTP 403

---

## 3. Internal PHP Service Classes

These are the core PHP classes that form the FusionPBX internal API. They are used by all modules for database access, authentication, configuration, and inter-process communication.

| # | Class / File | Namespace / Path | Description | Key Methods |
|---|-------------|------------------|-------------|-------------|
| 1 | `database` | `resources/classes/database.php` | PDO-based database abstraction layer supporting PostgreSQL and SQLite | `select()`, `insert()`, `update()`, `delete()`, `execute()`, `find()` |
| 2 | `authentication` | `resources/classes/authentication.php` | Handles user authentication, session management, and login validation | `validate()`, `login()`, `logout()`, `get_domain()`, `totp_verify()` |
| 3 | `event_socket` | `resources/classes/event_socket.php` | FreeSWITCH Event Socket Layer (ESL) client for sending commands to FreeSWITCH | `connect()`, `send()`, `request()`, `api()`, `bgapi()`, `disconnect()` |
| 4 | `settings` | `resources/classes/settings.php` | Hierarchical settings manager (default -> domain -> user) | `get()`, `set()`, `reload()` |
| 5 | `permissions` | `resources/classes/permissions.php` | Role-based access control enforcement | `exists()`, `add()`, `delete()`, `groups()` |
| 6 | `cache` | `resources/classes/cache.php` | In-memory and file-based caching layer | `get()`, `set()`, `delete()`, `flush()` |
| 7 | `schema` | `resources/classes/schema.php` | Database schema migration and table management | `exec()`, `diff()`, `sql()` |
| 8 | `message` | `resources/classes/message.php` | User-facing flash message system (success, warning, error) | `add()`, `render()` |
| 9 | `template` | `resources/classes/template.php` | Email and notification template rendering engine | `render()`, `send()` |
| 10 | `text` | `resources/classes/text.php` | Internationalization (i18n) text translation | `get()`, `load()` |
| 11 | `domains` | `resources/classes/domains.php` | Domain management and domain-context resolution | `get()`, `count()`, `select()` |
| 12 | `users` | `resources/classes/users.php` | User management operations | `get()`, `count()`, `groups()` |
| 13 | `upload` | `resources/classes/upload.php` | Secure file upload handling with type validation | `process()`, `validate()`, `move()` |
| 14 | `csv` | `resources/classes/csv.php` | CSV import/export utility | `import()`, `export()`, `parse()` |

### Class Usage Pattern

```php
// Typical module pattern
require_once "resources/require.php";
require_once "resources/classes/database.php";

// Authentication check
$auth = new authentication;
if (!$auth->validate()) { header("Location: /login.php"); exit; }

// Database operations
$db = new database;
$rows = $db->select("SELECT * FROM v_extensions WHERE domain_uuid = :domain_uuid", [':domain_uuid' => $_SESSION['domain_uuid']]);

// FreeSWITCH command
$esl = new event_socket;
if ($esl->connect('127.0.0.1', '8021', 'ClueCon')) {
    $response = $esl->api("reloadxml");
}
```

---

## 4. FreeSWITCH ESL Integration Points

FusionPBX communicates with FreeSWITCH via the Event Socket Layer (ESL). The following ESL commands are used throughout the application.

### 4.1 Configuration & Reload Commands

| # | ESL Command | Trigger Context | Description |
|---|------------|-----------------|-------------|
| 1 | `reloadxml` | Dialplan/IVR/Extension save | Reloads the XML configuration (dialplans, directory, etc.) without restarting FreeSWITCH |
| 2 | `reload mod_sofia` | SIP profile change | Reloads the SIP module to apply profile changes |
| 3 | `reloadacl` | ACL edit | Reloads access control lists |
| 4 | `reload mod_callcenter` | Call center config change | Reloads the call center module configuration |

### 4.2 Real-Time Status Commands

| # | ESL Command | Used In | Description |
|---|------------|---------|-------------|
| 5 | `show channels` | Active Calls page | Returns all active call channels with caller/callee info |
| 6 | `show calls` | Active Calls page | Returns all active bridged calls |
| 7 | `show registrations` | Registrations page | Returns all currently registered SIP endpoints |
| 8 | `sofia status` | SIP Status page | Returns Sofia SIP stack status (profiles, gateways) |
| 9 | `sofia status profile {name}` | SIP Profile detail | Returns status of a specific SIP profile |
| 10 | `sofia status gateway {name}` | Gateway status | Returns registration status of a specific gateway |
| 11 | `status` | Switch Status page | Returns FreeSWITCH uptime, sessions, and version info |

### 4.3 Call Control Commands

| # | ESL Command | Used In | Description |
|---|------------|---------|-------------|
| 12 | `originate` | Click-to-Call, Call Broadcast | Initiates a new outbound call between two endpoints |
| 13 | `uuid_kill {uuid}` | Active Calls (hangup) | Terminates an active call by channel UUID |
| 14 | `uuid_transfer {uuid} {dest}` | Active Calls (transfer) | Transfers an active call to another destination |

### 4.4 Conference Commands

| # | ESL Command | Used In | Description |
|---|------------|---------|-------------|
| 15 | `conference {name} list` | Active Conferences | Lists all participants in a conference room |
| 16 | `conference {name} kick {member_id}` | Active Conferences (remove participant) | Removes a participant from a conference |

### 4.5 ESL Connection Configuration

| Parameter | Default Value | Setting Location |
|-----------|---------------|------------------|
| Host | `127.0.0.1` | Default Settings > Event Socket > Host |
| Port | `8021` | Default Settings > Event Socket > Port |
| Password | `ClueCon` | Default Settings > Event Socket > Password |
| Timeout | `5` seconds | Default Settings > Event Socket > Timeout |

---

## 5. Webhook / External Integration Points

| # | Integration | Endpoint / Method | Description |
|---|------------|-------------------|-------------|
| 1 | Provisioning HTTP | `GET /app/provision/?mac={mac}` | Auto-provisioning endpoint queried by IP phones on boot |
| 2 | Click-to-Call URL | `GET /app/click_to_call/click_to_call.php?src={ext}&dest={number}` | External URL-triggered call origination |
| 3 | Fax-to-Email | Internal (via FreeSWITCH) | Inbound fax received by FreeSWITCH is emailed to configured address |
| 4 | Email-to-Fax | Internal (email queue) | Outbound fax sent via email queue processing |
| 5 | Voicemail-to-Email | Internal (via FreeSWITCH) | Voicemail message notification with audio attachment |
| 6 | Azure Integration | `/app/azure/azure.php` | Microsoft Azure cloud integration hooks |

---

## 6. Security Considerations

| Concern | Implementation |
|---------|---------------|
| Authentication | All endpoints (except login and provisioning) require an active PHP session |
| CSRF Protection | Token-based CSRF protection on all POST forms |
| SQL Injection | Parameterized queries via the `database` class PDO layer |
| XSS Prevention | Output encoding in templates; Content-Security-Policy headers |
| Session Management | PHP session with configurable timeout; optional 2FA via TOTP |
| ESL Security | ESL connection is localhost-only by default; password-protected |
| File Upload | Type validation, size limits, and secure storage path |
| ACL Enforcement | IP-based access control for SIP and provisioning endpoints |
