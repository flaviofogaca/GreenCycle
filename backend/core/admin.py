from django.contrib import admin
from .models import (
    Avaliacoes, Clientes, Coletas, Enderecos,
    Materiais, MateriaisParceiros, MateriaisPontosColeta, Pagamentos,
    Parceiros, PontosColeta, Solicitacoes, Telefones, Usuarios
)


@admin.register(Avaliacoes)
class AvaliacoesAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'id_parceiros',
        'id_clientes',
        'nota_parceiros',
        'descricao_parceiros',
        'nota_clientes',
        'descricao_clientes',
        'criado_em',
        'atualizado_em',
    )


@admin.register(Clientes)
class ClientesAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'id_usuarios',
        'cpf',
        'criado_em',
        'atualizado_em',
    )


@admin.register(Coletas)
class ColetasAdmin(admin.ModelAdmin):
    list_display = (
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
    )


@admin.register(Enderecos)
class EnderecosAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'cep',
        'estado',
        'cidade',
        'rua',
        'criado_em',
        'atualizado_em',
    )


@admin.register(Materiais)
class MateriaisAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'nome',
        'descricao',
        'preco',
        'criado_em',
        'atualizado_em',
    )


@admin.register(MateriaisParceiros)
class MateriaisParceirosAdmin(admin.ModelAdmin):
    list_display = (
        'id_materiais',
        'id_parceiros',
    )


@admin.register(MateriaisPontosColeta)
class MateriaisPontosColetaAdmin(admin.ModelAdmin):
    list_display = (
        'id_materiais',
        'id_pontos_coleta',
    )


@admin.register(Pagamentos)
class PagamentosAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'valor_pagamento',
        'saldo_pagamento',
        'estado_pagamento',
        'criado_em',
        'atualizado_em',
    )


@admin.register(Parceiros)
class ParceirosAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'id_usuarios',
        'cnpj',
        'criado_em',
        'atualizado_em',
    )


@admin.register(PontosColeta)
class PontosColetaAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'nome',
        'id_enderecos',
        'descricao',
        'horario_funcionamento',
        'criado_em',
        'atualizado_em',
    )


@admin.register(Solicitacoes)
class SolicitacoesAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'estado_solicitacao',
        'observacoes',
        'latitude',
        'longitude',
        'finalizado_em',
        'criado_em',
        'atualizado_em',
    )


@admin.register(Telefones)
class TelefonesAdmin(admin.ModelAdmin):
    list_display = (
        'id_usuarios',
        'numero',
        'criado_em',
        'atualizado_em',
    )


@admin.register(Usuarios)
class UsuariosAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'nome',
        'email',
        'senha',
        'id_endereco',
        'criado_em',
        'atualizado_em',
    )
