# Plugin Certification Pipeline

Task 203 introduces a multi-stage CI/CD workflow that automatically vets and signs third-party plugins before they are published. The pipeline rejects any plugin that fails a security or compliance gate.

```mermaid
flowchart LR
    A[Plugin Source] --> B(SCA)
    B --> C(SAST & Secrets)
    C --> D(Sandbox Tests)
    D --> E(Compliance)
    E --> F(Signing)
    F --> G[Publish]
```

## 1. Software Composition Analysis (SCA)
- Tools such as `pip-audit` and Snyk inspect dependencies for known CVEs and incompatible licenses.
- The job fails if a high-severity issue is detected.

```mermaid
flowchart TD
    src[Plugin Requirements] --> sca[Dependency Scanners]
    sca -->|Report| result{Issues?}
    result -- "None" --> pass[Proceed]
    result -- "Found" --> fail[Reject]
```

## 2. Static Application Security Testing (SAST)
- Runs Semgrep and Bandit to detect insecure code patterns and secrets.
- Only a clean report allows the pipeline to continue.

```mermaid
flowchart TD
    code[Plugin Code] --> sast[Semgrep/Bandit]
    sast -->|Findings| decision{Critical Issues?}
    decision -- "No" --> next[Next Stage]
    decision -- "Yes" --> stop[Fail Build]
```

## 3. Sandboxed Tests
- The plugin is executed inside the Docker sandbox described in [`sandbox.md`](sandbox.md).
- Unit tests run with the network disabled and the file system mounted read-only.

```mermaid
flowchart TD
    build[Build Plugin] --> sandbox[Run in Sandbox]
    sandbox -->|Tests Pass| ok[Continue]
    sandbox -->|Failure| stop[Fail Build]
```

## 4. Compliance and Signing
- The Ethical Sentinel verifies policy compliance after sandbox execution.
- Successful artifacts are signed twice using `cosign` and uploaded to the marketplace.

```mermaid
flowchart TD
    vetted[Passed Tests] --> sentinel[Ethical Sentinel]
    sentinel --> sign[cosign Sign]
    sign --> release[Publish Artifact]
```

This certification workflow ensures only trustworthy plugins become part of the ecosystem.
