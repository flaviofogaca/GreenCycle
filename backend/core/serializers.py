from rest_framework import serializers
from rest_framework.serializers import (
    ModelSerializer, CharField, PrimaryKeyRelatedField, DateField, Serializer,
    ValidationError
)
from .models import (
    Avaliacoes, Clientes, Coletas, Enderecos,
    Materiais, MateriaisParceiros, MateriaisPontosColeta, Pagamentos,
    Parceiros, PontosColeta, Solicitacoes, Telefones, Usuarios, ImagemColetas
)
from django.core.validators import MinLengthValidator
from .mixins import (
    ValidacaoCFPMixin,
    ValidacaoCNPJMixin,
    ValidacaoCEPMixin,
    GeocodingMixin
)
import requests
# from django.contrib.auth.hashers import make_password

# Lembrar disso para os serializers
# CRUD (create, retrieve, update, delete)


class UsuarioCreateSerializer(ModelSerializer):
    senha = CharField(
        # write_only=True,
        required=True,
        validators=[MinLengthValidator(8)],
        style={'input_type': 'password'}
    )

    class Meta:
        model = Usuarios
        fields = [
            'id',
            'usuario',
            'nome',
            'email',
            'senha',
            'id_endereco',
        ]
        extra_kwargs = {
            'senha': {'write_only': True},
            'email': {'required': True}
        }

    def create(self, validated_data):
        # Criptografa a senha antes de salvar
        # validated_data['senha'] = make_password(validated_data['senha'])

        usuario = Usuarios(**validated_data)
        usuario.save()
        return usuario


class UsuarioRetrieveSerializer(ModelSerializer):
    class Meta:
        model = Usuarios
        fields = [
            'id',
            'usuario',
            'nome',
            'senha',
            'email',
            'id_endereco'
        ]
        depth = 1


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
            'id_endereco'       # Campo do usuário
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
    id_usuarios = UsuarioCreateSerializer(read_only=True)

    class Meta:
        model = Clientes
        fields = [
            'id',
            'id_usuarios',
            'cpf',
            'data_nascimento',
            'sexo'
        ]
        depth = 0


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
        model = Clientes
        fields = [
            'nome',
            'usuario',
            'email',
            'senha',
            'id_endereco',
            'cnpj',
            'materiais'
        ]

    def validate_cnpj(self, value):
        if value:
            return self.validar_cnpj(value)
        return value

    def update(self, instance, validated_data):
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

        # Atualiza dados do cliente
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
    id_usuarios = UsuarioCreateSerializer(read_only=True)
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
        ]


class ImagemColetaSerializer(ModelSerializer):
    class Meta:
        model = ImagemColetas
        fields = ['id', 'imagem', 'criado_em']


class ColetasRetrieveSerializer(serializers.ModelSerializer):
    imagens_coletas = ImagemColetaSerializer(many=True, read_only=True)
    
    cliente_nome = serializers.SerializerMethodField()
    parceiro_nome = serializers.SerializerMethodField()
    material_nome = serializers.SerializerMethodField()
    endereco_completo = serializers.SerializerMethodField()
    valor_pagamento = serializers.SerializerMethodField()
    status_solicitacoes = serializers.SerializerMethodField()

    class Meta:
        model = Coletas
        fields = [
            'id',
            #'id_clientes',
            'cliente_nome',
            #'id_parceiros',
            'parceiro_nome',
           # 'id_materiais',
            'material_nome',
            'peso_material',
            'quantidade_material',
           # 'id_enderecos',
            'endereco_completo',
           # 'id_solicitacoes',
            'status_solicitacoes',
           # 'id_pagamentos',
            'valor_pagamento',
            'criado_em',
            'atualizado_em',
            'imagens_coletas'
        ]
        depth = 1

    def get_cliente_nome(self, obj):
        if obj.id_clientes and obj.id_clientes.id_usuarios:
            return obj.id_clientes.id_usuarios.nome
        return None

    def get_parceiro_nome(self, obj):
        if obj.id_parceiros and obj.id_parceiros.id_usuarios:
            return obj.id_parceiros.id_usuarios.nome
        return None

    def get_material_nome(self, obj):
        if obj.id_materiais:
            return obj.id_materiais.nome
        return None

    def get_valor_pagamento(self, obj):
        if obj.id_pagamentos:
            return obj.id_pagamentos.valor_pagamento
        return None

    def get_status_solicitacoes(self, obj):
        if obj.id_solicitacoes:
            return obj.id_solicitacoes.estado_solicitacao
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
                endereco_str += f" - {endereco.complemento}"
            return endereco_str
        return None

class SolicitacaoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Solicitacoes
        fields = ['estado_solicitacao', 'observacoes', 'latitude', 'longitude']
        extra_kwargs = {
            'estado_solicitacao': {'default': 'pendente'},
            'observacoes': {'required': False, 'allow_blank': True}
        }

class PagamentoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pagamentos
        fields = ['valor_pagamento', 'saldo_pagamento', 'estado_pagamento']
        extra_kwargs = {
            'valor_pagamento': {'required': False},
            'saldo_pagamento': {'default': 0},
            'estado_pagamento': {'default': 'pendente'}
        }

class EnderecoColetaSerializer(serializers.ModelSerializer, GeocodingMixin):
    class Meta:
        model = Enderecos
        fields = ['cep', 'estado', 'cidade', 'rua', 'bairro', 'numero', 'complemento']
        extra_kwargs = {
            'complemento': {'required': False, 'allow_blank': True}
        }

    def create(self, validated_data):
        endereco_completo = (
            f"{validated_data.get('rua')}, {validated_data.get('numero')}, "
            f"{validated_data.get('bairro')}, {validated_data.get('cidade')}, "
            f"{validated_data.get('estado')}, {validated_data.get('cep')}"
        )
        coordenadas = self.get_lat_lon(endereco_completo)
        if not coordenadas:
            # Coordenadas padrão se geocoding falhar vai pra praça dante Caxias do Sul
            coordenadas = (-29.1683344324061, -51.17962293682549)  

        validated_data['latitude'] = coordenadas[0]
        validated_data['longitude'] = coordenadas[1]
        return super().create(validated_data)
    
class ColetasCreateUpdateSerializer(serializers.ModelSerializer):
    imagens_upload = serializers.ListField(
        child=serializers.ImageField(max_length=100000, allow_empty_file=False, use_url=False),
        write_only=True,
        required=False
    )
    dados_solicitacao = SolicitacaoCreateSerializer(required=True, write_only=True, source='id_solicitacoes')
    dados_pagamento = PagamentoCreateSerializer(required=False, write_only=True, source='id_pagamentos')
    dados_endereco = EnderecoColetaSerializer(required=False, write_only=True, source='id_enderecos')
    
    class Meta:
        model = Coletas
        fields = [
            'id',
            'id_clientes',
            'id_parceiros',
            'id_materiais',
            'peso_material',
            'quantidade_material',
            'dados_endereco',  # Para criar novo endereço
            'id_enderecos',   # Para usar endereço existente
            'dados_solicitacao',
            'dados_pagamento',
            'imagens_upload'
        ]
        extra_kwargs = {
            'id_clientes': {'required': True},
            'id_materiais': {'required': True},
            'id_enderecos': {'required': False, 'allow_null': True}
        }

    def validate(self, data):
        if not data.get('dados_endereco') and not data.get('id_enderecos'):
            raise serializers.ValidationError(
                "Forneça um endereço existente (id_enderecos) ou os dados de um novo endereço (dados_endereco)"
            )
        if data.get('dados_endereco') and data.get('id_enderecos'):
            raise serializers.ValidationError(
                "Forneça apenas um endereço existente ou os dados de um novo endereço, não ambos"
            )
        return data

    def create(self, validated_data):
        solicitacao_data = validated_data.pop('id_solicitacoes')
        pagamento_data = validated_data.pop('id_pagamentos', None)
        endereco_data = validated_data.pop('id_enderecos', None)
        imagens_data = validated_data.pop('imagens_upload', [])
        
        if isinstance(endereco_data, dict):
            endereco_serializer = EnderecoColetaSerializer(data=endereco_data)
            endereco_serializer.is_valid(raise_exception=True)
            endereco = endereco_serializer.save()
            validated_data['id_enderecos'] = endereco
        
        solicitacao = Solicitacoes.objects.create(**solicitacao_data)
        
        if pagamento_data:
            pagamento = Pagamentos.objects.create(**pagamento_data)
            validated_data['id_pagamentos'] = pagamento
        
        coleta = Coletas.objects.create(
            id_solicitacoes=solicitacao,
            **validated_data
        )

        for imagem in imagens_data:
            ImagemColetas.objects.create(coleta=coleta, imagem=imagem)

        return coleta

    def to_representation(self, instance):
        return ColetasRetrieveSerializer(instance, context=self.context).data

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


class PontosColetaRetrieveSerializer(ModelSerializer):
    materiais = MateriaisSerializer(many=True, read_only=True)
    id_parceiros = ParceiroComUsuarioCreateSerializer()

    class Meta:
        model = PontosColeta
        fields = [
            'id',
            'nome',
            'id_enderecos',
            'descricao',
            'horario_funcionamento',
            'id_parceiros',
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
        ]


class TelefonesSerializer(ModelSerializer):
    class Meta:
        model = Telefones
        fields = [
            'id_usuarios',
            'numero',
        ]
