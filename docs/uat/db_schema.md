# FusionPBX Database Schema Reference

> Complete database table inventory organized by functional category.
> Date: 2026-02-22 | Version: 1.0

---

## Summary

| Category | Table Count |
|----------|------------|
| Core System | 18 |
| Contacts | 10 |
| Dashboard | 2 |
| Extensions and Call Routing | 14 |
| Queuing (Call Center and Ring Groups) | 6 |
| Voice and Media | 10 |
| Fax | 4 |
| Devices and Provisioning | 5 |
| SIP and Network | 6 |
| CDR and Logging | 4 |
| FreeSWITCH Core Tables | 8 |
| **Total** | **87** |

---

## 1. Core System Tables

These tables form the foundation of the FusionPBX multi-tenant architecture.

| # | Table Name | Description | Key Columns | Relationships |
|---|-----------|-------------|-------------|---------------|
| 1 | v_domains | Multi-tenant domain definitions | domain_uuid (PK), domain_name, domain_description, domain_enabled | Parent for almost all other tables |
| 2 | v_domain_settings | Per-domain configuration overrides | domain_setting_uuid (PK), domain_uuid (FK), domain_setting_category, domain_setting_subcategory, domain_setting_name, domain_setting_value | References v_domains |
| 3 | v_users | User accounts | user_uuid (PK), domain_uuid (FK), username, password, salt, user_email, user_enabled | References v_domains |
| 4 | v_user_settings | Per-user settings | user_setting_uuid (PK), user_uuid (FK), user_setting_category, user_setting_subcategory, user_setting_name, user_setting_value | References v_users |
| 5 | v_user_logs | User activity audit trail | user_log_uuid (PK), domain_uuid (FK), user_uuid (FK), timestamp, type, result, remote_address | References v_users, v_domains |
| 6 | v_groups | Security groups (superadmin, admin, user, agent) | group_uuid (PK), domain_uuid (FK), group_name, group_description | References v_domains |
| 7 | v_user_groups | User-to-group membership mapping | user_group_uuid (PK), domain_uuid (FK), user_uuid (FK), group_uuid (FK), group_name | References v_users, v_groups |
| 8 | v_permissions | Application-level permissions | permission_uuid (PK), permission_name, permission_description, permission_assigned | Referenced by group permissions |
| 9 | v_group_permissions | Group-to-permission assignments | group_permission_uuid (PK), domain_uuid (FK), group_uuid (FK), permission_name, permission_assigned | References v_groups |
| 10 | v_default_settings | Global system defaults | default_setting_uuid (PK), default_setting_category, default_setting_subcategory, default_setting_name, default_setting_value, default_setting_enabled | Standalone |
| 11 | v_menus | Navigation menu definitions | menu_uuid (PK), menu_name, menu_description | Parent for v_menu_items |
| 12 | v_menu_items | Individual menu entries | menu_item_uuid (PK), menu_uuid (FK), menu_item_title, menu_item_link, menu_item_icon, menu_item_order | References v_menus |
| 13 | v_menu_item_groups | Menu visibility per group | menu_item_group_uuid (PK), menu_uuid (FK), menu_item_uuid (FK), group_name | References v_menu_items |
| 14 | v_email_templates | Email notification templates | email_template_uuid (PK), domain_uuid (FK), template_category, template_subcategory, template_subject, template_body | References v_domains |
| 15 | v_email_queue | Outbound email queue | email_queue_uuid (PK), domain_uuid (FK), email_from, email_to, email_subject, email_body, email_status, email_date | References v_domains |
| 16 | v_email_queue_attachments | Email queue file attachments | email_queue_attachment_uuid (PK), email_queue_uuid (FK), email_attachment_type, email_attachment_name, email_attachment_path | References v_email_queue |
| 17 | v_notifications | User notification preferences | notification_uuid (PK), domain_uuid (FK), notification_type, notification_enabled | References v_domains |
| 18 | v_software | Software version tracking | software_uuid (PK), software_name, software_version | Standalone |
---

## 2. Contacts Tables

