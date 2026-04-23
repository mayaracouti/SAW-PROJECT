import pandas as pd

class Normalizacao:
    def valorMaximoColuna(self, planilhaDeDados):
        return planilhaDeDados.max()
    
    def valoMinimoColuna(self, planilhaDeDados):
        return planilhaDeDados.min()
    
    @staticmethod
    def aplicarPesos(dfNormalizado, dfCriterios):
        # 1. Criamos um mapa de pesos: {'ID_DA_COLUNA': VALOR_DO_PESO}
        # Isso garante que o Python encontre o peso pelo nome, não pela posição
        mapa_pesos = dict(zip(dfCriterios['criterioId'], dfCriterios['peso']))
        
        # 2. Criamos uma cópia para não mexer nos dados originais
        dfPonderado = pd.DataFrame(index=dfNormalizado.index)

        for coluna in dfNormalizado.columns:
            if coluna in mapa_pesos:
                # 3. Realiza a multiplicação apenas se o ID existir no mapa
                dfPonderado[coluna] = dfNormalizado[coluna] * mapa_pesos[coluna]
            else:
                # Caso o nome da coluna não bata com o ID do critério, avisamos
                print(f"Aviso: Coluna {coluna} não encontrada nos critérios.")
                dfPonderado[coluna] = 0.0
                
        return dfPonderado

    @staticmethod
    def normalizar_saw(dfDados, dfCriterios):
        mapa_objetivos = dict(zip(dfCriterios["criterioId"], dfCriterios["objetivo"]))
        dfNormalizado = pd.DataFrame(index=dfDados.index)

        for coluna in dfDados.columns:
            objetivo = mapa_objetivos.get(coluna)
            serie = pd.to_numeric(dfDados[coluna], errors="coerce")

            if serie.isna().all():
                raise ValueError(f"A coluna {coluna} não possui valores numéricos válidos.")

            if objetivo == "bom":
                denominador = serie.max()
                if pd.isna(denominador) or denominador == 0:
                    dfNormalizado[coluna] = 0.0
                else:
                    dfNormalizado[coluna] = serie / denominador
            elif objetivo == "ruim":
                numerador = serie.min()
                if pd.isna(numerador) or numerador == 0:
                    positivos = serie[serie > 0]
                    numerador = positivos.min() if not positivos.empty else 0

                if numerador == 0:
                    dfNormalizado[coluna] = 0.0
                else:
                    dfNormalizado[coluna] = serie.apply(
                        lambda valor: 0.0 if pd.isna(valor) or valor == 0 else numerador / valor
                    )
            else:
                raise ValueError(f"Objetivo do critério {coluna} não definido. Use 'bom' ou 'ruim'.")

        return dfNormalizado.fillna(0.0)
    
    def somaProduto(dadosPonderados):

        municipios = dadosPonderados["Município"]

        dadosNumericos = dadosPonderados.drop(columns=["Município"])

        somaIndicadores = dadosNumericos.sum(axis=1)

        somaIndicadores.name = "Score"

        dfRanqueado = pd.concat([municipios, somaIndicadores], axis=1)

        return dfRanqueado
    
    def rankinMunicipios(somaProdutoTabela):
        ranking = somaProdutoTabela.sort_values(by="Score", ascending=False)
        ranking = ranking.reset_index(drop=True)
        ranking.index = ranking.index + 1
        ranking.index.name = "Posição"
        return ranking
