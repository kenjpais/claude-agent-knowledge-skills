#!/bin/bash

echo "========================================"
echo "Evaluation Loop Workflow Verification"
echo "========================================"
echo

# Test 1: Verify spawn-coding-agent references retrieve-from-graph
echo "Test 1: Spawn coding agent uses retrieve-from-graph"
if grep -q "retrieve-from-graph" skills/evaluation/spawn-coding-agent.md; then
    echo "✅ PASS: spawn-coding-agent mentions retrieve-from-graph"
else
    echo "❌ FAIL: spawn-coding-agent missing retrieve-from-graph reference"
    exit 1
fi
echo

# Test 2: Verify spawn-judge-agent uses validation skills
echo "Test 2: Spawn judge agent uses validation skills"
if grep -q "validate-yaml-schema" skills/evaluation/spawn-judge-agent.md && \
   grep -q "check-api-versions" skills/evaluation/spawn-judge-agent.md; then
    echo "✅ PASS: spawn-judge-agent references validation skills"
else
    echo "❌ FAIL: spawn-judge-agent missing validation skill references"
    exit 1
fi
echo

# Test 3: Verify main agent has evaluation loop pattern
echo "Test 3: Main agent has evaluation loop pattern"
if grep -q "Evaluation Loop" agents/main-agent.md; then
    echo "✅ PASS: Main agent defines evaluation loop"
else
    echo "❌ FAIL: Main agent missing evaluation loop pattern"
    exit 1
fi
echo

# Test 4: Verify retry logic with max 3 attempts
echo "Test 4: Verify retry logic (max 3 attempts)"
if grep -qE "(max 3|retry.*3|3.*retry)" agents/main-agent.md; then
    echo "✅ PASS: Main agent includes retry logic with max 3 attempts"
else
    echo "❌ FAIL: Main agent missing retry logic"
    exit 1
fi
echo

# Test 5: Verify judge outputs JSON
echo "Test 5: Verify judge outputs JSON only"
if grep -q "Output ONLY JSON" agents/sub-agents/judge-agent.md; then
    echo "✅ PASS: Judge agent outputs JSON only"
else
    echo "❌ FAIL: Judge agent missing JSON output requirement"
    exit 1
fi
echo

# Test 6: Verify pass threshold is 14/20 (70%)
echo "Test 6: Verify pass threshold"
if grep -qE "(14|70%)" agents/sub-agents/judge-agent.md; then
    echo "✅ PASS: Judge has correct pass threshold"
else
    echo "❌ FAIL: Judge missing correct pass threshold"
    exit 1
fi
echo

# Test 7: Verify record-evaluation stores to database
echo "Test 7: Verify evaluation recording"
if grep -qi "sqlite3\|data\.db" skills/evaluation/record-evaluation.md; then
    echo "✅ PASS: record-evaluation uses database storage"
else
    echo "❌ FAIL: record-evaluation missing database storage"
    exit 1
fi
echo

# Test 8: Verify validate-yaml-schema uses oc create
echo "Test 8: Verify YAML validation uses oc"
if grep -q "oc create --dry-run" skills/evaluation/validate-yaml-schema.md; then
    echo "✅ PASS: validate-yaml-schema uses oc create --dry-run"
else
    echo "❌ FAIL: validate-yaml-schema missing oc command"
    exit 1
fi
echo

# Test 9: Verify check-api-versions has stable APIs
echo "Test 9: Verify API version checking"
if grep -q "apps/v1" skills/evaluation/check-api-versions.md && \
   grep -q "deprecated" skills/evaluation/check-api-versions.md; then
    echo "✅ PASS: check-api-versions includes API references"
else
    echo "❌ FAIL: check-api-versions missing API references"
    exit 1
fi
echo

# Test 10: Verify test results document metrics
echo "Test 10: Verify test results metrics"
if grep -q "100%" tests/evaluation/TEST_RESULTS.md; then
    echo "✅ PASS: Test results show 100% metrics"
else
    echo "❌ FAIL: Test results missing key metrics"
    exit 1
fi
echo

echo "========================================"
echo "All Workflow Tests Passed! ✅"
echo "========================================"
echo
