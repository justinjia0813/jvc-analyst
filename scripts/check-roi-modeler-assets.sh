#!/usr/bin/env bash
set -euo pipefail

scripts/check-jvc-assets.sh jvc-roi-modeler
python3 skills/jvc-roi-modeler/scripts/validate_csv.py templates/roi-modeler-template.csv
