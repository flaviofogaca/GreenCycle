# from django.contrib.auth.hashers import make_password
import requests
from django.core.validators import MinLengthValidator
from django.db import transaction
from rest_framework import serializers
from rest_framework.serializers import (CharField, DateField, ImageField,
                                        ModelSerializer,
                                        PrimaryKeyRelatedField, Serializer,
                                        ValidationError)

from .mixins import (GeocodingMixin, ValidacaoCEPMixin, ValidacaoCFPMixin,
                     ValidacaoCNPJMixin, ValidacaoTelefoneMixin)
from .models import (Avaliacoes, Clientes, Coletas, Enderecos, ImagemColetas,
                     ImagemPerfil, Materiais, MateriaisParceiros,
                     MateriaisPontosColeta, Pagamentos, Parceiros,
                     PontosColeta, Solicitacoes, Telefones, Usuarios)
from .services import imagekit_service

# Lembrar disso para os serializers
# CRUD (create, retrieve, update, delete)


# ====================== SERIALIZERS DE TELEFONE ======================

class TelefoneCreateSerializer(ValidacaoTelefoneMixin, ModelSerializer):
    numero = CharField(max_length=20, required=True)
    
    class Meta:
        model = Telefones
        fields = ['id_usuarios', 'numero']
        
    def validate_numero(self, value):
        return self.validar_telefone(value)
        
    def create(self, validated_data):
        # Verifica se o usuário já tem telefone
        usuario = validated_data['id_usuarios']
        if Telefones.objects.filter(id_usuarios=usuario).exists():
            raise ValidationError({'detail': 'Este usuário já possui um telefone cadastrado'})
        
        return super().create(validated_data)


class TelefoneUpdateSerializer(ValidacaoTelefoneMixin, ModelSerializer):
    numero = CharField(max_length=20, required=True)
    
    class Meta:
        model = Telefones
        fields = ['numero']
        
    def validate_numero(self, value):
        return self.validar_telefone(value)


class TelefoneRetrieveSerializer(ModelSerializer):
    usuario_nome = serializers.SerializerMethodField()
    
    class Meta:
        model = Telefones
        fields = ['id_usuarios', 'numero', 'usuario_nome', 'criado_em', 'atualizado_em']
        
    def get_usuario_nome(self, obj):
        return obj.id_usuarios.nome if obj.id_usuarios else None


# ====================== SERIALIZERS DE USUÁRIO ======================

class UsuarioCreateSerializer(ModelSerializer):
    senha = CharField(
        # write_only=True,
        required=True,
        validators=[MinLengthValidator(8)],
        style={'input_type': 'password'}
    )
    telefone = CharField(max_length=20, required=False, write_only=True, allow_blank=True)

    class Meta:
        model = Usuarios
        fields = [
            'id',
            'usuario',
            'nome',
            'email',
            'senha',
            'id_endereco',
            'telefone'
        ]
        extra_kwargs = {
            'senha': {'write_only': True},
            'email': {'required': True}
        }

    def create(self, validated_data):
        # Extrai o telefone dos dados
        telefone_numero = validated_data.pop('telefone', None)
        
        # Criptografa a senha antes de salvar
        # validated_data['senha'] = make_password(validated_data['senha'])

        usuario = Usuarios(**validated_data)
        usuario.save()
        
        # Cria o telefone se foi fornecido
        if telefone_numero and telefone_numero.strip():
            Telefones.objects.create(
                id_usuarios=usuario,
                numero=telefone_numero.strip()
            )
        
        return usuario


class UsuarioRetrieveSerializer(ModelSerializer):
    telefone = serializers.SerializerMethodField()
    
    class Meta:
        model = Usuarios
        fields = [
            'id',
            'usuario',
            'nome',
            'senha',
            'email',
            'id_endereco',
            'telefone'
        ]
        depth = 1
        
    def get_telefone(self, obj):
        try:
            telefone = Telefones.objects.get(id_usuarios=obj.id)
            return {
                'numero': telefone.numero,
                'criado_em': telefone.criado_em,
                'atualizado_em': telefone.atualizado_em
            }
        except Telefones.DoesNotExist:
            return None


# Serializer para endereços do usuário (para listagem na criação de coleta)
class EnderecoUsuarioSerializer(ModelSerializer):
    endereco_completo = serializers.SerializerMethodField()

    class Meta:
        model = Enderecos
        fields = ['id', 'endereco_completo', 'cep', 'estado', 'cidade', 'rua', 'bairro', 'numero', 'complemento']

    def get_endereco_completo(self, obj):
        partes = [obj.rua, str(obj.numero), obj.bairro, obj.cidade, obj.estado]
        endereco = ', '.join(filter(None, partes))
        if obj.complemento:
            endereco += f" - {obj.complemento}"
        return endereco


