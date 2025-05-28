#!/bin/bash

# Script to test all GitHub Actions workflows locally using act

# Default values
VERBOSE=false
TIMEOUT=600  # Default timeout in seconds (10 minutes)
SKIP_WORKFLOWS=""
TEST_ONLY=""
ACT_IMAGE="ghcr.io/catthehacker/ubuntu:act-latest"
JOB=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -t|--timeout)
            TIMEOUT="$2"
            shift 2
            ;;
        -s|--skip)
            SKIP_WORKFLOWS="$2"
            shift 2
            ;;
        -w|--test-only)
            TEST_ONLY="$2"
            shift 2
            ;;
        -j|--job)
            JOB="$2"
            shift 2
            ;;
        -i|--image)
            ACT_IMAGE="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [options]"
            echo "Options:"
            echo "  -v, --verbose     Show detailed output from tests"
            echo "  -t, --timeout     Set timeout in seconds (default: 600)"
            echo "  -s, --skip        Comma-separated list of workflows to skip"
            echo "  -w, --test-only   Comma-separated list of workflows to test"
            echo "  -j, --job         Specific job to run in the workflow"
            echo "  -i, --image       Docker image to use with act (default: ghcr.io/catthehacker/ubuntu:act-latest)"
            echo "  -h, --help        Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Check if act is installed
if ! command -v act &> /dev/null; then
    echo "Error: 'act' is not installed. Please install it first."
    echo "Visit https://github.com/nektos/act for installation instructions."
    exit 1
fi

ROOT_DIR="$(pwd)"
echo "Starting GitHub Actions tests from root directory: $ROOT_DIR"

# Find all GitHub Actions workflow files
WORKFLOWS=$(find "$ROOT_DIR" -path "*/.github/workflows/*.yml" -o -path "*/.github/workflows/*.yaml" | grep -v "node_modules")

# Counter for results
TOTAL=0
PASSED=0
FAILED=0
SKIPPED=0
TIMEOUT_COUNT=0

echo "Found $(echo "$WORKFLOWS" | wc -l) GitHub Actions workflow files"

# Convert comma-separated lists to arrays
IFS=',' read -ra SKIP_ARRAY <<< "$SKIP_WORKFLOWS"
IFS=',' read -ra TEST_ONLY_ARRAY <<< "$TEST_ONLY"

# Create arrays for tracking
declare -a PASSED_WORKFLOWS
declare -a FAILED_WORKFLOWS
declare -a SKIPPED_WORKFLOWS
declare -a TIMEOUT_WORKFLOWS

echo "----------------------------------------"

