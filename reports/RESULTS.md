# Code security comparison

Thirty AI implementations and thirty human implementations were compared using SonarQube Community 26.3.0.120487 with the recorded Sonar way profiles. The scan covered 30 AI files and 225 human files. The implementation, rather than the individual source file, is the comparison unit.

AI code was generated on 24 March 2026 using ChatGPT through its web interface and GitHub Copilot Chat version 0.35.2 in Visual Studio Code Agent mode. Most recorded Copilot requests used Auto model selection; sample 28 used Gemini 3 Pro Preview. Multiple Copilot prompts shared a conversation. The researcher reported one run per prompt and no user-defined custom or memory instructions related to code generation. The ChatGPT model is not specified here because its historical label remains to be resolved.

Six AI JavaScript files received syntax-only corrections on eleven lines to enable parsing. Both original and scanned versions are supplied, with the correction record. Human implementations were selected by core task; repository commits, selected source files and implementation differences are documented in data/human-sources.csv. Their sizes and development histories differ, so these results describe this sample rather than a causal effect of AI authorship.

SonarQube reported 16 Vulnerability findings in AI code and 9 in human code, all classified BLOCKER by the tool. Deduplication yielded 11 AI and 7 human issues, affecting 11 AI and 6 human implementations. Overlapping reports of the same secret assignment were counted once.

The researcher reported confirming all 18 deduplicated issues as security concerns through manual code review, with no false positives or context-dependent Vulnerability issues. Of 116 Security Hotspots, 94 were classified as concerns (44 AI, 50 human); 22 debug-mode hotspots (16 AI, 6 human) required deployment context. These decisions were transcribed from the researcher’s statements; no second-reviewer agreement or exploitation testing is reported.

The recorded comparison of raw finding counts was not statistically significant (two-sided Mann–Whitney p = 0.156). The observed difference does not establish that the groups have equal security. This p-value concerns raw findings, not deduplicated or manually classified issues.

Source references are supplied for all thirty human implementations. Human code is not bundled while redistribution questions are being resolved. Licence findings are recorded in licences/Repository_Licences.csv.
