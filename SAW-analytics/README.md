# SAW Analytics

Projeto em Python para ler uma planilha Excel com indicadores de saneamento, aplicar a metodologia SAW (`Simple Additive Weighting`) e gerar um ranking dos municípios.

O sistema foi ajustado para:

- ler o arquivo na pasta `src/dados/dadosBruto/`
- localizar a aba `dados2024_PCJ`
- identificar automaticamente, no cabeçalho da planilha, quais indicadores são `bom` e quais são `ruim`
- normalizar os dados conforme a regra do SAW
- aplicar os pesos dos critérios
- gerar o ranking final dos municípios
- abrir um popup com opções para exportar a planilha e visualizar os resultados

## Estrutura do Projeto

```text
SAW-analytics/
├── requirements.txt
├── README.md
└── src/
    ├── main.py
    ├── dados/
    │   ├── dadosBruto/
    │   │   └── preferencias_seg_hidrica_PCJ_2024(1).xlsx
    │   └── resultado/
    ├── models/
    │   ├── CarregamentoDados.py
    │   └── Criterio.py
    └── utils/
        ├── desrealizadorDeDados.py
        └── normalizacao.py
```

## Indicadores Utilizados

O cálculo atual usa os seguintes critérios:

- `IAG0001` - Índice de atendimento total Abs. Água - peso `0.20`
- `IAG2008` - Índice de vol. água disponibilizada economia - peso `0.09`
- `IAG2013` - Perdas totais de água na distribuição - peso `0.31`
- `IAG3008` - Índice de reclamações água - peso `0.06`
- `IES0001` - Índice de atendimento total Col. Esgoto - peso `0.17`
- `IES2002` - Esgoto coletado referido à água consumida - peso `0.17`

## Regra de Negócio do Cálculo SAW

O projeto identifica a classificação diretamente no nome das colunas da aba `dados2024_PCJ`.

Exemplo de cabeçalho:

- `IAG0001-bom`
- `IAG2013-ruim`

Com isso, a regra aplicada é:

- Para indicador `bom`: quanto maior o valor, melhor
- Para indicador `ruim`: quanto menor o valor, melhor

### Normalização usada

- Se o indicador for `bom`:

```text
valor_normalizado = valor / maior_valor_da_coluna
```

- Se o indicador for `ruim`:

```text
valor_normalizado = menor_valor_da_coluna / valor
```

### Cálculo final

Depois da normalização:

1. cada indicador é multiplicado pelo seu peso
2. os valores ponderados são somados
3. o município com maior `Score` fica melhor posicionado no ranking

## Como Rodar

### 1. Entrar na raiz do projeto

```bash
cd /home/mayara/Projetos/SAW-PROJECT
```

### 2. Instalar as dependências

Se necessário:

```bash
pip3 install -r SAW-analytics/requirements.txt
```

### 3. Executar o sistema

```bash
python3 SAW-analytics/src/main.py
```

## O que acontece ao executar

Ao rodar o comando, o sistema:

1. lê a planilha `preferencias_seg_hidrica_PCJ_2024(1).xlsx`
2. acessa a aba `dados2024_PCJ`
3. identifica os critérios `bom` e `ruim`
4. calcula o ranking SAW
5. salva o ranking em CSV
6. abre uma janela popup com ações de visualização e exportação

## Interface Gráfica

Ao final da execução, um popup será exibido com as opções:

- `1. Baixar planilha`
- `2. Visualizar ranking e indicadores`

### Baixar planilha

Permite exportar os resultados em:

- `.xlsx`
- `.csv`

No arquivo Excel, são criadas duas abas:

- `ranking_municipios`
- `indicadores`

### Visualizar ranking e indicadores

Abre uma tela com:

- tabela do ranking dos municípios
- score calculado
- valores dos indicadores utilizados
- tabela com os indicadores, nome, peso e classificação (`bom` ou `ruim`)

## Arquivos de Saída

O CSV gerado automaticamente fica em:

```text
SAW-analytics/src/dados/resultado/ranking_saw_pcj_2024.csv
```

## Observações

- A interface gráfica usa `tkinter`, que normalmente já vem com o Python
- O projeto espera que a planilha esteja no caminho `src/dados/dadosBruto/`
- A aba usada no cálculo está fixada como `dados2024_PCJ`
- Se os nomes das colunas mudarem e não seguirem o padrão `CODIGO-bom` ou `CODIGO-ruim`, o sistema pode falhar na identificação da classificação

## Exemplo de Execução

```bash
cd /home/mayara/Projetos/SAW-PROJECT
python3 SAW-analytics/src/main.py
```

## Tecnologias

- Python 3
- pandas
- openpyxl
- tkinter

