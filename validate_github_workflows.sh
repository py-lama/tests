#!/bin/bash

# Script to validate GitHub Actions workflow files

# Default values
VERBOSE=false
FIX_ISSUES=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -f|--fix)
            FIX_ISSUES=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [options]"
            echo "Options:"
            echo "  -v, --verbose     Show detailed output"
            echo "  -f, --fix         Attempt to fix common issues"
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

ROOT_DIR="$(pwd)"
echo "Starting GitHub Actions workflow validation from root directory: $ROOT_DIR"

# Find all GitHub Actions workflow files
WORKFLOWS=$(find "$ROOT_DIR" -path "*/.github/workflows/*.yml" -o -path "*/.github/workflows/*.yaml" | grep -v "node_modules")

# Counter for results
TOTAL=0
VALID=0
INVALID=0
FIXED=0

echo "Found $(echo "$WORKFLOWS" | wc -l) GitHub Actions workflow files"

# Create arrays for tracking
declare -a VALID_WORKFLOWS
declare -a INVALID_WORKFLOWS
declare -a FIXED_WORKFLOWS

echo "----------------------------------------"

# Check if actionlint is installed
if ! command -v actionlint &> /dev/null; then
    echo "actionlint not found. Installing..."
    # Try to install actionlint
    if command -v go &> /dev/null; then
        go install github.com/rhysd/actionlint/cmd/actionlint@latest
    else
        echo "Warning: Go is not installed. Using alternative installation method..."
        bash <(curl https://raw.githubusercontent.com/rhysd/actionlint/main/scripts/download-actionlint.bash)
        chmod +x ./actionlint
        sudo mv ./actionlint /usr/local/bin/
    fi
fi

# Process each workflow file
for workflow in $WORKFLOWS; do
    rel_path=${workflow#$ROOT_DIR/}
    project=$(echo "$rel_path" | cut -d'/' -f1)
    workflow_name=$(basename "$workflow")
    workflow_id="$project/$workflow_name"
    
    echo -e "\nValidating workflow: $workflow_id"
    echo "File: $workflow"
    
    # Validate the workflow file with actionlint
    if command -v actionlint &> /dev/null; then
        if [[ "$VERBOSE" == true ]]; then
            actionlint "$workflow"
            lint_result=$?
        else
            actionlint "$workflow" > /dev/null 2>&1
            lint_result=$?
        fi
        
        if [ $lint_result -eq 0 ]; then
            echo "✅ Workflow is valid: $workflow_id"
            VALID=$((VALID+1))
            VALID_WORKFLOWS+=("$workflow_id")
        else
            echo "❌ Workflow has issues: $workflow_id"
            INVALID=$((INVALID+1))
            INVALID_WORKFLOWS+=("$workflow_id")
            
            # Show detailed errors if not in verbose mode
            if [[ "$VERBOSE" != true ]]; then
                echo "Errors:"
                actionlint "$workflow"
            fi
            
            # Try to fix common issues
            if [[ "$FIX_ISSUES" == true ]]; then
                echo "Attempting to fix issues..."
                
                # Check for common issues and fix them
                fixed=false
                
                # 1. Check for outdated actions
                if grep -q "uses: actions/checkout@v1\|uses: actions/checkout@v2\|uses: actions/checkout@v3" "$workflow"; then
                    echo "Updating actions/checkout to v4"
                    sed -i 's/uses: actions\/checkout@v[123]/uses: actions\/checkout@v4/g' "$workflow"
                    fixed=true
                fi
                
                if grep -q "uses: actions/setup-python@v1\|uses: actions/setup-python@v2\|uses: actions/setup-python@v3\|uses: actions/setup-python@v4" "$workflow"; then
                    echo "Updating actions/setup-python to v5"
                    sed -i 's/uses: actions\/setup-python@v[1234]/uses: actions\/setup-python@v5/g' "$workflow"
                    fixed=true
                fi
                
                # 2. Check for outdated artifact actions
                if grep -q "uses: actions/upload-artifact@v1\|uses: actions/upload-artifact@v2\|uses: actions/upload-artifact@v3" "$workflow"; then
                    echo "Updating actions/upload-artifact to v4"
                    sed -i 's/uses: actions\/upload-artifact@v[123]/uses: actions\/upload-artifact@v4/g' "$workflow"
                    fixed=true
                fi
                
                # 3. Add timeout to jobs
                if ! grep -q "timeout-minutes:" "$workflow"; then
                    echo "Adding timeout-minutes to jobs"
                    sed -i '/runs-on:/a\    timeout-minutes: 15  # Add timeout to prevent hanging jobs' "$workflow"
                    fixed=true
                fi
                
                # 4. Check if workflow was fixed
                if [[ "$fixed" == true ]]; then
                    echo "Re-validating workflow after fixes..."
                    
                    if actionlint "$workflow" > /dev/null 2>&1; then
                        echo "✅ Workflow fixed: $workflow_id"
                        FIXED=$((FIXED+1))
                        FIXED_WORKFLOWS+=("$workflow_id")
                        INVALID=$((INVALID-1))
                        
                        # Remove from invalid workflows
                        for i in "${!INVALID_WORKFLOWS[@]}"; do
                            if [[ "${INVALID_WORKFLOWS[$i]}" = "$workflow_id" ]]; then
                                unset 'INVALID_WORKFLOWS[$i]'
                            fi
                        done
                    else
                        echo "⚠️ Workflow still has issues after fixes"
                    fi
                fi
            fi
        fi
    else
        echo "⚠️ actionlint not available, skipping validation"
    fi
    
    TOTAL=$((TOTAL+1))
    echo "----------------------------------------"
done

# Print summary
echo -e "\n📊 Validation Summary:"
echo "Total workflows: $TOTAL"
echo "Valid: $VALID"
echo "Invalid: $INVALID"
if [[ "$FIX_ISSUES" == true ]]; then
    echo "Fixed: $FIXED"
fi

# Print detailed results
echo -e "\n📋 Detailed Results:"

if [[ ${#VALID_WORKFLOWS[@]} -gt 0 ]]; then
    echo "✅ Valid workflows:"
    for workflow in "${VALID_WORKFLOWS[@]}"; do
        echo "  - $workflow"
    done
fi

if [[ ${#INVALID_WORKFLOWS[@]} -gt 0 ]]; then
    echo "❌ Invalid workflows:"
    for workflow in "${INVALID_WORKFLOWS[@]}"; do
        echo "  - $workflow"
    done
fi

if [[ "$FIX_ISSUES" == true && ${#FIXED_WORKFLOWS[@]} -gt 0 ]]; then
    echo "🔧 Fixed workflows:"
    for workflow in "${FIXED_WORKFLOWS[@]}"; do
        echo "  - $workflow"
    done
fi

# Create a report file
report_file="$ROOT_DIR/tests/github_workflows_validation_report.md"
echo "# GitHub Actions Workflow Validation Report" > "$report_file"
echo "" >> "$report_file"
echo "Generated on: $(date)" >> "$report_file"
echo "" >> "$report_file"
echo "## Summary" >> "$report_file"
echo "" >> "$report_file"
echo "- Total workflows: $TOTAL" >> "$report_file"
echo "- Valid: $VALID" >> "$report_file"
echo "- Invalid: $INVALID" >> "$report_file"
if [[ "$FIX_ISSUES" == true ]]; then
    echo "- Fixed: $FIXED" >> "$report_file"
fi
echo "" >> "$report_file"

echo "## Detailed Results" >> "$report_file"
echo "" >> "$report_file"

if [[ ${#VALID_WORKFLOWS[@]} -gt 0 ]]; then
    echo "### ✅ Valid workflows" >> "$report_file"
    echo "" >> "$report_file"
    for workflow in "${VALID_WORKFLOWS[@]}"; do
        echo "- $workflow" >> "$report_file"
    done
    echo "" >> "$report_file"
fi

if [[ ${#INVALID_WORKFLOWS[@]} -gt 0 ]]; then
    echo "### ❌ Invalid workflows" >> "$report_file"
    echo "" >> "$report_file"
    for workflow in "${INVALID_WORKFLOWS[@]}"; do
        echo "- $workflow" >> "$report_file"
    done
    echo "" >> "$report_file"
fi

if [[ "$FIX_ISSUES" == true && ${#FIXED_WORKFLOWS[@]} -gt 0 ]]; then
    echo "### 🔧 Fixed workflows" >> "$report_file"
    echo "" >> "$report_file"
    for workflow in "${FIXED_WORKFLOWS[@]}"; do
        echo "- $workflow" >> "$report_file"
    done
    echo "" >> "$report_file"
fi

echo "Report saved to: $report_file"

# Return exit code based on validation results
if [[ $INVALID -eq 0 ]]; then
    echo -e "\n✅ All workflows are valid!"
    exit 0
else
    echo -e "\n❌ Some workflows have issues!"
    exit 1
fi
