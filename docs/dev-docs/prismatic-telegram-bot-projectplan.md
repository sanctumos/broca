# ⚠️ REPOSITORY MOVED ⚠️

**This repository has moved to: [http://github.com/sanctumos/broca](http://github.com/sanctumos/broca)**

Please update your git remotes and use the new repository location for all future development and contributions.

---

# **Prismatic Broca2 – Telegram BOT Plugin (aiogram) MVP**

> **PLUGIN-ONLY task. Absolutely NO changes to Broca2 core, runtime, DB schema, or queue logic.**

---

## 1. Project Goal

* Create a **new plugin folder** `/plugins/telegram_bot` with an **aiogram (≥ 3.x) BOT plugin** that enforces **strict 1 : 1 owner-only** messaging.
* This is a **separate plugin** from the existing Telethon plugin - do not modify the existing plugin.
* MVP must plug into the existing buffer → queue → agent loop unchanged, be testable, and future-extensible.

---

## 2. Implementation Rules

| Topic                   | Exactly What To Do                                                                                                                                                                                                    |
| ----------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Library**             | Use **aiogram 3.x** *only*. No Telethon, python-telegram-bot, pyrogram, etc.                                                                                                                                          |
| **Folder / Config**     | Create new plugin folder structure:<br>`/plugins/telegram_bot/`<br>├── `__init__.py`<br>├── `plugin.py`<br>├── `handlers.py`<br>├── `settings.py`<br>└── `message_handler.py`<br><br>the master `.env` **must** contain:<br>`TELEGRAM_BOT_TOKEN={token}`<br>AND EXACTLY ONE OF:<br>`TELEGRAM_OWNER_ID={numeric_id}`<br>`TELEGRAM_OWNER_USERNAME={username}` (without @)                                              |
| **Interface**           | Implement same public methods as the current plugin (`get_name()`, `get_platform()`, `start()`, `stop()`, handlers). Fit under the existing Broca2 plugin manager—**do not touch core code.**                         |
| **Message Flow**        | 1. Receive message → if sender doesn't match owner ID/username, log & ignore.<br>2. If owner: pass text to queue exactly like old plugin.<br>3. Send agent's response back to owner.<br>*(Buffer/queue logic remains untouched.)* |
| **Non-Owner Handling**  | **Silently ignore.**<br>Log once per message:<br>`[PLUGIN][INFO] Ignored message from non-owner user_id={id}`                                                                                                         |
| **Buffering**           | **KEEP** existing Broca2 MessageBuffer / delay / batching. Do **not** optimize or remove. SAME CLASS. DONT WRITE A NEW ONE.                                                                                                                             |
| **Logging**             | Use Broca2 console style: `[PLUGIN][INFO] …`, `[PLUGIN][ERROR] …` – nothing fancy.                                                                                                                                    |
| **Performance Targets** | Aim: processing < 100 ms, round-trip < 2 s. *Log timings; don't hard-abort on slow dev boxes.*                                                                                                                        |
| **Deployment**          | Agents run via `screen` from their folder. Systemd is optional, not in MVP scope.                                                                                                                                     |

---

## 3. Phases & Checklist

### Phase 1 – Plugin Code

* [ ] Scaffold or copy the files from the user based telegram plugin in the new plugin folder.
* [ ] Read `.env`, create `Bot` with aiogram, hook handlers.
* [ ] Maintain public plugin interface.

### Phase 2 – 1 : 1 Enforcement

* [ ] Owner-ID filter (private chat only).
* [ ] Ignore everything else, log as specified.
* [ ] No group / channel logic.

### Phase 3 – Tests

Unit (≥ 90 % total, 100 % on access control):

* Message filter paths.
* Send / receive stubs.
* Error branches.

Integration:

* Mock Telegram API or use a test bot token.
* End-to-end loop: Telegram → Plugin → Queue → Agent → Plugin → Telegram.
* Negative paths: non-owner messages, DB offline, plugin restart.

### Phase 4 – Ops Docs

* [ ] README snippet: how to copy agent folder, drop `.env`, run `screen`.
* [ ] Optional helper script for new-agent creation (nice-to-have).

---

## 4. Milestones / Acceptance

* ✅ Code passes review; no core files touched.
* ✅ Owner-only verified (no crosstalk).
* ✅ Tests green; coverage target met.
* ✅ Logs show correct ignores / errors.
* ✅ README / ops notes updated; new agent can be spun in < 2 min from template.

---

## 5. Negative Prompts (Instant-Fail)

* ❌ Modify Broca2 core, DB, queue, or buffer code.
* ❌ Use any Telegram lib except **aiogram 3.x**.
* ❌ Introduce group chat, multi-user, or profile tables.
* ❌ Symlink shared logs/config—each agent must copy.
* ❌ Ship code without unit + integration tests.

---

## 6. Positive Prompts (Do These)

* ✅ Keep everything async & modular.
* ✅ Log clearly; ignore non-owners quietly.
* ✅ Follow existing buffer/queue; plug-and-play.
* ✅ Ask if uncertain—don't improvise beyond this spec.

---

### Example – Ignored Message

```python
if message.from_user.id != OWNER_ID:
    print(f"[PLUGIN][INFO] Ignored message from non-owner user_id={message.from_user.id}")
    return
```

