# GitHub Issues to Create

This file contains structured issues based on the codebase audit. These can be manually created in GitHub once issues are enabled on the repository.

## How to Use This File

1. Enable issues on the repository (requires admin permissions)
2. Copy each issue section below and create individual GitHub issues
3. Use the suggested labels for proper organization
4. Reference the AUDIT_RECOMMENDATIONS.md file for detailed context

---

## HIGH PRIORITY ISSUES

### 🔒 Security Issues

#### Issue #1: Create .env.example template and improve credential management
**Labels:** `security`, `high-priority`, `documentation`

**Description:**
Missing .env.example file creates security risk where developers may commit real credentials to the repository.

**Issues Identified:**
- No .env.example template for developers
- Risk of credential exposure in commits
- Missing environment variable validation on startup

**Recommended Actions:**
- [ ] Create .env.example with placeholder values for all required environment variables
- [ ] Ensure .env is in .gitignore
- [ ] Implement environment variable validation on startup
- [ ] Add documentation about proper credential management

**Implementation Details:**
Create a validation function in main.py to check for test/placeholder values in production.

**Files to Create/Modify:**
- .env.example (new)
- main.py (add validation)
- docs/configuration.md (update documentation)

**Audit Reference:** AUDIT_RECOMMENDATIONS.md - Security Recommendations #1

---

#### Issue #2: Remove API key exposure in logs
**Labels:** `security`, `high-priority`, `logging`

**Description:**
API keys may be partially exposed in debug logs, creating security vulnerabilities.

**Current Issue:**
```python
# Found in runtime/core/letta_client.py:23
logger.debug(f"Using API key: {self.api_key[:4]}...")
```

**Recommended Actions:**
- [ ] Remove API key logging entirely in production
- [ ] Implement secure logging levels that exclude sensitive data
- [ ] Add configuration option to control sensitive data logging
- [ ] Review all logging statements for potential credential exposure

**Files to Modify:**
- runtime/core/letta_client.py
- common/logging.py
- All files with potential credential logging

**Audit Reference:** AUDIT_RECOMMENDATIONS.md - Security Recommendations #2

---

#### Issue #3: Implement comprehensive SQL injection prevention
**Labels:** `security`, `high-priority`, `database`

**Description:**
While using SQLAlchemy, some raw SQL queries were found that could pose security risks.

**Current Issues:**
- Raw SQL queries in database operations
- Need for consistent parameterized query usage
- Missing input validation for database operations

**Recommended Actions:**
- [ ] Review all database operations for SQL injection risks
- [ ] Ensure parameterized queries are used consistently
- [ ] Add input validation for all database operations
- [ ] Implement database security best practices

