#! /bin/sh

GIT_COLOR="#f14e32"

git_color_text () {
  gum style --foreground "$GIT_COLOR" "$1"
}

get_branches () {
  if [ ${1+x} ]; then
    # Se passar argumento (limite), limita a escolha
    gum choose --selected.foreground="$GIT_COLOR" --limit="$1" $(git branch --format="%(refname:short)")
  else
    # Se não passar argumento, permite múltipla escolha (no-limit)
    gum choose --selected.foreground="$GIT_COLOR" --no-limit $(git branch --format="%(refname:short)")
  fi
}

# Verifica se está numa pasta Git
git rev-parse --git-dir > /dev/null 2>&1
if [ $? -ne 0 ];
then
  echo "$(git_color_text "!!") Must be run in a $(git_color_text "git") repo" 
  exit 1
fi

# Cabeçalho bonito
gum style \
  --border normal \
  --margin "1" \
  --padding "1" \
  --border-foreground "$GIT_COLOR" \
  "$(git_color_text ' Git') Branch Manager"

echo "Choose $(git_color_text 'branches') to operate on:"
branches=$(get_branches)

# Se o usuário cancelar (ESC), sai do script
if [ -z "$branches" ]; then
    echo "Nenhuma branch selecionada."
    exit 0
fi

echo ""
echo "Choose a $(git_color_text "command"):"

# --- CORREÇÃO AQUI: Adicionado 'checkout' na lista ---
command=$(gum choose --cursor.foreground="$GIT_COLOR" checkout rebase delete update)
echo ""

# Loop para processar as branches escolhidas
echo $branches | tr " " "\n" | while read -r branch
do
  case $command in
    checkout)
      git checkout "$branch"
      ;;     
    rebase)
      base_branch=$(get_branches 1)
      git fetch origin
      git checkout "$branch"
      git rebase "origin/$base_branch"
      ;;
    delete)
      git branch -D "$branch"
      ;;
    update)
      git checkout "$branch"
      git pull --ff-only
      ;;
  esac
done
