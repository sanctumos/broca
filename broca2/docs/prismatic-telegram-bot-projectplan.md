
## **Telegram BOT Plugin, Prismatic Edition**

### **Project Goal**

* Build a new Telegram plugin for the Broca2 agent framework that uses **bot token authentication** and is strictly **1:1 (owner-only)**, replacing the existing multi-user Telethon-based plugin.
* MVP must be stable, testable, and easily extended or re-themed later.

---

### **Scope & Phases**

#### **Phase 1: Plugin Development**

* [ ] Analyze the \[telegram-plugin-spec.md] spec and identify all required hooks with the core Broca2 system.
* [ ] Implement a new plugin (e.g., `telegram_bot_token.py`) based on the provided interface and business/tech requirements.
* [ ] Use **python-telegram-bot** library for bot-token mode (do NOT use Telethon or StringSession).
* [ ] Read all config (bot token, owner ID, etc.) from `.env` as in the spec.

#### **Phase 2: 1:1 Logic Implementation**

* [ ] All incoming messages must be filtered: **only accept and respond to the configured owner’s Telegram user ID**.
* [ ] Disable (or ignore) all group chat, multi-user, or human session logic.
* [ ] On every inbound message, plugin should:

  * Validate it is a private chat from the owner.
  * Forward to the queue/core for processing.
  * Return the generated response to the owner only.
* [ ] Implement status/error handling, graceful degradation, and logging as in the spec.

#### **Phase 3: Integration & System Testing**

* [ ] Ensure plugin integrates cleanly with Broca2’s queue, plugin manager, and DB layer (no refactor to core loop expected).
* [ ] Confirm **owner-only** logic cannot be bypassed, even if plugin is spammed or probed from outside users.
* [ ] Test with both `echo`, `listen`, and `live` modes.
* [ ] Log all input/output, errors, and performance metrics.

#### **Phase 4: Agent Lifecycle & Ops Scripting**

* [ ] Support easy deployment: copy template folder, drop in new `.env` with bot token/owner ID, run in a `screen` session.
* [ ] Optional: Provide simple CLI/script for creating new agents with correct folder/config.
* [ ] Document launch and monitor steps for ops.

---

### **Milestones & Acceptance Criteria**

* [ ] New plugin code committed, passing code review
* [ ] Owner-only messaging verified in test Telegram bot (no leaks, no crosstalk)
* [ ] MVP tested in `echo`, `listen`, and `live` modes
* [ ] At least 90% unit test coverage on plugin logic; 100% coverage for 1:1 access control
* [ ] Integration tests pass for queue, DB, and end-to-end message flow
* [ ] Log output is clean, actionable, and performance metrics are visible
* [ ] Ops docs updated: agent spawn, update, and restart steps are clear

---

### **Negative Prompts (What Not To Do)**

* ❌ **Do NOT use Telethon** or any session-string logic—bot token only.
* ❌ **Do NOT support group chats or multiple user IDs**—MVP is 1:1 private chat only.
* ❌ **Do NOT add user/profile tables or multi-user logic**—no platform\_profiles, no extra DB joins.
* ❌ **Do NOT alter the core Broca2 runtime loop or queue logic**—all changes at the plugin layer.
* ❌ **Do NOT ignore unit and integration testing**—untested code = rejected PR.
* ❌ **Do NOT symlink config or logs**—always copy for each agent folder.
* ❌ **Do NOT skip input sanitization, error handling, or log statements**.
* ❌ **Do NOT assume future features—MVP only.** No group support, no commands, no media.

---

### **Positive Prompts (What To Absolutely Do)**

* ✅ Keep all plugin logic **async-friendly** and cleanly separated.
* ✅ Log all errors, state changes, and suspicious input.
* ✅ Treat **owner-only enforcement** as a security feature—test for bypasses.
* ✅ Write *unit tests* for all major plugin functions (message filter, owner check, send/receive).
* ✅ Write *integration tests* for queue interaction, agent response, and DB logging.
* ✅ Confirm **performance targets** (response <2s, process <100ms) in test runs.
* ✅ Keep code and comments clear—future devs should be able to extend this easily.

---

### **Testing Checklist**

#### **Unit Testing**

* [ ] Message filter: owner vs. not-owner, private vs. group, valid vs. invalid messages
* [ ] Message processing: handling, sanitization, error conditions
* [ ] Outbound messaging: correct user, correct format
* [ ] Buffering/delay logic

#### **Integration Testing**

* [ ] Full message loop: Telegram → Plugin → Queue → Agent → Plugin → Telegram
* [ ] DB storage/retrieval: all expected data is logged and retrievable
* [ ] Ops: new agent creation, launch, and restart (manual or scripted)
* [ ] Negative tests: message injection from non-owner, malformed input, DB unavailable, plugin restart