class ClienteComUsuarioCreateSerializer(ValidacaoCFPMixin, ModelSerializer):
    nome = CharField(write_only=True, max_length=100)
    usuario = CharField(
        write_only=True,
        max_length=100,
        required=False
    )
    email = CharField(
        write_only=True,
        max_length=100,
        required=False,
        allow_null=True
    )
    senha = CharField(
        write_only=True,
        required=True,
        validators=[MinLengthValidator(8)],
        style={'input_type': 'password'}
    )
    telefone = CharField(max_length=20, required=False, write_only=True, allow_blank=True)
    id_endereco = PrimaryKeyRelatedField(
        queryset=Enderecos.objects.all(),
        write_only=True,
        required=False,
        allow_null=True
    )
    id_usuarios = PrimaryKeyRelatedField(read_only=True)
    data_nascimento = DateField()
    sexo = CharField(max_length=1)

    class Meta:
        model = Clientes
        fields = [
            'id',               # Campo do cliente
            'id_usuarios',      # Campo do usuário
            'usuario',          # Campo do usuário
            'cpf',              # Campo do cliente
            'data_nascimento',  # Campo do cliente
            'sexo',             # Campo do cliente
            'nome',             # Campo do usuário
            'email',            # Campo do usuário
            'senha',            # Campo do usuário
            'id_endereco',      # Campo do usuário
            'telefone'          # Campo do telefone
        ]
        read_only_fields = [
            'id',
            'id_usuarios',
        ]

    def validate_cpf(self, value):
        if value:
            return self.validar_cpf(value)
        return value

    def create(self, validated_data):
        # Extrai o telefone dos dados
        telefone_numero = validated_data.pop('telefone', None)
        
        # Extrai os dados do usuário
        usuario_data = {
            'nome': validated_data.pop('nome'),
            'usuario': validated_data.pop('usuario'),
            'email': validated_data.pop('email', None),
            'senha': validated_data.pop('senha'),
            'id_endereco': validated_data.pop('id_endereco', None)
        }

        # Cria o usuário primeiro
        usuario = Usuarios.objects.create(**usuario_data)

        # Cria o telefone se foi fornecido
        if telefone_numero and telefone_numero.strip():
            Telefones.objects.create(
                id_usuarios=usuario,
                numero=telefone_numero.strip()
            )

        # Cria o cliente vinculado ao usuário
        cliente = Clientes.objects.create(
            id_usuarios=usuario,
            **validated_data
        )

        return cliente


class ClienteComUsuarioUpdateSerializer(ValidacaoCFPMixin, ModelSerializer):
    nome = CharField(required=False)
    usuario = CharField(
        write_only=True,
        max_length=100,
        required=False
    )
    email = CharField(required=False)
    senha = CharField(
        required=False,
        validators=[MinLengthValidator(8)],
        style={'input_type': 'password'}
    )
    telefone = CharField(max_length=20, required=False, write_only=True, allow_blank=True)
    id_endereco = PrimaryKeyRelatedField(
        queryset=Enderecos.objects.all(),
        write_only=True,
        required=False,
        allow_null=True
    )
    cpf = CharField(required=False)
    data_nascimento = DateField(required=False)
    sexo = CharField(max_length=1, required=False)

    class Meta:
        model = Clientes
        fields = [
            'nome',
            'usuario',
            'email',
            'senha',
            'telefone',
            'id_endereco',
            'cpf',
            'data_nascimento',
            'sexo'
        ]

    def validate_cpf(self, value):
        if value:
            return self.validar_cpf(value)
        return value

    def update(self, instance, validated_data):
        # Trata o telefone
        telefone_numero = validated_data.pop('telefone', None)
        
        # Atualiza dados do usuário
        usuario = instance.id_usuarios
        if 'nome' in validated_data:
            usuario.nome = validated_data['nome']
        if 'usuario' in validated_data:
            usuario.usuario = validated_data['usuario']
        if 'email' in validated_data:
            usuario.email = validated_data['email']
        if 'senha' in validated_data:
            usuario.senha = validated_data['senha']
        if 'id_endereco' in validated_data:
            usuario.id_endereco = validated_data['id_endereco']
        usuario.save()

        # Atualiza ou cria telefone
        if telefone_numero is not None:  # Permite string vazia para remover telefone
            if telefone_numero.strip():
                # Atualiza ou cria telefone
                telefone, created = Telefones.objects.get_or_create(
                    id_usuarios=usuario,
                    defaults={'numero': telefone_numero.strip()}
                )
                if not created:
                    telefone.numero = telefone_numero.strip()
                    telefone.save()
            else:
                # Remove telefone se string vazia
                Telefones.objects.filter(id_usuarios=usuario).delete()

        # Atualiza dados do cliente
        if 'cpf' in validated_data:
            instance.cpf = validated_data['cpf']
        if 'data_nascimento' in validated_data:
            instance.data_nascimento = validated_data['data_nascimento']
        if 'sexo' in validated_data:
            instance.sexo = validated_data['sexo']
        instance.save()

        return instance


