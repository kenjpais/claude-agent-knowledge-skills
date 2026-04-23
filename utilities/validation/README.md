# Validation Utilities

Python utilities for validating agentic documentation quality.

## Usage

### Navigation Depth Checker

```python
from pathlib import Path
from utilities.validation.validator import NavigationDepthChecker

checker = NavigationDepthChecker(
    root_file=Path("AGENTS.md"),
    max_depth=3
)

result = checker.check(agentic_dir=Path("agentic/"))

if not result.passed:
    print("Navigation violations:")
    for violation in result.violations:
        print(f"  - {violation}")
        
print(f"Max depth found: {result.metadata['max_depth_found']}")
print(f"Orphaned files: {result.metadata['orphaned_files']}")
```

### Link Validator

```python
from pathlib import Path
from utilities.validation.validator import LinkValidator

validator = LinkValidator()
result = validator.check(docs_dir=Path("agentic/"))

if not result.passed:
    print("Broken links:")
    for link in result.violations:
        print(f"  - {link}")
```

### Quality Score Calculator

```python
from pathlib import Path
from utilities.validation.validator import QualityScoreCalculator

calculator = QualityScoreCalculator(
    repo_path=Path("."),
    agentic_dir=Path("agentic/")
)

scores = calculator.calculate()

print(f"Overall Quality Score: {scores['overall_score']}/100")
print(f"Passed: {scores['passed']}")
print(f"Completeness: {scores['completeness']['score']}/20")
print(f"Navigation: {scores['navigation']['score']}/10")
print(f"Linkage: {scores['linkage']['score']}/10")
```

## Integration with Claude Skills

These utilities are used by the validation skills:
- `check-navigation-depth` → Uses `NavigationDepthChecker`
- `check-quality-score` → Uses `QualityScoreCalculator`

The validator agent calls these utilities to perform quality checks.
