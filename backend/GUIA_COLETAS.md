# Guia Completo do Sistema de Coletas - GreenCycle

## Visão Geral

Este guia documenta todas as funcionalidades do sistema de coletas, incluindo regras de negócio, endpoints disponíveis e exemplos de uso.

## Regras de Negócio Implementadas

### 1. Criação de Coleta
- **Obrigatório**: cliente, endereço, material, pagamento, solicitação
- **Validação**: Apenas peso OU quantidade por coleta (nunca ambos)
- **Status inicial**: Pagamento e Solicitação começam como "Pendente"

### 2. Estados do Sistema

#### Estados de Pagamento:
- `pendente` - Pagamento aguardando processamento
- `pago` - Pagamento realizado pelo parceiro
- `cancelado` - Pagamento cancelado

#### Estados de Solicitação:
- `pendente` - Aguardando aceite de parceiro
- `aceitado` - Aceito por um parceiro
- `cancelado` - Cancelado pelo cliente
- `coletado` - Coleta finalizada pelo parceiro

### 3. Fluxo de Aceite
- Parceiro só pode aceitar coletas pendentes
- Verificação se trabalha com o material
- Aceite único (não pode ser aceito por múltiplos parceiros)

### 4. Upload de Imagens
- Nome personalizado: `{tipo_usuario}_{nome}_coleta_{id}_{timestamp}`
- Tipos: cliente ou parceiro

## Endpoints Principais

### 1. Criar Coleta
```http
POST /v1/coletas/
```

**Exemplo de Request:**
```json
{
    "id_clientes": 1,
    "id_materiais": 1,
    "peso_material": "10.5000",
    "id_enderecos": 1,
    "dados_solicitacao": {
        "observacoes": "Material na garagem",
        "latitude": "-29.1683",
        "longitude": "-51.1796"
    },
    "dados_pagamento": {
        "valor_pagamento": "50.00",
        "saldo_pagamento": "0.00"
    }
}
```

**Response:**
```json
{
    "id": 1,
    "cliente_id": 1,
    "cliente_nome": "João Silva",
    "parceiro_nome": null,
    "material_nome": "Plástico",
    "peso_material": "10.5000",
    "quantidade_material": null,
    "endereco_completo": "Rua das Flores, 123, Centro, Caxias do Sul",
    "status_solicitacao": "Pendente",
    "observacoes_solicitacao": "Material na garagem",
    "status_pagamento": "Pendente",
    "valor_pagamento": "50.00",
    "criado_em": "2024-01-15T10:30:00Z",
    "atualizado_em": "2024-01-15T10:30:00Z",
    "imagens_coletas": []
}
```

### 2. Consultas Específicas

#### 2.1 Coletas Pendentes para Parceiro
```http
GET /v1/coletas/pendentes-parceiro/{parceiro_id}/
```

Lista coletas pendentes que o parceiro pode aceitar (baseado nos materiais que trabalha).

**Response:**
```json
[
    {
        "id": 1,
        "cliente_nome": "João Silva",
        "material_nome": "Plástico",
        "peso_material": "10.5000",
        "quantidade_material": null,
        "endereco_completo": "Rua das Flores, 123, Centro, Caxias do Sul",
        "valor_pagamento": "50.00",
        "distancia_km": null,
        "criado_em": "2024-01-15T10:30:00Z"
    }
]
```

#### 2.2 Coletas do Parceiro
```http
GET /v1/coletas/minhas-coletas-parceiro/{parceiro_id}/
```

Lista todas as coletas que o parceiro já aceitou.

#### 2.3 Coletas do Cliente
```http
GET /v1/coletas/minhas-coletas-cliente/{cliente_id}/
```

Lista todas as coletas criadas pelo cliente.

### 3. Ações da Coleta

#### 3.1 Aceitar Coleta
```http
POST /v1/coletas/{coleta_id}/aceitar-coleta/
```

**Request:**
```json
{
    "parceiro_id": 1
}
```

**Validações:**
- Coleta deve estar com status "pendente"
- Parceiro deve trabalhar com o material
- Coleta não pode ter sido aceita por outro parceiro

**Response:**
```json
{
    "message": "Coleta aceita com sucesso"
}
```

#### 3.2 Finalizar Coleta
```http
POST /v1/coletas/{coleta_id}/finalizar-coleta/
```