| # | Table Name | Description | Key Columns |
|---|-----------|-------------|-------------|
| 1 | v_contacts | Master contact records | contact_uuid (PK), domain_uuid (FK), contact_type, contact_organization, contact_name_given, contact_name_family, contact_title |
| 2 | v_contact_phones | Contact phone numbers | contact_phone_uuid (PK), contact_uuid (FK), phone_type, phone_number, phone_primary |
| 3 | v_contact_emails | Contact email addresses | contact_email_uuid (PK), contact_uuid (FK), email_address, email_primary |
| 4 | v_contact_addresses | Contact physical addresses | contact_address_uuid (PK), contact_uuid (FK), address_type, address_street, address_city, address_state, address_postal_code, address_country |
| 5 | v_contact_urls | Contact web URLs | contact_url_uuid (PK), contact_uuid (FK), url_label, url_address |
| 6 | v_contact_notes | Contact notes / comments | contact_note_uuid (PK), contact_uuid (FK), contact_note, last_mod_date |
| 7 | v_contact_groups | Contact-to-group associations | contact_group_uuid (PK), contact_uuid (FK), group_uuid (FK) |
| 8 | v_contact_relations | Contact-to-contact relationships | contact_relation_uuid (PK), contact_uuid (FK), relation_label, relation_contact_uuid |
| 9 | v_contact_settings | Per-contact settings | contact_setting_uuid (PK), contact_uuid (FK), contact_setting_category, contact_setting_name, contact_setting_value |
| 10 | v_contact_attachments | File attachments on contacts | contact_attachment_uuid (PK), contact_uuid (FK), attachment_filename, attachment_content |

---

## 3. Dashboard Tables

| # | Table Name | Description | Key Columns |
|---|-----------|-------------|-------------|
| 1 | v_dashboards | Dashboard definitions per user | dashboard_uuid (PK), domain_uuid (FK), dashboard_name, dashboard_user_uuid |
| 2 | v_dashboard_widgets | Widget instances on dashboards | dashboard_widget_uuid (PK), dashboard_uuid (FK), widget_name, widget_type, widget_order, widget_column, widget_enabled |

---

## 4. Extensions and Call Routing Tables

| # | Table Name | Description | Key Columns |
|---|-----------|-------------|-------------|
| 1 | v_extensions | SIP extensions | extension_uuid (PK), domain_uuid (FK), extension, password, caller_id_name, caller_id_number, user_context, enabled, description |
| 2 | v_extension_users | Extension-to-user mapping | extension_user_uuid (PK), extension_uuid (FK), user_uuid (FK) |
| 3 | v_extension_settings | Per-extension settings | extension_setting_uuid (PK), extension_uuid (FK), extension_setting_name, extension_setting_value |
| 4 | v_dialplans | Dialplan entries | dialplan_uuid (PK), domain_uuid (FK), dialplan_name, dialplan_context, dialplan_number, dialplan_order, dialplan_enabled |
| 5 | v_dialplan_details | Dialplan conditions and actions | dialplan_detail_uuid (PK), dialplan_uuid (FK), dialplan_detail_tag, dialplan_detail_type, dialplan_detail_data, dialplan_detail_order |
| 6 | v_destinations | External destination numbers | destination_uuid (PK), domain_uuid (FK), destination_type, destination_number, destination_caller_id_name, destination_caller_id_number, destination_action |
| 7 | v_call_flows | Toggle-based call flows (day/night) | call_flow_uuid (PK), domain_uuid (FK), call_flow_name, call_flow_extension, call_flow_feature_code, call_flow_status, call_flow_data |
| 8 | v_call_flow_destinations | Call flow destination options | call_flow_destination_uuid (PK), call_flow_uuid (FK), destination_type, destination_number |
| 9 | v_follow_me | Follow-me call forwarding rules | follow_me_uuid (PK), domain_uuid (FK), follow_me_enabled, follow_me_caller_id_name |
| 10 | v_follow_me_destinations | Follow-me destination list | follow_me_destination_uuid (PK), follow_me_uuid (FK), destination_number, destination_delay, destination_timeout |
| 11 | v_call_block | Blocked caller IDs | call_block_uuid (PK), domain_uuid (FK), call_block_name, call_block_number, call_block_action |
| 12 | v_bridges | Bridge endpoints | bridge_uuid (PK), domain_uuid (FK), bridge_name, bridge_destination |
| 13 | v_number_translations | Number translation rules | number_translation_uuid (PK), domain_uuid (FK), number_translation_name, number_translation_source, number_translation_destination |
| 14 | v_time_conditions | Time-based routing conditions | time_condition_uuid (PK), domain_uuid (FK), time_condition_name, dialplan_uuid (FK) |

---

## 5. Queuing Tables (Call Center and Ring Groups)

| # | Table Name | Description | Key Columns |
|---|-----------|-------------|-------------|
| 1 | v_call_center_queues | Call center queue definitions | call_center_queue_uuid (PK), domain_uuid (FK), queue_name, queue_extension, queue_strategy, queue_moh_sound, queue_timeout_action |
| 2 | v_call_center_agents | Call center agent registrations | call_center_agent_uuid (PK), domain_uuid (FK), agent_name, agent_type, agent_contact, agent_status, agent_max_no_answer |
| 3 | v_call_center_tiers | Agent-to-queue tier assignments | call_center_tier_uuid (PK), call_center_queue_uuid (FK), call_center_agent_uuid (FK), tier_level, tier_position |
| 4 | v_ring_groups | Ring group definitions | ring_group_uuid (PK), domain_uuid (FK), ring_group_name, ring_group_extension, ring_group_strategy, ring_group_timeout_app, ring_group_enabled |
| 5 | v_ring_group_destinations | Ring group member destinations | ring_group_destination_uuid (PK), ring_group_uuid (FK), destination_number, destination_delay, destination_timeout, destination_prompt |
| 6 | v_fifo | FIFO queue definitions | fifo_uuid (PK), domain_uuid (FK), fifo_name, fifo_extension |

