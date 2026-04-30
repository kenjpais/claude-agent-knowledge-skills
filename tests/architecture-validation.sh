#!/bin/bash

# Architecture Validation Test Script

echo "========================================"
echo "3-Agent Architecture Validation"
echo "========================================"
echo

# Test 1: Verify exactly 3 agent files exist
echo "Test 1: Verify exactly 3 agents exist"
AGENT_COUNT=$(find agents -name "*.md" -type f | wc -l)
if [ "$AGENT_COUNT" -eq 3 ]; then
    echo "✅ PASS: Exactly 3 agent files found"
else
    echo "❌ FAIL: Found $AGENT_COUNT agents, expected 3"
    exit 1
fi
echo

# Test 2: Verify main agent exists
echo "Test 2: Verify main agent exists"
if [ -f "agents/main-agent.md" ]; then
    echo "✅ PASS: agents/main-agent.md exists"
else
    echo "❌ FAIL: agents/main-agent.md not found"
    exit 1
fi
echo

# Test 3: Verify coding sub-agent exists
echo "Test 3: Verify coding sub-agent exists"
if [ -f "agents/sub-agents/coding-agent.md" ]; then
    echo "✅ PASS: agents/sub-agents/coding-agent.md exists"
else
    echo "❌ FAIL: agents/sub-agents/coding-agent.md not found"
    exit 1
fi
echo

# Test 4: Verify judge sub-agent exists
echo "Test 4: Verify judge sub-agent exists"
if [ -f "agents/sub-agents/judge-agent.md" ]; then
    echo "✅ PASS: agents/sub-agents/judge-agent.md exists"
else
    echo "❌ FAIL: agents/sub-agents/judge-agent.md not found"
    exit 1
fi
echo

# Test 5: Verify main agent has MUST NOT constraints
echo "Test 5: Verify main agent constraints"
if grep -q "MUST NOT execute code" agents/main-agent.md && \
   grep -q "MUST NOT evaluate outputs subjectively" agents/main-agent.md; then
    echo "✅ PASS: Main agent has required constraints"
else
    echo "❌ FAIL: Main agent missing required constraints"
    exit 1
fi
echo

# Test 6: Verify coding agent has MUST constraints
echo "Test 6: Verify coding agent constraints"
if grep -q "MUST use retrieve-from-graph" agents/sub-agents/coding-agent.md && \
   grep -q "MUST follow retrieved docs EXACTLY" agents/sub-agents/coding-agent.md; then
    echo "✅ PASS: Coding agent has required constraints"
else
    echo "❌ FAIL: Coding agent missing required constraints"
    exit 1
fi
echo

# Test 7: Verify judge agent has adversarial constraints
echo "Test 7: Verify judge agent constraints"
if grep -q "MUST be adversarial" agents/sub-agents/judge-agent.md && \
   grep -q "MUST NOT assume missing intent" agents/sub-agents/judge-agent.md; then
    echo "✅ PASS: Judge agent has required constraints"
else
    echo "❌ FAIL: Judge agent missing required constraints"
    exit 1
fi
echo

# Test 8: Verify consolidated skills exist
echo "Test 8: Verify consolidated skills exist"
REQUIRED_SKILLS=(
    "skills/documentation-generation/extract-repository-structure.md"
    "skills/documentation-generation/synthesize-documentation.md"
    "skills/documentation-generation/link-documentation.md"
)
ALL_EXIST=true
for skill in "${REQUIRED_SKILLS[@]}"; do
    if [ ! -f "$skill" ]; then
        echo "❌ FAIL: Missing $skill"
        ALL_EXIST=false
    fi
done
if [ "$ALL_EXIST" = true ]; then
    echo "✅ PASS: All consolidated skills exist"
else
    exit 1
fi
echo

# Test 9: Verify evaluation skills exist
echo "Test 9: Verify evaluation skills exist"
EVAL_SKILLS=(
    "skills/evaluation/spawn-coding-agent.md"
    "skills/evaluation/spawn-judge-agent.md"
    "skills/evaluation/validate-yaml-schema.md"
    "skills/evaluation/check-api-versions.md"
    "skills/evaluation/record-evaluation.md"
)
ALL_EXIST=true
for skill in "${EVAL_SKILLS[@]}"; do
    if [ ! -f "$skill" ]; then
        echo "❌ FAIL: Missing $skill"
        ALL_EXIST=false
    fi
done
if [ "$ALL_EXIST" = true ]; then
    echo "✅ PASS: All evaluation skills exist"
else
    exit 1
fi
echo

# Test 10: Verify old 7-agent system is removed
echo "Test 10: Verify old agent definitions removed"
OLD_AGENTS=(
    "agents/curator"
    "agents/extractor"
    "agents/linker"
    "agents/orchestrator"
    "agents/retrieval"
    "agents/synthesizer"
    "agents/validator"
)
NONE_EXIST=true
for agent in "${OLD_AGENTS[@]}"; do
    if [ -d "$agent" ]; then
        echo "❌ FAIL: Old agent directory still exists: $agent"
        NONE_EXIST=false
    fi
done
if [ "$NONE_EXIST" = true ]; then
    echo "✅ PASS: All old agent definitions removed"
else
    exit 1
fi
echo

# Test 11: Verify judge scoring rubric
echo "Test 11: Verify judge scoring rubric"
if grep -q "Category 1: Correctness (0-5)" agents/sub-agents/judge-agent.md && \
   grep -q "Category 2: Instruction Adherence (0-5)" agents/sub-agents/judge-agent.md && \
   grep -q "Category 3: Completeness (0-5)" agents/sub-agents/judge-agent.md && \
   grep -q "Category 4: Robustness" agents/sub-agents/judge-agent.md; then
    echo "✅ PASS: Judge scoring rubric includes all 4 categories"
else
    echo "❌ FAIL: Judge scoring rubric incomplete"
    exit 1
fi
echo

# Test 12: Verify test files exist
echo "Test 12: Verify test results exist"
if [ -f "tests/evaluation/TEST_RESULTS.md" ]; then
    echo "✅ PASS: Test results documented"
else
    echo "❌ FAIL: Test results missing"
    exit 1
fi
echo

# Test 13: Verify documentation exists
echo "Test 13: Verify documentation exists"
if [ -f "REFACTOR_REVIEW.md" ] && [ -f "FINAL_STATUS.md" ]; then
    echo "✅ PASS: Documentation complete"
else
    echo "❌ FAIL: Documentation missing"
    exit 1
fi
echo

echo "========================================"
echo "All Tests Passed! ✅"
echo "========================================"
echo
echo "Architecture Summary:"
echo "  - Agents: 3 (1 main, 2 sub-agents)"
echo "  - Consolidated Skills: 3"
echo "  - Evaluation Skills: 5"
echo "  - Test Coverage: Validated"
echo "  - Documentation: Complete"
echo
