# RoadFixerAPI

## Instalação

Este documento descreve a API inicial para gerenciamento da interface do RoadFixer.
De forma geral, consideramos alguns módulos no desenvolvimento da API, os quais estão referenciados no ```requirements.txt``` da base da pasta ```RoadFixerAPI```.

Todos eles podem ser instalados usando ```pip install -r requirements.txt```.

## Uso

Para usar a API, devemos usar o comando ```uvicorn API.main:server --reload --host 0.0.0.0 --port 8000```.

Isso configura a API para auto-recarregar toda vez que fizermos uma alteração, ir para o primeiro IP possível de host e usar a porta 8000.

Podemos acessar os dados a partir do GET abaixo.

```http
GET http://<seu-ip>/<rota>
```

O recomendável é usar uma biblioteca como Axios para consumir a API na interface Web.