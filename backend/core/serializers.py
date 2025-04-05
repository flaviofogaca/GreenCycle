from rest_framework.serializers import ModelSerializer
from .models import (
    Avaliacoes, Clientes, Coletas, Enderecos,
    Materiais, MateriaisParceiros, MateriaisPontosColeta, Pagamentos,
    Parceiros, PontosColeta, Solicitacoes, Telefones, Usuarios
)


class AvaliacoesSerializer(ModelSerializer):
    class Meta:
        model = Avaliacoes
        fields = [
            'id',
            'id_parceiros',
            'id_clientes',
            'nota_parceiros',
            'descricao_parceiros',
            'nota_clientes',
            'descricao_clientes',
            'criado_em',
            'atualizado_em',
        ]

class UsuariosSerializer(ModelSerializer):
    class Meta:
        model = Usuarios
        fields = [
            'id',
            'nome',
            'usuario',
            'email',
            'senha',
            'id_endereco',
            'criado_em',
            'atualizado_em',
        ]

class ClientesSerializer(ModelSerializer):
    id_usuarios = UsuariosSerializer()

    class Meta:
        model = Clientes
        fields = [
            'id',
            'id_usuarios',
            'cpf',
            'data_nascimento',
            'sexo',
            'criado_em',
            'atualizado_em',
        ]


class ColetasSerializer(ModelSerializer):
    class Meta:
        model = Coletas
        fields = [
            'id',
            'id_clientes',
            'id_parceiros',
            'id_materiais',
            'peso_material',
            'quantidade_material',
            'id_enderecos',
            'id_solicitacoes',
            'id_pagamentos',
            'criado_em',
            'atualizado_em',
        ]


class EnderecosSerializer(ModelSerializer):
    class Meta:
        model = Enderecos
        fields = [
            'id',
            'cep',
            'estado',
            'cidade',
            'rua',
            'criado_em',
            'atualizado_em',
        ]


class MateriaisSerializer(ModelSerializer):
    class Meta:
        model = Materiais
        fields = [
            'id',
            'nome',
            'descricao',
            'preco',
            'criado_em',
            'atualizado_em',
        ]


class MateriaisParceirosSerializer(ModelSerializer):
    class Meta:
        model = MateriaisParceiros
        fields = [
            'id_materiais',
            'id_parceiros',
        ]


class MateriaisPontosColetaSerializer(ModelSerializer):
    class Meta:
        model = MateriaisPontosColeta
        fields = [
            'id_materiais',
            'id_pontos_coleta',
        ]


class PagamentosSerializer(ModelSerializer):
    class Meta:
        model = Pagamentos
        fields = [
            'id',
            'valor_pagamento',
            'saldo_pagamento',
            'estado_pagamento',
            'criado_em',
            'atualizado_em',
        ]


class ParceirosSerializer(ModelSerializer):
    class Meta:
        model = Parceiros
        fields = [
            'id',
            'id_usuarios',
            'cnpj',
            'criado_em',
            'atualizado_em',
        ]


class PontosColetaSerializer(ModelSerializer):
    class Meta:
        model = PontosColeta
        fields = [
            'id',
            'nome',
            'id_enderecos',
            'descricao',
            'horario_funcionamento',
            'criado_em',
            'atualizado_em',
        ]


class SolicitacoesSerializer(ModelSerializer):
    class Meta:
        model = Solicitacoes
        fields = [
            'id',
            'estado_solicitacao',
            'observacoes',
            'latitude',
            'longitude',
            'finalizado_em',
            'criado_em',
            'atualizado_em',
        ]


class TelefonesSerializer(ModelSerializer):
    class Meta:
        model = Telefones
        fields = [
            'id_usuarios',
            'numero',
            'criado_em',
            'atualizado_em',
        ]
