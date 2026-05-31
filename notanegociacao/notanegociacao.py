from notanegociacao.negociorealizado import NegocioRealizado
from notanegociacao.resumofinanceiro import ResumoFinanceiro
from notanegociacao.resumonegocios import ResumoNegocios
from notanegociacao.util import strToFloat, strToInt, extractNumber
import datetime


class NotaNegociacao:
    numero: str
    dataPregao: datetime.date
    negociosRealizados: list[NegocioRealizado]
    resumoNegocios: ResumoNegocios
    resumoFinanceiro: ResumoFinanceiro

    OBS = [
        '2',  # Corretora ou pessoa vinculada atuou na contra parte
        '#',  # Negócio direto
        '8',  # Liquidação Institucional
        'D',  # Day Trade
        'F',  # Cobertura
        'B',  # Debêntures
        'A',  # Posição futuro
        'C',  # Clubes e fundos de Ações
        'P',  # Carteira Própria
        'H',  # Home Broker
        'X',  # Box
        'Y',  # Desmanche de Box
        'L',  # Precatório
        'T',  # Liquidação pelo Bruto
        'I',  # POP
    ]

    def __init__(self, numero: str):
        self.numero = numero

        self.negociosRealizados = []
        self.resumoNegocios = ResumoNegocios()
        self.resumoFinanceiro = ResumoFinanceiro()

    @staticmethod
    def parseText(text: str, notas: list['NotaNegociacao'] = []) -> list['NotaNegociacao']:
        nota: NotaNegociacao | None = None
        folhaAtual = 0

        lines = text.splitlines()

        i = 0
        while (i < len(lines)):
            if ('Nr. nota' in lines[i]):
                i += 1
                line = lines[i].split()
                folhaAtual = strToInt(line[1])

                nota = next(
                    (nota for nota in notas if nota.numero == line[0]), None)

                if (nota == None):
                    nota = NotaNegociacao(line[0])
                    notas.append(nota)

                nota.dataPregao = datetime.datetime.strptime(
                    line[2], '%d/%m/%Y').date()

            if (lines[i] == 'Negócios realizados'):
                i += 2

                while ('Resumo dos Negócios' not in lines[i] and nota != None):
                    nota.negociosRealizados.append(NotaNegociacao.__getNegocioInfo(
                        lines[i], folhaAtual))

                    i += 1

                # verifica se a listagem de operações continua em outra folha
                j = i
                while ('Total Bovespa' not in lines[j]):
                    j += 1

                if ('CONTINUA' in lines[j]):
                    break

            if ('Clearing' in lines[i] and nota != None):
                nota.resumoNegocios.debentures = strToFloat(lines[i][lines[i].find(
                    ' ') + 1:lines[i].rfind(' ')])

            if ('Vendas à vista' in lines[i] and nota != None):
                lines[i] = lines[i].replace('Vendas à vista ', '')
                nota.resumoNegocios.vendasVista = extractNumber(lines[i])

                creditoDebito = lines[i][-1:]
                lines[i] = lines[i][:lines[i].rfind(' ')]
                nota.resumoFinanceiro.clearing.valorLiquidoOperacoes = extractNumber(
                    lines[i])

                if (creditoDebito == 'D'):
                    nota.resumoFinanceiro.clearing.valorLiquidoOperacoes *= -1

            if ('Compras à vista' in lines[i] and nota != None):
                lines[i] = lines[i].replace('Compras à vista ', '')
                nota.resumoNegocios.comprasVista = extractNumber(lines[i])

                creditoDebito = lines[i][-1:]
                lines[i] = lines[i][:lines[i].rfind(' ')]
                nota.resumoFinanceiro.clearing.taxaLiquidacao = extractNumber(
                    lines[i])

                if (creditoDebito == 'D'):
                    nota.resumoFinanceiro.clearing.taxaLiquidacao *= -1

            if ('Opções - compras' in lines[i] and nota != None):
                lines[i] = lines[i].replace('Opções - compras ', '')
                nota.resumoNegocios.opcoesCompras = extractNumber(lines[i])

                creditoDebito = lines[i][-1:]
                lines[i] = lines[i][:lines[i].rfind(' ')]
                nota.resumoFinanceiro.clearing.taxaRegistro = extractNumber(
                    lines[i])

                if (creditoDebito == 'D'):
                    nota.resumoFinanceiro.clearing.taxaRegistro *= -1

            if ('Opções - vendas' in lines[i] and nota != None):
                lines[i] = lines[i].replace('Opções - vendas ', '')
                nota.resumoNegocios.opcoesVendas = extractNumber(lines[i])

                creditoDebito = lines[i][-1:]
                lines[i] = lines[i][:lines[i].rfind(' ')]
                nota.resumoFinanceiro.clearing.totalCBLC = extractNumber(
                    lines[i])

                if (creditoDebito == 'D'):
                    nota.resumoFinanceiro.clearing.totalCBLC *= -1

            if ('Operações à termo' in lines[i] and nota != None):
                lines[i] = lines[i].replace('Operações à termo ', '')
                nota.resumoNegocios.operacoesTermo = extractNumber(lines[i])

            if ('Valor das oper. c/ títulos públ. (v. nom.)' in lines[i] and nota != None):
                lines[i] = lines[i].replace(
                    'Valor das oper. c/ títulos públ. (v. nom.) ', '')
                nota.resumoNegocios.valorOperacoesTitulosPublicosVNom = extractNumber(
                    lines[i])

                creditoDebito = lines[i][-1:]
                lines[i] = lines[i][:lines[i].rfind(' ')]
                nota.resumoFinanceiro.bolsa.taxaTermoOpcoes = extractNumber(
                    lines[i])

                if (creditoDebito == 'D'):
                    nota.resumoFinanceiro.bolsa.taxaTermoOpcoes *= -1

            if ('Valor das operações' in lines[i] and nota != None):
                lines[i] = lines[i].replace(
                    'Valor das operações ', '')
                nota.resumoNegocios.valorOperacoes = extractNumber(lines[i])

                creditoDebito = lines[i][-1:]
                lines[i] = lines[i][:lines[i].rfind(' ')]
                nota.resumoFinanceiro.bolsa.taxaANA = extractNumber(lines[i])

                if (creditoDebito == 'D'):
                    nota.resumoFinanceiro.bolsa.taxaANA *= -1

            if ('Emolumentos' in lines[i] and nota != None):
                creditoDebito = lines[i][-1:]
                lines[i] = lines[i][:lines[i].rfind(' ')]
                nota.resumoFinanceiro.bolsa.emolumentos = extractNumber(
                    lines[i])

                if (creditoDebito == 'D'):
                    nota.resumoFinanceiro.bolsa.emolumentos *= -1

            if ('Total Bovespa / Soma' in lines[i] and nota != None):
                creditoDebito = lines[i][-1:]
                lines[i] = lines[i][:lines[i].rfind(' ')]
                nota.resumoFinanceiro.bolsa.totalBovespaSoma = extractNumber(
                    lines[i])

                if (creditoDebito == 'D'):
                    nota.resumoFinanceiro.bolsa.totalBovespaSoma *= -1

            if ('Taxa Operacional' in lines[i] and nota != None):
                creditoDebito = lines[i][-1:]
                lines[i] = lines[i][:lines[i].rfind(' ')]
                nota.resumoFinanceiro.custosOperacionais.taxaOperacional = extractNumber(
                    lines[i])

                if (creditoDebito == 'D'):
                    nota.resumoFinanceiro.custosOperacionais.taxaOperacional *= -1

            if ('Execução' in lines[i] and nota != None):
                nota.resumoFinanceiro.custosOperacionais.execucao = extractNumber(
                    lines[i])

            if ('Taxa de Custódia' in lines[i] and nota != None):
                nota.resumoFinanceiro.custosOperacionais.taxaCustodia = extractNumber(
                    lines[i])

            if ('Impostos' in lines[i] and nota != None):
                lineInfo = lines[i].split()
                nota.resumoFinanceiro.custosOperacionais.impostos = extractNumber(
                    lines[i])

            if ('I.R.R.F. s/ operações' in lines[i] and nota != None):
                lineInfo = lines[i][lines[i].find('R$') + 2:].split()
                nota.resumoFinanceiro.custosOperacionais.irrfSOperacoesBase = strToFloat(
                    lineInfo[0])

                nota.resumoFinanceiro.custosOperacionais.irrfSOperacoes = strToFloat(
                    lineInfo[1])

                nota.resumoFinanceiro.custosOperacionais.irrfSOperacoes *= -1

            if ('IRRF Day Trade' in lines[i] and nota != None):
                lines[i] = lines[i][lines[i].find('R$') + 3:]
                nota.resumoFinanceiro.custosOperacionais.irrfDayTradeBase = extractNumber(
                    lines[i])

                lines[i] = lines[i][lines[i].find('R$') + 3:]
                nota.resumoFinanceiro.custosOperacionais.irrfDayTradeProjecao = extractNumber(
                    lines[i])

                lines[i] = lines[i][lines[i].find(' ') + 1:]
                lineInfo = lines[i].split()
                nota.resumoFinanceiro.custosOperacionais.outros = strToFloat(
                    lineInfo[1])

                if (lineInfo[2] == 'D'):
                    nota.resumoFinanceiro.custosOperacionais.outros *= -1
            elif ('Outros' in lines[i] and nota != None):
                nota.resumoFinanceiro.custosOperacionais.outros = extractNumber(
                    lines[i])

            if ('Total Custos / Despesas' in lines[i] and nota != None):
                nota.resumoFinanceiro.custosOperacionais.totalCustosDespesas = extractNumber(
                    lines[i])

            if ('Líquido para' in lines[i] and nota != None):
                creditoDebito = lines[i][-1:]
                lines[i] = lines[i][:lines[i].rfind(' ')]
                lines[i] = lines[i][lines[i].find('/') - 2:]

                lineInfo = lines[i].split()
                nota.resumoFinanceiro.liquidoParaData = datetime.datetime.strptime(
                    lineInfo[0], '%d/%m/%Y').date()

                nota.resumoFinanceiro.liquidoParaDataValor = strToFloat(
                    lineInfo[1])

                if (creditoDebito == 'D'):
                    nota.resumoFinanceiro.liquidoParaDataValor *= -1

            i += 1

        return notas

    @staticmethod
    def __getNegocioInfo(line: str, folha: int) -> NegocioRealizado:
        n = NegocioRealizado()
        n.folha = folha

        n.negociacao = line[:line.find(' ')]
        line = line[len(n.negociacao) + 1:]

        n.compraVenda = line[:1]
        line = line[2:]

        n.debitoCredito = line[-1:]
        line = line[:-2]

        n.valorOperacaoAjuste = strToFloat(line[line.rfind(' ') + 1:])
        line = line[:line.rfind(' ')]

        if (n.debitoCredito == 'D'):
            n.valorOperacaoAjuste *= -1

        n.precoAjuste = strToFloat(line[line.rfind(' ') + 1:])
        line = line[:line.rfind(' ')]

        n.quantidade = strToInt(line[line.rfind(' ') + 1:])
        line = line[:line.rfind(' ')]

        obs = ''
        obsLine = line
        while (obsLine[-1:] != ' ' and obsLine[-1:] in NotaNegociacao.OBS):
            obs = obsLine[-1:] + obs
            obsLine = obsLine[:-1]
            if (obsLine[-1:] == ' '):
                line = obsLine[:-1]

        if (obsLine[-1:] == ' '):
            n.obs = obs

        if (line[:5] == 'VISTA'):
            n.tipoMercado = line[:5]
            line = line[6:]

            # algumas notas possuem "Prazo" para vendas à vista
            # o que é um erro e deve ser tratado
            # para estes casos, o "Prazo" é descartado aqui
            if (line[2:3] == '/' and line[5:6] == ' '):
                line = line[6:]
        else:
            n.tipoMercado = line[:line.find('/') - 3]
            line = line[line.find('/') - 2:]

            n.prazo = line[:5]
            line = line[6:]

        n.especificacaoTitulo = line

        return n
