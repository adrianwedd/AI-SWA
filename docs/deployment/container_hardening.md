# Container Hardening

This project ships multiple service images. Follow these guidelines to keep containers secure in production.

## Least privilege

- Each Dockerfile creates an unprivileged user and switches to it. Avoid running processes as root.
- Limit container capabilities with `--cap-drop=ALL` and only add the ones required by the service.

## Minimal base images

- Use slim or alpine variants of base images to reduce the attack surface.
- Regularly update images and rebuild to pull in security patches.

## Vulnerability scanning

- The CI pipeline runs `pip-audit`, `npm audit`, and **Trivy** to detect known vulnerabilities.
- Review scan reports on every pull request and fix high or critical issues before release.

## Runtime security

- Mount volumes read-only where possible.
- Configure resource limits to prevent denial-of-service attacks.
- Keep secrets out of images by passing them via environment variables or secret stores.
