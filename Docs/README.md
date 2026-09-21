# Documentação do projeto

## Organização

- `Server/templates/`: páginas HTML/Jinja2. Os templates cuidam apenas da estrutura e dos dados exibidos.
- `Server/static/css/`: estilos específicos de páginas.
- `Server/static/css/pages.css`: identidade visual e estilos compartilhados entre as páginas.
- `Server/static/js/`: scripts específicos de páginas e formulários.
- `Server/static/img_posts/`: imagens usadas nas notícias.
- `Server/Databases/`: scripts de criação e inicialização do banco.
- `Docs/Models_DB/`: modelo visual do banco de dados.

## Convenção para novas páginas

1. Crie o template em `Server/templates/Tcc/<Pagina>/`.
2. Crie os estilos em `Server/static/css/<pagina>.css`.
3. Crie os scripts em `Server/static/js/<pagina>.js`.
4. Referencie assets com `url_for('static', filename='...')`.
5. Registre a página em `Server/main.py` ou no blueprint responsável.

Evite CSS e JavaScript inline nos templates. Código compartilhado deve permanecer nos arquivos globais; código específico deve ficar no diretório da página dentro de `static/`.

## Documentos existentes

Os arquivos de requisitos e informações do projeto continuam na raiz para manter os links atuais. Materiais visuais e modelos ficam em `Docs/`.