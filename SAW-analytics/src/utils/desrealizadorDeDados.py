from models.Alternativa import Alternativa
import os
from pathlib import Path
import pandas as pd

class desrealizadorDeDados():
    def __init__(self):
        # Define a raiz do projeto (ajuste o número de 'parents' conforme necessário)
        self.raiz_projeto = Path(__file__).resolve().parent.parent.parent

    def extracaoDadosBruto(self, nomeArquivoDeDadosBruto, nomeAba=None):
        
        print("Extraindo os dados...")
        
        caminho_arquivo = self.raiz_projeto / "src" / "dados" / "dadosBruto" / nomeArquivoDeDadosBruto
        if not caminho_arquivo.exists():
            raise FileNotFoundError(f"O sistema não encontrou o arquivo no caminho: {caminho_arquivo}")
        else:
             print(f"Tentando abrir: {caminho_arquivo}")
    
        df = pd.read_excel(caminho_arquivo, sheet_name=nomeAba, engine="openpyxl", decimal=",")
        
        #print(df.head())
        return df

    def listarAbas(self, nomeArquivoDeDadosBruto):
        caminho_arquivo = self.raiz_projeto / "src" / "dados" / "dadosBruto" / nomeArquivoDeDadosBruto
        if not caminho_arquivo.exists():
            raise FileNotFoundError(f"O sistema não encontrou o arquivo no caminho: {caminho_arquivo}")

        arquivo_excel = pd.ExcelFile(caminho_arquivo, engine="openpyxl")
        return arquivo_excel.sheet_names

    def tratarCelulasVazias():
        return
