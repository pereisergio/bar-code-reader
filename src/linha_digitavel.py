from constants import (MODULO10_VALOR_EFETIVO,
                       MODULO10_QUANTIDADE_MOEDA,
                       MODULO11_VALOR_EFETIVO,
                       MODULO11_QUANTIDADE_MOEDA)


class LinhaDigitavel:
    def calcular_dac(self, codigo_de_barras: str) -> str:
        codigo_de_barras_limpo = self.limpar_codigo_de_barras(codigo_de_barras)
        if len(codigo_de_barras_limpo) != 44:
            raise Exception('Código de barra inválido.')

        codigo_moeda = int(codigo_de_barras_limpo[2])
        modulo = self.dac_func(codigo_moeda)
        if modulo is None:
            raise Exception('Código moeda inválido.')

        str_linha_digitavel = ''

        partes = [
            codigo_de_barras_limpo[i: i + 11]
            for i in range(0, len(codigo_de_barras_limpo), 11)
        ]

        for parte in partes:
            str_linha_digitavel += parte + ' ' + str(modulo(parte)) + ' '

        return str_linha_digitavel.strip()

    def limpar_codigo_de_barras(self, codigo_de_barras: str):
        return ''.join(
            [i for i in codigo_de_barras if codigo_de_barras.isdigit()])

    def dac_func(self, codigo_moeda):
        modulo = None
        if (
            int(codigo_moeda) == MODULO10_VALOR_EFETIVO
            or int(codigo_moeda) == MODULO10_QUANTIDADE_MOEDA
        ):
            modulo = self.calc_dac_modulo10
        elif (
            int(codigo_moeda) == MODULO11_VALOR_EFETIVO
            or int(codigo_moeda) == MODULO11_QUANTIDADE_MOEDA
        ):
            modulo = self.calc_dac_modulo11
        return modulo

    def calc_dac_modulo10(self, sequencia: str) -> int:
        multiplicador_atual = 2
        soma = 0

        for element in sequencia[::-1]:
            resultado = int(element) * multiplicador_atual
            multiplicador_atual = 1 if multiplicador_atual == 2 else 2
            if resultado < 10:
                soma += resultado
            else:
                soma += int(resultado / 10)
                soma += resultado % 10

        resto_divisao = soma % 10
        if resto_divisao == 0:
            return resto_divisao
        return 10 - resto_divisao

    def calc_dac_modulo11(self, sequencia) -> int:
        multiplicador_atual = 2
        soma = 0

        for element in sequencia[::-1]:
            resultado = int(element) * multiplicador_atual
            multiplicador_atual = (
                2 if multiplicador_atual == 9 else multiplicador_atual + 1
            )
            soma += resultado

        resto_divisao = soma % 11
        if resto_divisao in (0, 1):
            return 0
        if resto_divisao == 10:
            return 1
        return 11 - resto_divisao


if __name__ == '__main__':
    code1 = '81710000000115503062024121603060009841431124'
    code2 = '23791989300000035003509090103764462000013100'
    c1 = LinhaDigitavel().calcular_dac(code1)
    c2 = LinhaDigitavel().calcular_dac(code2)
    print(c1)
    print('81710000000 6   11550306202 4   41216030600 4   09841431124 5')
    print(c2)
    print()
    code3 = '85860000001 2 36710297243 5 52012900002 3 43521484100 4'
    code4 = '85850000000 2 18220297243 8 52992900002 1 43521484400 3'