class ClienteComUsuarioRetrieveSerializer(ModelSerializer):
    id_usuarios = UsuarioRetrieveSerializer(read_only=True)
    enderecos_usuario = serializers.SerializerMethodField()

    class Meta:
        model = Clientes
        fields = [
            'id',
            'id_usuarios',
            'cpf',
            'data_nascimento',
            'sexo',
            'enderecos_usuario'
        ]
        depth = 0

    def get_enderecos_usuario(self, obj):
        # Lista todos os endereços associados ao usuário do cliente
        if obj.id_usuarios and obj.id_usuarios.id_endereco:
            endereco = obj.id_usuarios.id_endereco
            return EnderecoUsuarioSerializer(endereco).data
        return None


class ParceiroComUsuarioCreateSerializer(ValidacaoCNPJMixin, ModelSerializer):
    nome = CharField(write_only=True, max_length=100)
    usuario = CharField(
        write_only=True,
        max_length=100,
        required=False
    )
    email = CharField(
        write_only=True,
        max_length=100,
        required=False,
        allow_null=True
    )
    senha = CharField(
        write_only=True,
        required=True,
        validators=[MinLengthValidator(8)],
        style={'input_type': 'password'}
    )
    telefone = CharField(max_length=20, required=False, write_only=True, allow_blank=True)
    id_endereco = PrimaryKeyRelatedField(
        queryset=Enderecos.objects.all(),
        write_only=True,
        required=False,
        allow_null=True
    )
    id_usuarios = PrimaryKeyRelatedField(read_only=True)
    materiais = PrimaryKeyRelatedField(
        queryset=Materiais.objects.all(),
        many=True,
        required=False,
        write_only=True,
        allow_null=True
    )

    class Meta:
        model = Parceiros
        fields = [
            'id',             # Campo do parceiro
            'id_usuarios',    # Campo do usuário
            'usuario',        # Campo do usuário
            'cnpj',           # Campo do parceiro
            'nome',           # Campo do usuário
            'email',          # Campo do usuário
            'senha',          # Campo do usuário
            'telefone',       # Campo do telefone
            'id_endereco',    # Campo do usuário
            'materiais'       # Campo de materiais
        ]
        read_only_fields = [
            'id',
            'id_usuarios',
        ]

    def validate_cnpj(self, value):
        if value:
            return self.validar_cnpj(value)
        return value

    def create(self, validated_data):
        # Extrai os materiais se existirem
        materiais_data = validated_data.pop('materiais', [])
        
        # Extrai o telefone dos dados
        telefone_numero = validated_data.pop('telefone', None)

        # Extrai os dados do usuário
        usuario_data = {
            'nome': validated_data.pop('nome'),
            'usuario': validated_data.pop('usuario'),
            'email': validated_data.pop('email', None),
            'senha': validated_data.pop('senha'),
            'id_endereco': validated_data.pop('id_endereco', None)
        }

        # Cria o usuário primeiro
        usuario = Usuarios.objects.create(**usuario_data)

        # Cria o telefone se foi fornecido
        if telefone_numero and telefone_numero.strip():
            Telefones.objects.create(
                id_usuarios=usuario,
                numero=telefone_numero.strip()
            )

        # Cria o parceiro vinculado ao usuário
        parceiro = Parceiros.objects.create(
            id_usuarios=usuario,
            **validated_data
        )

        # Cria os relacionamentos com materiais
        for material in materiais_data:
            MateriaisParceiros.objects.create(
                id_materiais=material,
                id_parceiros=parceiro
            )

        return parceiro


