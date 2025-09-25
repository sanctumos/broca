#!/bin/bash

# Script to create GitHub issues from audit recommendations
# This script requires GitHub CLI (gh) to be installed and authenticated
# Run this script after enabling issues on the repository

set -e

echo "🚀 Creating GitHub issues from audit recommendations..."

# Check if GitHub CLI is authenticated
if ! gh auth status >/dev/null 2>&1; then
    echo "❌ Error: GitHub CLI is not authenticated. Run 'gh auth login' first."
    exit 1
fi

# Check if issues are enabled on the repository
if [ "$(gh repo view --json hasIssuesEnabled --jq '.hasIssuesEnabled')" = "false" ]; then
    echo "❌ Error: Issues are not enabled on this repository."
    echo "Please enable issues in the repository settings first."
    exit 1
fi

echo "✅ GitHub CLI authenticated and issues enabled. Creating issues..."

# HIGH PRIORITY ISSUES

echo "📋 Creating HIGH PRIORITY issues..."

# Issue #1: Environment Security
gh issue create \
  --title "🔒 [SECURITY] Create .env.example template and improve credential management" \
  --label "security,high-priority,documentation" \
  --body "## Priority: HIGH

### Description
Missing .env.example file creates security risk where developers may commit real credentials to the repository.

### Issues Identified
- No .env.example template for developers
- Risk of credential exposure in commits
- Missing environment variable validation on startup

### Recommended Actions
- [ ] Create .env.example with placeholder values for all required environment variables
- [ ] Ensure .env is in .gitignore
- [ ] Implement environment variable validation on startup
- [ ] Add documentation about proper credential management

### Implementation Details
Create a validation function in main.py to check for test/placeholder values in production.

### Files to Create/Modify
- .env.example (new)
- main.py (add validation)
- docs/configuration.md (update documentation)

### Audit Reference
See AUDIT_RECOMMENDATIONS.md - Security Recommendations #1"

echo "✅ Created issue: Environment Security"

# Issue #2: API Key Logging
gh issue create \
  --title "🔒 [SECURITY] Remove API key exposure in logs" \
  --label "security,high-priority,logging" \
  --body "## Priority: HIGH

### Description
API keys may be partially exposed in debug logs, creating security vulnerabilities.

### Current Issue
Found in runtime/core/letta_client.py:23 - API key logging in debug mode

### Recommended Actions
- [ ] Remove API key logging entirely in production
- [ ] Implement secure logging levels that exclude sensitive data
- [ ] Add configuration option to control sensitive data logging
- [ ] Review all logging statements for potential credential exposure

### Files to Modify
- runtime/core/letta_client.py
- common/logging.py
- All files with potential credential logging

### Audit Reference
See AUDIT_RECOMMENDATIONS.md - Security Recommendations #2"

echo "✅ Created issue: API Key Logging Security"

# Issue #3: SQL Injection Prevention
gh issue create \
  --title "🔒 [SECURITY] Implement comprehensive SQL injection prevention" \
  --label "security,high-priority,database" \
  --body "## Priority: HIGH

### Description
While using SQLAlchemy, some raw SQL queries were found that could pose security risks.

### Current Issues
- Raw SQL queries in database operations
- Need for consistent parameterized query usage
- Missing input validation for database operations

### Recommended Actions
- [ ] Review all database operations for SQL injection risks
- [ ] Ensure parameterized queries are used consistently
- [ ] Add input validation for all database operations
- [ ] Implement database security best practices

