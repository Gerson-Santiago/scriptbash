#!/bin/bash

# Define cor para o Gum
COLOR="#00f2ea" # Um ciano bonito

echo "Escolha o visual do seu terminal:"

# Mostra o menu com Gum
CHOICE=$(gum choose --cursor.foreground="$COLOR" \
    "1. Normal (Bash Padrão)" \
    "2. Git Nativo (Leve)" \
    "3. Starship (Moderno)")

case $CHOICE in
    "1. Normal (Bash Padrão)")
        # Remove ganchos do Starship se existirem
        unset PROMPT_COMMAND
        # Define o PS1 simples: usuario@host:pasta$
        export PS1='\[\033[01;32m\]\u@\h\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]\$ '
        clear
        echo "✅ Modo: Normal"
        ;;
        
    "2. Git Nativo (Leve)")
        # Remove ganchos do Starship
        unset PROMPT_COMMAND
        
        # Carrega script do Git (tenta achar em locais comuns do Linux/WSL)
        if [ -f /usr/lib/git-core/git-sh-prompt ]; then
            source /usr/lib/git-core/git-sh-prompt
        elif [ -f ~/.git-prompt.sh ]; then
            source ~/.git-prompt.sh
        fi
        
        # Configurações do Git
        export GIT_PS1_SHOWDIRTYSTATE=1
        export GIT_PS1_SHOWUNTRACKEDFILES=1
        export GIT_PS1_SHOWUPSTREAM="auto"
        export GIT_PS1_SHOWCOLORHINTS=1
        
        # Define o PS1 com a função do Git
        export PS1='\[\033[01;32m\]\u@\h\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]$(__git_ps1 " (%s)")\$ '
        clear
        echo "✅ Modo: Git Nativo"
        ;;
        
    "3. Starship (Moderno)")
        # Reinicia o Starship
        eval "$(starship init bash)"
        clear
        # O Starship se anuncia sozinho, não precisa de echo
        ;;
esac
