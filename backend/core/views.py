import os

# from rest_framework.decorators import action
from django.core.cache import cache
from django.db import transaction
from django.db.models import Prefetch, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from .models import (Avaliacoes, Clientes, Coletas, Enderecos, EnderecoCliente, ImagemColetas,
                     ImagemPerfil, Materiais, MateriaisParceiros,
                     MateriaisPontosColeta, Pagamentos, Parceiros,
                     PontosColeta, Solicitacoes, Telefones, Usuarios)
from .serializers import (AvaliacaoClienteSerializer,
                          AvaliacaoCreateSerializer,
                          AvaliacaoParceiroSerializer,
                          AvaliacaoRetrieveSerializer, AvaliacoesSerializer,
                          ClienteComUsuarioCreateSerializer,
                          ClienteComUsuarioRetrieveSerializer,
                          ClienteComUsuarioUpdateSerializer,
                          ColetasCreateSerializer,
                          ColetasPendentesParceiroSerializer,
                          ColetasRetrieveSerializer, ColetasUpdateSerializer,
                          EnderecoBuscaCEPSerializer, EnderecoCreateSerializer,
                          EnderecoRetrieveSerializer, EnderecoUpdateSerializer,
                          EstatisticasClienteSerializer,
                          EstatisticasParceiroSerializer,
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
                          TelefoneCreateSerializer, TelefoneRetrieveSerializer,
                          TelefonesSerializer, TelefoneUpdateSerializer,
                          UsuarioCreateSerializer, UsuarioRetrieveSerializer, EnderecoClienteSerializer)
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

