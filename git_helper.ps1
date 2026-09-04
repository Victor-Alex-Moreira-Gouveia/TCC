# Script de Gerenciamento do Git em PowerShell

function Exibir-Config {
    Write-Host "`n--- Configuração Atual do Git ---" -ForegroundColor Cyan
    Write-Host "Usuário: " -NoNewline; git config user.name
    Write-Host "Email:   " -NoNewline; git config user.email
}

function Definir-Config {
    Write-Host "`n--- Nova Configuração Global ---" -ForegroundColor Yellow
    $nome = Read-Host "Digite o Nome de Usuário"
    $email = Read-Host "Digite o E-mail"
    
    if ($nome -and $email) {
        git config --global user.name "$nome"
        git config --global user.email "$email"
        Write-Host "Configuração atualizada com sucesso!" -ForegroundColor Green
    } else {
        Write-Host "Nome ou e-mail inválidos. Operação cancelada." -ForegroundColor Red
    }
}

function Executar-CommitEPush {
    Write-Host "`n--- Commit e Push ---" -ForegroundColor Yellow
    $branch = Read-Host "Digite o nome da branch para envio (ex: main, dev)"
    $mensagem = Read-Host "Digite a mensagem do commit"
    
    if ($branch -and $mensagem) {
        Write-Host "`nAdicionando arquivos..." -ForegroundColor Gray
        git add .
        
        Write-Host "Criando commit..." -ForegroundColor Gray
        git commit -m "$mensagem"
        
        Write-Host "Enviando alterações para o repositório remoto..." -ForegroundColor Gray
        git push origin $branch
        
        Write-Host "`nProcesso concluído com sucesso!" -ForegroundColor Green
    } else {
        Write-Host "Branch e mensagem são obrigatórias!" -ForegroundColor Red
    }
}

# Menu Principal Interativo
do {
    Write-Host "`n==================================" -ForegroundColor Cyan
    Write-Host "      PAINEL DE CONTROLE GIT      " -ForegroundColor Cyan
    Write-Host "==================================" -ForegroundColor Cyan
    Write-Host "1. Ver usuário e e-mail atuais"
    Write-Host "2. Configurar novo usuário e e-mail (--global)"
    Write-Host "3. Executar Git Add, Commit e Push"
    Write-Host "0. Sair"
    
    $opcao = Read-Host "`nEscolha uma opção"
    
    switch ($opcao) {
        "1" { Exibir-Config }
        "2" { Definir-Config }
        "3" { Executar-CommitEPush }
        "0" { Write-Host "Encerrando script..." -ForegroundColor Gray }
        default { Write-Host "Opção inválida, tente novamente." -ForegroundColor Red }
    }
} while ($opcao -ne "0")