# Reproducing a scan

The recorded runs used SonarQube Community 26.3.0.120487 and SonarScanner CLI 8.0.1.6346. Exact analyzer versions are in `versions.json`; active Python/JavaScript rules and exported profiles are in `profiles/`. AI was scanned on 12 October 2026; human code on 11 October 2026.

Reproducing the statistical analysis does not require running SonarQube again. Use the top-level README instructions to work from the archived results.

To perform a fresh scan:

1. Retrieve the human files with `python analysis/fetch_human.py`. This verifies all 225 files against the archived SHA-256 hashes. Files are placed in the gitignored `data/human-local/` directory. Check applicable repository terms before redistribution.
2. Start a dedicated SonarQube instance with the recorded version and matching Python/JavaScript analyzers. Check the active rules against the archived profile exports. Existing Sonar way profiles may differ in newer releases; matching the name alone is insufficient.
3. Create projects `research-ai` and `research-human`, assign the matching profiles and create a scan token. Configure the token through the environment, never a committed file.
4. From the repository root, run the commands below with the recorded scanner version. Scan the provided source files as text; do not run the sample applications.

```sh
export SONAR_HOST_URL=http://localhost:9000
read -s -p 'SonarQube token: ' SONAR_TOKEN
export SONAR_TOKEN
sonar-scanner -Dproject.settings=scan/ai.properties
sonar-scanner -Dproject.settings=scan/human.properties
unset SONAR_TOKEN
```

The token prompt above is Bash syntax. In other shells, set `SONAR_TOKEN` through that shell's secure input facility. The configuration preserves the original scan choices: Python/JavaScript inclusion, UTF-8 encoding, disabled SCM integration and excluded duplication detection. Each configuration scans only its corresponding source directory.

The archived `raw/` data remains the input to `analysis/reproduce.py`. Fresh scans do not overwrite it automatically. To analyse a new run, export its issue, hotspot, component and file-metric records using the same structure and explicitly version the new results. Finding identifiers and manual-review mappings will change.

No Docker service is started by the scripts in this repository.
