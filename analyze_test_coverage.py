#!/usr/bin/env python3
"""
Test Coverage Analysis Script

Analyzes test coverage across unit, integration, and e2e test categories.
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any


def run_coverage(category: str, test_path: str) -> Dict[str, Any]:
    """Run coverage for a specific test category."""
    print(f"\n{'='*70}")
    print(f"Running coverage analysis for {category.upper()} tests")
    print(f"{'='*70}\n")
    
    # Run pytest with coverage (including branch coverage)
    cmd = [
        sys.executable, "-m", "pytest",
        "--cov=.",
        "--cov-branch",
        "--cov-report=json",
        "--cov-report=term",
        "--cov-report=term-missing",
        test_path,
        "-q"
    ]
    
    result = subprocess.run(
        cmd,
        cwd=Path(__file__).parent,
        capture_output=True,
        text=True
    )
    
    # Parse coverage JSON
    coverage_data = {}
    coverage_file = Path(__file__).parent / "coverage.json"
    
    if coverage_file.exists():
        with open(coverage_file, 'r') as f:
            coverage_data = json.load(f)
    
    return {
        "exit_code": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "coverage": coverage_data
    }


def extract_coverage_summary(coverage_data: Dict[str, Any]) -> Dict[str, Any]:
    """Extract coverage summary from coverage data."""
    if not coverage_data or "totals" not in coverage_data:
        return {
            "lines_covered": 0.0,
            "statements_covered": 0.0,
            "branches_covered": 0.0,
            "functions_covered": 0.0,
            "num_statements": 0,
            "num_branches": 0,
            "covered_lines": 0,
            "missing_lines": 0
        }
    
    totals = coverage_data["totals"]
    
    # Calculate branch coverage if available
    branch_coverage = 0.0
    if "num_branches" in totals and totals["num_branches"] > 0:
        covered_branches = totals.get("covered_branches", 0)
        branch_coverage = (covered_branches / totals["num_branches"]) * 100.0
    
    return {
        "lines_covered": totals.get("percent_covered", 0.0),
        "statements_covered": totals.get("percent_statements_covered", totals.get("percent_covered", 0.0)),
        "branches_covered": branch_coverage,
        "functions_covered": totals.get("percent_covered_functions", 0.0),
        "num_statements": totals.get("num_statements", 0),
        "num_branches": totals.get("num_branches", 0),
        "covered_lines": totals.get("covered_lines", 0),
        "missing_lines": totals.get("missing_lines", 0),
        "covered_branches": totals.get("covered_branches", 0)
    }


def get_file_coverage(coverage_data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """Get per-file coverage information."""
    if not coverage_data or "files" not in coverage_data:
        return {}
    
    file_coverage = {}
    for filepath, data in coverage_data["files"].items():
        # Only include source files, not test files
        if "test_" not in filepath and "/tests/" not in filepath:
            file_coverage[filepath] = {
                "percent_covered": data.get("summary", {}).get("percent_covered", 0.0),
                "num_statements": data.get("summary", {}).get("num_statements", 0),
                "missing_lines": data.get("missing_lines", [])
            }
    
    return file_coverage


def generate_report(results: Dict[str, Dict[str, Any]]) -> str:
    """Generate a comprehensive coverage report."""
    report = []
    report.append("\n" + "="*80)
    report.append("TEST COVERAGE ANALYSIS REPORT")
    report.append("="*80 + "\n")
    
    # Overall summary
    report.append("OVERALL SUMMARY")
    report.append("-"*80)
    
    all_categories = ["unit", "integration", "e2e"]
    for category in all_categories:
        if category in results:
            coverage = extract_coverage_summary(results[category]["coverage"])
            report.append(f"\n{category.upper()} Tests:")
            report.append(f"  Lines Covered:     {coverage['lines_covered']:.2f}% ({coverage['covered_lines']}/{coverage['covered_lines'] + coverage['missing_lines']} lines)")
            report.append(f"  Statements:        {coverage['statements_covered']:.2f}% ({coverage['num_statements']} total statements)")
            if coverage['num_branches'] > 0:
                report.append(f"  Branches:          {coverage['branches_covered']:.2f}% ({coverage['covered_branches']}/{coverage['num_branches']} branches)")
            else:
                report.append(f"  Branches:          N/A (branch coverage not measured)")
            report.append(f"  Functions:         {coverage['functions_covered']:.2f}%")
            report.append(f"  Exit Code:         {results[category]['exit_code']}")
            if results[category]['exit_code'] == 5:
                report.append(f"  Note:              No tests found in this category")
        else:
            report.append(f"\n{category.upper()} Tests: No tests found")
    
    # Detailed file coverage for unit tests (most comprehensive)
    if "unit" in results and results["unit"]["coverage"]:
        report.append("\n" + "="*80)
        report.append("DETAILED FILE COVERAGE (Unit Tests)")
        report.append("="*80 + "\n")
        
        file_coverage = get_file_coverage(results["unit"]["coverage"])
        
        # Sort by coverage percentage
        sorted_files = sorted(
            file_coverage.items(),
            key=lambda x: x[1]["percent_covered"],
            reverse=True
        )
        
        report.append(f"{'File':<50} {'Coverage':<12} {'Statements':<12}")
        report.append("-"*80)
        
        for filepath, data in sorted_files[:30]:  # Top 30 files
            rel_path = filepath.replace(str(Path.cwd()) + "/", "")
            report.append(
                f"{rel_path:<50} {data['percent_covered']:>6.2f}%     "
                f"{data['num_statements']:>6}"
            )
        
        if len(sorted_files) > 30:
            report.append(f"\n... and {len(sorted_files) - 30} more files")
    
    # Files with zero or low coverage
    if "unit" in results and results["unit"]["coverage"]:
        report.append("\n" + "="*80)
        report.append("FILES WITH LOW COVERAGE (< 50%)")
        report.append("="*80 + "\n")
        
        file_coverage = get_file_coverage(results["unit"]["coverage"])
        low_coverage = [
            (f, d) for f, d in file_coverage.items()
            if d["percent_covered"] < 50.0
        ]
        
        if low_coverage:
            sorted_low = sorted(low_coverage, key=lambda x: x[1]["percent_covered"])
            report.append(f"{'File':<50} {'Coverage':<12}")
            report.append("-"*80)
            for filepath, data in sorted_low:
                rel_path = filepath.replace(str(Path.cwd()) + "/", "")
                report.append(
                    f"{rel_path:<50} {data['percent_covered']:>6.2f}%"
                )
        else:
            report.append("No files with low coverage found!")
    
    return "\n".join(report)


def main():
    """Main function."""
    results = {}
    
    # Run coverage for each category
    categories = {
        "unit": "tests/unit",
        "integration": "tests/integration",
        "e2e": "tests/e2e"
    }
    
    for category, test_path in categories.items():
        try:
            results[category] = run_coverage(category, test_path)
        except Exception as e:
            print(f"Error running {category} tests: {e}")
            results[category] = {
                "exit_code": 1,
                "stdout": "",
                "stderr": str(e),
                "coverage": {}
            }
    
    # Generate and print report
    report = generate_report(results)
    print(report)
    
    # Save report to file
    report_file = Path(__file__).parent / "test_coverage_report.txt"
    with open(report_file, 'w') as f:
        f.write(report)
    
    print(f"\n\nFull report saved to: {report_file}")
    
    # Also save JSON summary
    summary = {}
    for category in categories.keys():
        if category in results:
            summary[category] = extract_coverage_summary(results[category]["coverage"])
    
    summary_file = Path(__file__).parent / "test_coverage_summary.json"
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"Summary saved to: {summary_file}")


if __name__ == "__main__":
    main()
