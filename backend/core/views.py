import os

# from rest_framework.decorators import action
from django.core.cache import cache
from django.db import transaction
from django.db.models import Prefetch, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from .models import (Avaliacoes, Clientes, Coletas, Enderecos, ImagemColetas,
                     ImagemPerfil, Materiais, MateriaisParceiros,
                     MateriaisPontosColeta, Pagamentos, Parceiros,
                     PontosColeta, Solicitacoes, Telefones, Usuarios)
from .serializers import (AvaliacoesSerializer,
                          ClienteComUsuarioCreateSerializer,
                          ClienteComUsuarioRetrieveSerializer,
                          ClienteComUsuarioUpdateSerializer,
                          ColetasCreateSerializer,
                          ColetasPendentesParceiroSerializer,
                          ColetasRetrieveSerializer, ColetasUpdateSerializer,
                          EnderecoBuscaCEPSerializer, EnderecoCreateSerializer,
                          EnderecoRetrieveSerializer, EnderecoUpdateSerializer,
                          ImagemPerfilCreateSerializer,
                          ImagemPerfilRetrieveSerializer,
                          MateriaisParceirosSerializer,
                          MateriaisPontosColetaSerializer, MateriaisSerializer,
                          PagamentosSerializer,
                          ParceiroComUsuarioCreateSerializer,
                          ParceiroComUsuarioRetrieveSerializer,
                          ParceiroComUsuarioUpdateSerializer,
                          PontosColetaCreateSerializer,
                          PontosColetaRetrieveSerializer,
                          PontosColetaUpdateSerializer, SolicitacoesSerializer,
                          TelefonesSerializer, UsuarioCreateSerializer,
                          UsuarioRetrieveSerializer)
from .services import imagekit_service


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
        serializer = EnderecoBuscaCEPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        endereco = serializer.buscar_endereco()
        return Response(endereco)


