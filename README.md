# Meus Scripts Bash

Este repositório contém scripts para automação do meu ambiente Linux (WSL e ChromeOS).

## 🚀 Como Instalar

Se você estiver em uma máquina nova, rode os comandos abaixo:

### 1. Instalar Aparência e Ferramentas (Starship + Gum)
```bash
# 1. Instalando StarShip (Visual do Terminal)
curl -sS https://starship.rs/install.sh | sh
echo 'eval "$(starship init bash)"' >> ~/.bashrc

# 2. Instalando Gum (Menus Interativos)
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://repo.charm.sh/apt/gpg.key | sudo gpg --dearmor -o /etc/apt/keyrings/charm.gpg
echo "deb [signed-by=/etc/apt/keyrings/charm.gpg] https://repo.charm.sh/apt/ * *" | sudo tee /etc/apt/sources.list.d/charm.list
sudo apt update && sudo apt install gum -y
```

### 2. Configurar os Atalhos (Alias)
Estes comandos configuram o `gcb` e `gbm` no seu sistema:

```bash
# Adiciona os atalhos ao final do .bashrc
echo "" >> ~/.bashrc
echo "# --- Meus Scripts Git ---" >> ~/.bashrc
echo "alias gcb='git checkout $(git branch --format=\"%(refname:short)\" | gum choose)'" >> ~/.bashrc
echo "alias gbm='~/scriptbash/git-manager.sh'" >> ~/.bashrc

# Dá permissão para o script rodar
chmod +x ~/scriptbash/git-manager.sh

# Atualiza o terminal agora
source ~/.bashrc
```

## 🛠️ Comandos Disponíveis

- **`gcb`**: Selecionar e mudar de branch rapidamente.
- **`gbm`**: Gerenciador completo (Checkout, Delete, Rebase, Update).
