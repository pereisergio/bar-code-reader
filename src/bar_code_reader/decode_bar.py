from abc import ABC, abstractmethod
from collections.abc import Callable
from datetime import date, datetime, timedelta

from PIL import Image
from pyzbar import pyzbar

from bar_code_reader.constants import (
    MODULO10_QUANTIDADE_MOEDA,
    MODULO10_VALOR_EFETIVO,
    MODULO11_QUANTIDADE_MOEDA,
    MODULO11_VALOR_EFETIVO,
)


class DecodeBar:
    def __init__(self, path) -> None:
        self.image = Image.open(path)

    def decoded_bar(self):
        return pyzbar.decode(self.image)


class LineCode(ABC):
    @abstractmethod
    def calc_modulo10(self, field: str):
        pass

    @abstractmethod
    def calc_modulo11(self, field: str):
        pass

    @abstractmethod
    def __str__(self) -> str:
        pass

    @abstractmethod
    def __repr__(self) -> str:
        pass


class CollectionGuide(LineCode):
    def __init__(self, code: str) -> None:
        """
        Posição     Tamanho     Conteúdo
        01 a 01     01          Identificação do Produto
        02 a 02     01          Identificação do Segmento
        03 a 03     01          Identificação do valor real ou referência
        04 a 04     01          Dígito verificador geral (módulo 10 ou 11)
        05 a 15     11          Valor
        16 a 19     04          Identificação da Empresa/Órgão
        20 a 44     25          Campo livre de utilização da Empresa/Órgão
        """
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
        field = (
            self.product
            + self.segment
            + self.currency_code
            + self.check_digit
            + self.value[:7]
        )
        check_digit = self.modulo(field)
        return field + check_digit

    @property
    def field_2(self) -> str:
        field = self.value[7:] + self.company_identify + self.free_field[:3]
        check_digit = self.modulo(field)
        return field + check_digit

    @property
    def field_3(self) -> str:
        field = self.free_field[3:14]
        check_digit = self.modulo(field)
        return field + check_digit

    @property
    def field_4(self) -> str:
        field = self.free_field[14:]
        check_digit = self.modulo(field)
        return field + check_digit

    def module_func(self) -> Callable:
        codigo_moeda = self.currency_code

        if (
            int(codigo_moeda) == MODULO10_VALOR_EFETIVO
            or int(codigo_moeda) == MODULO10_QUANTIDADE_MOEDA
        ):
            return self.calc_modulo10
        if (
            int(codigo_moeda) == MODULO11_VALOR_EFETIVO
            or int(codigo_moeda) == MODULO11_QUANTIDADE_MOEDA
        ):
            return self.calc_modulo11
        return lambda x: "Error"

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
            return "0"
        if resto_divisao == 10:
            return "1"
        return str(11 - resto_divisao)

    def __str__(self) -> str:
        if hasattr(self.modulo, "__name__") and self.modulo.__name__ == "<lambda>":
            return f"Erro: Código moeda inválido {self.currency_code}"
        return f"{self.field_1}{self.field_2}{self.field_3}{self.field_4}"

    def __repr__(self) -> str:
        if hasattr(self.modulo, "__name__") and self.modulo.__name__ == "<lambda>":
            return f"Erro: Código moeda inválido {self.currency_code}"
        return (
            f"{self.field_1[:-1]} {self.field_1[-1:]} "
            f"{self.field_2[:-1]} {self.field_2[-1:]} "
            f"{self.field_3[:-1]} {self.field_3[-1:]} "
            f"{self.field_4[:-1]} {self.field_4[-1:]}"
        )


class TransferGuide(LineCode):
    def __init__(self, code: str) -> None:
        """
        Posição     Tamanho     Picture     Conteúdo
        01 a 03     03          9(03)       Código do Banco na Câmara
                                            de Compensação = '001'
        04 a 04     01          9(01)       Código da Moeda = 9 (Real)
        05 a 05     01          9(01)       Digito Verificador (DV) do
                                            código de Barras*
        06 a 09     04          9(04)       Fator de Vencimento **
        10 a 19     10          9(08)V(2)   Valor
        20 a 44     03          9(03)       Campo Livre ***
        """
        self.bank = code[0:3]
        self.currency_code = code[3:4]
        self.check_digit = code[4:5]
        self.expiration_factor = code[5:9]
        self.value = code[9:19]
        self.free_field = code[19:44]
        self.date_fixed = self.fator_vencimento()

    @property
    def vencimento(self) -> date:
        return self.date_fixed + timedelta(days=int(self.expiration_factor))

    @property
    def field_1(self) -> str:
        field = self.bank + self.currency_code + self.free_field[:5]
        check_digit = self.calc_modulo10(field)
        return field + check_digit

    @property
    def field_2(self):
        field = self.free_field[5:15]
        check_digit = self.calc_modulo10(field)
        return field + check_digit

    @property
    def field_3(self):
        field = self.free_field[15:25]
        check_digit = self.calc_modulo10(field)
        return field + check_digit

    @property
    def field_4(self):
        return self.check_digit

    @property
    def field_5(self):
        return self.expiration_factor + self.value

    def fator_vencimento(self) -> date:
        """
        Calcula-se o número de dias corridos entre a data base
        (“Fixada” em 07/10/1997) e a do vencimento desejado.

        A partir de 22.02.2025, o fator retorna para “1000”
        adicionando-se “1” a cada dia subsequente a este fator.
        """
        if 1000 <= int(self.expiration_factor) < 5001:
            return datetime.strptime("29/05/2022", "%d/%m/%Y").date()
        return datetime.strptime("07/10/1997", "%d/%m/%Y").date()

    def calc_modulo10(self, sequencia: str) -> str:
        multiplicador_atual = 2
        soma = 0

        for element in sequencia[::-1]:
            resultado = int(element) * multiplicador_atual
            multiplicador_atual = 1 if multiplicador_atual == 2 else 2
            if resultado <= 9:
                soma += resultado
            else:
                soma += int(str(resultado)[0]) + int(str(resultado)[1])

        dezena_superior = (int(str(soma)[0]) + 1) * 10
        resto_divisao = soma % 10

        digito_verificador = dezena_superior - resto_divisao
        if digito_verificador == 10:
            digito_verificador = 0
        return str(digito_verificador)[-1]

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
            return "1"
        if resto_divisao in (10, 11):
            return "1"
        return str(11 - resto_divisao)

    def __str__(self) -> str:
        if self.currency_code != "9":
            return f"Erro: Código moeda inválido {self.currency_code}"
        if self.check_digit == "0":
            return f"Erro: Digito verificado {self.check_digit}"
        return f"{self.field_1}{self.field_2}{self.field_3}{self.field_4}{self.field_5}"

    def __repr__(self) -> str:
        if self.currency_code != "9":
            return f"Erro: Código moeda inválido {self.currency_code}"
        if self.check_digit == "0":
            return f"Erro: Digito verificador {self.check_digit}"
        return (
            f"{self.field_1[:5]}.{self.field_1[5:]} "
            f"{self.field_2[:5]}.{self.field_2[5:]} "
            f"{self.field_3[:5]}.{self.field_3[5:]} "
            f"{self.field_4} "
            f"{self.field_5}"
        )
