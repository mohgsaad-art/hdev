#!/usr/bin/env bash
# Builds the VECTO command line (VectoConsole -> vectocmd.dll) from the fork and runs it on this machine.
# Fork: mohgsaad-art/VECTO, branch IEPC-experiments, commit b8d6126 (VectoCore 4.3.4-DEV). Needs a .NET SDK >= 6 (here: 9.0.319 with
# net6.0 target, run on the 9.0 runtime through DOTNET_ROLL_FORWARD=Major because no 6.0 runtime is installed).
# Usage: bash build_vecto.sh [VECTO_DIR] [OUT_DIR]
set -euo pipefail
VECTO_DIR="${1:-$(cd "$(dirname "$0")/../../../.." && pwd)/VECTO}"
OUT_DIR="${2:-$(cd "$(dirname "$0")/../../../.." && pwd)/vectocmd}"
export DOTNET_NOLOGO=1 DOTNET_CLI_TELEMETRY_OPTOUT=1
cd "$VECTO_DIR"
git rev-parse HEAD | grep -q '^b8d6126' || echo "WARNING: fork is not at b8d6126"
dotnet build VectoConsole/VectoConsole.csproj -c Release -f net6.0 -o "$OUT_DIR"
echo "run:  DOTNET_ROLL_FORWARD=Major DOTNET_SYSTEM_GLOBALIZATION_INVARIANT=1 dotnet $OUT_DIR/vectocmd.dll [-mod] [-t] JOB.vecto"
