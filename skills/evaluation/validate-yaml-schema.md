---
name: validate-yaml-schema
description: Validates Kubernetes/OpenShift YAML against schemas using oc create --dry-run
type: skill
category: evaluation
phase: validation
---

# Validate YAML Schema

## Purpose

Validates Kubernetes and OpenShift YAML manifests using `oc create --dry-run` to catch:
- Invalid API versions
- Missing required fields
- Type mismatches
- Invalid label selectors
- Broken references

## When to Use

- During judge sub-agent evaluation (robustness scoring)
- Before deploying manifests
- In CI/CD validation pipelines

## Input

```yaml
yaml_content: string  # YAML manifest content
validation_mode: client | server
  # client: Client-side validation only (fast)
  # server: Server-side validation (requires cluster access)
context: string  # Optional: kubeconfig context to use
```

## Output

```yaml
validation_result:
  valid: boolean
  
  errors: array<object>
    - type: string  # parse_error | missing_field | invalid_value | schema_violation
      field: string
      message: string
      line: integer
      
  warnings: array<object>
    - type: string  # deprecated_api | best_practice
      message: string
      
  metadata:
    api_version: string
    kind: string
    name: string
```

## Process

### Step 1: Parse YAML

```python
import yaml

try:
    manifest = yaml.safe_load(yaml_content)
except yaml.YAMLError as e:
    return {
        'valid': False,
        'errors': [{
            'type': 'parse_error',
            'message': str(e),
            'line': e.problem_mark.line if hasattr(e, 'problem_mark') else 0
        }]
    }
```

### Step 2: Run oc create --dry-run

```bash
# Write YAML to temp file
echo "$yaml_content" > /tmp/manifest.yaml

# Validate
oc create --dry-run=client -f /tmp/manifest.yaml 2>&1

# OR for server-side validation (requires cluster)
oc create --dry-run=server -f /tmp/manifest.yaml 2>&1
```

### Step 3: Parse Validation Output

```python
def parse_oc_validation(output, return_code):
    """
    Parse oc create output for errors and warnings
    """
    
    errors = []
    warnings = []
    
    if return_code != 0:
        # Validation failed
        for line in output.splitlines():
            if 'error:' in line.lower():
                error = parse_error_line(line)
                errors.append(error)
    
    # Check for deprecation warnings
    if 'deprecated' in output.lower():
        warnings.append({
            'type': 'deprecated_api',
            'message': extract_deprecation_message(output)
        })
    
    return {
        'valid': len(errors) == 0,
        'errors': errors,
        'warnings': warnings
    }
```

### Step 4: Check Common Issues

```python
def check_kubernetes_best_practices(manifest):
    """
    Additional checks beyond schema validation
    """
    
    warnings = []
    
    # Check for :latest image tag
    if 'Deployment' in manifest['kind'] or 'StatefulSet' in manifest['kind']:
        containers = manifest['spec']['template']['spec']['containers']
        for container in containers:
            if ':latest' in container.get('image', '') or ':' not in container.get('image', ''):
                warnings.append({
                    'type': 'best_practice',
                    'message': f"Container '{container['name']}' uses :latest or no tag (not recommended for production)"
                })
    
    # Check for resource limits
    if 'Deployment' in manifest['kind']:
        containers = manifest['spec']['template']['spec']['containers']
        for container in containers:
            if 'resources' not in container or 'limits' not in container.get('resources', {}):
                warnings.append({
                    'type': 'best_practice',
                    'message': f"Container '{container['name']}' has no resource limits"
                })
    
    # Check for liveness/readiness probes
    if 'Deployment' in manifest['kind']:
        containers = manifest['spec']['template']['spec']['containers']
        for container in containers:
            if 'livenessProbe' not in container:
                warnings.append({
                    'type': 'best_practice',
                    'message': f"Container '{container['name']}' has no liveness probe"
                })
    
    return warnings
```

## Example Usage

### Valid Deployment

```yaml
Input:
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx
spec:
  replicas: 2
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.21

Output:
{
  "valid": true,
  "errors": [],
  "warnings": [
    {
      "type": "best_practice",
      "message": "Container 'nginx' has no resource limits"
    },
    {
      "type": "best_practice",
      "message": "Container 'nginx' has no liveness probe"
    }
  ],
  "metadata": {
    "api_version": "apps/v1",
    "kind": "Deployment",
    "name": "nginx"
  }
}
```

### Invalid Deployment (Selector Mismatch)

```yaml
Input:
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx
spec:
  replicas: 2
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        name: nginx  # ❌ Doesn't match selector
    spec:
      containers:
      - name: nginx
        image: nginx:1.21

Output:
{
  "valid": false,
  "errors": [
    {
      "type": "schema_violation",
      "field": "spec.template.metadata.labels",
      "message": "selector does not match template labels",
      "line": 12
    }
  ],
  "warnings": [],
  "metadata": {
    "api_version": "apps/v1",
    "kind": "Deployment",
    "name": "nginx"
  }
}
```

### Deprecated API Version

```yaml
Input:
apiVersion: apps/v1beta1  # ❌ Deprecated
kind: Deployment
...

Output:
{
  "valid": true,
  "errors": [],
  "warnings": [
    {
      "type": "deprecated_api",
      "message": "apps/v1beta1 is deprecated, use apps/v1"
    }
  ],
  "metadata": {
    "api_version": "apps/v1beta1",
    "kind": "Deployment",
    "name": "nginx"
  }
}
```

## Integration

This skill is used by:
- **Judge Sub-Agent** - For robustness scoring
- **Main Agent** - For pre-deployment validation
