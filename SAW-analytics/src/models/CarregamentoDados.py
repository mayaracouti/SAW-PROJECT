import matplotlib.pyplot as plt
import matplotlib.cm as cm # Importa os mapas de cores
import numpy as np

class CarregamentoDados:
    def plotarRanking(self, ranking):
        ranking = ranking.sort_values(by="Score", ascending=True)

        # 1. Preparar as cores baseadas no Score
        # Usamos 'RdYlGn' (Red-Yellow-Green): Vermelho para baixo, Verde para alto
        norm = plt.Normalize(ranking["Score"].min(), ranking["Score"].max())
        cores = cm.RdYlGn(norm(ranking["Score"].values))

        plt.figure(figsize=(12, 16))

        # 2. Aplicar as cores no parâmetro 'color'
        plt.barh(ranking["Município"], ranking["Score"], color=cores, edgecolor='black', alpha=0.8)

        plt.xlabel("Score (Desempenho)")
        plt.ylabel("Municípios")
        plt.title("Ranking dos Municípios - Método SAW")
        
        # 3. Adicionar uma barra de legenda lateral para a escala de cores
        sm = plt.cm.ScalarMappable(cmap=cm.RdYlGn, norm=norm)
        plt.colorbar(sm, label="Escala de Desempenho", ax=plt.gca())

        plt.grid(axis='x', linestyle=':', alpha=0.6)
        plt.tight_layout()
        plt.show()