# Updating Dependencies When pip-audit Fails

The CI workflow runs `pip-audit` to check `requirements.lock` for known vulnerabilities. If the audit reports medium or higher severity issues, the build will fail.

To resolve a failing audit:

1. **Upgrade the affected packages**
   ```bash
   pip install --upgrade <package>
   ```
2. **Regenerate the lock file** using [pip-tools](https://pypi.org/project/pip-tools/).
   ```bash
   pip install pip-tools
   pip-compile requirements.txt --output-file requirements.lock
   pip-sync requirements.lock  # remove unused packages
   ```
3. **Verify locally** by running:
   ```bash
   pip-audit -r requirements.lock
   ```
   Ensure no vulnerabilities remain.
4. Commit the updated `requirements.txt` and `requirements.lock` files.

The next CI run should pass once all vulnerabilities have been addressed.
