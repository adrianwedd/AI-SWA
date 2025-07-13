# Plugin Approval Workflow and Supply-Chain Policies

The AI-SWA marketplace follows a strict process to vet third-party plugins before they are published. This document summarizes how submissions are approved and how supply-chain integrity is maintained.
See [certification_pipeline.md](certification_pipeline.md) for a detailed look at the CI gates.

## 1. Pre-Submission and CI Scanning

- Developers run local linting and security tools before submitting a plugin.
- The mandatory CI pipeline performs SAST, SCA, secret scanning and license checks.
- Only submissions that pass all automated scans progress to manual review.

## 2. Multi-Stage Review

1. **Triaging** – After automated scans, plugins are classified by risk level.
   - *Low risk* updates that introduce no new permissions may be auto-approved.
   - *Medium or high risk* submissions require human review via the ticket system.
2. **Feedback Loop** – Reviewers provide comments and request changes as needed.
3. **Approval** – Once all issues are resolved, the plugin is approved and a signed artifact is produced. Monitoring continues for vulnerabilities or ownership changes.

## 3. Runtime Isolation

Approved plugins run inside a sandbox container with no network access and read-only file mounts. Manifests must match `plugins/manifest_schema.json` and, when `PLUGIN_SIGNING_KEY` is configured, include a valid HMAC signature. Optional policy files restrict which plugins and permissions are allowed.

## 4. Supply-Chain Policies

- **SLSA Build Provenance** – Builds run on trusted infrastructure and generate non‑falsifiable provenance metadata.
- **Cryptographic Signing** – Plugins are signed by immutable digest (preferably using Sigstore/Cosign). Signatures are stored in a transparency log.
- **Dual-Signing** – The marketplace verifies the developer signature and re‑signs the plugin with its own key before publishing. Badges indicate which checks were passed.

The combination of automated scanning, manual review and signed provenance ensures only trustworthy plugins become part of the ecosystem.
