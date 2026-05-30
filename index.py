from notanegociacao.corretora import Corretora


def main():
    corretora = Corretora("./notas/")
    print(len(corretora.notasNegociacao))


if __name__ == "__main__":
    main()