class EnderecoClienteViewSet(viewsets.ModelViewSet):
    serializer_class = EnderecoClienteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return EnderecoCliente.objects.filter(cliente=self.request.user)

    def perform_create(self, serializer):
        serializer.save(cliente=self.request.user)


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
    queryset = Avaliacoes.objects.all().select_related(
        'id_clientes__id_usuarios',
        'id_parceiros__id_usuarios',
        'id_coletas__id_materiais'
    )
    
    def get_serializer_class(self):
        if self.action == 'retrieve' or self.action == 'list':
            return AvaliacaoRetrieveSerializer
        elif self.action == 'avaliar_parceiro':
            return AvaliacaoClienteSerializer
        elif self.action == 'avaliar_cliente':
            return AvaliacaoParceiroSerializer
        elif self.action in ['estatisticas_cliente', 'estatisticas_parceiro']:
            return AvaliacaoRetrieveSerializer  # Placeholder
        return AvaliacoesSerializer

    def create(self, request, *args, **kwargs):
        """Criação automática de avaliação - uso interno apenas"""
        return Response(
            {'error': 'Use os endpoints específicos para avaliar'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=False, methods=['post'], url_path='avaliar-parceiro')
    def avaliar_parceiro(self, request):
        """
        Permite que um cliente avalie um parceiro após coleta finalizada
        """
        coleta_id = request.data.get('coleta_id')
        cliente_id = request.data.get('cliente_id')
        
        if not coleta_id or not cliente_id:
            return Response(
                {'error': 'coleta_id e cliente_id são obrigatórios'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            coleta = Coletas.objects.select_related(
                'id_solicitacoes', 'id_pagamentos', 'id_clientes', 'id_parceiros'
            ).get(id=coleta_id)
        except Coletas.DoesNotExist:
            return Response(
                {'error': 'Coleta não encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Verificar se o cliente da requisição é o mesmo da coleta
        if coleta.id_clientes.id_usuarios.id != int(cliente_id):
            return Response(
                {'error': 'Você só pode avaliar suas próprias coletas'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Verificar se a coleta está finalizada e paga
        if (coleta.id_solicitacoes.estado_solicitacao != 'finalizado' or 
            coleta.id_pagamentos.estado_pagamento != 'pago'):
            return Response(
                {'error': 'A coleta deve estar finalizada e paga para ser avaliada'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Buscar avaliação existente (sempre deve existir após finalização)
        try:
            avaliacao = Avaliacoes.objects.get(id_coletas=coleta)
        except Avaliacoes.DoesNotExist:
            return Response(
                {'error': 'Avaliação não encontrada. A coleta pode não ter sido finalizada corretamente.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Cliente pode editar sua avaliação quantas vezes quiser
        # (removida validação que impedia re-avaliação)
        
        # Atualizar avaliação do parceiro
        serializer = AvaliacaoClienteSerializer(data=request.data)
        if serializer.is_valid():
            avaliacao.nota_parceiros = serializer.validated_data['nota_parceiros']
            avaliacao.descricao_parceiros = serializer.validated_data.get('descricao_parceiros', '')
            avaliacao.save()
            
            # Verificar se é primeira avaliação ou edição
            if avaliacao.nota_parceiros == 0:
                mensagem = 'Avaliação do parceiro realizada com sucesso'
            else:
                mensagem = 'Avaliação do parceiro atualizada com sucesso'
            
            return Response(
                {'message': mensagem},
                status=status.HTTP_200_OK
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='avaliar-cliente')
    def avaliar_cliente(self, request):
        """
        Permite que um parceiro avalie um cliente após coleta finalizada
        """
        coleta_id = request.data.get('coleta_id')
        parceiro_id = request.data.get('parceiro_id')
        
        if not coleta_id or not parceiro_id:
            return Response(
                {'error': 'coleta_id e parceiro_id são obrigatórios'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            coleta = Coletas.objects.select_related(
                'id_solicitacoes', 'id_pagamentos', 'id_clientes', 'id_parceiros'
            ).get(id=coleta_id)
        except Coletas.DoesNotExist:
            return Response(
                {'error': 'Coleta não encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Verificar se o parceiro da requisição é o mesmo da coleta
        if not coleta.id_parceiros or coleta.id_parceiros.id_usuarios.id != int(parceiro_id):
            return Response(
                {'error': 'Você só pode avaliar coletas que você realizou'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Verificar se a coleta está finalizada e paga
        if (coleta.id_solicitacoes.estado_solicitacao != 'finalizado' or 
            coleta.id_pagamentos.estado_pagamento != 'pago'):
            return Response(
                {'error': 'A coleta deve estar finalizada e paga para ser avaliada'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Buscar avaliação existente (sempre deve existir após finalização)
        try:
            avaliacao = Avaliacoes.objects.get(id_coletas=coleta)
        except Avaliacoes.DoesNotExist:
            return Response(
                {'error': 'Avaliação não encontrada. A coleta pode não ter sido finalizada corretamente.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Parceiro pode editar sua avaliação quantas vezes quiser
        # (removida validação que impedia re-avaliação)
        
        # Atualizar avaliação do cliente
        serializer = AvaliacaoParceiroSerializer(data=request.data)
        if serializer.is_valid():
            avaliacao.nota_clientes = serializer.validated_data['nota_clientes']
            avaliacao.descricao_clientes = serializer.validated_data.get('descricao_clientes', '')
            avaliacao.save()
            
            # Verificar se é primeira avaliação ou edição
            if avaliacao.nota_clientes == 0:
                mensagem = 'Avaliação do cliente realizada com sucesso'
            else:
                mensagem = 'Avaliação do cliente atualizada com sucesso'
                
            return Response(
                {'message': mensagem},
                status=status.HTTP_200_OK
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='estatisticas-cliente/(?P<cliente_id>[^/]+)')
    def estatisticas_cliente(self, request, cliente_id=None):
        """
        Retorna estatísticas de avaliações de um cliente
        """
        try:
            cliente = Clientes.objects.select_related('id_usuarios').get(
                id_usuarios=cliente_id
            )
        except Clientes.DoesNotExist:
            return Response(
                {'error': 'Cliente não encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Buscar avaliações onde o cliente foi avaliado
        avaliacoes = Avaliacoes.objects.filter(
            id_clientes=cliente,
            nota_clientes__gt=0  # Apenas avaliações com nota válida
        )

        if not avaliacoes.exists():
            return Response({
                'cliente_id': cliente.id_usuarios.id,
                'cliente_nome': cliente.id_usuarios.nome,
                'total_avaliacoes': 0,
                'media_notas': 0,
                'notas_detalhadas': {str(i): 0 for i in range(6)},
                'total_coletas_finalizadas': 0
            })

        # Calcular estatísticas
        notas = [av.nota_clientes for av in avaliacoes]
        media_notas = sum(notas) / len(notas)
        
        # Contar cada nota
        notas_detalhadas = {str(i): 0 for i in range(6)}
        for nota in notas:
            notas_detalhadas[str(nota)] += 1

        # Total de coletas finalizadas do cliente
        total_coletas = Coletas.objects.filter(
            id_clientes=cliente,
            id_solicitacoes__estado_solicitacao='finalizado',
            id_pagamentos__estado_pagamento='pago'
        ).count()

        return Response({
            'cliente_id': cliente.id_usuarios.id,
            'cliente_nome': cliente.id_usuarios.nome,
            'total_avaliacoes': len(notas),
            'media_notas': round(media_notas, 2),
            'notas_detalhadas': notas_detalhadas,
            'total_coletas_finalizadas': total_coletas
        })

    @action(detail=False, methods=['get'], url_path='estatisticas-parceiro/(?P<parceiro_id>[^/]+)')
    def estatisticas_parceiro(self, request, parceiro_id=None):
        """
        Retorna estatísticas de avaliações de um parceiro
        """
        try:
            parceiro = Parceiros.objects.select_related('id_usuarios').get(
                id_usuarios=parceiro_id
            )
        except Parceiros.DoesNotExist:
            return Response(
                {'error': 'Parceiro não encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Buscar avaliações onde o parceiro foi avaliado
        avaliacoes = Avaliacoes.objects.filter(
            id_parceiros=parceiro,
            nota_parceiros__gt=0  # Apenas avaliações com nota válida
        )

        if not avaliacoes.exists():
            return Response({
                'parceiro_id': parceiro.id_usuarios.id,
                'parceiro_nome': parceiro.id_usuarios.nome,
                'total_avaliacoes': 0,
                'media_notas': 0,
                'notas_detalhadas': {str(i): 0 for i in range(6)},
                'total_coletas_finalizadas': 0
            })

        # Calcular estatísticas
        notas = [av.nota_parceiros for av in avaliacoes]
        media_notas = sum(notas) / len(notas)
        
        # Contar cada nota
        notas_detalhadas = {str(i): 0 for i in range(6)}
        for nota in notas:
            notas_detalhadas[str(nota)] += 1

        # Total de coletas finalizadas do parceiro
        total_coletas = Coletas.objects.filter(
            id_parceiros=parceiro,
            id_solicitacoes__estado_solicitacao='finalizado',
            id_pagamentos__estado_pagamento='pago'
        ).count()

        return Response({
            'parceiro_id': parceiro.id_usuarios.id,
            'parceiro_nome': parceiro.id_usuarios.nome,
            'total_avaliacoes': len(notas),
            'media_notas': round(media_notas, 2),
            'notas_detalhadas': notas_detalhadas,
            'total_coletas_finalizadas': total_coletas
        })


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

    @action(detail=True, methods=['post'], url_path='marcar-coletado')
    def marcar_coletado(self, request, pk=None):
        """
        Permite que um parceiro marque uma coleta como coletada
        """
        coleta = self.get_object()
        
        if coleta.id_solicitacoes.estado_solicitacao != 'aceitado':
            return Response(
                {'error': 'Esta coleta não pode ser marcada como coletada'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        with transaction.atomic():
            # Atualizar status da solicitação para coletado
            solicitacao = coleta.id_solicitacoes
            solicitacao.estado_solicitacao = 'coletado'
            solicitacao.save()
            
            return Response(
                {'message': 'Coleta marcada como coletada com sucesso'},
                status=status.HTTP_200_OK
            )

    @action(detail=True, methods=['post'], url_path='cancelar-coleta')
    def cancelar_coleta(self, request, pk=None):
        """
        Permite que um cliente cancele uma coleta
        Condições: pagamento pendente E solicitação pendente
        """
        coleta = self.get_object()
        
        # Validar se pode cancelar: pagamento pendente E solicitação pendente
        if (coleta.id_pagamentos.estado_pagamento != 'pendente' or 
            coleta.id_solicitacoes.estado_solicitacao != 'pendente'):
            return Response(
                {'error': 'Esta coleta só pode ser cancelada se estiver com pagamento pendente e solicitação pendente'},
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

    @action(detail=True, methods=['post'], url_path='finalizar-coleta')
    def finalizar_coleta(self, request, pk=None):
        """
        Permite que um cliente finalize uma coleta
        Condições: pagamento pendente E solicitação coletado
        Ao finalizar: muda solicitação para finalizado E pagamento para pago
        NOVO: Cria automaticamente registro de avaliação
        """
        coleta = self.get_object()
        
        # Validar se pode finalizar: pagamento pendente E solicitação coletado
        if (coleta.id_pagamentos.estado_pagamento != 'pendente' or 
            coleta.id_solicitacoes.estado_solicitacao != 'coletado'):
            return Response(
                {'error': 'Esta coleta só pode ser finalizada se estiver com pagamento pendente e solicitação coletado'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        with transaction.atomic():
            # Atualizar status da solicitação para finalizado
            solicitacao = coleta.id_solicitacoes
            solicitacao.estado_solicitacao = 'finalizado'
            solicitacao.finalizado_em = timezone.now()
            solicitacao.save()
            
            # Atualizar status do pagamento para pago
            pagamento = coleta.id_pagamentos
            pagamento.estado_pagamento = 'pago'
            pagamento.save()
            
            # Criar registro de avaliação automaticamente
            # Verificar se já não existe (por segurança)
            if not hasattr(coleta, 'avaliacao') or not coleta.avaliacao:
                Avaliacoes.objects.create(
                    id_coletas=coleta,
                    id_clientes=coleta.id_clientes,
                    id_parceiros=coleta.id_parceiros,
                    nota_parceiros=0,  # Valor padrão até cliente avaliar
                    nota_clientes=0,   # Valor padrão até parceiro avaliar
                    descricao_parceiros='',
                    descricao_clientes=''
                )
            
            return Response(
                {'message': 'Coleta finalizada com sucesso e avaliação criada'},
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
    queryset = Telefones.objects.all().select_related('id_usuarios')
    lookup_field = 'id_usuarios'  # Permite buscar por ID do usuário

    def get_serializer_class(self):
        if self.action == 'create':
            return TelefoneCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return TelefoneUpdateSerializer
        elif self.action == 'retrieve':
            return TelefoneRetrieveSerializer
        return TelefoneRetrieveSerializer

    def get_object(self):
        # Sobrescreve o método get_object para usar o lookup_field corretamente
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        obj = get_object_or_404(self.get_queryset(), **filter_kwargs)
        self.check_object_permissions(self.request, obj)
        return obj

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            TelefoneRetrieveSerializer(serializer.instance).data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    @action(detail=False, methods=['get'], url_path='por-usuario/(?P<usuario_id>[^/]+)')
    def por_usuario(self, request, usuario_id=None):
        """
        Busca telefone por ID do usuário
        """
        try:
            telefone = Telefones.objects.get(id_usuarios=usuario_id)
            serializer = TelefoneRetrieveSerializer(telefone)
            return Response(serializer.data)
        except Telefones.DoesNotExist:
            return Response(
                {'detail': 'Telefone não encontrado para este usuário'},
                status=status.HTTP_404_NOT_FOUND
            )


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
