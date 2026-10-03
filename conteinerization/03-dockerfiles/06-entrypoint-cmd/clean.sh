#!/usr/bin/env bash
set -Eeuo pipefail
docker rmi ep-shell:1.0 ep-exec:1.0 ep-loop:1.0 ep-simple:1.0 ep-both:1.0
