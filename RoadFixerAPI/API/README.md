# RoadFixerAPI

## Instalação

Este documento descreve a API inicial para gerenciamento da interface do RoadFixer.
De forma geral, consideramos alguns módulos no desenvolvimento da API, sendo eles:

```text
fastapi[standard]
osmnx
folium
pandas
```

Todos eles podem ser instalados usando o comando ```pip install <módulo>```.

## Uso

Para usar a API, devemos usar o comando ```uvicorn API.main:server --reload --host 0.0.0.0 --port 8000```.

Isso configura a API para auto-recarregar toda vez que fizermos uma alteração, ir para o primeiro IP possível de host e usar a porta 8000.

Podemos acessar os dados a partir do:

```http
GET http://<seu-ip>/<rota>
```

O recomendável é usar uma biblioteca como Axios para consumir a API na interface Web.