class ParceiroComUsuarioUpdateSerializer(ValidacaoCNPJMixin, ModelSerializer):
    nome = CharField(required=False)
    usuario = CharField(
        write_only=True,
        max_length=100,
        required=False
    )
    email = CharField(required=False)
    senha = CharField(
        required=False,
        validators=[MinLengthValidator(8)],
        style={'input_type': 'password'}
    )
    telefone = CharField(max_length=20, required=False, write_only=True, allow_blank=True)
    id_endereco = PrimaryKeyRelatedField(
        queryset=Enderecos.objects.all(),
        write_only=True,
        required=False,
        allow_null=True
    )
    cnpj = CharField(required=False)
    materiais = PrimaryKeyRelatedField(
        queryset=Materiais.objects.all(),
        many=True,
        required=False,
        write_only=True,
        allow_null=True
    )

    class Meta:
        model = Parceiros
        fields = [
            'nome',
            'usuario',
            'email',
            'senha',
            'telefone',
            'id_endereco',
            'cnpj',
            'materiais'
        ]

    def validate_cnpj(self, value):
        if value:
            return self.validar_cnpj(value)
        return value

    def update(self, instance, validated_data):
        # Trata o telefone
        telefone_numero = validated_data.pop('telefone', None)
        
        # Atualiza materiais se fornecidos
        if 'materiais' in validated_data:
            materiais_data = validated_data.pop('materiais')
            # Remove relacionamentos existentes
            MateriaisParceiros.objects.filter(id_parceiros=instance).delete()
            # Cria novos relacionamentos
            for material in materiais_data:
                MateriaisParceiros.objects.create(
                    id_materiais=material,
                    id_parceiros=instance
                )

        # Atualiza dados do usuário
        usuario = instance.id_usuarios
        if 'nome' in validated_data:
            usuario.nome = validated_data['nome']
        if 'usuario' in validated_data:
            usuario.usuario = validated_data['usuario']
        if 'email' in validated_data:
            usuario.email = validated_data['email']
        if 'senha' in validated_data:
            usuario.senha = validated_data['senha']
        if 'id_endereco' in validated_data:
            usuario.id_endereco = validated_data['id_endereco']
        usuario.save()

        # Atualiza ou cria telefone
        if telefone_numero is not None:  # Permite string vazia para remover telefone
            if telefone_numero.strip():
                # Atualiza ou cria telefone
                telefone, created = Telefones.objects.get_or_create(
                    id_usuarios=usuario,
                    defaults={'numero': telefone_numero.strip()}
                )
                if not created:
                    telefone.numero = telefone_numero.strip()
                    telefone.save()
            else:
                # Remove telefone se string vazia
                Telefones.objects.filter(id_usuarios=usuario).delete()

        # Atualiza dados do parceiro
        if 'cnpj' in validated_data:
            instance.cnpj = validated_data['cnpj']
        instance.save()

        return instance


class MateriaisSerializer(ModelSerializer):
    class Meta:
        model = Materiais
        fields = [
            'id',
            'nome',
            'descricao',
            'preco',
        ]


class ParceiroComUsuarioRetrieveSerializer(ModelSerializer):
    id_usuarios = UsuarioRetrieveSerializer(read_only=True)
    materiais = MateriaisSerializer(many=True, read_only=True)

    class Meta:
        model = Parceiros
        fields = [
            'id',
            'id_usuarios',
            'cnpj',
            'materiais'
        ]
        depth = 1


class EnderecoBuscaCEPSerializer(Serializer, ValidacaoCEPMixin):
    cep = CharField(max_length=15)

    def validate_cep(self, value):
        cep = self.validar_cep(value)

        # Consulta a API ViaCEP
        url = f'https://viacep.com.br/ws/{cep}/json/'
        response = requests.get(url)

        if response.status_code != 200 or response.json().get('erro'):
            raise ValidationError('CEP não encontrado')

        return cep

    def buscar_endereco(self):
        cep = self.validated_data['cep']  # type: ignore
        url = f'https://viacep.com.br/ws/{cep}/json/'
        response = requests.get(url)
        data = response.json()

        return {
            'cep': data.get('cep', '').replace('-', ''),
            'estado': data.get('uf', ''),
            'cidade': data.get('localidade', ''),
            'bairro': data.get('bairro', ''),
            'rua': data.get('logradouro', '')
        }


class EnderecoCreateSerializer(
    ModelSerializer,
    ValidacaoCEPMixin,
    GeocodingMixin
):
    cep = CharField(max_length=15)

    class Meta:
        model = Enderecos
        fields = [
            'id',
            'cep',
            'estado',
            'cidade',
            'rua',
            'bairro',
            'numero',
            'complemento',
        ]
        read_only_fields = [
            'id',
        ]

    def create(self, validated_data):
        # Monta o endereço completo para geocoding
        endereco_completo = (
            f"{validated_data.get('rua')}, {validated_data.get('numero')}, "
            f"{validated_data.get('bairro')}, {validated_data.get('cidade')}, "
            f"{validated_data.get('estado')}, {validated_data.get('cep')}"
        )

        # Obtém as coordenadas
        coordenadas = self.get_lat_lon(endereco_completo)

        if not coordenadas:
            # Se não conseguir geocodificar,
            # usa coordenadas padrão (centro do estado)
            coordenadas = (-15.7801, -47.9292)  # Coordenadas de Brasília

        validated_data['latitude'] = coordenadas[0]
        validated_data['longitude'] = coordenadas[1]

        return super().create(validated_data)


