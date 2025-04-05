import django.contrib.admin as django_admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from . import admin
from .views import (
    AvaliacoesViewSet, ClientesViewSet, ColetasViewSet, EnderecosViewSet,
    MateriaisViewSet, MateriaisParceirosViewSet, MateriaisPontosColetaViewSet,
    PagamentosViewSet, ParceirosViewSet, PontosColetaViewSet,
    SolicitacoesViewSet, TelefonesViewSet, UsuariosViewSet, home, ClientesApiView, ParceirosApiView
)

router = DefaultRouter()
router.register(r'avaliacoes', AvaliacoesViewSet)
router.register(r'clientes', ClientesViewSet)
router.register(r'coletas', ColetasViewSet)
router.register(r'enderecos', EnderecosViewSet)
router.register(r'materiais', MateriaisViewSet)
router.register(r'materiais-parceiros', MateriaisParceirosViewSet)
router.register(r'materiais-pontos-coleta', MateriaisPontosColetaViewSet)
router.register(r'pagamentos', PagamentosViewSet)
router.register(r'parceiros', ParceirosViewSet)
router.register(r'pontos-coleta', PontosColetaViewSet)
router.register(r'solicitacoes', SolicitacoesViewSet)
router.register(r'telefones', TelefonesViewSet)
router.register(r'usuarios', UsuariosViewSet)

urlpatterns = [
    path('', home, name='home'),
    path('admin/', django_admin.site.urls),
    path('v1/', include(router.urls)),
    path('v1/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('v1/clientes/', ClientesApiView.as_view(), name='clientes-list'),
    path('v1/parceiros/', ParceirosApiView.as_view(), name='parceiros-list'),
]
