#ARmazena os tipos de ndicadores e seus pesos
import pandas as pd

class Criterio:

    def __init__(self, criterioId, descricaoCriterio, pesoCriterio):
        self.criterioId = criterioId
        self.descricaoCriterio = descricaoCriterio
        self.pesoCriterio = pesoCriterio

    def criaDataframeDeCriterios(listaCriterios):
        listaCriteriosDf = []
        for c in listaCriterios:
            dicionarioCriterios = {
            "criterioId": c.criterioId,
            "peso": c.pesoCriterio
            }
            listaCriteriosDf.append(dicionarioCriterios)
        df_criterios = pd.DataFrame(listaCriteriosDf) 
        return df_criterios