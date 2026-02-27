# Leads API

API para gerenciamento de Leads, construída com Python, FastAPI e MongoDB.
Durante o cadastro, a API consulta um serviço externo para obter e salvar a data de nascimento (`birth_date`).

## Requisitos
- Docker
- Docker Compose

## Como rodar o projeto

1. Clone o repositório ou navegue até a pasta do projeto.
2. Crie o arquivo `.env` a partir do exemplo:
   ```bash
   cp .env-example .env
   ```
3. Construa e inicie os containers com o comando:
   ```bash
   docker-compose up -d --build
   ```
   ou
   ```bash
   docker compose up -d --build
   ```
4. (Opcional) Execute os testes automatizados para garantir que tudo está ok:
   ```bash
   docker exec teste-api-1 pytest
   ```
   A API estará disponível em `http://localhost:8000`. O MongoDB estará rodando nativamente na porta `27017` via Docker.

## Como testar manualmente os endpoints

Você pode usar o Swagger UI gerado automaticamente pelo FastAPI para testar os endpoints:
Acesse **http://localhost:8000/docs** no seu navegador.

Lá você encontrará os seguintes endpoints:
- `POST /leads`: Cria um novo lead. (Requer `name`, `email` e `phone`).
- `GET /leads`: Retorna todos os leads cadastrados.
- `GET /leads/{id}`: Retorna os detalhes de um lead específico.

Também é possível usar o `curl`:

**Criar Lead:**
```bash
curl -X 'POST' \
  'http://localhost:8000/leads/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "name": "João Silva",
  "email": "joao@email.com",
  "phone": "+5511999999999"
}'
```

**Exemplo de Resposta (Sucesso):**
```json
{
  "status": "Ok",
  "data": {
    "name": "João Silva",
    "email": "joao@email.com",
    "phone": "+5511999999999",
    "birth_date": "1996-5-30",
    "id": "69a0e89826eb59355579bf9c"
  }
}
```

**Listar Leads (Com Paginação):**
```bash
curl -X 'GET' \
  'http://localhost:8000/leads/?page=1&per_page=10' \
  -H 'accept: application/json'
```

**Exemplo de Resposta (Sucesso):**
```json
{
  "status": "Ok",
  "data": [
    {
      "name": "João Silva",
      "email": "joao@email.com",
      "phone": "+5511999999999",
      "birth_date": "1996-5-30",
      "id": "69a0e89826eb59355579bf9c"
    }
  ]
}
```

**Obter Detalhes de um Lead Específico:**
Substitua `{OBJECT_ID}` pelo id retornado na criação ou listagem:
```bash
curl -X 'GET' \
  'http://localhost:8000/leads/{OBJECT_ID}' \
  -H 'accept: application/json'
```

**Exemplo de Resposta (Sucesso):**
```json
{
  "status": "Ok",
  "data": {
    "name": "João Silva",
    "email": "joao@email.com",
    "phone": "+5511999999999",
    "birth_date": "1996-5-30",
    "id": "69a0e89826eb59355579bf9c"
  }
}
```

**Exemplo de Respostas de Erro (Padronizadas):**

*Erro de Validação (ex: telefone inválido):*
```json
{
  "status": "Error",
  "data": "The phone number should be in format like (ex: +5511999999999)"
}
```

*Erro de Regra de Negócio (ex: e-mail duplicado):*
```json
{
  "status": "Error",
  "data": "Lead with this email already exists"
}
```

## Arquitetura Adotada

A aplicação segue uma arquitetura baseada em Clean Architecture e responsabilidades bem definidas, visando baixo acoplamento:
- **`app/main.py`**: Ponto de entrada, configuração do FastAPI e ciclo de vida do banco (Lifespan).
- **`app/core/`**: Configurações globais e variáveis de ambiente (pydantic-settings).
- **`app/db/`**: Gerenciamento de conexão com o MongoDB.
- **`app/models/`**: Camada de Domínio. Contém os modelos de dados da aplicação (`LeadModel`) e a lógica de validação principal (ex: Regex de telefone) que deve ser respeitada em todo o sistema.
- **`app/schemas/`**: Camada de Contratos (DTOs). Define como os dados entram (`LeadCreate`) e saem (`LeadResponse`) da API, além de gerenciar os envelopes de resposta padronizados.
- **`app/clients/`**: Camada de Integrações Externas. Contém os clientes para comunicação com APIs de terceiros (`external_api.py`).
- **`app/services/`**: Camada de Regras de Negócio (Serviços Internos). Contém a lógica de orquestração do sistema (`lead_service.py`).
- **`app/api/endpoints/`**: Controladores de rota do FastAPI. Apenas recebem a requisição e chamam o service correspondente.

## Como rodar os testes

Os testes automatizados foram implementados com `pytest` e rodam dentro do container da API para garantir que todas as dependências estejam presentes.

Para rodar a suíte de testes completa:
```bash
docker exec teste-api-1 pytest
```

Os testes utilizam o `mongomock-motor` para simular o banco de dados em memória, garantindo que os testes sejam rápidos e não afetem os dados reais do MongoDB.

## Comportamento em caso de falha da API Externa

Se a integração com a API externa (que busca o `birthDate` na URL configurada) falhar (por exemplo, timeout ou serviço fora do ar), o sistema foi projetado para **não interromper o cadastro do Lead**. 
O erro é silenciado (registrado internamente apenas via logs) e a propriedade `birth_date` é persistida no documento como `null` no MongoDB e refletida da mesma forma na resposta JSON.

### Como testar este cenário no Docker:

1. Abra o arquivo `.env` na raiz do projeto.
2. Altere a variável `EXTERNAL_API_URL` para uma URL inválida, por exemplo:
   ```env
   EXTERNAL_API_URL=https://dummyjson.error.com/users/1
   ```
3. Para que a alteração no `.env` seja aplicada ao container, você deve recriar o container com:
   ```bash
   docker-compose up -d
   ```
4. Realize uma nova requisição `POST /leads`. Você verá que o lead será criado com sucesso, mas o campo `birth_date` retornará como `null`.
5. Verifique os logs do container para ver o erro registrado:
   ```bash
   docker logs teste-api-1
   ```
6. Após o teste, restaure a URL original no `.env` e aplique novamente:
   ```bash
   docker-compose up -d
   ```
