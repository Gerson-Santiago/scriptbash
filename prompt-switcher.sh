#!/bin/bash

# Define cor para o Gum (Ciano)
COLOR="#00f2ea"

echo "Escolha o visual do seu terminal:"

CHOICE=$(gum choose --cursor.foreground="$COLOR" \
    "1. Bash Padrão" \
    "2. Git Nativo" \
    "3. Starship")

case $CHOICE in
    "1. Bash Padrão")
        unset PROMPT_COMMAND
        export PS1='\[\033[01;32m\]\u@\h\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]\$ '
        clear
        ;;
        
    "2. Git Nativo")
        unset PROMPT_COMMAND
        
        # Carrega o script do git
        if [ -f /usr/lib/git-core/git-sh-prompt ]; then
            source /usr/lib/git-core/git-sh-prompt
        elif [ -f ~/.git-prompt.sh ]; then
            source ~/.git-prompt.sh
        fi

        # --- A FAXINA: Remove os símbolos (* % + =) ---
        unset GIT_PS1_SHOWDIRTYSTATE
        unset GIT_PS1_SHOWUNTRACKEDFILES
        unset GIT_PS1_SHOWUPSTREAM
        unset GIT_PS1_SHOWCOLORHINTS
        unset GIT_PS1_SHOWSTASHSTATE

        # Visual: Verde(user) : Azul(pasta) (Vermelho branch)
        export PS1='\[\033[01;32m\]\u@\h\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]$(__git_ps1 " (\033[31m%s\033[00m)")\$ '
        
        clear
        ;;
        
    "3. Starship")
        eval "$(starship init bash)"
        clear
        ;;
esac