---

## 6. Voice and Media Tables

| # | Table Name | Description | Key Columns |
|---|-----------|-------------|-------------|
| 1 | v_voicemails | Voicemail box configuration | voicemail_uuid (PK), domain_uuid (FK), voicemail_id, voicemail_password, voicemail_mail_to, voicemail_enabled, voicemail_description |
| 2 | v_voicemail_messages | Individual voicemail messages | voicemail_message_uuid (PK), voicemail_uuid (FK), created_epoch, caller_id_name, caller_id_number, message_length, message_status |
| 3 | v_voicemail_greetings | Voicemail greeting recordings | voicemail_greeting_uuid (PK), voicemail_uuid (FK), greeting_name, greeting_filename, greeting_base64 |
| 4 | v_voicemail_destinations | Voicemail forwarding destinations | voicemail_destination_uuid (PK), voicemail_uuid (FK), voicemail_dest_mail_to |
| 5 | v_recordings | Audio recording files (IVR, prompts) | recording_uuid (PK), domain_uuid (FK), recording_name, recording_filename, recording_description |
| 6 | v_call_recordings | Call recording metadata | call_recording_uuid (PK), domain_uuid (FK), call_recording_name, call_recording_path, call_recording_length, call_recording_date |
| 7 | v_ivr_menus | IVR menu definitions | ivr_menu_uuid (PK), domain_uuid (FK), ivr_menu_name, ivr_menu_extension, ivr_menu_greet_long, ivr_menu_greet_short, ivr_menu_timeout |
| 8 | v_ivr_menu_options | IVR digit-to-action mappings | ivr_menu_option_uuid (PK), ivr_menu_uuid (FK), ivr_menu_option_digits, ivr_menu_option_action, ivr_menu_option_param, ivr_menu_option_order |
| 9 | v_conference_centers | Conference center definitions | conference_center_uuid (PK), domain_uuid (FK), conference_center_name, conference_center_enabled |
| 10 | v_conference_rooms | Individual conference rooms | conference_room_uuid (PK), conference_center_uuid (FK), conference_room_name, conference_room_moderator_pin, conference_room_participant_pin, conference_room_max_members |

---

## 7. Fax Tables

| # | Table Name | Description | Key Columns |
|---|-----------|-------------|-------------|
| 1 | v_fax | Fax extension configuration | fax_uuid (PK), domain_uuid (FK), fax_extension, fax_name, fax_email, fax_caller_id_name, fax_caller_id_number |
| 2 | v_fax_files | Sent and received fax documents | fax_file_uuid (PK), fax_uuid (FK), fax_file_type, fax_file_path, fax_caller_id_name, fax_caller_id_number, fax_date |
| 3 | v_fax_queue | Outbound fax queue | fax_queue_uuid (PK), domain_uuid (FK), fax_uuid (FK), fax_queue_number, fax_queue_status, fax_queue_retry_count |
| 4 | v_fax_logs | Fax transmission logs | fax_log_uuid (PK), fax_uuid (FK), fax_success, fax_result_code, fax_result_text, fax_date |

---

## 8. Devices and Provisioning Tables

| # | Table Name | Description | Key Columns |
|---|-----------|-------------|-------------|
| 1 | v_devices | Provisioned device definitions | device_uuid (PK), domain_uuid (FK), device_mac_address, device_label, device_vendor, device_model, device_template, device_enabled |
| 2 | v_device_lines | Device line/account assignments | device_line_uuid (PK), device_uuid (FK), line_number, server_address, user_id, password, display_name |
| 3 | v_device_keys | Programmable key assignments | device_key_uuid (PK), device_uuid (FK), device_key_category, device_key_type, device_key_label, device_key_value |
| 4 | v_device_profiles | Shared device configuration profiles | device_profile_uuid (PK), domain_uuid (FK), device_profile_name, device_profile_description |
| 5 | v_device_profile_keys | Profile-level programmable keys | device_profile_key_uuid (PK), device_profile_uuid (FK), device_key_category, device_key_type, device_key_label, device_key_value |

---

## 9. SIP and Network Tables

