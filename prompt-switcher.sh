#!/bin/bash

# Define cor para o Gum
COLOR="#00f2ea"

echo "Escolha o visual do seu terminal:"

CHOICE=$(gum choose --cursor.foreground="$COLOR" \
    "1. Normal (Bash Padrão)" \
    "2. Git Nativo (Seu Estilo)" \
    "3. Starship (Moderno)")

case $CHOICE in
    "1. Normal (Bash Padrão)")
        unset PROMPT_COMMAND # Desliga o Starship
        export PS1='\[\033[01;32m\]\u@\h\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]\$ '
        clear
        echo "✅ Modo: Normal"
        ;;
        
    "2. Git Nativo (Seu Estilo)")
        unset PROMPT_COMMAND # Desliga o Starship
        
        # Importa o script de prompt do git (Verifica locais comuns)
        if [ -f /usr/lib/git-core/git-sh-prompt ]; then
            source /usr/lib/git-core/git-sh-prompt
        elif [ -f ~/.git-prompt.sh ]; then
            source ~/.git-prompt.sh
        fi

        # --- A CONFIGURAÇÃO QUE VOCÊ PEDIU ---
        # \u=Verde, \w=Azul, Branch=Vermelha
        export PS1='\[\033[01;32m\]\u@\h\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]$(__git_ps1 " (\033[31m%s\033[00m)")\$ '
        
        clear
        echo "✅ Modo: Git Nativo (Estilo Personalizado)"
        ;;
        
    "3. Starship (Moderno)")
        eval "$(starship init bash)"
        clear
        # Starship assume o controle
        ;;
esac
