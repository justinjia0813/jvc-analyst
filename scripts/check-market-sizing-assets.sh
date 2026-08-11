#!/usr/bin/env bash
set -euo pipefail

python3 skills/jvc-market-sizing/scripts/check_package.py
scripts/check-jvc-assets.sh jvc-market-sizing