| # | Table Name | Description | Key Columns |
|---|-----------|-------------|-------------|
| 1 | v_gateways | SIP gateway / trunk definitions | gateway_uuid (PK), domain_uuid (FK), gateway, username, password, proxy, register, profile, enabled, description |
| 2 | v_sip_profiles | SIP stack profile definitions | sip_profile_uuid (PK), sip_profile_name, sip_profile_description, sip_profile_enabled |
| 3 | v_sip_profile_settings | Per-profile SIP parameters | sip_profile_setting_uuid (PK), sip_profile_uuid (FK), sip_profile_setting_name, sip_profile_setting_value, sip_profile_setting_enabled |
| 4 | v_sip_profile_domains | Domains associated with SIP profiles | sip_profile_domain_uuid (PK), sip_profile_uuid (FK), sip_profile_domain_name |
| 5 | v_access_controls | IP access control lists | access_control_uuid (PK), access_control_name, access_control_default, access_control_description |
| 6 | v_access_control_nodes | ACL rules (allow/deny per CIDR) | access_control_node_uuid (PK), access_control_uuid (FK), node_type, node_cidr, node_description |

---

## 10. CDR and Logging Tables

| # | Table Name | Description | Key Columns |
|---|-----------|-------------|-------------|
| 1 | v_xml_cdr | Call detail records | xml_cdr_uuid (PK), domain_uuid (FK), extension_uuid, start_stamp, end_stamp, duration, billsec, caller_id_name, caller_id_number, destination_number, hangup_cause, direction, bridge_uuid |
| 2 | v_database_transactions | Database audit trail | database_transaction_uuid (PK), domain_uuid (FK), user_uuid, transaction_code, transaction_address, transaction_type, transaction_date, transaction_old, transaction_new, transaction_result |
| 3 | v_emergency | Emergency call logs | emergency_uuid (PK), domain_uuid (FK), emergency_name, emergency_number, emergency_date |
| 4 | v_event_guard_logs | Event guard security logs | event_guard_log_uuid (PK), hostname, guard_name, ip_address, event, status, filter, event_date |

---

## 11. FreeSWITCH Core Tables

These tables are managed by FreeSWITCH itself (not by FusionPBX application code) and are used for real-time state. FusionPBX reads from these for status displays.

| # | Table Name | Description | Key Columns |
|---|-----------|-------------|-------------|
| 1 | agents | Call center agent state (mod_callcenter) | name, instance_id, uuid, type, contact, status, state, max_no_answer, reject_delay_time |
| 2 | tiers | Call center tier assignments (mod_callcenter) | queue, agent, state, level, position |
| 3 | channels | Active call channels | uuid, direction, created, created_epoch, name, state, cid_name, cid_num, dest, application, application_data |
| 4 | calls | Active bridged calls | caller_uuid, callee_uuid, hostname |
| 5 | registrations | Directory registrations | reg_user, realm, token, url, expires, network_ip, network_port, hostname |
| 6 | sip_registrations | SIP-specific registration details | call_id, sip_user, sip_host, contact, status, ping_status, ping_time, network_ip, network_port, user_agent |
| 7 | interfaces | Loaded FreeSWITCH interface modules | type, name, description, ikey, filename |
| 8 | nat | NAT detection table | proto, sticky, port, proto_name |

---

## Entity Relationship Overview

v_domains is the central tenant table. All domain-scoped entities reference it via domain_uuid:

- v_domains (1) to many v_users
- v_domains (1) to many v_extensions
- v_domains (1) to many v_gateways
- v_domains (1) to many v_dialplans, each with many v_dialplan_details
- v_domains (1) to many v_ring_groups, each with many v_ring_group_destinations
- v_domains (1) to many v_call_center_queues
- v_domains (1) to many v_voicemails, each with many v_voicemail_messages
- v_domains (1) to many v_ivr_menus, each with many v_ivr_menu_options
- v_domains (1) to many v_devices, each with many v_device_lines
- v_domains (1) to many v_contacts, each with many v_contact_phones
- v_domains (1) to many v_fax, each with many v_fax_files
- v_domains (1) to many v_xml_cdr
- v_users (N) to many v_groups via v_user_groups (many-to-many)
- v_extensions (N) to many v_users via v_extension_users (many-to-many)
- v_call_center_queues (N) to many v_call_center_agents via v_call_center_tiers (many-to-many)

---

## Notes

- All v_* tables use UUID primary keys (*_uuid columns) as text/varchar fields.
- The domain_uuid foreign key provides multi-tenant data isolation at the database level.
- FreeSWITCH core tables (section 11) use an in-memory database (SQLite or ODBC) and are populated at runtime.
- Schema migrations are managed by the core/upgrade module and the schema PHP class.
- FusionPBX supports PostgreSQL (recommended for production) and SQLite (development/small deployments).
