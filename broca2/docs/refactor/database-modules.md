# Database Module Split

## Overview
The database operations have been split into separate modules for better organization and maintainability:

- `shared.py`: Core database operations (initialization, migration, common utilities)
- `users.py`: User-related operations (get_or_create_user, platform lookup, etc)
- `messages.py`: Message-related operations (insert, update, history, etc)
- `queue.py`: Queue-related operations (add, get, update, flush, etc)

## Migration Notes
- All functions from the original `operations.py` have been moved to their respective modules
- Imports have been updated across the codebase to use the new module structure
- The original `operations.py` has been removed
- All tests have been updated to use the new import paths

## Benefits
- Better code organization and separation of concerns
- Easier to maintain and extend specific functionality
- Clearer dependencies between components
- Improved code readability and discoverability 