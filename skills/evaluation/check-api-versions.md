---
name: check-api-versions
description: Checks Kubernetes/OpenShift API versions are current (not deprecated or removed)
type: skill
category: evaluation
phase: validation
---

# Check API Versions

## Purpose

Verifies that Kubernetes and OpenShift resources use current, supported API versions.

Catches:
- Deprecated APIs (e.g., `apps/v1beta1` → `apps/v1`)
- Removed APIs (e.g., `extensions/v1beta1` for Deployments)
- Beta/Alpha APIs in production code

## When to Use

- During judge sub-agent evaluation (robustness scoring)
- Code review for YAML manifests
- Migration planning

## Input

```yaml
yaml_content: string  # OR
manifests: array<object>  # Parsed YAML objects

kubernetes_version: string  # e.g., "1.28" (optional, defaults to latest)
openshift_version: string  # e.g., "4.14" (optional)
```

## Output

```yaml
api_check_result:
  all_current: boolean  # True if all APIs are current
  
  deprecated: array<object>
    - api_version: string
      kind: string
      recommended: string
      removal_version: string
      
  removed: array<object>
    - api_version: string
      kind: string
      error: string
      
  beta_or_alpha: array<object>
    - api_version: string
      kind: string
      stability: beta | alpha
      
  summary:
    total_resources: integer
    current: integer
    deprecated: integer
    removed: integer
    beta_alpha: integer
```

## API Version Reference

### Kubernetes Stable APIs (Recommended)

```yaml
apps/v1:
  - Deployment
  - StatefulSet
  - DaemonSet
  - ReplicaSet

batch/v1:
  - Job
  - CronJob

core/v1:
  - Pod
  - Service
  - ConfigMap
  - Secret
  - PersistentVolume
  - PersistentVolumeClaim
  - ServiceAccount

rbac.authorization.k8s.io/v1:
  - Role
  - RoleBinding
  - ClusterRole
  - ClusterRoleBinding

networking.k8s.io/v1:
  - Ingress
  - NetworkPolicy
```

### Deprecated APIs (Avoid)

```yaml
apps/v1beta1:
  deprecated_in: "1.8"
  removed_in: "1.16"
  replacement: apps/v1

apps/v1beta2:
  deprecated_in: "1.9"
  removed_in: "1.16"
  replacement: apps/v1

extensions/v1beta1:
  deprecated_in: "1.14"
  removed_in: "1.22"
  replacement: apps/v1 (for Deployments), networking.k8s.io/v1 (for Ingress)

batch/v1beta1:
  deprecated_in: "1.21"
  removed_in: "1.25"
  replacement: batch/v1
```

### OpenShift-Specific APIs

```yaml
route.openshift.io/v1:
  - Route (stable)

image.openshift.io/v1:
  - ImageStream (stable)

build.openshift.io/v1:
  - BuildConfig (stable)

apps.openshift.io/v1:
  - DeploymentConfig (deprecated, use Deployment)
```

## Process

```python
API_VERSIONS = {
    # Stable
    'apps/v1': {'status': 'stable', 'kinds': ['Deployment', 'StatefulSet', 'DaemonSet', 'ReplicaSet']},
    'batch/v1': {'status': 'stable', 'kinds': ['Job', 'CronJob']},
    'core/v1': {'status': 'stable', 'kinds': ['Pod', 'Service', 'ConfigMap', 'Secret']},
    
    # Deprecated
    'apps/v1beta1': {
        'status': 'deprecated',
        'deprecated_in': '1.8',
        'removed_in': '1.16',
        'replacement': 'apps/v1'
    },
    'apps/v1beta2': {
        'status': 'deprecated',
        'deprecated_in': '1.9',
        'removed_in': '1.16',
        'replacement': 'apps/v1'
    },
    'extensions/v1beta1': {
        'status': 'removed',
        'removed_in': '1.22',
        'replacement': 'apps/v1 or networking.k8s.io/v1'
    },
    
    # Beta
    'batch/v1beta1': {
        'status': 'beta',
        'stable_alternative': 'batch/v1'
    }
}

def check_api_versions(manifests):
    results = {
        'deprecated': [],
        'removed': [],
        'beta_or_alpha': []
    }
    
    for manifest in manifests:
        api_version = manifest.get('apiVersion')
        kind = manifest.get('kind')
        
        if api_version in API_VERSIONS:
            api_info = API_VERSIONS[api_version]
            
            if api_info['status'] == 'deprecated':
                results['deprecated'].append({
                    'api_version': api_version,
                    'kind': kind,
                    'recommended': api_info['replacement'],
                    'removal_version': api_info.get('removed_in')
                })
            
            elif api_info['status'] == 'removed':
                results['removed'].append({
                    'api_version': api_version,
                    'kind': kind,
                    'error': f"API removed in {api_info['removed_in']}, use {api_info['replacement']}"
                })
            
            elif api_info['status'] in ['beta', 'alpha']:
                results['beta_or_alpha'].append({
                    'api_version': api_version,
                    'kind': kind,
                    'stability': api_info['status']
                })
    
    results['all_current'] = (
        len(results['deprecated']) == 0 and
        len(results['removed']) == 0 and
        len(results['beta_or_alpha']) == 0
    )
    
    return results
```

## Example Outputs

### All Current

```json
{
  "all_current": true,
  "deprecated": [],
  "removed": [],
  "beta_or_alpha": [],
  "summary": {
    "total_resources": 3,
    "current": 3,
    "deprecated": 0,
    "removed": 0,
    "beta_alpha": 0
  }
}
```

### Has Deprecated APIs

```json
{
  "all_current": false,
  "deprecated": [
    {
      "api_version": "apps/v1beta1",
      "kind": "Deployment",
      "recommended": "apps/v1",
      "removal_version": "1.16"
    }
  ],
  "removed": [],
  "beta_or_alpha": [],
  "summary": {
    "total_resources": 1,
    "current": 0,
    "deprecated": 1,
    "removed": 0,
    "beta_alpha": 0
  }
}
```

## Integration

This skill is used by:
- **Judge Sub-Agent** - Penalizes deprecated APIs in robustness score
- **validate-yaml-schema** - Complementary validation
