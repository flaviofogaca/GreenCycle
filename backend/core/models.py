from django.db import models

# Criado classe Base para que os campos que são iguais em outras
# tabelas sejam replicadas de uma forma mais inteligente,
# sem repetição de códigos


class Base(models.Model):
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


# class UsuarioManager(BaseUserManager):
#     def create_user(self, nome, email, senha, **extra_fields):
#         if not email:
#             raise ValueError('O email é obrigatório')

#         email = self.normalize_email(email)
#         user = self.model(
#             nome=nome,
#             email=email,
#             **extra_fields
#         )
#         user.set_password(senha)
#         user.save(using=self._db)
#         return user


# Modificar a classe Usuarios para herdar de AbstractBaseUser
# class Usuarios(AbstractBaseUser):
class Usuarios(Base):
    id = models.SmallAutoField(primary_key=True)
    nome = models.CharField(max_length=100)
    usuario = models.CharField(max_length=100, unique=True)
    email = models.CharField(max_length=100, blank=True, null=True)
    senha = models.TextField()  # futuro usar django.contrib.auth.hashers
    id_endereco = models.ForeignKey(
        'Enderecos',
        models.DO_NOTHING,
        db_column='id_endereco',
        blank=True,
        null=True
    )

    # Campos necessários para o auth
    # PASSWORD_FIELD = 'senha'
    # USERNAME_FIELD = 'email'
    # REQUIRED_FIELDS = ['nome']

    # objects = UsuarioManager()

    class Meta:
        managed = False
        db_table = 'usuarios'


class Clientes(Base):
    id = models.SmallAutoField(primary_key=True)
    id_usuarios = models.ForeignKey(
        'Usuarios',
        models.DO_NOTHING,
        db_column='id_usuarios',
        blank=True,
        null=True
    )
    cpf = models.CharField(unique=True, max_length=15)
    data_nascimento = models.DateField()
    sexo = models.CharField(max_length=1)

    class Meta:
        managed = False
        db_table = 'clientes'


class Parceiros(Base):
    id = models.SmallAutoField(primary_key=True)
    id_usuarios = models.OneToOneField(
        'Usuarios', models.DO_NOTHING, db_column='id_usuarios')
    cnpj = models.CharField(unique=True, max_length=20)

    materiais = models.ManyToManyField(
        'Materiais',
        through='MateriaisParceiros',
        related_name='parceiros'
    )

    class Meta:
        managed = False
        db_table = 'parceiros'


class Avaliacoes(Base):
    id = models.SmallAutoField(primary_key=True)
    id_parceiros = models.ForeignKey(
        'Parceiros', models.DO_NOTHING, db_column='id_parceiros')
    id_clientes = models.ForeignKey(
        'Clientes', models.DO_NOTHING, db_column='id_clientes')
    id_coletas = models.OneToOneField(
        'Coletas', models.CASCADE, db_column='id_coletas',
        unique=True, related_name='avaliacao')
    nota_parceiros = models.SmallIntegerField()
    descricao_parceiros = models.CharField(
        max_length=300, blank=True, null=True)
    nota_clientes = models.SmallIntegerField()
    descricao_clientes = models.CharField(
        max_length=300, blank=True, null=True
    )

    class Meta:
        managed = False
        db_table = 'avaliacoes'


class ImagemColetas(Base):
    id = models.SmallAutoField(primary_key=True)
    imagem = models.CharField(max_length=100, verbose_name="Imagem")
    id_coletas = models.ForeignKey(
        'Coletas', 
        related_name='imagens_coletas',
        on_delete=models.CASCADE, 
        db_column='id_coletas',
        verbose_name="Coleta"
    )

    class Meta:
        managed = False
        db_table = 'imagens_coleta'
        verbose_name = "Imagem da Coleta"
        verbose_name_plural = "Imagens da Coleta"


class Coletas(Base):
    id = models.SmallAutoField(primary_key=True)
    id_clientes = models.ForeignKey(
        Clientes, models.DO_NOTHING, db_column='id_clientes')
    id_parceiros = models.ForeignKey(
        'Parceiros', models.DO_NOTHING, db_column='id_parceiros',
        blank=True, null=True)
    id_materiais = models.ForeignKey(
        'Materiais', models.DO_NOTHING, db_column='id_materiais')
    peso_material = models.DecimalField(
        max_digits=15, decimal_places=4, blank=True, null=True)
    quantidade_material = models.SmallIntegerField(blank=True, null=True)
    id_enderecos = models.ForeignKey(
        'Enderecos', models.DO_NOTHING, db_column='id_enderecos')
    id_solicitacoes = models.ForeignKey(
        'Solicitacoes', models.DO_NOTHING, db_column='id_solicitacoes')
    id_pagamentos = models.ForeignKey(
        'Pagamentos', models.DO_NOTHING, db_column='id_pagamentos')

    def clean(self):
        from django.core.exceptions import ValidationError

        # Validar que só pode ter peso OU quantidade, não ambos
        if self.peso_material and self.quantidade_material:
            raise ValidationError("Uma coleta deve ter apenas peso OU quantidade, não ambos.")
        if not self.peso_material and not self.quantidade_material:
            raise ValidationError("Uma coleta deve ter peso OU quantidade.")

    class Meta:
        managed = False
        db_table = 'coletas'


