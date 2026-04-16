from pathlib import Path

import pandas as pd


class ETLIndicadores:
    """Filtra os municípios PCJ e monta uma base pronta para análise."""

    def __init__(self, bacias_por_municipio, criterios):
        self.bacias_por_municipio = bacias_por_municipio
        self.criterios = criterios
        self.codigos_ibge_pcj = {str(codigo) for codigo in bacias_por_municipio}

    def processar(self, planilhas):
        tabelas_tratadas = []

        for nome_aba, df_bruto in planilhas.items():
            df_tratado = self._tratar_aba(nome_aba, df_bruto)
            if not df_tratado.empty:
                tabelas_tratadas.append(df_tratado)

        if not tabelas_tratadas:
            raise ValueError(
                "Nenhuma aba com colunas 'Cod_IBGE' e 'Município' foi encontrada."
            )

        base_consolidada = pd.concat(tabelas_tratadas, ignore_index=True, sort=False)
        municipios_pcj = self._montar_base_municipios(base_consolidada)
        base_indicadores = self._montar_base_indicadores(base_consolidada, municipios_pcj)
        diagnostico = self._montar_diagnostico(base_consolidada, base_indicadores)

        return {
            "municipios_pcj": municipios_pcj,
            "base_indicadores": base_indicadores,
            "diagnostico_indicadores": diagnostico,
        }

    def salvar(self, resultado, nome_arquivo="indicadores_pcj.xlsx"):
        pasta_saida = Path(__file__).resolve().parents[1] / "Data" / "indicador_database"
        pasta_saida.mkdir(parents=True, exist_ok=True)

        caminho_arquivo = pasta_saida / nome_arquivo
        with pd.ExcelWriter(caminho_arquivo) as writer:
            resultado["municipios_pcj"].to_excel(
                writer, sheet_name="municipios_pcj", index=False
            )
            resultado["base_indicadores"].to_excel(
                writer, sheet_name="base_indicadores", index=False
            )
            resultado["diagnostico_indicadores"].to_excel(
                writer, sheet_name="diagnostico_indicadores", index=False
            )

        return caminho_arquivo

    def _tratar_aba(self, nome_aba, df_bruto):
        indice_cabecalho = self._encontrar_linha_cabecalho(df_bruto)
        if indice_cabecalho is None:
            return pd.DataFrame()

        cabecalho = self._normalizar_cabecalho(df_bruto.iloc[indice_cabecalho].tolist())
        df = df_bruto.iloc[indice_cabecalho + 1 :].copy()
        df.columns = cabecalho
        df = df.loc[:, [coluna for coluna in df.columns if coluna]]
        df = df.fillna("")

        if "Cod_IBGE" not in df.columns or "Município" not in df.columns:
            return pd.DataFrame()

        df["Cod_IBGE"] = df["Cod_IBGE"].apply(self._normalizar_codigo_ibge)
        df = df[df["Cod_IBGE"].isin(self.codigos_ibge_pcj)].copy()

        if df.empty:
            return pd.DataFrame()

        df["aba_origem"] = nome_aba
        return df

    def _encontrar_linha_cabecalho(self, df):
        for indice, linha in df.head(10).iterrows():
            valores = {str(valor).strip() for valor in linha.tolist() if str(valor).strip()}
            if "Cod_IBGE" in valores and "Município" in valores:
                return indice
        return None

    def _normalizar_cabecalho(self, colunas):
        cabecalho = []
        contadores = {}

        for coluna in colunas:
            nome = str(coluna).strip()
            if not nome:
                cabecalho.append("")
                continue

            quantidade = contadores.get(nome, 0)
            contadores[nome] = quantidade + 1
            cabecalho.append(nome if quantidade == 0 else f"{nome}_{quantidade}")

        return cabecalho

    def _normalizar_codigo_ibge(self, valor):
        valor_texto = "".join(ch for ch in str(valor) if ch.isdigit())
        return valor_texto

    def _montar_base_municipios(self, base_consolidada):
        colunas_preferidas = ["Cod_IBGE", "Município", "UF", "Região"]
        colunas_existentes = [
            coluna for coluna in colunas_preferidas if coluna in base_consolidada.columns
        ]

        municipios = (
            base_consolidada[colunas_existentes]
            .drop_duplicates(subset=["Cod_IBGE"])
            .sort_values("Município")
            .reset_index(drop=True)
        )

        municipios["bacias"] = municipios["Cod_IBGE"].map(self._buscar_bacias).str.join(", ")
        municipios["municipio_referencia_pcj"] = municipios["Cod_IBGE"].map(
            self._buscar_nome_pcj
        )
        return municipios

    def _montar_base_indicadores(self, base_consolidada, municipios_pcj):
        registros = municipios_pcj.copy()

        abas_por_municipio = (
            base_consolidada.groupby("Cod_IBGE")["aba_origem"]
            .apply(lambda abas: ", ".join(sorted(set(abas))))
            .to_dict()
        )
        registros["abas_encontradas_no_arquivo"] = registros["Cod_IBGE"].map(
            abas_por_municipio
        )

        for codigo_indicador, _descricao in self.criterios:
            registros[codigo_indicador] = self._extrair_indicador_pronto(
                base_consolidada, registros, codigo_indicador
            )

        return registros

    def _montar_diagnostico(self, base_consolidada, base_indicadores):
        colunas_arquivo = set(base_consolidada.columns)
        municipios_encontrados = set(base_indicadores["Cod_IBGE"])
        municipios_esperados = {str(codigo) for codigo in self.bacias_por_municipio}

        diagnostico = []
        for codigo_indicador, descricao in self.criterios:
            diagnostico.append(
                {
                    "indicador": codigo_indicador,
                    "descricao": descricao,
                    "encontrado_no_arquivo": codigo_indicador in colunas_arquivo,
                    "observacao": (
                        "Critério encontrado no arquivo e copiado para a tabela final."
                        if codigo_indicador in colunas_arquivo
                        else "Critério não foi localizado como coluna pronta no arquivo bruto atual."
                    ),
                }
            )

        faltantes = sorted(municipios_esperados - municipios_encontrados)
        if faltantes:
            diagnostico.append(
                {
                    "indicador": "MUNICIPIOS_PCJ",
                    "descricao": "Verificação de cobertura dos municípios da PCJ",
                    "encontrado_no_arquivo": False,
                    "observacao": (
                        "Municípios da lista PCJ ausentes no arquivo bruto: "
                        + ", ".join(faltantes)
                    ),
                }
            )

        return pd.DataFrame(diagnostico)

    def _buscar_bacias(self, codigo_ibge):
        return self.bacias_por_municipio.get(int(codigo_ibge), {}).get("bacias", [])

    def _buscar_nome_pcj(self, codigo_ibge):
        return self.bacias_por_municipio.get(int(codigo_ibge), {}).get("municipio", "")

    def _extrair_indicador_pronto(self, base_consolidada, registros, codigo_indicador):
        if codigo_indicador not in base_consolidada.columns:
            return pd.Series([pd.NA] * len(registros))

        valores = (
            base_consolidada[["Cod_IBGE", codigo_indicador]]
            .drop_duplicates(subset=["Cod_IBGE"])
            .set_index("Cod_IBGE")[codigo_indicador]
        )
        return registros["Cod_IBGE"].map(valores)
