#!/usr/bin/env bash
# Видалення образів прикладу.
set -Eeuo pipefail
docker rmi layers-many:1.0 layers-one:1.0 layers-leak:1.0 layers-clean:1.0
