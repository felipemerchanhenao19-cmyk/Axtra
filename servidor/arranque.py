"""Arranca Axtra en dos puertos dentro del mismo contenedor:
  8080: la app de Axtra (la publica el túnel, protegida con Cloudflare Access)
  8090: la ranura privada para los orbes de los negocios (el túnel NO la publica)
"""
import asyncio

import uvicorn

from . import config


async def main():
    servidores = [
        uvicorn.Server(uvicorn.Config("servidor.app:app", host="0.0.0.0", port=8080, proxy_headers=True)),
        uvicorn.Server(uvicorn.Config("servidor.ranura:app", host="0.0.0.0", port=config.RANURA_PUERTO)),
    ]
    await asyncio.gather(*(s.serve() for s in servidores))


if __name__ == "__main__":
    asyncio.run(main())
