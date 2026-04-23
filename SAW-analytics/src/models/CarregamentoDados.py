from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd

class CarregamentoDados:
    def _nome_aba_excel(self, nome, usados):
        caracteres_invalidos = ["\\", "/", "*", "?", ":", "[", "]"]
        nome_limpo = str(nome)
        for caractere in caracteres_invalidos:
            nome_limpo = nome_limpo.replace(caractere, " ")

        nome_limpo = " ".join(nome_limpo.split())[:31] or "ranking"
        nome_final = nome_limpo
        contador = 2
        while nome_final in usados:
            sufixo = f" {contador}"
            nome_final = f"{nome_limpo[:31 - len(sufixo)]}{sufixo}"
            contador += 1

        usados.add(nome_final)
        return nome_final

    def _combinar_rankings_para_csv(self, rankingDetalhado, rankingsPorNatureza, rankingsExtras):
        rankings = [rankingDetalhado.assign(Ranking="Geral")]

        for nome, ranking in rankingsExtras.items():
            rankings.append(ranking.assign(Ranking=nome))

        for natureza, ranking in rankingsPorNatureza.items():
            rankings.append(ranking.assign(Ranking=f"Natureza Jurídica - {natureza}"))

        colunas = ["Ranking"] + [coluna for coluna in rankingDetalhado.columns]
        return pd.concat(rankings, ignore_index=True)[colunas]

    def exportar_planilha(
        self,
        rankingDetalhado,
        criterios,
        caminho_padrao,
        rankingsPorNatureza=None,
        rankingsExtras=None,
    ):
        rankingsPorNatureza = rankingsPorNatureza or {}
        rankingsExtras = rankingsExtras or {}
        caminho_sugerido = Path(caminho_padrao)
        caminho_destino = filedialog.asksaveasfilename(
            title="Salvar planilha do ranking SAW",
            initialdir=str(caminho_sugerido.parent),
            initialfile=caminho_sugerido.name,
            defaultextension=".xlsx",
            filetypes=[
                ("Planilha Excel", "*.xlsx"),
                ("CSV", "*.csv"),
            ],
        )

        if not caminho_destino:
            return

        destino = Path(caminho_destino)
        if destino.suffix.lower() == ".csv":
            self._combinar_rankings_para_csv(rankingDetalhado, rankingsPorNatureza, rankingsExtras).to_csv(
                destino,
                sep=";",
                index=False,
                encoding="utf-8-sig",
            )
        else:
            with pd.ExcelWriter(destino, engine="openpyxl") as writer:
                nomes_abas = set()
                rankingDetalhado.to_excel(
                    writer,
                    sheet_name=self._nome_aba_excel("ranking_geral", nomes_abas),
                    index=False,
                )

                for nome, ranking in rankingsExtras.items():
                    ranking.to_excel(
                        writer,
                        sheet_name=self._nome_aba_excel(nome, nomes_abas),
                        index=False,
                    )

                for natureza, ranking in rankingsPorNatureza.items():
                    ranking.to_excel(
                        writer,
                        sheet_name=self._nome_aba_excel(natureza, nomes_abas),
                        index=False,
                    )

                criterios.to_excel(writer, sheet_name="indicadores", index=False)

        messagebox.showinfo("Exportação concluída", f"Arquivo salvo em:\n{destino}")

    def _criar_tabela(self, parent, dataframe, titulo):
        frame = ttk.LabelFrame(parent, text=titulo, padding=10)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        colunas = list(dataframe.columns)
        tree = ttk.Treeview(frame, columns=colunas, show="headings")

        for coluna in colunas:
            tree.heading(coluna, text=coluna)
            tree.column(coluna, width=140, anchor="center")

        for _, linha in dataframe.iterrows():
            valores = []
            for valor in linha.tolist():
                if isinstance(valor, float):
                    valores.append(f"{valor:.6f}".rstrip("0").rstrip("."))
                else:
                    valores.append(valor)
            tree.insert("", "end", values=valores)

        scroll_y = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        scroll_x = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

        tree.grid(row=0, column=0, sticky="nsew")
        scroll_y.grid(row=0, column=1, sticky="ns")
        scroll_x.grid(row=1, column=0, sticky="ew")

        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

    def visualizar_resultados(self, rankingDetalhado, criterios, rankingsPorNatureza=None, rankingsExtras=None):
        rankingsPorNatureza = rankingsPorNatureza or {}
        rankingsExtras = rankingsExtras or {}
        janela = tk.Toplevel()
        janela.title("Resultado SAW - Municípios PCJ")
        janela.geometry("1400x800")

        resumo = ttk.Label(
            janela,
            text="Ranking dos municípios e resumo dos indicadores usados no cálculo SAW",
            padding=10,
        )
        resumo.pack(anchor="w")

        abas = ttk.Notebook(janela)
        abas.pack(fill="both", expand=True, padx=10, pady=10)

        aba_geral = ttk.Frame(abas)
        abas.add(aba_geral, text="Ranking Geral")
        self._criar_tabela(aba_geral, rankingDetalhado.copy(), "Ranking Geral dos Municípios")

        for nome, ranking in rankingsExtras.items():
            aba_extra = ttk.Frame(abas)
            abas.add(aba_extra, text=nome[:24])
            self._criar_tabela(aba_extra, ranking.copy(), nome)

        for natureza, ranking in rankingsPorNatureza.items():
            aba_natureza = ttk.Frame(abas)
            abas.add(aba_natureza, text="Natureza Jurídica")
            abas_natureza = ttk.Notebook(aba_natureza)
            abas_natureza.pack(fill="both", expand=True, padx=10, pady=10)

            for natureza, ranking in rankingsPorNatureza.items():
                subaba_natureza = ttk.Frame(abas_natureza)
                abas_natureza.add(subaba_natureza, text=str(natureza)[:24])
                self._criar_tabela(
                    subaba_natureza,
                    ranking.copy(),
                    f"Ranking - {natureza}",
                )

        aba_indicadores = ttk.Frame(abas)
        abas.add(aba_indicadores, text="Indicadores")
        self._criar_tabela(aba_indicadores, criterios, "Indicadores")

    def mostrar_popup_resultados(
        self,
        rankingDetalhado,
        criterios,
        caminho_padrao,
        rankingsPorNatureza=None,
        rankingsExtras=None,
    ):
        rankingsPorNatureza = rankingsPorNatureza or {}
        rankingsExtras = rankingsExtras or {}
        root = tk.Tk()
        root.title("SAW Analytics")
        root.geometry("420x210")
        root.resizable(False, False)

        frame = ttk.Frame(root, padding=20)
        frame.pack(fill="both", expand=True)

        ttk.Label(
            frame,
            text="Processamento concluído com sucesso.",
            font=("TkDefaultFont", 11, "bold"),
        ).pack(anchor="w", pady=(0, 8))

        ttk.Label(
            frame,
            text="Escolha uma ação para o ranking e os indicadores calculados.",
            wraplength=360,
            justify="left",
        ).pack(anchor="w", pady=(0, 16))

        ttk.Button(
            frame,
            text="1. Baixar planilha",
            command=lambda: self.exportar_planilha(
                rankingDetalhado,
                criterios,
                caminho_padrao,
                rankingsPorNatureza,
                rankingsExtras,
            ),
        ).pack(fill="x", pady=6)

        ttk.Button(
            frame,
            text="2. Visualizar ranking e indicadores",
            command=lambda: self.visualizar_resultados(
                rankingDetalhado,
                criterios,
                rankingsPorNatureza,
                rankingsExtras,
            ),
        ).pack(fill="x", pady=6)

        ttk.Button(
            frame,
            text="Fechar",
            command=root.destroy,
        ).pack(fill="x", pady=(18, 0))

        root.mainloop()
