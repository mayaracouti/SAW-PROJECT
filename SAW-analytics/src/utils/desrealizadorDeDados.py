from models.Alternativa import Alternativa
import os
from pathlib import Path
import pandas as pd

class desrealizadorDeDados():
    def __init__(self):
        # Define a raiz do projeto (ajuste o número de 'parents' conforme necessário)
        self.raiz_projeto = Path(__file__).resolve().parent.parent.parent

    def extracaoDadosBruto(self, nomeArquivoDeDadosBruto):
        
        nomeArquivoDeDadosBruto = nomeArquivoDeDadosBruto
        print("Extraindo os dados...")
        
        caminho_arquivo = self.raiz_projeto / "src" / "dados" / "dadosBruto" / nomeArquivoDeDadosBruto
        if not caminho_arquivo.exists():
            raise FileNotFoundError(f"O sistema não encontrou o arquivo no caminho: {caminho_arquivo}")
        else:
             print(f"Tentando abrir: {caminho_arquivo}")
    
        df = pd.read_excel(caminho_arquivo, engine="odf", decimal=",")
        
        #print(df.head())
        return df

    def tratarCelulasVazias():
        return