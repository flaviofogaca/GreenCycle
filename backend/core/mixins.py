import re
from django.core.exceptions import ValidationError


class ValidacaoCFPMixin:
    @staticmethod
    # Lembrar que no front deve-se criar uma máscara para já
    # recebermos com a pontuação correta de CPF
    def validar_cpf(value):
        # Remove caracteres não numéricos
        cpf = re.sub(r'[^0-9]', '', value)

        # Verifica se tem 11 dígitos
        if len(cpf) != 11:
            raise ValidationError('CPF deve conter 11 dígitos')

        # Verifica se todos os dígitos são iguais
        if cpf == cpf[0] * 11:
            raise ValidationError('CPF inválido')

        # Validação dos dígitos verificadores
        for i in range(9, 11):
            value = sum(int(cpf[num]) * ((i+1) - num) for num in range(0, i))
            digit = ((value * 10) % 11) % 10
            if digit != int(cpf[i]):
                raise ValidationError('CPF inválido')

            # Retorna no formato 000.000.000-00
        return f'{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}'


class ValidacaoCNPJMixin:
    @staticmethod
    def validar_cnpj(value):
        # Remove caracteres não numéricos
        cnpj = re.sub(r'[^0-9]', '', value)

        # Verifica se tem 14 dígitos
        if len(cnpj) != 14:
            raise ValidationError('CNPJ deve conter 14 dígitos')

        # Verifica se todos os dígitos são iguais
        if cnpj == cnpj[0] * 14:
            raise ValidationError('CNPJ inválido')

        # Validação do primeiro dígito verificador
        peso = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        soma = sum(int(cnpj[i]) * peso[i] for i in range(12))
        resto = soma % 11
        digito1 = 0 if resto < 2 else 11 - resto

        # Validação do segundo dígito verificador
        peso = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        soma = sum(int(cnpj[i]) * peso[i] for i in range(13))
        resto = soma % 11
        digito2 = 0 if resto < 2 else 11 - resto

        # Verifica os dígitos
        if int(cnpj[12]) != digito1 or int(cnpj[13]) != digito2:
            raise ValidationError('CNPJ inválido')

        # Retorna no formato 00.000.000/0000-00
        return f'{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}'