class AvaliacoesViewSet(viewsets.ModelViewSet):
    queryset = Avaliacoes.objects.all()
    serializer_class = AvaliacoesSerializer


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

        # Filtros específicos
        id_cliente = self.request.query_params.get('id_cliente')
        id_parceiro = self.request.query_params.get('id_parceiro')
        status_solicitacao = self.request.query_params.get('status_solicitacao')

        if id_cliente:
            queryset = queryset.filter(id_clientes__id_usuarios=id_cliente)
        
        if id_parceiro:
            queryset = queryset.filter(id_parceiros__id_usuarios=id_parceiro)
            
        if status_solicitacao:
            queryset = queryset.filter(id_solicitacoes__estado_solicitacao=status_solicitacao)

        return queryset

    def get_serializer_class(self):
        if self.action == 'create':
            return ColetasCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ColetasUpdateSerializer
        elif self.action == 'pendentes_para_parceiro':
            return ColetasPendentesParceiroSerializer
        return ColetasRetrieveSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    @action(detail=False, methods=['get'], url_path='pendentes-parceiro/(?P<parceiro_id>[^/]+)')
    def pendentes_para_parceiro(self, request, parceiro_id=None):
        """
        Lista coletas pendentes que o parceiro pode aceitar
        (coletas com materiais que ele trabalha e status pendente)
        """
        try:
            parceiro = Parceiros.objects.get(id_usuarios=parceiro_id)
            
            # Busca materiais que o parceiro trabalha
            materiais_parceiro = MateriaisParceiros.objects.filter(
                id_parceiros=parceiro
            ).values_list('id_materiais', flat=True)
            
            # Filtra coletas pendentes com materiais que o parceiro trabalha
            coletas_pendentes = Coletas.objects.filter(
                id_materiais__in=materiais_parceiro,
                id_solicitacoes__estado_solicitacao='pendente',
                id_parceiros__isnull=True  # Ainda não foi aceita por nenhum parceiro
            ).select_related(
                'id_clientes__id_usuarios',
                'id_materiais',
                'id_enderecos',
                'id_pagamentos'
            ).order_by('-criado_em')
            
            serializer = self.get_serializer(coletas_pendentes, many=True)
            return Response(serializer.data)
            
        except Parceiros.DoesNotExist:
            return Response(
                {'detail': 'Parceiro não encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['get'], url_path='minhas-coletas-parceiro/(?P<parceiro_id>[^/]+)')
    def minhas_coletas_parceiro(self, request, parceiro_id=None):
        """
        Lista coletas que o parceiro já aceitou
        """
        try:
            parceiro = Parceiros.objects.get(id_usuarios=parceiro_id)
            
            coletas_parceiro = Coletas.objects.filter(
                id_parceiros=parceiro
            ).select_related(
                'id_clientes__id_usuarios',
                'id_materiais',
                'id_enderecos',
                'id_solicitacoes',
                'id_pagamentos'
            ).prefetch_related('imagens_coletas').order_by('-criado_em')
            
            serializer = ColetasRetrieveSerializer(coletas_parceiro, many=True)
            return Response(serializer.data)
            
        except Parceiros.DoesNotExist:
            return Response(
                {'detail': 'Parceiro não encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['get'], url_path='minhas-coletas-cliente/(?P<cliente_id>[^/]+)')
    def minhas_coletas_cliente(self, request, cliente_id=None):
        """
        Lista coletas que o cliente criou
        """
        try:
            cliente = Clientes.objects.get(id_usuarios=cliente_id)
            
            coletas_cliente = Coletas.objects.filter(
                id_clientes=cliente
            ).select_related(
                'id_parceiros__id_usuarios',
                'id_materiais',
                'id_enderecos',
                'id_solicitacoes',
                'id_pagamentos'
            ).prefetch_related('imagens_coletas').order_by('-criado_em')
            
            serializer = ColetasRetrieveSerializer(coletas_cliente, many=True)
            return Response(serializer.data)
            
        except Clientes.DoesNotExist:
            return Response(
                {'detail': 'Cliente não encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'], url_path='aceitar-coleta')
    def aceitar_coleta(self, request, pk=None):
        """
        Permite que um parceiro aceite uma coleta pendente
        """
        coleta = self.get_object()
        parceiro_id = request.data.get('parceiro_id')
        
        if not parceiro_id:
            return Response(
                {'error': 'ID do parceiro é obrigatório'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            parceiro = Parceiros.objects.get(id_usuarios=parceiro_id)
        except Parceiros.DoesNotExist:
            return Response(
                {'error': 'Parceiro não encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        with transaction.atomic():
            # Verificar se a coleta ainda está pendente
            if coleta.id_solicitacoes.estado_solicitacao != 'pendente':
                return Response(
                    {'error': 'Esta coleta não está mais disponível'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Verificar se já não foi aceita por outro parceiro
            if coleta.id_parceiros:
                return Response(
                    {'error': 'Esta coleta já foi aceita por outro parceiro'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Verificar se o parceiro trabalha com este material
            if not MateriaisParceiros.objects.filter(
                id_parceiros=parceiro,
                id_materiais=coleta.id_materiais
            ).exists():
                return Response(
                    {'error': 'Você não trabalha com este tipo de material'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Aceitar a coleta
            coleta.id_parceiros = parceiro
            coleta.save()
            
            # Atualizar status da solicitação
            solicitacao = coleta.id_solicitacoes
            solicitacao.estado_solicitacao = 'aceitado'
            solicitacao.save()
            
            return Response(
                {'message': 'Coleta aceita com sucesso'},
                status=status.HTTP_200_OK
            )

    @action(detail=True, methods=['post'], url_path='finalizar-coleta')
    def finalizar_coleta(self, request, pk=None):
        """
        Permite que um parceiro finalize uma coleta aceita
        """
        coleta = self.get_object()
        
        if coleta.id_solicitacoes.estado_solicitacao != 'aceitado':
            return Response(
                {'error': 'Esta coleta não pode ser finalizada'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        with transaction.atomic():
            # Atualizar status da solicitação
            solicitacao = coleta.id_solicitacoes
            solicitacao.estado_solicitacao = 'coletado'
            solicitacao.finalizado_em = timezone.now()
            solicitacao.save()
            
            # Atualizar status do pagamento
            pagamento = coleta.id_pagamentos
            pagamento.estado_pagamento = 'pago'
            pagamento.save()
            
            return Response(
                {'message': 'Coleta finalizada com sucesso'},
                status=status.HTTP_200_OK
            )

    @action(detail=True, methods=['post'], url_path='cancelar-coleta')
    def cancelar_coleta(self, request, pk=None):
        """
        Permite que um cliente cancele uma coleta
        """
        coleta = self.get_object()
        
        if coleta.id_solicitacoes.estado_solicitacao not in ['pendente', 'aceitado']:
            return Response(
                {'error': 'Esta coleta não pode ser cancelada'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        with transaction.atomic():
            # Atualizar status da solicitação
            solicitacao = coleta.id_solicitacoes
            solicitacao.estado_solicitacao = 'cancelado'
            solicitacao.save()
            
            # Atualizar status do pagamento
            pagamento = coleta.id_pagamentos
            pagamento.estado_pagamento = 'cancelado'
            pagamento.save()
            
            return Response(
                {'message': 'Coleta cancelada com sucesso'},
                status=status.HTTP_200_OK
            )

    @action(detail=True, methods=['post'], url_path='upload-imagem')
    def upload_imagem(self, request, pk=None):
        """
        Upload de imagem para coleta com nome personalizado
        """
        coleta = self.get_object()
        if 'imagem' not in request.FILES:
            return Response(
                {'error': 'Nenhuma imagem enviada'},
                status=status.HTTP_400_BAD_REQUEST
            )

        imagem = request.FILES['imagem']
        tipo_usuario = request.data.get('tipo_usuario')  # 'cliente' ou 'parceiro'
        
        # Determinar prefixo do nome baseado no tipo de usuário
        if tipo_usuario == 'cliente':
            nome_usuario = coleta.id_clientes.id_usuarios.nome
            prefixo = f"cliente_{nome_usuario}"
        elif tipo_usuario == 'parceiro' and coleta.id_parceiros:
            nome_usuario = coleta.id_parceiros.id_usuarios.nome
            prefixo = f"parceiro_{nome_usuario}"
        else:
            return Response(
                {'error': 'Tipo de usuário inválido ou parceiro não definido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Gerar nome único para o arquivo
        nome_original = imagem.name
        extensao = os.path.splitext(nome_original)[1]
        nome_personalizado = f"{prefixo}_coleta_{coleta.id}_{timezone.now().strftime('%Y%m%d_%H%M%S')}{extensao}"
        
        # Salvar no banco com nome personalizado
        ImagemColetas.objects.create(
            id_coletas=coleta, 
            imagem=nome_personalizado
        )
        
        return Response(
            {'message': 'Imagem adicionada com sucesso', 'nome_arquivo': nome_personalizado},
            status=status.HTTP_201_CREATED
        )


class MateriaisViewSet(viewsets.ModelViewSet):
    queryset = Materiais.objects.all()
    serializer_class = MateriaisSerializer


class MateriaisParceirosViewSet(viewsets.ModelViewSet):
    queryset = MateriaisParceiros.objects.all()
    serializer_class = MateriaisParceirosSerializer


class MateriaisPontosColetaViewSet(viewsets.ModelViewSet):
    queryset = MateriaisPontosColeta.objects.all()
    serializer_class = MateriaisPontosColetaSerializer


class PagamentosViewSet(viewsets.ModelViewSet):
    queryset = Pagamentos.objects.all()
    serializer_class = PagamentosSerializer


class PontosColetaViewSet(viewsets.ModelViewSet):
    queryset = PontosColeta.objects.all().select_related(
        'id_enderecos',
        'id_parceiros',
        'id_parceiros__id_usuarios'
    ).prefetch_related(
        Prefetch(
            'materiais',
            queryset=Materiais.objects.only(
                'nome', 'descricao'
            )
        ),
        'id_parceiros__id_usuarios__telefones'
    )

    def get_serializer_class(self):
        if self.action == 'create':
            return PontosColetaCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return PontosColetaUpdateSerializer
        return PontosColetaRetrieveSerializer


class SolicitacoesViewSet(viewsets.ModelViewSet):
    queryset = Solicitacoes.objects.all()
    serializer_class = SolicitacoesSerializer


class TelefonesViewSet(viewsets.ModelViewSet):
    queryset = Telefones.objects.all()
    serializer_class = TelefonesSerializer


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


class PingView(APIView):
    def get(self, request):
        return Response({"message": "pong"})


class ImagemPerfilViewSet(viewsets.ModelViewSet):
    queryset = ImagemPerfil.objects.all()
    lookup_field = 'id_usuarios'  # Define que vamos buscar pelo id_usuarios

    def get_object(self):
        # Sobrescreve o método get_object para usar o lookup_field corretamente
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        obj = get_object_or_404(self.get_queryset(), **filter_kwargs)
        self.check_object_permissions(self.request, obj)
        return obj

    def get_serializer_class(self):
        if self.action == 'create':
            return ImagemPerfilCreateSerializer
        return ImagemPerfilRetrieveSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            ImagemPerfilRetrieveSerializer(serializer.instance).data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        try:
            # Deleta do ImageKit
            imagekit_service.delete_image(instance.file_id)

            # Deleta do banco de dados
            self.perform_destroy(instance)

            return Response(status=status.HTTP_204_NO_CONTENT)

        except Exception as e:
            return Response(
                {"detail": f"Erro ao deletar imagem: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
