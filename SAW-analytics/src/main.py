from models.Criterio import Criterio
from utils.desrealizadorDeDados import desrealizadorDeDados
from utils.normalizacao import Normalizacao
import sys
import pandas as pd
import os
from models.CarregamentoDados import CarregamentoDados

# Isso força o Python a olhar dentro da pasta 'src'
sys.path.append(os.path.join(os.path.dirname(__file__), "."))


def main():

    print("Executando algoritmo SAW")

    c1 = Criterio("IAG0001", "Índice de atendimento total Abs. Água", 0.20)
    c2 = Criterio("IAG2008", "Índice de vol. água disponibilizada economia", 0.09)
    c3 = Criterio("IAG2013", "Perdas totais de água na distribuição", 0.31)
    c4 = Criterio("IAG3008", "Índice de reclamações água", 0.06)
    c5 = Criterio("IES0001", "Índice de atendimento total Col. Esgoto", 0.17)
    c6 = Criterio("IES2002", "Esgoto coletado referido à água consumida", 0.17)
   

    ListaDeCriterios = [c1, c2, c3, c4, c5, c6]

    # instancia obj chamado desrealizador
    desrealizador = desrealizadorDeDados()
    planilhaDeDados = desrealizador.extracaoDadosBruto("base-de-dados-teste.ods")

    # Fase 1: Dividir celulas pelo maior Nº de suas respectivas colunas
    municipios = planilhaDeDados["Município"]
    dadosNumericos = planilhaDeDados.drop(columns=["Município"])
    valoresMaximos = dadosNumericos.max()
    dadosNormalizados = dadosNumericos / valoresMaximos
    dataFrameNormalizado = pd.concat([municipios, dadosNormalizados], axis=1)   # axis = 1 ? percorre em linhas : 0 ? percorre em colunas

    # Validação de colunas obrigatórias
    required_cols = [c.criterioId for c in ListaDeCriterios]
    missing_cols = [col for col in required_cols if col not in planilhaDeDados.columns]
    if missing_cols:
        raise ValueError(f"Colunas obrigatórias não encontradas na planilha: {missing_cols}")

    # Fase 2: Soma do produto dados indicador * peso de indicador
    dfCriterios = Criterio.criaDataframeDeCriterios(ListaDeCriterios)
    if dfCriterios['peso'].sum() == 0:
        print("Aviso: todos os pesos são zero, definindo pesos iguais a 1 para cada critério.")
        dfCriterios['peso'] = 1

    dadosNumericosNormalizados = dataFrameNormalizado.drop(columns=["Município"])
    dadosPonderados = Normalizacao.aplicarPesos(dadosNumericosNormalizados, dfCriterios)
    dadosPonderados = pd.DataFrame(dadosPonderados, columns=dadosNumericosNormalizados.columns, index=municipios.index)
    resultadoFinal = pd.concat([municipios, dadosPonderados], axis=1)
    somaProdutoTabela = Normalizacao.somaProduto(resultadoFinal)

    #Fase 3: Cria Rankin dos municipios
    rankinMunicipios = Normalizacao.rankinMunicipios(somaProdutoTabela)
    carregamento_dados = CarregamentoDados()
    graficoRankingMunicipios = carregamento_dados.plotarRanking(rankinMunicipios)
    

    print(planilhaDeDados)
    print(dataFrameNormalizado)
    print(rankinMunicipios)
    print(graficoRankingMunicipios)

if __name__ == "__main__":
    main()