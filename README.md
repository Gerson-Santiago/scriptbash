# Meus Scripts Bash

Este repo terá script para o meu universo linux.


instalar se não tiver 

```
# 1 instalando StarShip
curl -sS https://starship.rs/install.sh | sh
# 2 atualizando bahs e dando a permissão necessario
echo 'eval "$(starship init bash)"' >> ~/.bashrc
# 3 Atualizando o bashrc
source ~/.bashrc


# Adiciona o repositório e instala o Gum
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://repo.charm.sh/apt/gpg.key | sudo gpg --dearmor -o /etc/apt/keyrings/charm.gpg
echo "deb [signed-by=/etc/apt/keyrings/charm.gpg] https://repo.charm.sh/apt/ * *" | sudo tee /etc/apt/sources.list.d/charm.list
sudo apt update && sudo apt install gum -y
```

# Adiciona os atalhos ao final do .bashrc
echo "" >> ~/.bashrc
echo "# --- Meus Scripts Git ---" >> ~/.bashrc
echo "alias gcb='git checkout \$(git branch --format=\"%(refname:short)\" | gum choose)'" >> ~/.bashrc
echo "alias gbm='~/scriptbash/git-manager.sh'" >> ~/.bashrc

# Dá permissão para o script rodar
chmod +x ~/scriptbash/git-manager.sh

# Atualiza o terminal agora
source ~/.bashrc
