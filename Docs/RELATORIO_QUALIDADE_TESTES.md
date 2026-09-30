# Relatório de Qualidade de Software e Testes de Integração
**Projeto:** Vozes que não podem gritar  
**Data:** 29/09/2026  
**Status dos Testes:** 17/17 Passou (100% de Sucesso)

---

## 1. Visão Geral das Melhorias Implementadas

### 1.1 Suporte a Múltiplos Formatos de Imagem
- **Formatos Aceitos:** `PNG`, `JPG`, `JPEG`, `WEBP`, `GIF`, `SVG`, `BMP`, `AVIF`, `TIFF`.
- **Detecção Dinâmica:** Implementada a função `detect_image_mime` no módulo `Server/utils.py`, capaz de inspecionar a extensão do arquivo e os *magic bytes* (assinatura binária do arquivo).
- **Validação de Segurança:** Tentativas de upload de arquivos executáveis, scripts ou documentos de texto são rejeitadas com HTTP 400 e código de erro `INVALID_IMAGE_FORMAT`.
- **Cabeçalhos de Resposta Dinâmicos:** O endpoint `GET /api/noticias/<id>/imagem` serve a imagem armazenada em `LONGBLOB` no banco de dados com o tipo MIME correto em `Content-Type` e adiciona `Cache-Control: public, max-age=86400` para otimização no navegador.

### 1.2 Otimização com Cache e Fallback Gracioso (*Graceful Fallback*)
- **Módulo de Cache (`Server/config/cache.py`):** Classe `GracefulCache` integrada ao Memcached com tratamento completo de exceções.
- **Invalidação Automática:** Criação, edição, exclusão de notícias, comentários e curtidas invalidam o cache para garantir consistência de dados.
- **Resiliência a Falhas (Fallback Gracioso):** Caso o servidor Memcached esteja inacessível ou caia, o sistema registra um aviso de log (*warning*) e desvia todas as consultas diretamente para o MariaDB sem interromper o serviço e sem retornar erro para o usuário final.

### 1.3 Tratamento de Erros e Diagnósticos HTTP
- Handlers globais de erro para status `400`, `404`, `405`, `413` e `500` com respostas JSON estruturadas:
```json
{
  "success": false,
  "error": "Descrição clara e amigável do erro",
  "code": "CODIGO_DE_ERRO_PADRONIZADO"
}
```
- Sistema de logs centralizado (`logging.basicConfig`) para facilitar a identificação de falhas em ambiente de produção.

---

## 2. Estratégias de Teste Aplicadas

### 2.1 Teste de Integração Bottom-Up (Da Unidade ao Sistema)
1. **Nível 1 (Unidade & Funções Auxiliares):** Teste isolado do reconhecedor de tipos MIME `detect_image_mime` e resiliência da classe `GracefulCache`.
2. **Nível 2 (Controladores & ORM):** Teste das funções de busca e mutação no SQLAlchemy, garantindo integridade dos dados e expiração de cache.
3. **Nível 3 (Rotas & Endpoints HTTP):** Validação de endpoints da API REST com autenticação e sessão.

### 2.2 Teste de Integração Incremental
- **Incremento 1 (Autenticação e Trava de Segurança):** Bloqueio de visitantes, perfil de permissão admin/user.
- **Incremento 2 (Notícias & Imagens Multi-Formato):** Inserção e recuperação de PNG, JPEG, WEBP e SVG.
- **Incremento 3 (Interatividade Social):** Comentários com higienização de XSS e controle de curtidas.
- **Incremento 4 (Ajuda & Denúncia):** Retorno de orientação imediata em denúncias sem PIX de doação.
- **Incremento 5 (Cache e Resiliência):** Validação de *cache hits* e comportamento resiliente sob indisponibilidade de cache.

---

## 3. Matriz de Execução dos Testes Automated (Pytest)

| Teste | Categoria / Técnica | Resultado | Tempo |
|---|---|---|---|
| `test_detect_image_mime_multiplos_formatos` | Bottom-Up / Unidade | PASSED | 0.01s |
| `test_graceful_cache_fallback_sem_excecao` | Bottom-Up / Resiliência | PASSED | 0.02s |
| `test_health_check_resiliencia` | Incremental / Healthcheck | PASSED | 0.05s |
| `test_visitante_bloqueado_na_api_noticias` | Incremental / Segurança | PASSED | 0.03s |
| `test_redirecionamento_pagina_restrita` | Incremental / Segurança | PASSED | 0.02s |
| `test_usuario_comum_bloqueado_de_criar_noticia` | Incremental / Permissões | PASSED | 0.12s |
| `test_upload_imagem_png` | Multi-Formato Imagem | PASSED | 0.15s |
| `test_upload_imagem_jpeg` | Multi-Formato Imagem | PASSED | 0.14s |
| `test_upload_imagem_webp` | Multi-Formato Imagem | PASSED | 0.14s |
| `test_upload_imagem_svg` | Multi-Formato Imagem | PASSED | 0.14s |
| `test_rejeicao_de_arquivo_nao_imagem` | Segurança / Validação | PASSED | 0.08s |
| `test_list_noticias_pre_cadastradas` | Incremental / Seed DB | PASSED | 0.18s |
| `test_curtidas_e_comentarios_com_seguranca` | Incremental / Social | PASSED | 0.22s |
| `test_list_noticias_com_cache` | Desempenho / Cache | PASSED | 0.15s |
| `test_invalida_cache_ao_criar_nova_noticia` | Desempenho / Cache | PASSED | 0.25s |
| `test_404_api_retorna_json_padronizado` | Tratamento de Erro | PASSED | 0.02s |
| `test_405_metodo_nao_permitido` | Tratamento de Erro | PASSED | 0.07s |

---

## 4. Conclusão
O sistema **Vozes que não podem gritar** encontra-se totalmente funcional, otimizado com cache resiliente, suporte completo a imagens em múltiplos formatos, mensagens de erro padronizadas e coberto por testes automatizados estruturados sob metodologias reconhecidas de qualidade de software (Bottom-Up e Incremental).