**Files to Review:**
- database/operations/*.py
- All files with database queries

**Audit Reference:** AUDIT_RECOMMENDATIONS.md - Security Recommendations #3

---

### 🏗️ Architecture Issues

#### Issue #4: Standardize error handling across the codebase
**Labels:** `architecture`, `high-priority`, `error-handling`

**Description:**
Inconsistent error handling patterns across the codebase make debugging and maintenance difficult.

**Current Issues:**
- Generic exception handling in multiple places
- No centralized error handling system
- Missing error context and recovery suggestions

**Recommended Actions:**
- [ ] Implement a centralized error handling system
- [ ] Create custom exception classes for different error types
- [ ] Add error context and recovery suggestions
- [ ] Standardize error logging format

**Implementation Example:**
```python
class BrocaError(Exception):
    def __init__(self, message: str, error_code: str = None, recovery_hint: str = None):
        super().__init__(message)
        self.error_code = error_code
        self.recovery_hint = recovery_hint
```

**Files to Modify:**
- common/exceptions.py (expand)
- All modules with exception handling

**Audit Reference:** AUDIT_RECOMMENDATIONS.md - Architecture Recommendations #1

---

#### Issue #5: Implement unified configuration management
**Labels:** `architecture`, `high-priority`, `configuration`

**Description:**
Settings are scattered across multiple files and formats, making configuration management complex.

**Current Issues:**
- settings.json for runtime settings
- Environment variables for secrets
- Plugin-specific configuration files
- No configuration validation

**Recommended Actions:**
- [ ] Implement a unified configuration management system
- [ ] Add configuration validation with schemas using Pydantic
- [ ] Support configuration hot-reloading for all components
- [ ] Create centralized configuration documentation

**Files to Create/Modify:**
- common/config.py (enhance)
- New configuration schema files
- All modules that use configuration

**Audit Reference:** AUDIT_RECOMMENDATIONS.md - Architecture Recommendations #2

---

### 🧪 Testing Issues

#### Issue #6: Implement comprehensive test coverage
**Labels:** `testing`, `high-priority`, `quality`

**Description:**
Limited test coverage (only 9 test files found) creates maintenance and reliability risks.

**Current Status:**
- Some plugins have tests (telegram_bot)
- Core functionality appears under-tested
- Integration tests missing
- No end-to-end testing

**Recommended Actions:**
- [ ] Achieve minimum 80% test coverage for core components
- [ ] Add integration tests for plugin system
- [ ] Implement end-to-end testing scenarios
- [ ] Set up automated test reporting

**Test Structure to Implement:**
```
tests/
├── unit/
│   ├── test_core/
│   ├── test_plugins/
│   └── test_database/
├── integration/
│   ├── test_plugin_system/
│   └── test_message_flow/
└── e2e/
    ├── test_telegram_bot/
    └── test_multi_agent/
```

**Audit Reference:** AUDIT_RECOMMENDATIONS.md - Testing Recommendations #1

---

## MEDIUM PRIORITY ISSUES

### ⚡ Performance Issues

#### Issue #7: Implement database connection pooling
**Labels:** `performance`, `medium-priority`, `database`

**Description:**
No evidence of connection pooling in database operations, which can impact performance under load.

**Recommended Actions:**
- [ ] Implement SQLAlchemy connection pooling
- [ ] Add connection health checks
- [ ] Monitor and optimize query performance
- [ ] Add database performance metrics

**Implementation:**
```python
from sqlalchemy.pool import QueuePool

engine = create_async_engine(
    database_url,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True
)
```

**Audit Reference:** AUDIT_RECOMMENDATIONS.md - Performance Recommendations #1

---

#### Issue #8: Optimize message processing with concurrency
**Labels:** `performance`, `medium-priority`, `async`

**Description:**
Sequential message processing in queue processor limits throughput.

**Current Issue:**
Messages are processed one at a time in the queue processor loop.

**Recommended Actions:**
- [ ] Implement concurrent message processing with limits
- [ ] Add message batching capabilities
- [ ] Optimize database queries with bulk operations
- [ ] Add performance monitoring

**Files to Modify:**
- runtime/core/queue.py

**Audit Reference:** AUDIT_RECOMMENDATIONS.md - Performance Recommendations #2

---

### 🛠️ Code Quality Issues

#### Issue #9: Add comprehensive type annotations
**Labels:** `code-quality`, `medium-priority`, `types`

**Description:**
Partially implemented type annotations with inconsistent coverage across the codebase.

**Recommended Actions:**
- [ ] Add comprehensive type annotations to all modules
- [ ] Use mypy for static type checking
- [ ] Add type checking to CI/CD pipeline
- [ ] Create type checking configuration

**Files to Modify:**
- All Python files lacking proper type annotations
- Setup mypy configuration

**Audit Reference:** AUDIT_RECOMMENDATIONS.md - Code Quality Recommendations #1

---

#### Issue #10: Reduce code duplication across plugins
**Labels:** `code-quality`, `medium-priority`, `refactoring`

**Description:**
Similar patterns found across plugins create maintenance overhead.

**Examples:**
- Message buffering logic in telegram plugins
- Settings validation patterns
- Database operation patterns

**Recommended Actions:**
- [ ] Extract common functionality into shared utilities
- [ ] Create base classes for common plugin patterns
- [ ] Implement mixins for repeated functionality
- [ ] Document common patterns

**Audit Reference:** AUDIT_RECOMMENDATIONS.md - Code Quality Recommendations #2

---

### 🚀 DevOps Issues

#### Issue #11: Add containerization support
**Labels:** `devops`, `medium-priority`, `docker`

**Description:**
No Docker configuration found, limiting deployment options.

**Recommended Actions:**
- [ ] Create Docker containers for the application
- [ ] Support both single-agent and multi-agent deployments
- [ ] Add Docker Compose for development environments
- [ ] Create deployment documentation

**Files to Create:**
- Dockerfile
- docker-compose.yml
- .dockerignore
- Docker deployment documentation

**Audit Reference:** AUDIT_RECOMMENDATIONS.md - DevOps Recommendations #1

---

#### Issue #12: Implement CI/CD pipeline
**Labels:** `devops`, `high-priority`, `automation`

**Description:**
No CI/CD configuration found, requiring manual testing and deployment.

**Recommended Actions:**
- [ ] Add GitHub Actions workflow
- [ ] Include automated testing, linting, and security scanning
- [ ] Add automated deployment strategies
- [ ] Set up code quality gates

**Files to Create:**
- .github/workflows/ci.yml
- .github/workflows/cd.yml
- Pre-commit configuration

**Audit Reference:** AUDIT_RECOMMENDATIONS.md - DevOps Recommendations #2

---

#### Issue #13: Pin dependency versions
**Labels:** `dependencies`, `high-priority`, `security`

**Description:**
requirements.txt doesn't pin versions, creating potential security and stability issues.

**Current Issue:**
```
telethon
python-dotenv
sqlalchemy
# ... other unpinned dependencies
```

**Recommended Actions:**
- [ ] Pin all dependency versions
- [ ] Use requirements-dev.txt for development dependencies
- [ ] Implement dependency vulnerability scanning
- [ ] Set up automated dependency updates

**Files to Modify:**
- requirements.txt
- Create requirements-dev.txt

**Audit Reference:** AUDIT_RECOMMENDATIONS.md - Dependency Management #1

---

### 📝 Documentation Issues

#### Issue #14: Enhance developer documentation
**Labels:** `documentation`, `medium-priority`, `developer-experience`

**Description:**
While good documentation exists, it could be enhanced for better developer experience.

**Recommended Actions:**
- [ ] Add API documentation with OpenAPI/Swagger
- [ ] Include code examples in all docstrings
- [ ] Add architecture decision records (ADRs)
- [ ] Create troubleshooting guides
- [ ] Add developer onboarding guide

**Files to Create/Modify:**
- docs/api/ (new directory)
- docs/adrs/ (new directory)
- docs/troubleshooting.md
- docs/developer-guide.md

**Audit Reference:** AUDIT_RECOMMENDATIONS.md - Documentation Improvements

---

## LOW PRIORITY ISSUES

### 📊 Monitoring Issues

#### Issue #15: Add monitoring and observability
**Labels:** `monitoring`, `low-priority`, `observability`

**Description:**
Missing monitoring and observability features for production deployments.

**Recommended Actions:**
- [ ] Add health check endpoints
- [ ] Implement metrics collection (Prometheus)
- [ ] Add distributed tracing
- [ ] Create monitoring dashboards

**Audit Reference:** AUDIT_RECOMMENDATIONS.md - Monitoring and Observability

---

#### Issue #16: Implement backup and recovery procedures
**Labels:** `backup`, `low-priority`, `reliability`

**Description:**
No automated backup and recovery procedures documented or implemented.

**Recommended Actions:**
- [ ] Implement automated database backups
- [ ] Add backup verification and restore testing
- [ ] Document disaster recovery procedures
- [ ] Test backup/restore processes

**Audit Reference:** AUDIT_RECOMMENDATIONS.md - Backup and Recovery

---

## Issue Creation Instructions

### For Repository Maintainers:

1. **Enable Issues**: Go to repository Settings → Features → Enable Issues
2. **Create Labels**: Set up the following labels:
   - `security` (red)
   - `high-priority` (red)
   - `medium-priority` (orange)
   - `low-priority` (green)
   - `architecture` (blue)
   - `testing` (purple)
   - `performance` (yellow)
   - `devops` (gray)
   - `documentation` (light blue)
   - `code-quality` (pink)

3. **Create Issues**: Copy each issue section above and create individual GitHub issues
4. **Assign Milestones**: Consider creating milestones for different priority levels
5. **Link to Audit**: Reference the AUDIT_RECOMMENDATIONS.md file in each issue

### Using GitHub CLI (once issues are enabled):

```bash
# Example command to create an issue
gh issue create \
  --title "🔒 [SECURITY] Create .env.example template and improve credential management" \
  --body "$(cat issue-content.md)" \
  --label "security,high-priority,documentation"
```

---

**Total Issues to Create: 16**
- High Priority: 6 issues
- Medium Priority: 8 issues  
- Low Priority: 2 issues

These issues represent actionable items from the comprehensive codebase audit and will help improve the security, reliability, and maintainability of Sanctum: Broca 2.