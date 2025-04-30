from rest_framework import viewsets, status
from rest_framework.generics import ListCreateAPIView
# from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
# from rest_framework.decorators import action
from django.core.cache import cache
from django.http import JsonResponse
from django.db.models import Prefetch
from .models import (
    Avaliacoes, Clientes, Coletas, Enderecos,
    Materiais, MateriaisParceiros, MateriaisPontosColeta, Pagamentos,
    Parceiros, PontosColeta, Solicitacoes, Telefones, Usuarios
)
from .serializers import (
    UsuarioCreateSerializer, UsuarioRetrieveSerializer,
    ClienteComUsuarioCreateSerializer, ClienteComUsuarioUpdateSerializer,
    ClienteComUsuarioRetrieveSerializer, ParceiroComUsuarioCreateSerializer,
    ParceiroComUsuarioUpdateSerializer, ParceiroComUsuarioRetrieveSerializer,
    AvaliacoesSerializer, ColetasRetrieveSerializer, ColetasCreateUpdateSerializer, MateriaisSerializer,
    EnderecoCreateSerializer, EnderecoUpdateSerializer,
    EnderecoRetrieveSerializer, EnderecoBuscaCEPSerializer,
    MateriaisParceirosSerializer, MateriaisPontosColetaSerializer,
    PagamentosSerializer, PontosColetaCreateSerializer,
    PontosColetaUpdateSerializer, PontosColetaRetrieveSerializer,
    SolicitacoesSerializer, TelefonesSerializer
)


def home(request):
    return JsonResponse({"mensagem": "APIs GreenCycle App"})


