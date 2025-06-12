# Broca 2 Changelog

## 2025-06-12
- **Update README links** (db2431c): Updated README links to point to the correct directory structure in broca2.
- **Enhance migration script** (43dadd6): Enhanced migration script for letta_users by adding error handling and logging of column names before and after migration. The script now ensures the new table is created correctly and drops any existing temporary tables. Additionally, a new script is introduced to print the current columns of letta_users to a file.
- **Refactor LettaUser model** (21a2a00): Refactored LettaUser model and related operations by removing redundant conversation_history_limit field. Updated documentation for clarity on user preferences and message history retrieval.
- **Update PID file and enhance Telegram message handling** (36deb4d): Updated PID file and enhanced Telegram message handling with bot ignore functionality.

## 2025-04-28
- **Silly update to README** (532520d): Minor update to README.

## 2025-04-24
- **Update version to 0.9.0** (94d3a4f): Actually update the version number to 0.9.0.
- **Stage CLI tool** (6af3052): Staging the CLI tool, but deciding to move on to other aspects, as Broca is stable v0.9 now.

## 2025-04-23
- **Routing and plugin management** (7929e98, 1ad8ab8, d5b3a14, 4b7adf7, 5272f7b, 43aafb1, 40498f0, 0465718, 2f489dc, 3f55841, b747cf4, 3275c6b, 8c4ec4c, 41057e1, cdf7c09): Various commits related to routing and plugin management refactoring.

## 2025-04-22
- **Migration to CLI mode** (9317189): Migrated away from the FLASK integration to a total CLI mode.
- **Fix issues** (c25014f, 0b162f8): Fixed various issues.
- **Migration to Broca2** (4063812): Migration to Broca2 works, echo mode is working.

## 2025-04-21
- **Core and DB migration** (07bb3c6): Broca 2 core and DB migration done.
- **Project setup** (f534b4c): Broca2 folders created, plan filled out.

## 2025-04-20
- **Initial commit** (e8477cf, 4efe81d): Broca2 started and first commit.
