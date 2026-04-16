# Guia de Conceitos para Evoluir o Projeto como um Bom ETL

Este documento foi pensado para te ensinar os conceitos que você precisa dominar para melhorar os projetos `Data-extract` e `SAW-analytics`.

O objetivo aqui nao e so explicar teoria. A ideia e te mostrar:

- o que cada conceito significa
- por que ele importa em um projeto ETL
- como ele aparece no seu projeto atual
- o que voce pode fazer para corrigir ou evoluir

## 1. O que e ETL

ETL significa `Extract, Transform, Load`.

- `Extract`: extrair os dados de uma fonte
- `Transform`: limpar, padronizar, validar e reorganizar os dados
- `Load`: salvar os dados tratados em um destino final

Um bom ETL nao e apenas um script que le uma planilha e gera outra. Um ETL bom precisa ser:

- confiavel
- repetivel
- testavel
- observavel
- facil de manter

## 2. Como isso se aplica ao seu projeto

Hoje o projeto parece dividido em duas partes:

- `Data-extract`: tenta fazer a extracao e parte da transformacao
- `SAW-analytics`: faz calculos analiticos e gera ranking

Conceitualmente, isso pode funcionar muito bem, desde que a fronteira entre os dois fique clara:

- `Data-extract` deve gerar um conjunto de dados tratado, padronizado e confiavel
- `SAW-analytics` deve consumir esse dado tratado para fazer analise, normalizacao, ponderacao e ranking

Se os dois lados leem arquivos brutos independentes ou aplicam regras de forma solta, o pipeline perde consistencia.

## 3. O que e arquitetura de pipeline

Arquitetura de pipeline e a forma como voce organiza o fluxo dos dados entre etapas.

Em um pipeline bem organizado, cada etapa tem responsabilidade clara:

1. entrada do dado bruto
2. limpeza e validacao
3. transformacao para formato analitico
4. armazenamento do dado confiavel
5. consumo pela camada de analise

### Exemplo de arquitetura recomendada para o seu caso

Uma estrutura conceitual simples poderia ser:

- `raw`: arquivos originais recebidos
- `staging`: dados lidos e minimamente estruturados
- `trusted`: dados validados e padronizados
- `analytics`: dados preparados para o algoritmo SAW e saidas finais

### Por que isso importa

Quando voce separa essas camadas, fica mais facil:

- rastrear erros
- reprocessar uma etapa sem refazer tudo
- saber qual dado ainda e bruto e qual dado ja foi confiabilizado
- evitar que a analise consuma dados inconsistentes

## 4. Contrato de dados e schema

Um dos conceitos mais importantes em ETL e o `schema`.

Schema e a definicao formal da estrutura esperada dos dados. Ele responde perguntas como:

- quais colunas devem existir
- quais sao opcionais
- qual o tipo de cada coluna
- quais valores nulos sao permitidos
- quais faixas de valor sao aceitaveis
- quais colunas formam uma chave ou identificador

### Exemplo

Se o `SAW-analytics` espera uma tabela com:

- `Municipio`
- `IAG0001`
- `IAG2008`
- `IAG2013`
- `IAG3008`
- `IES0001`
- `IES2002`

entao isso precisa estar formalizado, e nao apenas assumido no codigo.

### Por que isso importa

Sem schema:

- uma mudanca pequena na planilha pode quebrar tudo
- erros aparecem tarde demais
- a transformacao vira tentativa e erro

Com schema:

- o ETL falha cedo
- o erro fica claro
- a manutencao fica mais segura

## 5. Extracao robusta

Extracao robusta significa que a leitura dos dados precisa ser previsivel e controlada.

### O que voce precisa observar na extracao

- caminho do arquivo
- existencia do arquivo
- formato esperado
- engine correta de leitura
- codificacao
- nome das abas
- diferenca entre arquivos parecidos

### Boas praticas

- validar se o arquivo existe antes de processar
- registrar qual arquivo foi lido
- isolar a logica de leitura em uma classe ou servico
- evitar nomes de metodos incoerentes
- tratar erro de leitura com mensagem clara

### No seu projeto

Hoje ja existe a ideia de uma classe de extracao, mas ha uma quebra entre o metodo chamado e o metodo realmente implementado. Isso mostra um conceito importante:

`o contrato entre componentes precisa ser estavel`

Se o `main` chama um metodo que nao existe, o pipeline nem chega na transformacao.

## 6. Transformacao estruturada

Transformar dados nao e "achar qualquer valor numerico e seguir".
Transformacao boa precisa ser orientada por regra explicita.