# Process each workflow file
for workflow in $WORKFLOWS; do
    rel_path=${workflow#$ROOT_DIR/}
    project=$(echo "$rel_path" | cut -d'/' -f1)
    workflow_name=$(basename "$workflow")
    workflow_id="$project/$workflow_name"
    
    # Check if we should skip this workflow
    skip=false
    if [[ -n "$SKIP_WORKFLOWS" ]]; then
        for skip_workflow in "${SKIP_ARRAY[@]}"; do
            if [[ "$workflow_id" == *"$skip_workflow"* ]]; then
                skip=true
                break
            fi
        done
    fi
    
    # Check if we should only test specific workflows
    if [[ -n "$TEST_ONLY" ]]; then
        skip=true
        for test_workflow in "${TEST_ONLY_ARRAY[@]}"; do
            if [[ "$workflow_id" == *"$test_workflow"* ]]; then
                skip=false
                break
            fi
        done
    fi
    
    if [[ "$skip" == true ]]; then
        echo -e "\nSkipping workflow: $workflow_id"
        SKIPPED=$((SKIPPED+1))
        SKIPPED_WORKFLOWS+=("$workflow_id")
        continue
    fi
    
    echo -e "\nTesting workflow: $workflow_id"
    echo "File: $workflow"
    
    # Change to the project directory
    project_dir="$ROOT_DIR/$project"
    cd "$project_dir"
    
    # Build the act command
    act_cmd="act"
    
    # Add workflow file
    act_cmd="$act_cmd -W .github/workflows/$(basename "$workflow")"
    
    # Add job if specified
    if [[ -n "$JOB" ]]; then
        act_cmd="$act_cmd -j $JOB"
    fi
    
    # Add platform
    act_cmd="$act_cmd -P ubuntu-latest=$ACT_IMAGE"
    
    # Add verbose flag if needed
    if [[ "$VERBOSE" == true ]]; then
        act_cmd="$act_cmd -v"
    fi
    
    echo "Running: $act_cmd"
    
    # Create a log file
    log_file="$ROOT_DIR/tests/act_logs_$(basename "$workflow" .yml).log"
    mkdir -p "$(dirname "$log_file")"
    
    # Run the act command with timeout
    if [[ "$VERBOSE" == true ]]; then
        # Run with full output
        if timeout $TIMEOUT bash -c "$act_cmd" 2>&1 | tee "$log_file"; then
            echo "✅ Workflow passed: $workflow_id"
            PASSED=$((PASSED+1))
            PASSED_WORKFLOWS+=("$workflow_id")
        else
            exit_code=$?
            if [ $exit_code -eq 124 ]; then
                echo "⏱️ Workflow timed out: $workflow_id after ${TIMEOUT}s"
                TIMEOUT_COUNT=$((TIMEOUT_COUNT+1))
                TIMEOUT_WORKFLOWS+=("$workflow_id")
            else
                echo "❌ Workflow failed: $workflow_id (exit code: $exit_code)"
                FAILED=$((FAILED+1))
                FAILED_WORKFLOWS+=("$workflow_id")
            fi
        fi
    else
        # Run with minimal output
        if timeout $TIMEOUT bash -c "$act_cmd" > "$log_file" 2>&1; then
            echo "✅ Workflow passed: $workflow_id"
            PASSED=$((PASSED+1))
            PASSED_WORKFLOWS+=("$workflow_id")
        else
            exit_code=$?
            if [ $exit_code -eq 124 ]; then
                echo "⏱️ Workflow timed out: $workflow_id after ${TIMEOUT}s"
                TIMEOUT_COUNT=$((TIMEOUT_COUNT+1))
                TIMEOUT_WORKFLOWS+=("$workflow_id")
            else
                echo "❌ Workflow failed: $workflow_id (exit code: $exit_code)"
                echo "See log file for details: $log_file"
                FAILED=$((FAILED+1))
                FAILED_WORKFLOWS+=("$workflow_id")
            fi
        fi
    fi
    
    # Return to the root directory
    cd "$ROOT_DIR"
    
    TOTAL=$((TOTAL+1))
    echo "----------------------------------------"
done

# Print summary
echo -e "\n📊 Test Summary:"
echo "Total workflows found: $((PASSED + FAILED + SKIPPED + TIMEOUT_COUNT))"
echo "Workflows tested: $TOTAL"
echo "Passed: $PASSED"
echo "Failed: $FAILED"
echo "Timed out: $TIMEOUT_COUNT"
echo "Skipped: $SKIPPED"

# Print detailed results
echo -e "\n📋 Detailed Results:"

if [[ ${#PASSED_WORKFLOWS[@]} -gt 0 ]]; then
    echo "✅ Passed workflows:"
    for workflow in "${PASSED_WORKFLOWS[@]}"; do
        echo "  - $workflow"
    done
fi

if [[ ${#FAILED_WORKFLOWS[@]} -gt 0 ]]; then
    echo "❌ Failed workflows:"
    for workflow in "${FAILED_WORKFLOWS[@]}"; do
        echo "  - $workflow"
    done
fi

if [[ ${#TIMEOUT_WORKFLOWS[@]} -gt 0 ]]; then
    echo "⏱️ Timed out workflows:"
    for workflow in "${TIMEOUT_WORKFLOWS[@]}"; do
        echo "  - $workflow"
    done
fi

if [[ ${#SKIPPED_WORKFLOWS[@]} -gt 0 ]]; then
    echo "⏭️ Skipped workflows:"
    for workflow in "${SKIPPED_WORKFLOWS[@]}"; do
        echo "  - $workflow"
    done
fi

# Create a report file
report_file="$ROOT_DIR/tests/github_actions_report.md"
echo "# GitHub Actions Workflow Test Report" > "$report_file"
echo "" >> "$report_file"
echo "Generated on: $(date)" >> "$report_file"
echo "" >> "$report_file"
echo "## Summary" >> "$report_file"
echo "" >> "$report_file"
echo "- Total workflows found: $((PASSED + FAILED + SKIPPED + TIMEOUT_COUNT))" >> "$report_file"
echo "- Workflows tested: $TOTAL" >> "$report_file"
echo "- Passed: $PASSED" >> "$report_file"
echo "- Failed: $FAILED" >> "$report_file"
echo "- Timed out: $TIMEOUT_COUNT" >> "$report_file"
echo "- Skipped: $SKIPPED" >> "$report_file"
echo "" >> "$report_file"

echo "## Detailed Results" >> "$report_file"
echo "" >> "$report_file"

if [[ ${#PASSED_WORKFLOWS[@]} -gt 0 ]]; then
    echo "### ✅ Passed workflows" >> "$report_file"
    echo "" >> "$report_file"
    for workflow in "${PASSED_WORKFLOWS[@]}"; do
        echo "- $workflow" >> "$report_file"
    done
    echo "" >> "$report_file"
fi

if [[ ${#FAILED_WORKFLOWS[@]} -gt 0 ]]; then
    echo "### ❌ Failed workflows" >> "$report_file"
    echo "" >> "$report_file"
    for workflow in "${FAILED_WORKFLOWS[@]}"; do
        echo "- $workflow" >> "$report_file"
    done
    echo "" >> "$report_file"
fi

if [[ ${#TIMEOUT_WORKFLOWS[@]} -gt 0 ]]; then
    echo "### ⏱️ Timed out workflows" >> "$report_file"
    echo "" >> "$report_file"
    for workflow in "${TIMEOUT_WORKFLOWS[@]}"; do
        echo "- $workflow" >> "$report_file"
    done
    echo "" >> "$report_file"
fi

echo "Report saved to: $report_file"

# Return exit code based on test results
if [[ $FAILED -eq 0 && $TIMEOUT_COUNT -eq 0 ]]; then
    echo -e "\n✅ All workflows passed!"
    exit 0
else
    echo -e "\n❌ Some workflows failed or timed out!"
    exit 1
fi