### Files to Review
- database/operations/*.py
- All files with database queries

### Audit Reference
See AUDIT_RECOMMENDATIONS.md - Security Recommendations #3"

echo "✅ Created issue: SQL Injection Prevention"

# Issue #4: Error Handling
gh issue create \
  --title "🏗️ [ARCHITECTURE] Standardize error handling across the codebase" \
  --label "architecture,high-priority,error-handling" \
  --body "## Priority: HIGH

### Description
Inconsistent error handling patterns across the codebase make debugging and maintenance difficult.

### Current Issues
- Generic exception handling in multiple places
- No centralized error handling system
- Missing error context and recovery suggestions

### Recommended Actions
- [ ] Implement a centralized error handling system
- [ ] Create custom exception classes for different error types
- [ ] Add error context and recovery suggestions
- [ ] Standardize error logging format

### Files to Modify
- common/exceptions.py (expand)
- All modules with exception handling

### Audit Reference
See AUDIT_RECOMMENDATIONS.md - Architecture Recommendations #1"

echo "✅ Created issue: Error Handling Standardization"

# Issue #5: Configuration Management
gh issue create \
  --title "🏗️ [ARCHITECTURE] Implement unified configuration management" \
  --label "architecture,high-priority,configuration" \
  --body "## Priority: HIGH

### Description
Settings are scattered across multiple files and formats, making configuration management complex.

### Current Issues
- settings.json for runtime settings
- Environment variables for secrets
- Plugin-specific configuration files
- No configuration validation

### Recommended Actions
- [ ] Implement a unified configuration management system
- [ ] Add configuration validation with schemas using Pydantic
- [ ] Support configuration hot-reloading for all components
- [ ] Create centralized configuration documentation

### Files to Create/Modify
- common/config.py (enhance)
- New configuration schema files
- All modules that use configuration

### Audit Reference
See AUDIT_RECOMMENDATIONS.md - Architecture Recommendations #2"

echo "✅ Created issue: Configuration Management"

# Issue #6: Test Coverage
gh issue create \
  --title "🧪 [TESTING] Implement comprehensive test coverage" \
  --label "testing,high-priority,quality" \
  --body "## Priority: HIGH

### Description
Limited test coverage (only 9 test files found) creates maintenance and reliability risks.

### Current Status
- Some plugins have tests (telegram_bot)
- Core functionality appears under-tested
- Integration tests missing
- No end-to-end testing

### Recommended Actions
- [ ] Achieve minimum 80% test coverage for core components
- [ ] Add integration tests for plugin system
- [ ] Implement end-to-end testing scenarios
- [ ] Set up automated test reporting

### Audit Reference
See AUDIT_RECOMMENDATIONS.md - Testing Recommendations #1"

echo "✅ Created issue: Test Coverage"

# Issue #7: CI/CD Pipeline
gh issue create \
  --title "🚀 [DEVOPS] Implement CI/CD pipeline" \
  --label "devops,high-priority,automation" \
  --body "## Priority: HIGH

### Description
No CI/CD configuration found, requiring manual testing and deployment.

### Recommended Actions
- [ ] Add GitHub Actions workflow
- [ ] Include automated testing, linting, and security scanning
- [ ] Add automated deployment strategies
- [ ] Set up code quality gates

### Files to Create
- .github/workflows/ci.yml
- .github/workflows/cd.yml
- Pre-commit configuration

### Audit Reference
See AUDIT_RECOMMENDATIONS.md - DevOps Recommendations #2"

echo "✅ Created issue: CI/CD Pipeline"

# MEDIUM PRIORITY ISSUES

echo "📋 Creating MEDIUM PRIORITY issues..."

# Issue #8: Database Connection Pooling
gh issue create \
  --title "⚡ [PERFORMANCE] Implement database connection pooling" \
  --label "performance,medium-priority,database" \
  --body "## Priority: MEDIUM

### Description
No evidence of connection pooling in database operations, which can impact performance under load.

### Recommended Actions
- [ ] Implement SQLAlchemy connection pooling
- [ ] Add connection health checks
- [ ] Monitor and optimize query performance
- [ ] Add database performance metrics

### Audit Reference
See AUDIT_RECOMMENDATIONS.md - Performance Recommendations #1"

echo "✅ Created issue: Database Connection Pooling"

# Issue #9: Message Processing Concurrency
gh issue create \
  --title "⚡ [PERFORMANCE] Optimize message processing with concurrency" \
  --label "performance,medium-priority,async" \
  --body "## Priority: MEDIUM

### Description
Sequential message processing in queue processor limits throughput.

### Current Issue
Messages are processed one at a time in the queue processor loop.

### Recommended Actions
- [ ] Implement concurrent message processing with limits
- [ ] Add message batching capabilities
- [ ] Optimize database queries with bulk operations
- [ ] Add performance monitoring

### Files to Modify
- runtime/core/queue.py

### Audit Reference
See AUDIT_RECOMMENDATIONS.md - Performance Recommendations #2"

echo "✅ Created issue: Message Processing Concurrency"

# Issue #10: Type Annotations
gh issue create \
  --title "🛠️ [CODE-QUALITY] Add comprehensive type annotations" \
  --label "code-quality,medium-priority,types" \
  --body "## Priority: MEDIUM

### Description
Partially implemented type annotations with inconsistent coverage across the codebase.

### Recommended Actions
- [ ] Add comprehensive type annotations to all modules
- [ ] Use mypy for static type checking
- [ ] Add type checking to CI/CD pipeline
- [ ] Create type checking configuration

### Files to Modify
- All Python files lacking proper type annotations
- Setup mypy configuration

### Audit Reference
See AUDIT_RECOMMENDATIONS.md - Code Quality Recommendations #1"

echo "✅ Created issue: Type Annotations"

# Issue #11: Code Duplication
gh issue create \
  --title "🛠️ [CODE-QUALITY] Reduce code duplication across plugins" \
  --label "code-quality,medium-priority,refactoring" \
  --body "## Priority: MEDIUM

### Description
Similar patterns found across plugins create maintenance overhead.

### Examples
- Message buffering logic in telegram plugins
- Settings validation patterns
- Database operation patterns

### Recommended Actions
- [ ] Extract common functionality into shared utilities
- [ ] Create base classes for common plugin patterns
- [ ] Implement mixins for repeated functionality
- [ ] Document common patterns

### Audit Reference
See AUDIT_RECOMMENDATIONS.md - Code Quality Recommendations #2"

echo "✅ Created issue: Code Duplication Reduction"

# Issue #12: Containerization
gh issue create \
  --title "🚀 [DEVOPS] Add containerization support" \
  --label "devops,medium-priority,docker" \
  --body "## Priority: MEDIUM

### Description
No Docker configuration found, limiting deployment options.

### Recommended Actions
- [ ] Create Docker containers for the application
- [ ] Support both single-agent and multi-agent deployments
- [ ] Add Docker Compose for development environments
- [ ] Create deployment documentation

### Files to Create
- Dockerfile
- docker-compose.yml
- .dockerignore
- Docker deployment documentation

### Audit Reference
See AUDIT_RECOMMENDATIONS.md - DevOps Recommendations #1"

echo "✅ Created issue: Containerization Support"

# Issue #13: Dependency Pinning
gh issue create \
  --title "📦 [DEPENDENCIES] Pin dependency versions" \
  --label "dependencies,high-priority,security" \
  --body "## Priority: HIGH

### Description
requirements.txt doesn't pin versions, creating potential security and stability issues.

### Current Issue
All dependencies are unpinned (telethon, python-dotenv, sqlalchemy, etc.)

### Recommended Actions
- [ ] Pin all dependency versions
- [ ] Use requirements-dev.txt for development dependencies
- [ ] Implement dependency vulnerability scanning
- [ ] Set up automated dependency updates

### Files to Modify
- requirements.txt
- Create requirements-dev.txt

### Audit Reference
See AUDIT_RECOMMENDATIONS.md - Dependency Management #1"

echo "✅ Created issue: Dependency Version Pinning"

# LOW PRIORITY ISSUES

echo "📋 Creating LOW PRIORITY issues..."

# Issue #14: Documentation Enhancement
gh issue create \
  --title "📝 [DOCUMENTATION] Enhance developer documentation" \
  --label "documentation,medium-priority,developer-experience" \
  --body "## Priority: MEDIUM

### Description
While good documentation exists, it could be enhanced for better developer experience.

### Recommended Actions
- [ ] Add API documentation with OpenAPI/Swagger
- [ ] Include code examples in all docstrings
- [ ] Add architecture decision records (ADRs)
- [ ] Create troubleshooting guides
- [ ] Add developer onboarding guide

### Files to Create/Modify
- docs/api/ (new directory)
- docs/adrs/ (new directory)
- docs/troubleshooting.md
- docs/developer-guide.md

### Audit Reference
See AUDIT_RECOMMENDATIONS.md - Documentation Improvements"

echo "✅ Created issue: Documentation Enhancement"

# Issue #15: Monitoring
gh issue create \
  --title "📊 [MONITORING] Add monitoring and observability" \
  --label "monitoring,low-priority,observability" \
  --body "## Priority: LOW

### Description
Missing monitoring and observability features for production deployments.

### Recommended Actions
- [ ] Add health check endpoints
- [ ] Implement metrics collection (Prometheus)
- [ ] Add distributed tracing
- [ ] Create monitoring dashboards

### Audit Reference
See AUDIT_RECOMMENDATIONS.md - Monitoring and Observability"

echo "✅ Created issue: Monitoring and Observability"

# Issue #16: Backup and Recovery
gh issue create \
  --title "💾 [BACKUP] Implement backup and recovery procedures" \
  --label "backup,low-priority,reliability" \
  --body "## Priority: LOW

### Description
No automated backup and recovery procedures documented or implemented.

### Recommended Actions
- [ ] Implement automated database backups
- [ ] Add backup verification and restore testing
- [ ] Document disaster recovery procedures
- [ ] Test backup/restore processes

### Audit Reference
See AUDIT_RECOMMENDATIONS.md - Backup and Recovery"

echo "✅ Created issue: Backup and Recovery"

echo ""
echo "🎉 Successfully created all audit issues!"
echo ""
echo "Summary:"
echo "- High Priority Issues: 7"
echo "- Medium Priority Issues: 7" 
echo "- Low Priority Issues: 2"
echo "- Total Issues Created: 16"
echo ""
echo "Next steps:"
echo "1. Review the created issues in the GitHub repository"
echo "2. Assign team members to appropriate issues"
echo "3. Create milestones for different priority levels"
echo "4. Start implementing based on priority and business needs"
echo ""
echo "For detailed information, see:"
echo "- AUDIT_RECOMMENDATIONS.md (comprehensive audit report)"
echo "- .github/ISSUES_TO_CREATE.md (structured issue templates)"