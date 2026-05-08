#ARmazena os tipos de ndicadores e seus pesos
import pandas as pd

class Criterio:

    def __init__(self, criterioId, descricaoCriterio, pesoCriterio, objetivo=None):
        self.criterioId = criterioId
        self.descricaoCriterio = descricaoCriterio
        self.pesoCriterio = pesoCriterio
        self.objetivo = objetivo

    def criaDataframeDeCriterios(listaCriterios):
        listaCriteriosDf = []
        for c in listaCriterios:
            dicionarioCriterios = {
            "criterioId": c.criterioId,
            "descricao": c.descricaoCriterio,
            "peso": c.pesoCriterio,
            "objetivo": c.objetivo
            }
            listaCriteriosDf.append(dicionarioCriterios)
        df_criterios = pd.DataFrame(listaCriteriosDf) 
        return df_criterios
