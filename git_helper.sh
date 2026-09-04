#!/bin/bash

# Cores para o terminal
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # Sem Cor

exibir_config() {
    echo -e "\n${CYAN}--- Configuração Atual do Git ---${NC}"
    echo -n "Usuário: "; git config user.name
    echo -n "Email:   "; git config user.email
}

definir_config() {
    echo -e "\n${YELLOW}--- Nova Configuração Global ---${NC}"
    read -p "Digite o Nome de Usuário: " nome
    read -p "Digite o E-mail: " email
    
    if [ -n "$nome" ] && [ -n "$email" ]; then
        git config --global user.name "$nome"
        git config --global user.email "$email"
        echo -e "${GREEN}Configuração atualizada com sucesso!${NC}"
    else
        echo -e "${RED}Nome ou e-mail inválidos. Operação cancelada.${NC}"
    fi
}

executar_commit_push() {
    echo -e "\n${YELLOW}--- Commit e Push ---${NC}"
    read -p "Digite o nome da branch para envio (ex: main, dev): " branch
    read -p "Digite a mensagem do commit: " mensagem
    
    if [ -n "$branch" ] && [ -n "$mensagem" ]; then
        echo -e "\nAdicionando arquivos..."
        git add .
        
        echo "Criando commit..."
        git commit -m "$mensagem"
        
        echo "Enviando alterações para o repositório remoto..."
        git push origin "$branch"
        
        echo -e "${GREEN}\nProcesso concluído com sucesso!${NC}"
    else
        echo -e "${RED}Branch e mensagem são obrigatórias!${NC}"
    fi
}

# Menu Principal Interativo
while true; do
    echo -e "\n${CYAN}==================================${NC}"
    echo -e "${CYAN}      PAINEL DE CONTROLE GIT      ${NC}"
    echo -e "${CYAN}==================================${NC}"
    echo "1. Ver usuário e e-mail atuais"
    echo "2. Configurar novo usuário e e-mail (--global)"
    echo "3. Executar Git Add, Commit e Push"
    echo "0. Sair"
    
    read -p "Escolha uma opção: " opcao
    
    case $opcao in
        1) exibir_config ;;
        2) definir_config ;;
        3) executar_commit_push ;;
        0) echo "Encerrando script..."; break ;;
        *) echo -e "${RED}Opção inválida, tente novamente.${NC}" ;;
    esac
done