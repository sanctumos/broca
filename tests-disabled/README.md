# Disabled tests

Tests in this folder are for **disabled or removed plugins** and are not run by the main test suite.

They are kept for reference or until those plugins are re-enabled:

- **fake_plugin** – test plugin (removed or never present in this tree)
- **telegram** (legacy) – replaced by `telegram_bot`; these tests import `plugins.telegram.*`
- **web_chat** – tests import `plugins.web_chat.*` (module layout may have changed)

To run them (e.g. after re-enabling a plugin):

```bash
pytest tests-disabled/ -v
```
