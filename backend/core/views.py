from rest_framework import viewsets
from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from .models import (
    Avaliacoes, Clientes, Coletas, Enderecos,
    Materiais, MateriaisParceiros, MateriaisPontosColeta, Pagamentos,
    Parceiros, PontosColeta, Solicitacoes, Telefones, Usuarios
)
from .serializers import (
    AvaliacoesSerializer, ClientesSerializer, ColetasSerializer,
    EnderecosSerializer, MateriaisSerializer, MateriaisParceirosSerializer,
    MateriaisPontosColetaSerializer, PagamentosSerializer, ParceirosSerializer,
    PontosColetaSerializer, SolicitacoesSerializer, TelefonesSerializer,
    UsuariosSerializer
)

def home(request):
    return JsonResponse({"mensagem": "APIs GreenCycle App"})

# ViewSets
class AvaliacoesViewSet(viewsets.ModelViewSet):
    queryset = Avaliacoes.objects.all()
    serializer_class = AvaliacoesSerializer
    #permission_classes = [IsAuthenticated]

class ClientesViewSet(viewsets.ModelViewSet):
    queryset = Clientes.objects.all()
    serializer_class = ClientesSerializer
    #permission_classes = [IsAuthenticated]

class ColetasViewSet(viewsets.ModelViewSet):
    queryset = Coletas.objects.all()
    serializer_class = ColetasSerializer
    #permission_classes = [IsAuthenticated]

class EnderecosViewSet(viewsets.ModelViewSet):
    queryset = Enderecos.objects.all()
    serializer_class = EnderecosSerializer
    #permission_classes = [IsAuthenticated]

class MateriaisViewSet(viewsets.ModelViewSet):
    queryset = Materiais.objects.all()
    serializer_class = MateriaisSerializer
    #permission_classes = [IsAuthenticated]

class MateriaisParceirosViewSet(viewsets.ModelViewSet):
    queryset = MateriaisParceiros.objects.all()
    serializer_class = MateriaisParceirosSerializer
    #permission_classes = [IsAuthenticated]

class MateriaisPontosColetaViewSet(viewsets.ModelViewSet):
    queryset = MateriaisPontosColeta.objects.all()
    serializer_class = MateriaisPontosColetaSerializer
    #permission_classes = [IsAuthenticated]

class PagamentosViewSet(viewsets.ModelViewSet):
    queryset = Pagamentos.objects.all()
    serializer_class = PagamentosSerializer
    #permission_classes = [IsAuthenticated]

class ParceirosViewSet(viewsets.ModelViewSet):
    queryset = Parceiros.objects.all()
    serializer_class = ParceirosSerializer
    #permission_classes = [IsAuthenticated]

class PontosColetaViewSet(viewsets.ModelViewSet):
    queryset = PontosColeta.objects.all()
    serializer_class = PontosColetaSerializer
    #permission_classes = [IsAuthenticated]

class SolicitacoesViewSet(viewsets.ModelViewSet):
    queryset = Solicitacoes.objects.all()
    serializer_class = SolicitacoesSerializer
    #permission_classes = [IsAuthenticated]

class TelefonesViewSet(viewsets.ModelViewSet):
    queryset = Telefones.objects.all()
    serializer_class = TelefonesSerializer
    #permission_classes = [IsAuthenticated]

class UsuariosViewSet(viewsets.ModelViewSet):
    queryset = Usuarios.objects.all()
    serializer_class = UsuariosSerializer
    #permission_classes = [IsAuthenticated]

class LoginAPIView(APIView):
    def post(self, request):
        nome = request.data.get('nome')
        senha = request.data.get('senha')

        try:
            usuario = Usuarios.objects.get(nome=nome)

            if usuario.senha == senha:
                serializer = UsuariosSerializer(usuario)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({'detail': 'Senha incorreta'}, status=status.HTTP_401_UNAUTHORIZED)
        except Usuarios.DoesNotExist:
            return Response({'detail': 'Usuário não encontrado'}, status=status.HTTP_404_NOT_FOUND)

class ClientesApiView(ListCreateAPIView):
    queryset = Clientes.objects.all()
    serializer_class = ClientesSerializer

class ParceirosApiView(ListCreateAPIView):
    queryset = Parceiros.objects.all()
    serializer_class = ParceirosSerializer