### O que normalmente entra na transformacao

- limpeza de nulos
- padronizacao de nomes
- conversao de tipos
- remocao de duplicidades
- ajuste de formato de datas
- correcao de separador decimal
- mapeamento de categorias
- selecao de colunas
- derivacao de colunas novas

### O que deve ser evitado

- procurar municipio e indicador no texto da linha inteira
- pegar o primeiro numero disponivel sem saber o que ele representa
- misturar regra de negocio com tentativa generica de extracao

### Conceito importante: transformacao deterministica

Uma transformacao deterministica e aquela que sempre produz o mesmo resultado para a mesma entrada.

Se a regra for explicita, por exemplo:

- coluna X representa o municipio
- coluna Y representa o indicador A
- coluna Z representa o indicador B

entao o resultado sera previsivel.

Se a regra for:

- "varrer a linha e achar algo parecido"

o resultado fica fragil.

## 7. Qualidade de dados

Qualidade de dados e o conjunto de verificacoes que garantem que a informacao faz sentido.

### Dimensoes mais importantes

- `completude`: ha dados faltando?
- `validade`: o valor esta no formato certo?
- `unicidade`: existem duplicatas indevidas?
- `consistencia`: nomes, tipos e regras batem entre arquivos e etapas?
- `integridade`: os relacionamentos fazem sentido?
- `precisao`: os valores refletem o que deveriam representar?

### Exemplos no seu caso

- municipio escrito de formas diferentes
- indicador esperado ausente
- valor numerico lido como texto
- coluna extra aparecendo sem mapeamento
- pesos de criterios nao fechando como esperado

### O que um ETL bom faz

Um ETL bom mede e registra qualidade dos dados. Exemplo:

- quantas linhas entraram
- quantas foram descartadas
- quantos municipios ficaram sem indicador
- quantos valores ficaram nulos apos transformacao

## 8. Validacao de dados

Validacao e a aplicacao pratica das regras de qualidade.

### Tipos comuns de validacao

- colunas obrigatorias presentes
- tipos corretos
- intervalo minimo e maximo
- ausencia de nulos em campos criticos
- chaves sem duplicidade
- pesos com soma esperada

### Validacao sintatica x semantica

- `sintatica`: verifica formato
- `semantica`: verifica se o valor faz sentido

Exemplos:

- sintatica: a coluna e numerica
- semantica: o numero nao deveria ser negativo

## 9. Observabilidade e logging

Observabilidade significa conseguir entender o que o pipeline fez.

Em ETL, isso comeca com `logging`.

### Diferenca entre print e logging

`print` e util para teste rapido.
`logging` e melhor para operacao real.

Com logging voce pode registrar:

- inicio e fim de execucao
- arquivo lido
- quantidade de abas
- quantidade de linhas processadas
- alertas de colunas ausentes
- erros com contexto

### Niveis comuns

- `INFO`: eventos normais
- `WARNING`: algo inesperado, mas nao fatal
- `ERROR`: falha na execucao

### No seu projeto

Hoje ha muito `print`.
Para um ETL melhor, o ideal e migrar para `logging` e padronizar mensagens.

## 10. Tratamento de erros

Um bom ETL nao apenas falha. Ele falha bem.

Falhar bem significa:

- interromper quando o erro compromete o resultado
- mostrar uma mensagem clara
- apontar onde ocorreu
- permitir diagnostico rapido

### O que evitar

- `except:` generico
- erro silencioso
- continuar processamento com dado invalido sem registrar

### O que preferir

- `FileNotFoundError` para arquivo ausente
- `ValueError` para dado fora do esperado
- erros personalizados para regra de negocio

## 11. Configuracao externa

Configuracao e tudo aquilo que pode mudar sem que a logica do programa precise ser reescrita.

### Exemplos de configuracao no seu projeto

- lista de municipios
- lista de indicadores
- codigos e pesos dos criterios
- diretorios de entrada e saida
- nome do arquivo fonte

### Por que tirar isso do codigo

Quando essas definicoes ficam hardcoded:

- qualquer ajuste exige editar codigo
- aumenta o risco de erro
- dificulta reuso

### Alternativas melhores

- arquivo `.env`
- JSON
- YAML
- CSV de parametros
- planilha de configuracao

## 12. Acoplamento e coesao

Dois conceitos importantes em arquitetura:

- `coesao`: cada modulo faz uma coisa bem definida
- `acoplamento`: o quanto um modulo depende fortemente de outro