# ViewSets
class UsuariosCreateViewSet(viewsets.ModelViewSet):
    queryset = Usuarios.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return UsuarioRetrieveSerializer
        else:
            return UsuarioCreateSerializer

    # def list(self, request, *args, **kwargs):
    #     cache_key = 'usuarios_list'
    #     cached_data = cache.get(cache_key)

    #     if cached_data is not None:
    #         return Response(cached_data)

    #     queryset = self.filter_queryset(self.get_queryset())
    #     serializer = self.get_serializer(queryset, many=True)
    #     data = serializer.data

    #     # Armazena no cache por 15 minutos
    #     cache.set(cache_key, data, timeout=60*15)

    #     return Response(data)

    def create(self, request, *args, **kwargs):
        # Verifica se o email já está cadastrado
        email = request.data.get('email')
        if email and Usuarios.objects.filter(email=email).exists():
            return Response(
                {'email': 'Já existe um usuário com este email.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer_class = self.get_serializer(data=request.data)
        serializer_class.is_valid(raise_exception=True)

        # Cria o usuário com a senha já validada pelo serializer_class
        self.perform_create(serializer_class)

        headers = self.get_success_headers(serializer_class.data)

        # Remove cache de listagem de usuários se existir
        cache.delete('usuarios_list')

        return Response(
            serializer_class.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )
    # permission_classes = [IsAuthenticated]


class ClienteComUsuarioCreateViewSet(viewsets.ModelViewSet):
    queryset = Clientes.objects.all().select_related('id_usuarios')

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ClienteComUsuarioRetrieveSerializer
        elif self.action in ['create']:
            return ClienteComUsuarioCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ClienteComUsuarioUpdateSerializer
        return ClienteComUsuarioRetrieveSerializer

    def create(self, request, *args, **kwargs):
        # Verifica se o email já está cadastrado
        email = request.data.get('email')
        if email and Usuarios.objects.filter(email=email).exists():
            return Response(
                {'email': 'Já existe um usuário com este email.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Verifica se o CPF já está cadastrado
        cpf = request.data.get('cpf')
        if cpf and Clientes.objects.filter(cpf=cpf).exists():
            return Response(
                {'cpf': 'Já existe um cliente com este CPF.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer_class = self.get_serializer(data=request.data)
        serializer_class.is_valid(raise_exception=True)
        self.perform_create(serializer_class)
        headers = self.get_success_headers(serializer_class.data)

        # Remove cache de listagem de clientes se existir
        cache.delete('clientes_list')

        return Response(
            serializer_class.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    @action(
        detail=False,
        methods=['get'],
        url_path='por-usuario/(?P<usuario>[^/]+)'
    )
    def por_usuario(self, request, usuario=None):
        try:
            cliente = Clientes.objects.get(id_usuarios__usuario=usuario)
            serializer = self.get_serializer(cliente)
            return Response(serializer.data)
        except Clientes.DoesNotExist:
            return Response(
                {'detail': 'Cliente não encontrado com este nome de usuário'},
                status=status.HTTP_404_NOT_FOUND
            )


class ParceiroComUsuarioCreateViewSet(viewsets.ModelViewSet):
    queryset = Parceiros.objects.all().select_related(
        'id_usuarios'
    ).prefetch_related(
        'materiaisparceiros_set__id_materiais'
    )

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ParceiroComUsuarioRetrieveSerializer
        elif self.action in ['create']:
            return ParceiroComUsuarioCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ParceiroComUsuarioUpdateSerializer
        return ParceiroComUsuarioRetrieveSerializer

    def create(self, request, *args, **kwargs):
        # Verifica se o email já está cadastrado
        email = request.data.get('email')
        if email and Usuarios.objects.filter(email=email).exists():
            return Response(
                {'email': 'Já existe um usuário com este email.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Verifica se o CNPJ já está cadastrado
        cnpj = request.data.get('cnpj')
        if cnpj and Parceiros.objects.filter(cnpj=cnpj).exists():
            return Response(
                {'cnpj': 'Já existe um parceiro com este CNPJ.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer_class = self.get_serializer(data=request.data)
        serializer_class.is_valid(raise_exception=True)
        self.perform_create(serializer_class)
        headers = self.get_success_headers(serializer_class.data)

        # Remove cache de listagem de parceiros se existir
        cache.delete('parceiros_list')

        return Response(
            serializer_class.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    @action(
        detail=False,
        methods=['get'],
        url_path='por-usuario/(?P<usuario>[^/]+)'
    )
    def por_usuario(self, request, usuario=None):
        try:
            parceiro = Parceiros.objects.get(id_usuarios__usuario=usuario)
            serializer = self.get_serializer(parceiro)
            return Response(serializer.data)
        except Parceiros.DoesNotExist:
            return Response(
                {'detail': 'Parceiro não encontrado com este nome de usuário'},
                status=status.HTTP_404_NOT_FOUND
            )
    # permission_classes = [IsAuthenticated]


class EnderecosViewSet(viewsets.ModelViewSet):
    queryset = Enderecos.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return EnderecoCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return EnderecoUpdateSerializer
        elif self.action == 'buscar_cep':
            return EnderecoBuscaCEPSerializer
        return EnderecoRetrieveSerializer

    @action(detail=False, methods=['post'], url_path='buscar-cep')
    def buscar_cep(self, request):
        serializer_class = EnderecoBuscaCEPSerializer(data=request.data)
        serializer_class.is_valid(raise_exception=True)
        endereco = serializer_class.buscar_endereco()
        return Response(endereco)


class AvaliacoesViewSet(viewsets.ModelViewSet):
    queryset = Avaliacoes.objects.all()
    serializer_class = AvaliacoesSerializer
    # permission_classes = [IsAuthenticated]


class ColetasViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        queryset = Coletas.objects.all().select_related(
            'id_clientes__id_usuarios',
            'id_parceiros__id_usuarios',
            'id_materiais',
            'id_enderecos',
            'id_solicitacoes',
            'id_pagamentos'
        ).prefetch_related('imagens_coletas')

        id_clientes = self.request.query_params.get('id_clientes')
        if id_clientes:
            queryset = queryset.filter(id_clientes=id_clientes)

        return queryset

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ColetasCreateUpdateSerializer
        return ColetasRetrieveSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    @action(detail=True, methods=['post'], url_path='upload-imagem')
    def upload_imagem(self, request, pk=None):
        coleta = self.get_object()
        if 'imagem' not in request.FILES:
            return Response(
                {'error': 'Nenhuma imagem enviada'},
                status=status.HTTP_400_BAD_REQUEST
            )

        imagem = request.FILES['imagem']
        ImagemColetas.objects.create(coleta=coleta, imagem=imagem)
        return Response(
            {'status': 'Imagem adicionada com sucesso'},
            status=status.HTTP_201_CREATED
        )

    def get_queryset(self):
        queryset = Coletas.objects.all().select_related(
            'id_clientes__id_usuarios',
            'id_parceiros__id_usuarios',
            'id_materiais',
            'id_enderecos',
            'id_solicitacoes',
            'id_pagamentos'
        ).prefetch_related('imagens_coletas')

        id_clientes = self.request.query_params.get('id_clientes', None)
        if id_clientes is not None:
            queryset = queryset.filter(id_clientes__id_usuarios=id_clientes)
        return queryset


class MateriaisViewSet(viewsets.ModelViewSet):
    queryset = Materiais.objects.all()
    serializer_class = MateriaisSerializer
    # permission_classes = [IsAuthenticated]


class MateriaisParceirosViewSet(viewsets.ModelViewSet):
    queryset = MateriaisParceiros.objects.all()
    serializer_class = MateriaisParceirosSerializer
    # permission_classes = [IsAuthenticated]


class MateriaisPontosColetaViewSet(viewsets.ModelViewSet):
    queryset = MateriaisPontosColeta.objects.all()
    serializer_class = MateriaisPontosColetaSerializer
    # permission_classes = [IsAuthenticated]


class PagamentosViewSet(viewsets.ModelViewSet):
    queryset = Pagamentos.objects.all()
    serializer_class = PagamentosSerializer
    # permission_classes = [IsAuthenticated]


class PontosColetaViewSet(viewsets.ModelViewSet):
    queryset = PontosColeta.objects.all().select_related(
        'id_enderecos',
        'id_parceiros',
        'id_parceiros__id_usuarios'
    ).prefetch_related(
        Prefetch('materiais', queryset=Materiais.objects.only('nome', 'descricao')),
        'id_parceiros__id_usuarios__telefones'
    )  


    def get_serializer_class(self):
        if self.action == 'create':
            return PontosColetaCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return PontosColetaUpdateSerializer
        return PontosColetaRetrieveSerializer
    # permission_classes = [IsAuthenticated]


class SolicitacoesViewSet(viewsets.ModelViewSet):
    queryset = Solicitacoes.objects.all()
    serializer_class = SolicitacoesSerializer
    # permission_classes = [IsAuthenticated]


class TelefonesViewSet(viewsets.ModelViewSet):
    queryset = Telefones.objects.all()
    serializer_class = TelefonesSerializer
    # permission_classes = [IsAuthenticated]


class LoginAPIView(APIView):
    def post(self, request):
        nome = request.data.get('nome')
        senha = request.data.get('senha')

        try:
            usuario = Usuarios.objects.get(nome=nome)

            if usuario.senha == senha:
                serializer = UsuarioCreateSerializer(usuario)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(
                    {'detail': 'Senha incorreta'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
        except Usuarios.DoesNotExist:
            return Response(
                {'detail': 'Usuário não encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )


class ClientesApiView(ListCreateAPIView):
    queryset = Clientes.objects.all()
    serializer_class = ClienteComUsuarioCreateSerializer


class ParceirosApiView(ListCreateAPIView):
    queryset = Parceiros.objects.all()
    serializer_class = ParceiroComUsuarioCreateSerializer