class EnderecoUpdateSerializer(
    ModelSerializer,
    ValidacaoCEPMixin,
    GeocodingMixin
):
    cep = CharField(max_length=15, required=False)
    estado = CharField(max_length=50, required=False)
    cidade = CharField(max_length=50, required=False)
    rua = CharField(max_length=50, required=False)
    bairro = CharField(max_length=50, required=False)

    class Meta:
        model = Enderecos
        fields = [
            'cep',
            'estado',
            'cidade',
            'rua',
            'bairro',
            'numero',
            'complemento'
        ]

    def update(self, instance, validated_data):
        # Verifica se algum campo relevante para geocoding foi alterado
        campos_geocoding = [
            'cep', 'estado', 'cidade', 'rua', 'bairro', 'numero'
        ]
        precisa_geocodificar = any(
            campo in validated_data for campo in campos_geocoding
        )

        if precisa_geocodificar:
            # Usa os novos valores ou mantém os existentes
            endereco_completo = (
                f"{validated_data.get('rua', instance.rua)}, "
                f"{validated_data.get('numero', instance.numero)}, "
                f"{validated_data.get('bairro', instance.bairro)}, "
                f"{validated_data.get('cidade', instance.cidade)}, "
                f"{validated_data.get('estado', instance.estado)}, "
                f"{validated_data.get('cep', instance.cep)}"
            )

            coordenadas = self.get_lat_lon(endereco_completo)

            if coordenadas:
                instance.latitude = coordenadas[0]
                instance.longitude = coordenadas[1]
            elif not instance.latitude or not instance.longitude:
                # Se não conseguir geocodificar e
                # não tiver coordenadas existentes
                coordenadas = (-15.7801, -47.9292)  # Coordenadas de Brasília
                instance.latitude = coordenadas[0]
                instance.longitude = coordenadas[1]

        # Atualiza os outros campos normalmente
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class EnderecoRetrieveSerializer(ModelSerializer):
    class Meta:
        model = Enderecos
        fields = [
            'id',
            'cep',
            'estado',
            'cidade',
            'rua',
            'bairro',
            'numero',
            'complemento',
            'latitude',
            'longitude',
        ]


# ====================== SERIALIZERS DE AVALIAÇÃO ======================

class AvaliacaoCreateSerializer(ModelSerializer):
    """Serializer para criação de avaliação - apenas para uso interno"""
    class Meta:
        model = Avaliacoes
        fields = [
            'id_coletas',
            'id_parceiros', 
            'id_clientes',
            'nota_parceiros',
            'descricao_parceiros',
            'nota_clientes',
            'descricao_clientes',
        ]

    def validate(self, data):
        # Validar notas (0-5)
        if data.get('nota_parceiros') is not None:
            if not (0 <= data['nota_parceiros'] <= 5):
                raise ValidationError({'nota_parceiros': 'A nota deve ser entre 0 e 5'})
        
        if data.get('nota_clientes') is not None:
            if not (0 <= data['nota_clientes'] <= 5):
                raise ValidationError({'nota_clientes': 'A nota deve ser entre 0 e 5'})
        
        return data


class AvaliacaoClienteSerializer(ModelSerializer):
    """Serializer para cliente avaliar parceiro"""
    nota_parceiros = serializers.IntegerField(min_value=0, max_value=5)
    descricao_parceiros = serializers.CharField(max_length=300, required=False, allow_blank=True)

    class Meta:
        model = Avaliacoes
        fields = ['nota_parceiros', 'descricao_parceiros']


class AvaliacaoParceiroSerializer(ModelSerializer):
    """Serializer para parceiro avaliar cliente"""
    nota_clientes = serializers.IntegerField(min_value=0, max_value=5)
    descricao_clientes = serializers.CharField(max_length=300, required=False, allow_blank=True)

    class Meta:
        model = Avaliacoes
        fields = ['nota_clientes', 'descricao_clientes']


class AvaliacaoRetrieveSerializer(ModelSerializer):
    cliente_nome = serializers.SerializerMethodField()
    parceiro_nome = serializers.SerializerMethodField()
    material_nome = serializers.SerializerMethodField()
    cliente_id = serializers.SerializerMethodField()
    parceiro_id = serializers.SerializerMethodField()

    class Meta:
        model = Avaliacoes
        fields = [
            'id',
            'id_coletas',
            'cliente_id',
            'cliente_nome',
            'parceiro_id',
            'parceiro_nome',
            'material_nome',
            'nota_parceiros',
            'descricao_parceiros',
            'nota_clientes',
            'descricao_clientes',
            'criado_em',
            'atualizado_em'
        ]

    def get_cliente_nome(self, obj):
        return obj.id_clientes.id_usuarios.nome if obj.id_clientes and obj.id_clientes.id_usuarios else None

    def get_parceiro_nome(self, obj):
        return obj.id_parceiros.id_usuarios.nome if obj.id_parceiros and obj.id_parceiros.id_usuarios else None

    def get_cliente_id(self, obj):
        return obj.id_clientes.id_usuarios.id if obj.id_clientes and obj.id_clientes.id_usuarios else None

    def get_parceiro_id(self, obj):
        return obj.id_parceiros.id_usuarios.id if obj.id_parceiros and obj.id_parceiros.id_usuarios else None

    def get_material_nome(self, obj):
        return obj.id_coletas.id_materiais.nome if obj.id_coletas and obj.id_coletas.id_materiais else None


