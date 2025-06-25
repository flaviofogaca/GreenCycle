from django.contrib import admin

from .models import (Avaliacoes, Clientes, Coletas, Enderecos, ImagemColetas,
                     ImagemPerfil, Materiais, MateriaisParceiros,
                     MateriaisPontosColeta, Pagamentos, Parceiros,
                     PontosColeta, Solicitacoes, Telefones, Usuarios)


@admin.register(Avaliacoes)
class AvaliacoesAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'id_coletas',
        'get_cliente_nome',
        'get_parceiro_nome',
        'nota_parceiros',
        'nota_clientes',
        'criado_em',
        'atualizado_em',
    )
    list_filter = ('nota_parceiros', 'nota_clientes', 'criado_em')
    search_fields = (
        'id_clientes__id_usuarios__nome',
        'id_parceiros__id_usuarios__nome',
        'descricao_parceiros',
        'descricao_clientes'
    )
    list_select_related = (
        'id_clientes__id_usuarios',
        'id_parceiros__id_usuarios',
        'id_coletas'
    )
    readonly_fields = ('criado_em', 'atualizado_em')

    def get_cliente_nome(self, obj):
        return obj.id_clientes.id_usuarios.nome if obj.id_clientes and obj.id_clientes.id_usuarios else None
    get_cliente_nome.short_description = 'Cliente'
    
    def get_parceiro_nome(self, obj):
        return obj.id_parceiros.id_usuarios.nome if obj.id_parceiros and obj.id_parceiros.id_usuarios else None
    get_parceiro_nome.short_description = 'Parceiro'


@admin.register(Clientes)
class ClientesAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'id_usuarios',
        'cpf',
        'criado_em',
        'atualizado_em',
    )
    search_fields = ('cpf', 'id_usuarios__nome', 'id_usuarios__email')
    list_filter = ('sexo', 'criado_em')


@admin.register(Coletas)
class ColetasAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'id_clientes',
        'id_parceiros',
        'id_materiais',
        'peso_material',
        'quantidade_material',
        'get_estado_solicitacao',
        'get_estado_pagamento',
        'get_possui_avaliacao',
        'criado_em',
        'atualizado_em',
    )
    list_filter = (
        'id_solicitacoes__estado_solicitacao',
        'id_pagamentos__estado_pagamento',
        'id_materiais',
        'criado_em'
    )
    search_fields = (
        'id_clientes__id_usuarios__nome',
        'id_parceiros__id_usuarios__nome',
        'id_materiais__nome'
    )
    readonly_fields = ('criado_em', 'atualizado_em')

    def get_estado_solicitacao(self, obj):
        return obj.id_solicitacoes.get_estado_solicitacao_display() if obj.id_solicitacoes else None
    get_estado_solicitacao.short_description = 'Estado Solicitação'

    def get_estado_pagamento(self, obj):
        return obj.id_pagamentos.get_estado_pagamento_display() if obj.id_pagamentos else None
    get_estado_pagamento.short_description = 'Estado Pagamento'

    def get_possui_avaliacao(self, obj):
        return hasattr(obj, 'avaliacao') and obj.avaliacao is not None
    get_possui_avaliacao.short_description = 'Possui Avaliação'
    get_possui_avaliacao.boolean = True


@admin.register(ImagemColetas)
class ImagemColetasAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'id_coletas',
        'imagem',
        'criado_em',
        'atualizado_em',
    )
    list_filter = ('criado_em',)
    search_fields = ('id_coletas__id', 'imagem')


@admin.register(Enderecos)
class EnderecosAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'cep',
        'estado',
        'cidade',
        'rua',
        'numero',
        'criado_em',
        'atualizado_em',
    )
    list_filter = ('estado', 'cidade', 'criado_em')
    search_fields = ('cep', 'cidade', 'rua', 'bairro')


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
    search_fields = ('nome', 'descricao')
    list_filter = ('criado_em',)


@admin.register(MateriaisParceiros)
class MateriaisParceirosAdmin(admin.ModelAdmin):
    list_display = (
        'id_materiais',
        'id_parceiros',
    )
    list_filter = ('id_materiais', 'id_parceiros')


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
    list_filter = ('estado_pagamento', 'criado_em')
    search_fields = ('estado_pagamento',)


@admin.register(Parceiros)
class ParceirosAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'id_usuarios',
        'cnpj',
        'criado_em',
        'atualizado_em',
    )
    search_fields = ('cnpj', 'id_usuarios__nome', 'id_usuarios__email')
    list_filter = ('criado_em',)


@admin.register(PontosColeta)
class PontosColetaAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'nome',
        'id_enderecos',
        'id_parceiros',
        'descricao',
        'horario_funcionamento',
        'criado_em',
        'atualizado_em',
    )
    search_fields = ('nome', 'descricao')
    list_filter = ('id_parceiros', 'criado_em')


@admin.register(Solicitacoes)
class SolicitacoesAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'estado_solicitacao',
        'observacoes',
        'finalizado_em',
        'criado_em',
        'atualizado_em',
    )
    list_filter = ('estado_solicitacao', 'criado_em', 'finalizado_em')
    search_fields = ('estado_solicitacao', 'observacoes')


@admin.register(Telefones)
class TelefonesAdmin(admin.ModelAdmin):
    list_display = (
        'id_usuarios',
        'get_usuario_nome',
        'numero',
        'criado_em',
        'atualizado_em',
    )
    list_select_related = ('id_usuarios',)
    search_fields = ('numero', 'id_usuarios__nome', 'id_usuarios__usuario')
    list_filter = ('criado_em',)
    readonly_fields = ('criado_em', 'atualizado_em')

    def get_usuario_nome(self, obj):
        return obj.id_usuarios.nome if obj.id_usuarios else None
    get_usuario_nome.short_description = 'Nome do Usuário'


@admin.register(Usuarios)
class UsuariosAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'nome',
        'usuario',
        'email',
        'senha',
        'id_endereco',
        'criado_em',
        'atualizado_em',
    )
    search_fields = ('nome', 'usuario', 'email')
    list_filter = ('criado_em',)


@admin.register(ImagemPerfil)
class ImagemPerfilAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'id_usuarios',
        'file_id',
        'criado_em',
        'atualizado_em',
    )
    list_select_related = ('id_usuarios',)
    search_fields = ('id_usuarios__usuario', 'id_usuarios__nome')
    readonly_fields = ('file_id', 'criado_em', 'atualizado_em')