### O ideal

- alta coesao
- baixo acoplamento

### No seu caso

O `main` do `SAW-analytics` concentra muita regra de negocio.
Isso reduz a coesao dos servicos e aumenta o acoplamento com a execucao manual.

Uma organizacao melhor seria:

- um modulo para carregar dados preparados
- um modulo para validar entrada analitica
- um modulo para normalizacao
- um modulo para pesos
- um modulo para ranking
- um modulo para exportar resultados e graficos

## 13. Reprodutibilidade

Reprodutibilidade significa que outra pessoa, ou voce no futuro, consegue rodar o projeto e obter o mesmo comportamento.

### Isso depende de

- dependencias fixadas
- caminhos previsiveis
- configuracoes controladas
- entradas versionadas
- ambiente padronizado

### Sinais de baixa reprodutibilidade

- cada modulo com setup diferente
- ambiente virtual dentro do repositorio
- ausencia de instrucoes consistentes
- script funcionando apenas "na maquina do autor"

## 14. Versionamento das camadas de dados

Em ETL, nao basta versionar codigo. Muitas vezes voce tambem precisa versionar a evolucao das saidas.

### O que isso quer dizer

Voce pode salvar artefatos com:

- data de processamento
- versao da fonte
- nome do lote
- hash ou identificador do arquivo original

### Beneficios

- saber qual dado gerou qual analise
- comparar processamentos diferentes
- auditar mudancas

## 15. Formatos de saida

Escolher o formato certo de saida faz diferenca.

### Excel

Bom para:

- consulta manual
- entrega para usuarios nao tecnicos

Ruim para:

- pipelines automatizados
- performance
- controle de schema

### CSV

Bom para:

- interoperabilidade
- simplicidade

Exige cuidado com:

- separador
- encoding
- casas decimais

### Parquet

Bom para:

- pipelines analiticos
- performance
- tipos de dados mais consistentes

## 16. Testes automatizados

Se voce quer confiar em um ETL, voce precisa de testes.

### Tipos de testes que mais ajudam

- `teste de unidade`: valida uma funcao isolada
- `teste de integracao`: valida o fluxo entre modulos
- `teste com dados de exemplo`: valida o comportamento com uma pequena amostra controlada

### O que testar no seu projeto

- leitura de arquivo
- validacao de colunas obrigatorias
- conversao de tipos
- comportamento com valor nulo
- aplicacao de pesos
- score final esperado
- ordenacao do ranking

### Exemplo de ideia de teste

Dado um dataset pequeno com 3 municipios e 2 criterios:

- a normalizacao deve gerar valores esperados
- a ponderacao deve respeitar os pesos
- o ranking final deve ficar na ordem correta

## 17. Funcoes puras e testabilidade

Uma funcao pura recebe entrada e devolve saida sem depender de estado externo imprevisivel.

### Exemplo bom

Uma funcao que recebe um DataFrame e devolve outro DataFrame transformado.

### Exemplo ruim para teste

Uma funcao que:

- le arquivo
- imprime no terminal
- faz conta
- salva grafico
- muda estado global

Quanto mais pura for a logica central, mais facil sera testar e manter.

## 18. Orquestracao

Orquestracao e a capacidade de controlar a execucao do pipeline.

Mesmo em projeto pequeno, vale pensar nisso.

### O minimo desejavel

Executar por linha de comando com parametros como:

- arquivo de entrada
- pasta de saida
- modo de execucao
- nivel de log

### Futuro possivel

Depois, se o projeto crescer, ele pode ser integrado a:

- `cron`
- `Airflow`
- `Prefect`
- `Dagster`

## 19. Interface entre ETL e analise

Esse e um dos pontos mais importantes do seu caso.

`Data-extract` e `SAW-analytics` precisam conversar por meio de um contrato claro.

### Perguntas que precisam ter resposta objetiva

- qual arquivo o ETL gera?
- em qual formato?
- com quais colunas?
- com quais nomes padronizados?
- como o modulo analitico valida que a entrada esta correta?

### Regra pratica

O modulo analitico nao deveria depender de planilha bruta.
Ele deveria depender de um dado ja preparado pelo ETL.

## 20. Normalizacao e ponderacao no contexto do SAW

Como o `SAW-analytics` trabalha com criterios e pesos, ha conceitos especificos importantes.

### Normalizacao

Normalizar significa colocar indicadores em escala comparavel.

Sem isso, indicadores com magnitudes muito diferentes distorcem a analise.

### Ponderacao