class EstatisticasClienteSerializer(serializers.Serializer):
    cliente_id = serializers.IntegerField()
    cliente_nome = serializers.CharField()
    total_avaliacoes = serializers.IntegerField()
    media_notas = serializers.DecimalField(max_digits=3, decimal_places=2)
    notas_detalhadas = serializers.DictField()
    total_coletas_finalizadas = serializers.IntegerField()


class EstatisticasParceiroSerializer(serializers.Serializer):
    parceiro_id = serializers.IntegerField()
    parceiro_nome = serializers.CharField()
    total_avaliacoes = serializers.IntegerField()
    media_notas = serializers.DecimalField(max_digits=3, decimal_places=2)
    notas_detalhadas = serializers.DictField()
    total_coletas_finalizadas = serializers.IntegerField()


class AvaliacoesSerializer(ModelSerializer):
    """Serializer antigo - mantido para compatibilidade"""
    class Meta:
        model = Avaliacoes
        fields = [
            'id',
            'id_parceiros',
            'id_clientes',
            'id_coletas',
            'nota_parceiros',
            'descricao_parceiros',
            'nota_clientes',
            'descricao_clientes',
        ]


class ImagemColetaSerializer(ModelSerializer):
    class Meta:
        model = ImagemColetas
        fields = ['id', 'imagem', 'criado_em']


# Serializers específicos para criação de coleta
class SolicitacaoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Solicitacoes
        fields = ['observacoes']
        extra_kwargs = {
            'observacoes': {'required': False, 'allow_blank': True}
        }


class PagamentoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pagamentos
        fields = ['valor_pagamento', 'saldo_pagamento']
        extra_kwargs = {
            'valor_pagamento': {'required': True},
            'saldo_pagamento': {'default': '0.00'}
        }


class ColetasCreateSerializer(serializers.ModelSerializer):
    dados_solicitacao = SolicitacaoCreateSerializer(write_only=True)
    dados_pagamento = PagamentoCreateSerializer(write_only=True)

    class Meta:
        model = Coletas
        fields = [
            'id_clientes',
            'id_materiais',
            'peso_material',
            'quantidade_material',
            'id_enderecos',
            'dados_solicitacao',
            'dados_pagamento'
        ]

    def validate(self, data):
        # Validar que apenas peso OU quantidade foi fornecido
        peso = data.get('peso_material')
        quantidade = data.get('quantidade_material')
        
        if peso and quantidade:
            raise serializers.ValidationError(
                "Uma coleta deve ter apenas peso OU quantidade, não ambos."
            )
        if not peso and not quantidade:
            raise serializers.ValidationError(
                "Uma coleta deve ter peso OU quantidade."
            )
        
        return data

    @transaction.atomic
    def create(self, validated_data):
        solicitacao_data = validated_data.pop('dados_solicitacao')
        pagamento_data = validated_data.pop('dados_pagamento')

        # Criar solicitação com status padrão 'pendente'
        solicitacao = Solicitacoes.objects.create(
            estado_solicitacao='pendente',
            **solicitacao_data
        )

        # Criar pagamento com status padrão 'pendente'
        pagamento = Pagamentos.objects.create(
            estado_pagamento='pendente',
            **pagamento_data
        )

        # Criar coleta
        coleta = Coletas.objects.create(
            id_solicitacoes=solicitacao,
            id_pagamentos=pagamento,
            **validated_data
        )

        return coleta


class ColetasUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coletas
        fields = [
            'peso_material',
            'quantidade_material',
            'id_parceiros'
        ]

    def validate(self, data):
        # Validar que apenas peso OU quantidade foi fornecido
        peso = data.get('peso_material')
        quantidade = data.get('quantidade_material')
        
        if peso and quantidade:
            raise serializers.ValidationError(
                "Uma coleta deve ter apenas peso OU quantidade, não ambos."
            )
            
        return data