class Enderecos(Base):
    id = models.SmallAutoField(primary_key=True)
    cep = models.CharField(max_length=15)
    estado = models.CharField(max_length=50)
    cidade = models.CharField(max_length=50)
    bairro = models.CharField(max_length=50)
    rua = models.CharField(max_length=50)
    numero = models.SmallIntegerField()
    complemento = models.CharField(max_length=100, blank=True, null=True)
    latitude = models.FloatField()
    longitude = models.FloatField()

    class Meta:
        managed = False
        db_table = 'enderecos'


class Materiais(Base):
    id = models.SmallAutoField(primary_key=True)
    nome = models.CharField(unique=True, max_length=50)
    descricao = models.CharField(max_length=150, blank=True, null=True)
    preco = models.TextField()  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'materiais'


class MateriaisParceiros(models.Model):
    # The composite primary key (id_materiais, id_parceiros)
    # found, that is not supported. The first column is selected.
    id_materiais = models.OneToOneField(
        Materiais, models.DO_NOTHING, db_column='id_materiais',
        primary_key=True)
    id_parceiros = models.ForeignKey(
        'Parceiros', models.DO_NOTHING, db_column='id_parceiros')

    class Meta:
        managed = False
        db_table = 'materiais_parceiros'
        unique_together = (('id_materiais', 'id_parceiros'),)


class Pagamentos(Base):
    ESTADOS_PAGAMENTO = [
        ('pendente', 'Pendente'),
        ('pago', 'Pago'),
        ('cancelado', 'Cancelado'),
    ]
    
    id = models.SmallAutoField(primary_key=True)
    valor_pagamento = models.TextField()  # This field type is a guess.
    saldo_pagamento = models.TextField()  # This field type is a guess.
    estado_pagamento = models.CharField(
        max_length=10, 
        choices=ESTADOS_PAGAMENTO,
        default='pendente'
    )

    class Meta:
        managed = False
        db_table = 'pagamentos'


class PontosColeta(Base):
    id = models.SmallAutoField(primary_key=True)
    nome = models.CharField(max_length=100)
    id_enderecos = models.ForeignKey(
        Enderecos,
        models.DO_NOTHING,
        db_column='id_enderecos'
    )
    id_parceiros = models.ForeignKey(
        Parceiros,
        models.DO_NOTHING,
        db_column='id_parceiros'
    )
    materiais = models.ManyToManyField(
        'Materiais',
        through='MateriaisPontosColeta',
        related_name='pontos_de_coleta'
    )
    descricao = models.CharField(max_length=200, blank=True, null=True)
    horario_funcionamento = models.CharField(
        max_length=200,
        blank=True,
        null=True
    )

    class Meta:
        managed = False
        db_table = 'pontos_coleta'


class Solicitacoes(Base):
    ESTADOS_SOLICITACAO = [
        ('pendente', 'Pendente'),
        ('aceitado', 'Aceitado'),
        ('cancelado', 'Cancelado'),
        ('coletado', 'Coletado'),
        ('finalizado', 'Finalizado'),
    ]
    
    id = models.SmallAutoField(primary_key=True)
    estado_solicitacao = models.CharField(
        max_length=10,
        choices=ESTADOS_SOLICITACAO,
        default='pendente'
    )
    observacoes = models.CharField(max_length=100, blank=True, null=True)
    finalizado_em = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'solicitacoes'


class Telefones(Base):
    id_usuarios = models.OneToOneField(
        'Usuarios', models.DO_NOTHING,
        db_column='id_usuarios', primary_key=True)
    numero = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'telefones'


class MateriaisPontosColeta(models.Model):
    id_materiais = models.OneToOneField(
        'Materiais',
        models.DO_NOTHING,
        db_column='id_materiais',
        primary_key=True  # Indica que este é parte da chave primária
    )
    id_pontos_coleta = models.ForeignKey(
        'PontosColeta',
        models.DO_NOTHING,
        db_column='id_pontos_coleta'
    )

    class Meta:
        managed = False
        db_table = 'materiais_pontos_coleta'
        unique_together = (('id_materiais', 'id_pontos_coleta'),)
        auto_created = True


class ImagemPerfil(Base):
    id = models.SmallAutoField(primary_key=True)
    id_usuarios = models.OneToOneField(
        'Usuarios',
        models.DO_NOTHING,
        db_column='id_usuarios'
    )
    imagem = models.TextField()  # URL da imagem no ImageKit
    file_id = models.CharField(max_length=100)  # ID do arquivo no ImageKit

    class Meta:
        managed = False
        db_table = 'imagem_perfil'