Ponderar significa aplicar o peso de importancia de cada criterio.

### Cuidado importante

Nem todo criterio segue a mesma logica:

- alguns sao de `beneficio`: quanto maior, melhor
- alguns sao de `custo`: quanto menor, melhor

Se isso nao estiver formalizado, o ranking pode parecer correto tecnicamente, mas estar errado do ponto de vista de negocio.

## 21. Headless, graficos e automacao

Um pipeline automatizado normalmente roda sem interface grafica.

Por isso, usar `plt.show()` costuma nao ser a melhor estrategia em execucao automatica.

### Melhor abordagem

- salvar o grafico em arquivo
- registrar onde foi salvo
- permitir execucao sem interface

Isso deixa o projeto mais pronto para automacao e uso em servidor.

## 22. Organizacao de projeto Python

Projetos Python ganham muito com organizacao consistente.

### Recomendacoes gerais

- nomes de pastas coerentes
- convencao unica de nomenclatura
- modulos separados por responsabilidade
- evitar codigo grande dentro de `main.py`
- evitar `sys.path.append`

### Por que evitar `sys.path.append`

Porque isso costuma mascarar problema de empacotamento e estrutura.
O ideal e organizar o projeto para imports funcionarem naturalmente.

## 23. Documentacao tecnica

Documentacao nao e luxo em ETL. E parte da confiabilidade.

### O que vale documentar

- entrada esperada
- regras de transformacao
- saida gerada
- criterios e pesos
- significado das colunas
- fluxo completo do pipeline

### O que isso resolve

- onboarding mais rapido
- menos dependencia de memoria do autor
- menos risco de regra escondida no codigo

## 24. Roadmap de maturidade para o seu projeto

Aqui vai uma ordem recomendada de estudo e implementacao.

### Etapa 1: fazer o pipeline rodar corretamente

Aprender e ajustar:

- contrato entre classes e metodos
- organizacao basica de modulos
- leitura correta do arquivo
- separacao entre extracao e analise

### Etapa 2: garantir consistencia dos dados

Aprender e ajustar:

- schema
- validacao
- tratamento de nulos
- padronizacao de colunas
- mapeamento explicito dos indicadores

### Etapa 3: tornar o pipeline confiavel

Aprender e ajustar:

- logging
- tratamento de erros
- configuracao externa
- testes automatizados

### Etapa 4: tornar o pipeline profissional

Aprender e ajustar:

- versionamento de saidas
- estrutura de camadas de dados
- CLI com parametros
- geracao de artefatos analiticos formais

## 25. O que estudar primeiro

Se voce quiser uma ordem de aprendizado, eu sugiro esta:

1. ETL e arquitetura de pipeline
2. schema e validacao de dados
3. transformacao deterministica
4. logging e tratamento de erros
5. testes automatizados com `pytest`
6. configuracao externa
7. integracao entre ETL e analise
8. normalizacao e ponderacao para SAW

## 26. Traduzindo tudo para o seu projeto

Em termos bem praticos, o que esse conhecimento significa para voces:

- o `Data-extract` precisa deixar de ser apenas um script de leitura e virar uma etapa confiavel de preparo de dados
- o `SAW-analytics` precisa parar de depender diretamente de dado bruto e passar a consumir dado tratado
- as regras de municipios, indicadores, colunas e pesos precisam virar contratos claros
- a execucao precisa ser testavel, observavel e repetivel

## 27. Checklist conceitual de um bom ETL

Voce pode usar esta lista para avaliar se o projeto esta amadurecendo:

- o pipeline roda de ponta a ponta sem ajuste manual?
- a entrada esperada esta documentada?
- existe validacao de colunas e tipos?
- as regras de transformacao sao explicitas?
- os erros sao claros?
- ha logs suficientes para diagnostico?
- a saida e padronizada?
- o modulo analitico consome dado tratado?
- ha testes cobrindo as regras principais?
- outro desenvolvedor conseguiria rodar e entender o fluxo?

## 28. Fechamento

Se voce dominar os conceitos deste documento, ja tera uma base muito boa para transformar esse projeto em um pipeline ETL bem mais solido.

O mais importante e pensar assim:

`um bom ETL nao e so um codigo que funciona hoje; e um processo confiavel que continua funcionando quando o dado muda, quando o projeto cresce e quando outra pessoa precisa manter`

Se quiser, no proximo passo eu posso transformar este guia em um `plano de estudo por semanas` ou em um `roteiro de implementacao no seu codigo`, apontando exatamente o que mexer em cada arquivo.