class ColetasRetrieveSerializer(serializers.ModelSerializer):
    imagens_coletas = ImagemColetaSerializer(many=True, read_only=True)
    cliente_nome = serializers.SerializerMethodField()
    cliente_id = serializers.SerializerMethodField()
    parceiro_nome = serializers.SerializerMethodField()
    parceiro_id = serializers.SerializerMethodField()
    material_nome = serializers.SerializerMethodField()
    endereco_completo = serializers.SerializerMethodField()
    valor_pagamento = serializers.SerializerMethodField()
    status_pagamento = serializers.SerializerMethodField()
    status_solicitacao = serializers.SerializerMethodField()
    observacoes_solicitacao = serializers.SerializerMethodField()

    class Meta:
        model = Coletas
        fields = [
            'id',
            'cliente_id',
            'cliente_nome',
            'parceiro_id',
            'parceiro_nome',
            'material_nome',
            'peso_material',
            'quantidade_material',
            'endereco_completo',
            'status_solicitacao',
            'observacoes_solicitacao',
            'status_pagamento',
            'valor_pagamento',
            'criado_em',
            'atualizado_em',
            'imagens_coletas'
        ]

    def get_cliente_nome(self, obj):
        if obj.id_clientes and obj.id_clientes.id_usuarios:
            return obj.id_clientes.id_usuarios.nome
        return None

    def get_cliente_id(self, obj):
        if obj.id_clientes and obj.id_clientes.id_usuarios:
            return obj.id_clientes.id_usuarios.id
        return None

    def get_parceiro_nome(self, obj):
        if obj.id_parceiros and obj.id_parceiros.id_usuarios:
            return obj.id_parceiros.id_usuarios.nome
        return None

    def get_parceiro_id(self, obj):
        if obj.id_parceiros and obj.id_parceiros.id_usuarios:
            return obj.id_parceiros.id_usuarios.id
        return None

    def get_material_nome(self, obj):
        if obj.id_materiais:
            return obj.id_materiais.nome
        return None

    def get_endereco_completo(self, obj):
        if obj.id_enderecos:
            endereco = obj.id_enderecos
            partes = [
                endereco.rua,
                str(endereco.numero),
                endereco.bairro,
                endereco.cidade
            ]
            partes = [p for p in partes if p]
            endereco_str = ", ".join(partes)
            if endereco.complemento:
                endereco_str += f" - " + endereco.complemento
            return endereco_str
        return None

    def get_valor_pagamento(self, obj):
        if obj.id_pagamentos:
            return obj.id_pagamentos.valor_pagamento
        return None

    def get_status_pagamento(self, obj):
        if obj.id_pagamentos:
            return obj.id_pagamentos.get_estado_pagamento_display()
        return None

    def get_status_solicitacao(self, obj):
        if obj.id_solicitacoes:
            return obj.id_solicitacoes.get_estado_solicitacao_display()
        return None

    def get_observacoes_solicitacao(self, obj):
        if obj.id_solicitacoes:
            return obj.id_solicitacoes.observacoes
        return None


# Serializer para listagem de coletas pendentes para parceiros
class ColetasPendentesParceiroSerializer(serializers.ModelSerializer):
    cliente_nome = serializers.SerializerMethodField()
    material_nome = serializers.SerializerMethodField()
    endereco_completo = serializers.SerializerMethodField()
    valor_pagamento = serializers.SerializerMethodField()

    class Meta:
        model = Coletas
        fields = [
            'id',
            'cliente_nome',
            'material_nome',
            'peso_material',
            'quantidade_material',
            'endereco_completo',
            'valor_pagamento',
            'criado_em'
        ]

    def get_cliente_nome(self, obj):
        return obj.id_clientes.id_usuarios.nome if obj.id_clientes and obj.id_clientes.id_usuarios else None

    def get_material_nome(self, obj):
        return obj.id_materiais.nome if obj.id_materiais else None

    def get_endereco_completo(self, obj):
        if obj.id_enderecos:
            endereco = obj.id_enderecos
            return f"{endereco.rua}, {endereco.numero}, {endereco.bairro}, {endereco.cidade}"
        return None

    def get_valor_pagamento(self, obj):
        return obj.id_pagamentos.valor_pagamento if obj.id_pagamentos else None


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
        ]


class PontosColetaCreateSerializer(ModelSerializer):
    materiais = PrimaryKeyRelatedField(
        queryset=Materiais.objects.all(),
        many=True,
        required=True,
        write_only=True
    )

    class Meta:
        model = PontosColeta
        fields = [
            'id',
            'nome',
            'id_enderecos',
            'descricao',
            'horario_funcionamento',
            'id_parceiros',
            'materiais',
        ]
        extra_kwargs = {
            'id_enderecos': {'required': True},
            'id_parceiros': {'required': False, 'allow_null': True}
        }

    def create(self, validated_data):
        materiais_data = validated_data.pop('materiais', [])
        ponto_coleta = PontosColeta.objects.create(**validated_data)

        # Cria os relacionamentos com materiais
        for material in materiais_data:
            MateriaisPontosColeta.objects.create(
                id_materiais=material,
                id_pontos_coleta=ponto_coleta
            )

        return ponto_coleta


