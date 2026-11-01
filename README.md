# Bot-Math Plugins

Módulos de cores de perfil e painéis informativos para bots do Discord, mantidos por **pyyrho**. Cada módulo pode ser ativado separadamente e configurado pelo próprio Discord.

Esta distribuição contém somente os dois módulos descritos abaixo, os utilitários necessários e um inicializador independente. Não contém o bot completo, o sistema acadêmico ou os dados de servidores.

## Plugins

### `cores`

Painéis com botões para selecionar e remover cargos de cor. Ao trocar de cor, o módulo remove os outros cargos de cor configurados que o bot consegue gerenciar. Os botões continuam registrados após reiniciar o bot.

| Comando | Função |
| --- | --- |
| `/cores vincular_normal` | Vincula uma das nove cores a um cargo existente. |
| `/cores vincular_degrade` | Vincula uma das oito opções de degradê a um cargo existente. |
| `/cores canal_vip` | Define o canal cuja permissão de visualização autoriza o uso dos degradês. |
| `/cores painel` | Publica um painel de cores, com título, descrição, cor e imagens opcionais. |
| `/cores painel_vip` | Publica o painel de degradês. |
| `/cores lista` | Consulta os vínculos de cargos e a configuração VIP. |
| `/cores remover` | Remove os cargos de cor gerenciáveis de um membro. |

Os comandos de configuração exigem Administrador do membro que os executa. Os membros usam os botões públicos para escolher uma cor. O bot precisa de **Gerenciar cargos**, com seu cargo acima de todos os cargos de cor. Vincule somente cargos cosméticos, sem permissões administrativas.

Os cargos são criados e coloridos nas configurações do Discord. O plugin apenas atribui cargos existentes; ele não desbloqueia efeitos de degradê. Configure o canal VIP antes de publicar o painel de degradês: sem um canal válido configurado, o código não restringe o acesso a essas opções.

### `painel_interativo`

Construtor de painéis informativos com até 20 botões. Cada botão abre uma página visível somente para quem clicou, com texto e imagens opcionais. Os cliques continuam funcionando após reinícios, desde que os dados sejam preservados.

| Comando | Função |
| --- | --- |
| `/painel criar` | Abre o formulário de criação e o editor com botões. |
| `/painel adicionar_botao` | Adiciona um botão e sua página. |
| `/painel editar_principal` | Edita título, descrição, cor, imagens e rodapé. |
| `/painel editar_botao` | Edita uma página pelo número. |
| `/painel remover_botao` | Remove uma página e renumera as seguintes. |
| `/painel visualizar` | Mostra uma prévia privada. |
| `/painel publicar` | Publica uma nova cópia do painel. |
| `/painel listar` | Mostra os painéis salvos no servidor. |
| `/painel excluir` | Apaga a configuração; os botões publicados deixam de abrir páginas. |

Todos esses comandos exigem Administrador do membro. As páginas não possuem restrição por cargo: qualquer pessoa que consiga clicar no painel pode consultar seu conteúdo. Não coloque informações confidenciais nelas.

Ao editar textos das páginas, os cliques passam a ler os dados atualizados. Para atualizar o título, os botões ou a aparência da mensagem principal já enviada, publique uma nova cópia e remova manualmente a antiga.

## Instalação

Requisitos: Python 3.11 ou posterior e uma aplicação de bot própria no [Discord Developer Portal](https://discord.com/developers/applications).

1. Crie a aplicação e habilite **Server Members Intent** na seção Bot. Este inicializador usa comandos de barra e não exige Message Content Intent.
2. Instale a aplicação no servidor com os escopos `bot` e `applications.commands`.
3. Conceda ao bot acesso ao canal e permissão para enviar mensagens. Para cores, conceda também Gerenciar cargos e ajuste a hierarquia. Não é necessário dar Administrador ao bot.
4. Na pasta deste projeto, instale as dependências:

```sh
python -m venv .venv
```

No Windows PowerShell:

```powershell
.venv\Scripts\python -m pip install -r requirements.txt
$env:DISCORD_TOKEN = "TOKEN_DO_SEU_BOT"
$env:BOT_PLUGINS = "cores,painel_interativo"
.venv\Scripts\python main.py
```

No Linux/macOS:

```sh
.venv/bin/python -m pip install -r requirements.txt
read -rsp 'Token do bot: ' DISCORD_TOKEN
export DISCORD_TOKEN
export BOT_PLUGINS=cores,painel_interativo
.venv/bin/python main.py
```

Em serviços de hospedagem, defina as variáveis no painel do serviço. `.env.example` é apenas uma referência; o inicializador não carrega arquivos `.env` automaticamente. Não envie tokens ao GitHub.

## Primeira configuração

Para cores, crie um cargo Vermelho, coloque-o abaixo do cargo do bot e execute `/cores vincular_normal`, selecionando a cor e o cargo. Repita para as outras opções e publique com `/cores painel`. Clique uma vez para selecionar e novamente para remover.

Para informações, execute `/painel criar`, preencha o formulário, adicione as páginas e use os botões de prévia e publicação. Guarde o ID exibido pelo editor para usar os comandos posteriores.

## Configuração e persistência

| Variável | Padrão | Uso |
| --- | --- | --- |
| `DISCORD_TOKEN` | Obrigatória | Token da aplicação de bot. |
| `BOT_PLUGINS` | `cores,painel_interativo` | Lista de módulos, separada por vírgulas. |
| `DATA_DIR` | `data` | Diretório do arquivo `bot_data.json`. |
| `DATABASE_URL` | Vazia | Conexão PostgreSQL opcional. |

Sem PostgreSQL, execute uma única instância e mantenha `DATA_DIR` em disco persistente. Não publique o diretório de dados. Para PostgreSQL, instale `requirements-postgres.txt` e defina `DATABASE_URL`. O armazenamento herdado tenta usar JSON se o PostgreSQL falhar; confira os logs para saber qual modo foi ativado.

## Integrar a um bot existente

Copie `cogs/cores.py`, `cogs/painel_interativo.py` e os utilitários `utils/storage.py` e `utils/ui_v2.py`. Confira conflitos com pacotes já chamados `cogs` ou `utils`; ajuste os imports se necessário. No seu `setup_hook`, inicialize o armazenamento e carregue os módulos desejados:

```python
await store.init()
await self.load_extension("cogs.cores")
await self.load_extension("cogs.painel_interativo")
await self.tree.sync()
```

Importe `store` de `utils.storage` e execute `await store.close()` ao encerrar. Esta distribuição utiliza extensões do discord.py; não é um pacote compatível com o carregador de plugins do projeto `discord-math/bot`.

## Contribuições e licença

Consulte [CONTRIBUTING.md](CONTRIBUTING.md). Os arquivos desta distribuição estão sob a [BSD-3-Clause](LICENSE). Essa licença se aplica a esta distribuição, não concede acesso ao repositório completo nem se estende automaticamente aos demais módulos do Bot-Math. As dependências mantêm suas próprias licenças.
