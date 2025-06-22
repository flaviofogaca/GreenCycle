import re
from time import sleep
from urllib.parse import quote

import requests
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


class ValidacaoCEPMixin:
    @staticmethod
    def validar_cep(value):
        # Remove caracteres não numéricos
        cep_numerico = re.sub(r'[^0-9]', '', value)

        # Verifica se o CEP tem apenas números
        if not cep_numerico.isdigit():
            raise ValidationError("CEP deve conter apenas números")

        # Verifica se o CEP tem exatamente 8 dígitos
        if len(cep_numerico) != 8:
            raise ValidationError("O CEP deve conter exatamente 8 dígitos.")

        # Retorna o CEP formatado como string numérica
        return cep_numerico


class ValidacaoTelefoneMixin:
    @staticmethod
    def validar_telefone(value):
        """
        Valida número de telefone brasileiro
        Aceita formatos: (11) 99999-9999, 11 999999999, 11999999999
        """
        if not value:
            return value
            
        # Remove caracteres não numéricos
        telefone = re.sub(r'[^0-9]', '', value)
        
        # Verifica se tem pelo menos 10 dígitos (telefone fixo)
        # ou 11 dígitos (celular com 9)
        if len(telefone) < 10 or len(telefone) > 11:
            raise ValidationError('Telefone deve ter 10 ou 11 dígitos')
        
        # Verifica se é um número de celular (11 dígitos) e começa com 9
        if len(telefone) == 11 and telefone[2] != '9':
            raise ValidationError('Número de celular deve começar com 9 após o DDD')
        
        # Verifica se todos os dígitos são iguais
        if len(set(telefone)) == 1:
            raise ValidationError('Número de telefone inválido')
        
        # Retorna formatado
        if len(telefone) == 10:
            # Telefone fixo: (11) 1234-5678
            return f'({telefone[:2]}) {telefone[2:6]}-{telefone[6:]}'
        else:
            # Celular: (11) 99999-9999
            return f'({telefone[:2]}) {telefone[2:7]}-{telefone[7:]}'


class GeocodingMixin:
    @staticmethod
    def get_lat_lon(endereco_completo):
        """
        Obtém latitude e longitude usando a API Nominatim do OpenStreetMap

        Args:
            endereco_completo (str): Endereço no formato
            "Rua, Número, Bairro, Cidade, Estado, CEP"

        Returns:
            tuple: (latitude, longitude) ou None se não encontrar
        """
        try:
            # Formata o endereço para URL
            endereco_formatado = quote(endereco_completo)

            # URL da API Nominatim
            url = f"https://nominatim.openstreetmap.org/" \
                f"search?format=json&q={endereco_formatado}"

            # Headers para identificar corretamente a aplicação
            headers = {
                'User-Agent': 'GreenCycleApp/1.0 (seu-email@exemplo.com)'
            }

            # Faz a requisição com timeout
            response = requests.get(url, headers=headers, timeout=10)

            # Respeita o rate limit da API (1 segundo entre requisições)
            sleep(1)

            if response.status_code == 200:
                data = response.json()
                if data:
                    # Retorna a primeira ocorrência (mais relevante)
                    return (float(data[0]['lat']), float(data[0]['lon']))

            return None

        except requests.exceptions.RequestException as e:
            # Logar este erro em produção
            print(f"Erro ao acessar API Nominatim: {e}")
            return None
        except (KeyError, IndexError, ValueError) as e:
            print(f"Erro ao processar resposta da API: {e}")
            return None