**Efeitos:**
- Status da solicitação → "coletado"
- Status do pagamento → "pago"
- Define `finalizado_em`

#### 3.3 Cancelar Coleta
```http
POST /v1/coletas/{coleta_id}/cancelar-coleta/
```

**Efeitos:**
- Status da solicitação → "cancelado"
- Status do pagamento → "cancelado"

#### 3.4 Upload de Imagem
```http
POST /v1/coletas/{coleta_id}/upload-imagem/
```

**Request (multipart/form-data):**
```
imagem: [arquivo]
tipo_usuario: "cliente" ou "parceiro"
```

**Response:**
```json
{
    "message": "Imagem adicionada com sucesso",
    "nome_arquivo": "cliente_JoaoSilva_coleta_1_20240115_103000.jpg"
}
```

### 4. Buscar Endereço por CEP
```http
POST /v1/enderecos/buscar-cep/
```

**Request:**
```json
{
    "cep": "95020360"
}
```

**Response:**
```json
{
    "cep": "95020360",
    "estado": "RS",
    "cidade": "Caxias do Sul",
    "bairro": "Centro",
    "rua": "Rua Coronel Flores"
}
```

## Filtros Disponíveis

### Coletas com Filtros
```http
GET /v1/coletas/?id_cliente={id}&id_parceiro={id}&status_solicitacao={status}
```

**Parâmetros:**
- `id_cliente`: Filtra por cliente específico
- `id_parceiro`: Filtra por parceiro específico  
- `status_solicitacao`: Filtra por status (pendente, aceitado, cancelado, coletado)

## Exemplos de Fluxo Completo

### Fluxo 1: Cliente cria coleta e parceiro aceita

1. **Cliente cria coleta:**
```bash
curl -X POST http://localhost:8000/v1/coletas/ \
  -H "Content-Type: application/json" \
  -d '{
    "id_clientes": 1,
    "id_materiais": 1,
    "peso_material": "10.5000",
    "id_enderecos": 1,
    "dados_solicitacao": {
        "observacoes": "Material na garagem",
        "latitude": "-29.1683",
        "longitude": "-51.1796"
    },
    "dados_pagamento": {
        "valor_pagamento": "50.00"
    }
  }'
```

2. **Parceiro consulta coletas disponíveis:**
```bash
curl http://localhost:8000/v1/coletas/pendentes-parceiro/1/
```

3. **Parceiro aceita coleta:**
```bash
curl -X POST http://localhost:8000/v1/coletas/1/aceitar-coleta/ \
  -H "Content-Type: application/json" \
  -d '{"parceiro_id": 1}'
```

4. **Cliente adiciona imagem:**
```bash
curl -X POST http://localhost:8000/v1/coletas/1/upload-imagem/ \
  -F "imagem=@foto_material.jpg" \
  -F "tipo_usuario=cliente"
```

5. **Parceiro finaliza coleta:**
```bash
curl -X POST http://localhost:8000/v1/coletas/1/finalizar-coleta/
```

### Fluxo 2: Cliente cancela coleta

```bash
curl -X POST http://localhost:8000/v1/coletas/1/cancelar-coleta/
```

## Validações e Erros

### Erros Comuns:

1. **Peso e quantidade juntos:**
```json
{
    "non_field_errors": ["Uma coleta deve ter apenas peso OU quantidade, não ambos."]
}
```

2. **Aceitar coleta já aceita:**
```json
{
    "error": "Esta coleta já foi aceita por outro parceiro"
}
```

3. **Material incompatível:**
```json
{
    "error": "Você não trabalha com este tipo de material"
}
```

4. **Status inválido para ação:**
```json
{
    "error": "Esta coleta não pode ser finalizada"
}
```

## Considerações Técnicas

### Performance
- Queries otimizadas com `select_related` e `prefetch_related`
- Cache implementado para listagens de usuários

### Segurança
- Validações de negócio implementadas
- Transações atômicas para operações críticas
- Verificações de permissão para ações

### Extensibilidade
- Sistema preparado para cálculo de distâncias
- Estrutura flexível para novos tipos de material
- Support para múltiplos endereços por usuário (futuro)

## Próximos Passos

1. Implementar cálculo de distância para parceiros
2. Sistema de notificações
3. Relatórios e métricas
4. API de pagamentos integrada
5. Sistema de avaliações pós-coleta 