from config.parametros import BACIAS_POR_MUNICIPIO_PCJ, criterios
from model.extracao_dados_brutos import ExtracaoDadosBrutos
from service.etl_indicadores import ETLIndicadores


def main():
    print("Iniciando extração de indicadores dos municípios PCJ...")

    extrator = ExtracaoDadosBrutos()
    planilhas = extrator.leitura_dados_brutos()

    etl = ETLIndicadores(BACIAS_POR_MUNICIPIO_PCJ, criterios)
    resultado = etl.processar(planilhas)
    caminho_arquivo = etl.salvar(resultado)

    print("Processo finalizado.")
    print(f"Arquivo gerado em: {caminho_arquivo}")


if __name__ == "__main__":
    main()
