#!/usr/bin/env bash
# Mensagens que o Lucca digitou na sessão, uma por linha (base da /lacunas).
# Uso: mensagens.sh [session-id]   (sem argumento: transcript mais recente do projeto)
# Raiz do repo, não a pasta atual: a sessão pode estar numa subpasta
raiz=$(git -C "$(dirname "$0")" rev-parse --show-toplevel)
proj=~/.claude/projects/$(echo "$raiz" | sed 's|[^A-Za-z0-9]|-|g')
if [[ -n "$1" && -f "$proj/$1.jsonl" ]]; then
  f="$proj/$1.jsonl"
else
  f=$(ls -t "$proj"/*.jsonl 2>/dev/null | head -1)
fi
[[ -f "$f" ]] || { echo "Transcript não encontrado em $proj"; exit 1; }

# Só o texto digitado: sem colagem (<pasted_content>), comando de skill nem mensagem de sistema
jq -r '
  select(.type == "user" and (.isMeta | not) and (.isSidechain | not))
  | .message.content
  | if type == "string" then . else ([.[] | select(.type == "text") | .text] | join(" ")) end
  | gsub("<pasted_content[^>]*>[\\s\\S]*?</pasted_content[^>]*>"; " ")
  | if startswith("<") then empty else . end
  | gsub("\\s+"; " ") | sub("^ "; "") | sub(" $"; "")
  | select(length > 0)
  | "- " + .
' "$f" | grep -vE "^- \[Request interrupted"
