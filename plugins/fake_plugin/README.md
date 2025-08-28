# ⚠️ REPOSITORY MOVED ⚠️

**This repository has moved to: [http://github.com/sanctumos/broca](http://github.com/sanctumos/broca)**

Please update your git remotes and use the new repository location for all future development and contributions.

---

# Fake Plugin

This is a minimal fake plugin for testing Broca2's plugin discovery mechanism.

## Purpose

- Test if Broca2 can automatically discover and load plugins
- Verify the plugin loading mechanism works correctly
- Provide a simple baseline for plugin development

## Features

- Implements the minimal `Plugin` interface
- Provides basic logging when started/stopped
- No external dependencies or complex functionality
- Always validates successfully

## Expected Behavior

When Broca2 starts, it should:
1. Discover this plugin in the `plugins/fake_plugin/` directory
2. Load the `FakePlugin` class
3. Start the plugin and log: `"🎭 Fake plugin started successfully"`
4. Stop the plugin when Broca2 shuts down

## Testing

If this plugin loads successfully, we know the plugin discovery mechanism works and we can proceed with implementing auto-discovery for all plugins. 