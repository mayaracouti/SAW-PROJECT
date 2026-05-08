from models.Criterio import Criterio
from utils.desrealizadorDeDados import desrealizadorDeDados
from utils.normalizacao import Normalizacao
import sys
import pandas as pd
import os
from pathlib import Path
from models.CarregamentoDados import CarregamentoDados

# Isso força o Python a olhar dentro da pasta 'src'
sys.path.append(os.path.join(os.path.dirname(__file__), "."))


def main():

    print("Executando algoritmo SAW")

    c1 = Criterio("IAG0001", "Índice de atendimento total Abs. Água", 0.15441)
    c2 = Criterio("IAG2008", "Índice de vol. água disponibilizada economia", 0.06732)
    c3 = Criterio("IAG2013", "Perdas totais de água na distribuição", 0.091701)
    c4 = Criterio("IAG3008", "Índice de reclamações água", 0.028359)
    c5 = Criterio("IES0001", "Índice de atendimento total Col. Esgoto", 0.253724)
    c6 = Criterio("IES2002", "Esgoto coletado referido à água consumida", 0.115267)
   
    ListaDeCriterios = [c1, c2, c3, c4, c5, c6]
    nome_arquivo = "preferencias_seg_hidrica_PCJ_2024(1).xlsx"
    nome_aba = "dados2024_PCJ"

    # instancia obj chamado desrealizador
    desrealizador = desrealizadorDeDados()
    abas_disponiveis = desrealizador.listarAbas(nome_arquivo)
    if nome_aba not in abas_disponiveis:
        raise ValueError(f"A aba {nome_aba} não foi encontrada. Abas disponíveis: {abas_disponiveis}")

    planilhaDeDados = desrealizador.extracaoDadosBruto(nome_arquivo, nome_aba)

    mapa_colunas = {}
    objetivos_criterios = {}
    for coluna in planilhaDeDados.columns:
        if isinstance(coluna, str) and "-" in coluna:
            criterio_id, objetivo = coluna.split("-", 1)
            mapa_colunas[coluna] = criterio_id.strip()
            objetivos_criterios[criterio_id.strip()] = objetivo.strip().lower()

    planilhaDeDados = planilhaDeDados.rename(columns=mapa_colunas)

    # Validação de colunas obrigatórias
    coluna_natureza_juridica = "Natureza Jurídica"
    coluna_tipologia = "Tipologia"
    required_cols = [c.criterioId for c in ListaDeCriterios]
    colunas_obrigatorias = ["Município", coluna_tipologia, coluna_natureza_juridica] + required_cols
    missing_cols = [col for col in colunas_obrigatorias if col not in planilhaDeDados.columns]
    if missing_cols:
        raise ValueError(f"Colunas obrigatórias não encontradas na planilha: {missing_cols}")

    for criterio in ListaDeCriterios:
        objetivo = objetivos_criterios.get(criterio.criterioId)
        if objetivo not in {"bom", "ruim"}:
            raise ValueError(f"Não foi possível identificar se o critério {criterio.criterioId} é bom ou ruim.")
        criterio.objetivo = objetivo

    colunas_resultado = ["Município", coluna_tipologia, coluna_natureza_juridica] + required_cols
    planilhaFiltrada = planilhaDeDados[colunas_resultado].copy()
    planilhaFiltrada = planilhaFiltrada.dropna(subset=["Município"])

    municipios = planilhaFiltrada["Município"]
    dadosNumericos = planilhaFiltrada[required_cols].apply(pd.to_numeric, errors="coerce")

    # Fase 2: Soma do produto dados indicador * peso de indicador
    dfCriterios = Criterio.criaDataframeDeCriterios(ListaDeCriterios)
    if dfCriterios['peso'].sum() == 0:
        raise ValueError("Os pesos dos critériosnão podem ser zero.")

    dadosNumericosNormalizados = Normalizacao.normalizar_saw(dadosNumericos, dfCriterios)
    dataFrameNormalizado = pd.concat([municipios, dadosNumericosNormalizados], axis=1)
    dadosPonderados = Normalizacao.aplicarPesos(dadosNumericosNormalizados, dfCriterios)
    dadosPonderados = pd.DataFrame(dadosPonderados, columns=dadosNumericosNormalizados.columns, index=municipios.index)
    resultadoFinal = pd.concat([municipios, dadosPonderados], axis=1)
    somaProdutoTabela = Normalizacao.somaProduto(resultadoFinal)

    #Fase 3: Cria Rankin dos municipios
    rankinMunicipios = Normalizacao.rankinMunicipios(somaProdutoTabela)
    criterios_identificados = dfCriterios[["criterioId", "descricao", "peso", "objetivo"]].copy()
    criterios_identificados.columns = ["Indicador", "Nome do indicador", "Peso", "Classificação"]

    rankingDetalhado = rankinMunicipios.reset_index().merge(
        planilhaFiltrada,
        on="Município",
        how="left"
    )
    rankingDetalhado = rankingDetalhado[
        ["Posição", "Município", coluna_tipologia, coluna_natureza_juridica, "Score"] + required_cols
    ]

    rankingsPorTipologia = {}
    for tipologia, rankingTipologia in rankingDetalhado.groupby(coluna_tipologia, dropna=False):
        nome_tipologia = "Sem tipologia" if pd.isna(tipologia) else f"Tipologia {tipologia}"
        rankingTipologia = rankingTipologia.sort_values(by="Score", ascending=False).reset_index(drop=True)
        rankingTipologia["Posição"] = rankingTipologia.index + 1
        rankingsPorTipologia[nome_tipologia] = rankingTipologia[rankingDetalhado.columns]

    rankingsPorNatureza = {}
    for natureza, rankingNatureza in rankingDetalhado.groupby(coluna_natureza_juridica, dropna=False):
        nome_natureza = "Sem natureza jurídica" if pd.isna(natureza) else str(natureza)
        rankingNatureza = rankingNatureza.sort_values(by="Score", ascending=False).reset_index(drop=True)
        rankingNatureza["Posição"] = rankingNatureza.index + 1
        rankingsPorNatureza[nome_natureza] = rankingNatureza[rankingDetalhado.columns]

    rankingsExtras = {
        "top_10": rankingDetalhado.head(10).copy(),
        "bottom_10": rankingDetalhado.tail(10).sort_values(by="Score", ascending=True).copy(),
    }

    print("\nCritérios identificados na tabela:")
    print(criterios_identificados.to_string(index=False))

    print("\nDados normalizados:")
    print(dataFrameNormalizado.to_string(index=False))

    print("\nRanking final SAW:")
    print(rankinMunicipios.to_string())

    print("\nTop 10:")
    print(rankingsExtras["top_10"][["Posição", "Município", "Score"]].to_string(index=False))

    print("\nBottom 10:")
    print(rankingsExtras["bottom_10"][["Posição", "Município", "Score"]].to_string(index=False))

    print("\nRankings por Natureza Jurídica:")
    for natureza, rankingNatureza in rankingsPorNatureza.items():
        print(f"\nNatureza Jurídica: {natureza}")
        print(rankingNatureza[["Posição", "Município", "Score"]].to_string(index=False))

    print("\nRankings por Tipologia:")
    for tipologia, rankingTipologia in rankingsPorTipologia.items():
        print(f"\n{tipologia}")
        print(rankingTipologia[["Posição", "Município", "Score"]].to_string(index=False))

    pasta_resultados = Path(__file__).resolve().parent / "dados" / "resultado"
    pasta_resultados.mkdir(parents=True, exist_ok=True)

    interface = CarregamentoDados()
    arquivo_ranking = pasta_resultados / "ranking_saw_pcj_2024.xlsx"
    with pd.ExcelWriter(arquivo_ranking, engine="openpyxl") as writer:
        rankingDetalhado.to_excel(writer, sheet_name="ranking_geral", index=False)
        nomes_abas = {"ranking_geral"}
        for nome, rankingExtra in rankingsExtras.items():
            nome_aba = interface._nome_aba_excel(nome, nomes_abas)
            rankingExtra.to_excel(writer, sheet_name=nome_aba, index=False)
        for tipologia, rankingTipologia in rankingsPorTipologia.items():
            nome_aba = interface._nome_aba_excel(tipologia, nomes_abas)
            rankingTipologia.to_excel(writer, sheet_name=nome_aba, index=False)
        for natureza, rankingNatureza in rankingsPorNatureza.items():
            nome_aba = interface._nome_aba_excel(natureza, nomes_abas)
            rankingNatureza.to_excel(writer, sheet_name=nome_aba, index=False)
        criterios_identificados.to_excel(writer, sheet_name="indicadores", index=False)
    print(f"\nRanking salvo em: {arquivo_ranking}")

    interface.mostrar_popup_resultados(
        rankingDetalhado=rankingDetalhado,
        criterios=criterios_identificados,
        caminho_padrao=arquivo_ranking,
        rankingsPorNatureza=rankingsPorNatureza,
        rankingsPorTipologia=rankingsPorTipologia,
        rankingsExtras=rankingsExtras,
    )

    return rankinMunicipios

if __name__ == "__main__":
    main()

