from constants import (MODULO10_VALOR_EFETIVO,
                       MODULO10_QUANTIDADE_MOEDA,
                       MODULO11_VALOR_EFETIVO,
                       MODULO11_QUANTIDADE_MOEDA)
from typing import Callable


class CollectionGuide:
    def __init__(self, code: str) -> None:
        '''
        Posição     Tamanho     Conteúdo
        01 a 01     01          Identificação do Produto
        02 a 02     01          Identificação do Segmento
        03 a 03     01          Identificação do valor real ou referência
        04 a 04     01          Dígito verificador geral (módulo 10 ou 11)
        05 a 15     11          Valor
        16 a 19     04          Identificação da Empresa/Órgão
        20 a 44     25          Campo livre de utilização da Empresa/Órgão
        '''
        self.product = code[0:1]
        self.segment = code[1:2]
        self.currency_code = code[2:3]
        self.check_digit = code[3:4]
        self.value = code[4:15]
        self.company_identify = code[15:19]
        self.free_field = code[19:44]

        self.modulo = self.module_func()

    @property
    def field_1(self) -> str:
        field = (self.product + self.segment + self.currency_code +
                 self.check_digit + self.value[:7])
        check_digit = self.modulo(field)
        return field + check_digit

    @property
    def field_2(self) -> str:
        field = (self.value[7:] + self.company_identify +
                 self.free_field[:3])
        check_digit = self.modulo(field)
        return field + check_digit

    @property
    def field_3(self) -> str:
        field = (self.free_field[3:14])
        check_digit = self.modulo(field)
        return field + check_digit

    @property
    def field_4(self) -> str:
        field = (self.free_field[14:])
        check_digit = self.modulo(field)
        return field + check_digit

    def module_func(self) -> Callable:
        codigo_moeda = self.currency_code

        if (
            int(codigo_moeda) == MODULO10_VALOR_EFETIVO
            or int(codigo_moeda) == MODULO10_QUANTIDADE_MOEDA
        ):
            return self.calc_modulo10
        elif (
            int(codigo_moeda) == MODULO11_VALOR_EFETIVO
            or int(codigo_moeda) == MODULO11_QUANTIDADE_MOEDA
        ):
            return self.calc_modulo11
        else:
            return lambda x: 'Error'

    def calc_modulo10(self, sequencia: str) -> str:
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
            return str(resto_divisao)
        return str(10 - resto_divisao)

    def calc_modulo11(self, sequencia: str) -> str:
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
            return '0'
        if resto_divisao == 10:
            return '1'
        return str(11 - resto_divisao)

    def __str__(self) -> str:
        if hasattr(self.modulo, '__name__') and \
                self.modulo.__name__ == '<lambda>':
            return f'Erro: Código moeda inválido {self.currency_code}'
        else:
            return (
                f'{self.field_1}{self.field_2}{self.field_3}{self.field_4}')

    def __repr__(self) -> str:
        if hasattr(self.modulo, '__name__') and \
                self.modulo.__name__ == '<lambda>':
            return f'Erro: Código moeda inválido {self.currency_code}'
        else:
            return (
                f'{self.field_1[:-1]} {self.field_1[-1:]} '
                f'{self.field_2[:-1]} {self.field_2[-1:]} '
                f'{self.field_3[:-1]} {self.field_3[-1:]} '
                f'{self.field_4[:-1]} {self.field_4[-1:]}'
            )


if __name__ == '__main__':
    code1 = '81710000000115503062024121603060009841431124'
    code2 = '23791989300000035003509090103764462000013100'
    c1 = CollectionGuide(code1)
    print(c1)
    print(repr(c1))
    print('oiii')
    # c2 = CollectionGuide(code2).calcular_dac(code2)
    # print(c1)
    # print('81710000000 6   11550306202 4   41216030600 4   09841431124 5')
    # print(c2)
    # print()
    # code3 = '85860000001 2 36710297243 5 52012900002 3 43521484100 4'
    # code4 = '85850000000 2 18220297243 8 52992900002 1 43521484400 3'
