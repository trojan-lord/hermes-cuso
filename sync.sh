#!/bin/bash
# Thin wrapper -- the live sync script lives in ~/.hermes/scripts/.
exec "$HOME/.hermes/scripts/sync-hermes-backup.sh" "$@"
