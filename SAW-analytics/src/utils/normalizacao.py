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
    
    def somaProduto(dadosPonderados):

        municipios = dadosPonderados["Município"]

        dadosNumericos = dadosPonderados.drop(columns=["Município"])

        somaIndicadores = dadosNumericos.sum(axis=1)

        somaIndicadores.name = "Score"

        dfRanqueado = pd.concat([municipios, somaIndicadores], axis=1)

        return dfRanqueado
    
    def rankinMunicipios(somaProdutoTabela):
        ranking = somaProdutoTabela.sort_values(by="Score", ascending=False)
        return ranking