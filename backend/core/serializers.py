from rest_framework.serializers import (
    ModelSerializer, CharField, PrimaryKeyRelatedField, DateField, Serializer,
    ValidationError
)
from .models import (
    Avaliacoes, Clientes, Coletas, Enderecos,
    Materiais, MateriaisParceiros, MateriaisPontosColeta, Pagamentos,
    Parceiros, PontosColeta, Solicitacoes, Telefones, Usuarios
)
from django.core.validators import MinLengthValidator
from .mixins import (
    ValidacaoCFPMixin,
    ValidacaoCNPJMixin,
    ValidacaoCEPMixin
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
            'criado_em',
            'atualizado_em',
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
            'criado_em',        # Campo do cliente / usuário
            'atualizado_em',    # Campo do cliente / usuário
            'nome',             # Campo do usuário
            'email',            # Campo do usuário
            'senha',            # Campo do usuário
            'id_endereco'       # Campo do usuário
        ]
        read_only_fields = [
            'id',
            'id_usuarios',
            'criado_em',
            'atualizado_em'
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
            'criado_em',      # Campo do parceiro / usuário
            'atualizado_em',  # Campo do parceiro / usuário
            'nome',           # Campo do usuário
            'email',          # Campo do usuário
            'senha',          # Campo do usuário
            'id_endereco',    # Campo do usuário
            'materiais'       # Campo de materiais
        ]
        read_only_fields = [
            'id',
            'id_usuarios',
            'criado_em',
            'atualizado_em'
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


class EnderecoCreateSerializer(ModelSerializer, ValidacaoCEPMixin):
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
            'criado_em',
            'atualizado_em'
        ]
        read_only_fields = [
            'id',
            'criado_em',
            'atualizado_em'
        ]

    def validate_cep(self, value):
        return self.validar_cep(value)


class EnderecoUpdateSerializer(ModelSerializer):
    class Meta:
        model = Enderecos
        fields = [
            'numero',
            'complemento'
        ]


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
            'criado_em',
            'atualizado_em'
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
            'criado_em',
            'atualizado_em',
        ]


class ColetasSerializer(ModelSerializer):
    class Meta:
        model = Coletas
        fields = [
            'id',
            'id_clientes',
            'id_parceiros',
            'id_materiais',
            'peso_material',
            'quantidade_material',
            'id_enderecos',
            'id_solicitacoes',
            'id_pagamentos',
            'images',  # Adicionado coluna Images
            'criado_em',
            'atualizado_em',
        ]


class MateriaisSerializer(ModelSerializer):
    class Meta:
        model = Materiais
        fields = [
            'id',
            'nome',
            'descricao',
            'preco',
            'criado_em',
            'atualizado_em',
        ]


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
            'criado_em',
            'atualizado_em',
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
            'criado_em',
            'atualizado_em'
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
            'criado_em',
            'atualizado_em'
        ]
        depth = 1

    # def get_materiais(self, obj):
    #     relacionamentos = obj.materiaispontoscoleta_set.all()
    #     materiais = [rel.id_materiais for rel in relacionamentos]
    #     return MateriaisSerializer(materiais, many=True).data


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
            'criado_em',
            'atualizado_em',
        ]


class TelefonesSerializer(ModelSerializer):
    class Meta:
        model = Telefones
        fields = [
            'id_usuarios',
            'numero',
            'criado_em',
            'atualizado_em',
        ]