class PontosColetaUpdateSerializer(ModelSerializer):
    materiais = PrimaryKeyRelatedField(
        queryset=Materiais.objects.all(),
        many=True,
        required=False,
        write_only=True
    )
    nome = CharField(required=False)

    class Meta:
        model = PontosColeta
        fields = [
            'nome',
            'id_enderecos',
            'descricao',
            'horario_funcionamento',
            'id_parceiros',
            'materiais'
        ]
        extra_kwargs = {
            'id_enderecos': {'required': False},
            'id_parceiros': {'required': False},
            'descricao': {'required': False}
        }

    def update(self, instance, validated_data):
        materiais_data = validated_data.pop('materiais', None)

        # Atualiza os campos básicos
        instance = super().update(instance, validated_data)

        # Se materiais foram fornecidos, atualiza os relacionamentos
        if materiais_data is not None:
            # Remove relacionamentos existentes
            MateriaisPontosColeta.objects.filter(
                id_pontos_coleta=instance).delete()

            # Cria novos relacionamentos
            for material in materiais_data:
                MateriaisPontosColeta.objects.create(
                    id_materiais=material,
                    id_pontos_coleta=instance
                )

        return instance


class MateriaisSimplesSerializer(ModelSerializer):
    class Meta:
        model = Materiais
        fields = ['nome', 'descricao']


class MateriaisSimplesPCSerializer(ModelSerializer):
    class Meta:
        model = Materiais
        fields = ['nome', 'descricao']


class EnderecoSimplesPCSerializer(ModelSerializer):
    endereco_completo = serializers.SerializerMethodField()

    class Meta:
        model = Enderecos
        fields = ['endereco_completo', 'latitude', 'longitude']

    def get_endereco_completo(self, obj):
        partes = [
            obj.rua,
            str(obj.numero),
            obj.bairro,
            obj.cidade,
            obj.estado
        ]
        return ', '.join(filter(None, partes))


class PontosColetaRetrieveSerializer(ModelSerializer):
    materiais = MateriaisSerializer(many=True, read_only=True)
    id_parceiros = ParceiroComUsuarioCreateSerializer()
    # telefone_parceiro = serializers.SerializerMethodField()

    class Meta:
        model = PontosColeta
        fields = [
            'id',
            'nome',
            'id_enderecos',
            'descricao',
            'horario_funcionamento',
            'id_parceiros',
            # 'telefone_parceiro',
            'materiais'
        ]
        depth = 1

    def get_id_parceiros(self, obj):
        #  Método customizado para serializar o parceiro sem materiais
        return {
            'id': obj.id_parceiros.id,
            'cnpj': obj.id_parceiros.cnpj,
            'id_usuarios': obj.id_parceiros.id_usuarios,
        }

    # def get_telefone_parceiro(self, obj):
    #     if obj.id_parceiros and obj.id_parceiros.id_usuarios:
    #         try:
    #             telefone = obj.id_parceiros.id_usuarios.telefones
    #             return telefone.numero
    #         except Telefones.DoesNotExist:
    #             return None
    #     return None


class SolicitacoesSerializer(ModelSerializer):
    class Meta:
        model = Solicitacoes
        fields = [
            'id',
            'estado_solicitacao',
            'observacoes',
            'finalizado_em',
        ]


class TelefonesSerializer(ModelSerializer):
    """Serializer antigo - mantido para compatibilidade"""
    class Meta:
        model = Telefones
        fields = [
            'id_usuarios',
            'numero',
        ]


class ImagemPerfilCreateSerializer(serializers.ModelSerializer):
    imagem = serializers.ImageField(write_only=True)

    class Meta:
        model = ImagemPerfil
        fields = ['id_usuarios', 'imagem']

    def create(self, validated_data):
        usuario = validated_data['id_usuarios']
        imagem = validated_data['imagem']

        # Verifica se já existe imagem para o usuário
        try:
            imagem_existente = ImagemPerfil.objects.get(id_usuarios=usuario)
            # Deleta a imagem existente se houver
            imagekit_service.delete_image(imagem_existente.file_id)
            imagem_existente.delete()
        except ImagemPerfil.DoesNotExist:
            pass

        # Faz o upload da nova imagem
        try:
            upload_response = imagekit_service.create_profile_image(
                imagem, usuario
            )

            # Cria o registro no banco de dados
            return ImagemPerfil.objects.create(
                id_usuarios=usuario,
                imagem=upload_response.url,
                file_id=upload_response.file_id
            )

        except Exception as e:
            raise serializers.ValidationError(
                f"Erro ao criar imagem de perfil: {str(e)}"
            )


class ImagemPerfilRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImagemPerfil
        fields = ['id_usuarios', 'imagem', 'file_id']
