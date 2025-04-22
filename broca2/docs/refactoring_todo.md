# Broca Core Refactoring Plan

## Overview
This document outlines the steps and considerations for refactoring the Broca project into a more modular and testable structure. The goal is to reorganize the codebase while minimizing disruption to existing functionality.

## Current Structure vs Target Structure
Current structure is relatively flat, with main components in root directories. Target structure will be more modular with clear separation of concerns.

## Impact Analysis

### 1. File Moves and Path Updates
- [ ] Move `core/letta_client.py` → `broca-core/plugins/endpoints/letta.py`
- [ ] Move `telegram/client.py` and `telegram/handlers.py` → `broca-core/plugins/platforms/telegram.py`
- [ ] Move `core/queue.py` → `broca-core/middleware/queue.py`
- [ ] Move `core/agent.py` → `broca-core/middleware/agent.py`
- [ ] Move `core/message.py` → `broca-core/models/message.py`
- [ ] Move `web/app.py` → `broca-core/web/app.py`
- [ ] Move `templates/` → `broca-core/web/templates/`
- [ ] Move `static/` → `broca-core/web/static/`
- [ ] Update Flask app's `template_folder` and `static_folder` parameters in `app.py`

### 2. New Files to Create
- [ ] Create `broca-core/middleware/plugin_loader.py` (renamed from plugin_manager.py)
- [ ] Create `broca-core/models/state.py`
- [ ] Create `broca-core/utils/logger.py`
- [ ] Create `broca-core/config/plugins.json` (ensure clear namespace separation from settings.json)
- [ ] Create `__init__.py` in all new directories:
  - `broca-core/plugins/`
  - `broca-core/plugins/endpoints/`
  - `broca-core/plugins/platforms/`
  - `broca-core/middleware/`
  - `broca-core/models/`
  - `broca-core/database/`
  - `broca-core/web/`
  - `broca-core/utils/`
  - `broca-core/config/`

### 3. Path Updates Required
- [ ] Update all import statements in:
  - `main.py`
  - All moved files
  - Any files referencing moved components
- [ ] Update configuration file paths in:
  - `settings.json`
  - `.env` and `.env.example`
  - Any hardcoded paths in the codebase
- [ ] Update Alembic migration paths to point to new `models.py` location

### 4. Database Considerations
- [ ] Verify database migrations will work with new structure
- [ ] Update any database connection paths
- [ ] Ensure database models are properly imported in new location
- [ ] Keep `database/migrations/` folder structure intact
- [ ] Update migration scripts to reference new model paths

### 5. Testing Infrastructure
- [ ] Set up test directory structure:
  - `broca-core/tests/unit/`
  - `broca-core/tests/integration/`
- [ ] Create initial test configuration
- [ ] Update any existing tests to work with new structure
- [ ] Add test coverage for new modular components

### 6. Documentation Updates
- [ ] Update README.md with new structure
- [ ] Update any internal documentation
- [ ] Create/update API documentation if needed

## Implementation Steps

1. **Preparation Phase**
   - [ ] Create new directory structure with all `__init__.py` files
   - [ ] Create dedicated "refactor" git branch
   - [ ] Backup current working state in `bak/` directory
   - [ ] Create new configuration files
   - [ ] Update `.gitignore` to preserve `bak/` directory

2. **Core Migration**
   - [ ] Move core components first
   - [ ] Update imports and paths
   - [ ] Verify basic functionality

3. **Plugin System**
   - [ ] Implement plugin loader (formerly plugin_manager)
   - [ ] Migrate existing plugins
   - [ ] Test plugin loading

4. **Web Components**
   - [ ] Move web-related files
   - [ ] Update web server configuration
   - [ ] Update Flask template and static paths
   - [ ] Test web functionality

5. **Testing Setup**
   - [ ] Set up test environment with unit/integration split
   - [ ] Create initial test suite
   - [ ] Verify test coverage

6. **Documentation**
   - [ ] Update all documentation
   - [ ] Create migration guide
   - [ ] Update API documentation

## Risk Mitigation

1. **Backup Strategy**
   - Keep current working version in `bak/` directory
   - Create and work in dedicated "refactor" git branch
   - Regular commits during refactoring
   - Ensure `.gitignore` preserves `bak/` directory

2. **Testing Strategy**
   - Test each component after move
   - Maintain existing test coverage
   - Add new tests for modular components

3. **Rollback Plan**
   - Document rollback steps
   - Keep backup of critical files
   - Maintain working version in separate branch
   - Preserve ability to cherry-pick clean commits

## Dependencies to Check

1. **Python Packages**
   - Verify all imports work with new structure
   - Check for any hardcoded paths in dependencies
   - Update requirements.txt if needed

2. **Configuration Files**
   - Update paths in settings.json
   - Verify environment variables
   - Check plugin configurations
   - Ensure clear separation between settings.json and plugins.json

## Post-Refactoring Tasks

1. **Cleanup**
   - Remove old directories
   - Clean up any unused files
   - Update .gitignore if needed

2. **Verification**
   - Run full test suite
   - Verify all features work
   - Check performance metrics

3. **Documentation**
   - Finalize all documentation updates
   - Create migration guide for users
   - Update any deployment scripts

## Notes
- This refactoring should be done in small, testable steps
- Each move should be verified before proceeding
- Keep detailed notes of any issues encountered
- Regular testing is crucial throughout the process
- Ensure all new directories have proper `__init__.py` files
- Maintain clear separation between config and settings
- Preserve migration paths and update references
- Split test directory into unit and integration tests from the start 