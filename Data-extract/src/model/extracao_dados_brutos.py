from pathlib import Path
from zipfile import ZipFile
import xml.etree.ElementTree as ET

import pandas as pd


class ExtracaoDadosBrutos:
    """Lê arquivos brutos do projeto e devolve as abas como DataFrames."""

    NS = {
        "office": "urn:oasis:names:tc:opendocument:xmlns:office:1.0",
        "table": "urn:oasis:names:tc:opendocument:xmlns:table:1.0",
        "text": "urn:oasis:names:tc:opendocument:xmlns:text:1.0",
    }

    def __init__(self):
        self.raiz_projeto = Path(__file__).resolve().parents[2]
        self.pasta_raw_data = self.raiz_projeto / "src" / "Data" / "Raw_data"

    def leitura_dados_brutos(self, nome_arquivo=None):
        caminho_arquivo = self._resolver_caminho_arquivo(nome_arquivo)
        print(f"Lendo arquivo bruto: {caminho_arquivo.name}")

        if caminho_arquivo.suffix.lower() == ".ods":
            return self._ler_ods(caminho_arquivo)

        return pd.read_excel(caminho_arquivo, sheet_name=None)

    def _resolver_caminho_arquivo(self, nome_arquivo=None):
        if nome_arquivo:
            caminho_arquivo = self.pasta_raw_data / nome_arquivo
        else:
            candidatos = sorted(self.pasta_raw_data.glob("*.ods")) + sorted(
                self.pasta_raw_data.glob("*.xlsx")
            )
            if not candidatos:
                raise FileNotFoundError(
                    f"Nenhum arquivo .ods ou .xlsx foi encontrado em {self.pasta_raw_data}"
                )
            caminho_arquivo = candidatos[0]

        if not caminho_arquivo.exists():
            raise FileNotFoundError(
                f"O arquivo bruto informado não foi encontrado: {caminho_arquivo}"
            )

        return caminho_arquivo

    def _ler_ods(self, caminho_arquivo):
        with ZipFile(caminho_arquivo) as arquivo_zip:
            xml_raiz = ET.fromstring(arquivo_zip.read("content.xml"))

        planilhas = {}
        spreadsheet = (
            xml_raiz.find("office:body", self.NS).find("office:spreadsheet", self.NS)
        )

        for tabela in spreadsheet.findall("table:table", self.NS):
            nome_tabela = tabela.attrib.get(f"{{{self.NS['table']}}}name", "Sem nome")
            linhas = []

            for linha in tabela.findall("table:table-row", self.NS):
                repeticoes_linha = int(
                    linha.attrib.get(f"{{{self.NS['table']}}}number-rows-repeated", "1")
                )
                valores_linha = self._extrair_linha(linha)

                if not valores_linha:
                    continue

                for _ in range(repeticoes_linha):
                    linhas.append(list(valores_linha))

            planilhas[nome_tabela] = self._criar_dataframe(linhas)

        return planilhas

    def _extrair_linha(self, linha):
        valores = []

        for celula in list(linha):
            repeticoes_coluna = int(
                celula.attrib.get(
                    f"{{{self.NS['table']}}}number-columns-repeated", "1"
                )
            )

            if celula.tag.endswith("covered-table-cell"):
                # Células cobertas aparecem em áreas mescladas do ODS.
                # Para o ETL, uma posição vazia já representa essa área.
                valores.append("")
                continue

            texto = self._extrair_texto_celula(celula)
            if texto == "" and repeticoes_coluna > 1:
                valores.append("")
            else:
                valores.extend([texto] * repeticoes_coluna)

        while valores and valores[-1] == "":
            valores.pop()

        return valores

    def _extrair_texto_celula(self, celula):
        paragrafos = [
            "".join(paragrafo.itertext()).strip()
            for paragrafo in celula.findall(".//text:p", self.NS)
        ]
        paragrafos = [texto for texto in paragrafos if texto]

        if paragrafos:
            return " ".join(paragrafos)

        return celula.attrib.get(f"{{{self.NS['office']}}}value", "")

    def _criar_dataframe(self, linhas):
        if not linhas:
            return pd.DataFrame()

        quantidade_colunas = max(len(linha) for linha in linhas)
        linhas_preenchidas = [
            linha + [""] * (quantidade_colunas - len(linha)) for linha in linhas
        ]
        return pd.DataFrame(linhas_preenchidas)
