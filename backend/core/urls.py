import django.contrib.admin as django_admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView)

# from . import admin
from .views import (AvaliacoesViewSet, ClienteComUsuarioCreateViewSet,
                    ClientesApiView, ColetasViewSet, EnderecosViewSet,
                    ImagemPerfilViewSet, MateriaisParceirosViewSet,
                    MateriaisPontosColetaViewSet, MateriaisViewSet,
                    PagamentosViewSet, ParceiroComUsuarioCreateViewSet,
                    ParceirosApiView, PingView, PontosColetaViewSet,
                    SolicitacoesViewSet, TelefonesViewSet,
                    UsuariosCreateViewSet,EnderecoClienteViewSet, home)

# from django.conf.urls.static import static
# from django.conf import settings



# Configuração do router para as viewsets da API
router = DefaultRouter()

# Rotas para cadastro e gerenciamento de usuários
router.register(r'usuarios', UsuariosCreateViewSet, basename='usuarios')
router.register(
    r'clientes',
    ClienteComUsuarioCreateViewSet,
    basename='clientes'
)
router.register(
    r'parceiros',
    ParceiroComUsuarioCreateViewSet,
    basename='parceiros'
)
router.register(
    r'endereco-cliente',
    EnderecoClienteViewSet,
    basename='endereco-cliente'
)

# Rotas para entidades principais
router.register(r'avaliacoes', AvaliacoesViewSet, basename='avaliacoes')
router.register(r'coletas', ColetasViewSet, basename='coletas')
router.register(r'enderecos', EnderecosViewSet, basename='enderecos')
router.register(r'materiais', MateriaisViewSet, basename='materiais')

# Rotas para relacionamentos muitos-para-muitos
router.register(r'materiais-parceiros', MateriaisParceirosViewSet,
                basename='materiais-parceiros')
router.register(r'materiais-pontos-coleta', MateriaisPontosColetaViewSet,
                basename='materiais-pontos-coleta')

# Rotas para transações e operações
router.register(r'pagamentos', PagamentosViewSet, basename='pagamentos')
router.register(
    r'pontos-coleta',
    PontosColetaViewSet,
    basename='pontos-coleta'
)
router.register(r'solicitacoes', SolicitacoesViewSet, basename='solicitacoes')
router.register(r'telefones', TelefonesViewSet, basename='telefones')
router.register(
    r'imagens-perfil', ImagemPerfilViewSet, basename='imagens-perfil'
)

urlpatterns = [
    # Rota inicial da API
    path('', home, name='home'),

    # Painel de administração
    path('admin/', django_admin.site.urls),

    # API v1 - Todas as rotas registradas no router
    path('v1/', include(router.urls)),

    # Autenticação JWT
    path('v1/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path(
        'v1/token/refresh/',
        TokenRefreshView.as_view(),
        name='token_refresh'
    ),
    path('v1/clientes/', ClientesApiView.as_view(), name='clientes-list'),
    path('v1/parceiros/', ParceirosApiView.as_view(), name='parceiros-list'),
    path('ping/', PingView.as_view()),
]

# As seguintes rotas são criadas automaticamente pelo router:
# 
# COLETAS - Principais funcionalidades:
# GET /v1/coletas/pendentes-parceiro/{parceiro_id}/ - Lista coletas pendentes para parceiro
# GET /v1/coletas/minhas-coletas-parceiro/{parceiro_id}/ - Lista coletas do parceiro
# GET /v1/coletas/minhas-coletas-cliente/{cliente_id}/ - Lista coletas do cliente
# POST /v1/coletas/{id}/aceitar-coleta/ - Aceitar coleta (parceiro)
# POST /v1/coletas/{id}/marcar-coletado/ - Marcar como coletado (parceiro)
# POST /v1/coletas/{id}/finalizar-coleta/ - Finalizar coleta (cliente)
# POST /v1/coletas/{id}/cancelar-coleta/ - Cancelar coleta (cliente)
# POST /v1/coletas/{id}/upload-imagem/ - Upload de imagem
#
# AVALIAÇÕES - Sistema de avaliações mútuas:
# GET /v1/avaliacoes/ - Lista todas as avaliações
# GET /v1/avaliacoes/{id}/ - Buscar avaliação por ID
# POST /v1/avaliacoes/avaliar-parceiro/ - Cliente avalia parceiro (requer: coleta_id, cliente_id, nota_parceiros, descricao_parceiros)
# POST /v1/avaliacoes/avaliar-cliente/ - Parceiro avalia cliente (requer: coleta_id, parceiro_id, nota_clientes, descricao_clientes)
# GET /v1/avaliacoes/estatisticas-cliente/{cliente_id}/ - Estatísticas de avaliações do cliente
# GET /v1/avaliacoes/estatisticas-parceiro/{parceiro_id}/ - Estatísticas de avaliações do parceiro
#
# ENDEREÇOS:
# POST /v1/enderecos/buscar-cep/ - Buscar dados de endereço por CEP
#
# USUÁRIOS:
# GET /v1/clientes/por-usuario/{usuario}/ - Buscar cliente por nome de usuário
# GET /v1/parceiros/por-usuario/{usuario}/ - Buscar parceiro por nome de usuário
#
# TELEFONES:
# GET /v1/telefones/ - Lista todos os telefones
# POST /v1/telefones/ - Criar novo telefone
# GET /v1/telefones/{id_usuarios}/ - Buscar telefone por ID do usuário
# PUT /v1/telefones/{id_usuarios}/ - Atualizar telefone do usuário
# PATCH /v1/telefones/{id_usuarios}/ - Atualizar parcialmente telefone do usuário
# DELETE /v1/telefones/{id_usuarios}/ - Deletar telefone do usuário
# GET /v1/telefones/por-usuario/{usuario_id}/ - Buscar telefone por ID do usuário
