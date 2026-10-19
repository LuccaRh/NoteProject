#!/bin/bash
# Liga o workspace de IA neste clone: hooks do git e o atalho ai/np.
# Os hooks do Claude Code já vêm em .claude/settings.json (versionado).
set -eu
cd "$(dirname "$0")/../.."
git config core.hooksPath ai/tools/githooks
chmod +x ai/tools/githooks/* ai/tools/np.py
ln -sfn tools/np.py ai/np
python3 -c "import yaml" 2>/dev/null || echo "falta PyYAML: sudo pacman -S python-yaml"
command -v drawio >/dev/null || echo "sem drawio CLI: /diagrama gera só o .drawio (pacote drawio-desktop exporta svg/png)"
echo "ok: ai/np status"
