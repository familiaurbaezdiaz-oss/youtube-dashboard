# -*- coding: utf-8 -*-

path_server = r"C:\Users\hanse\Downloads\railway_dashboard\server.js"

with open(path_server, encoding="utf-8") as f:
    content = f.read()

marcador = "const express = require('express');"
nuevo = "require('dotenv').config();\nconst express = require('express');"

if marcador not in content:
    print("ERROR: no se encontro el marcador de express")
else:
    # Solo reemplazar la PRIMERA ocurrencia, ya que mas abajo en el
    # archivo hay codigo Python embebido que tambien podria mencionar
    # cosas similares (aunque en este caso es practicamente imposible
    # que coincida exactamente, pero por seguridad usamos count=1).
    content = content.replace(marcador, nuevo, 1)
    with open(path_server, "w", encoding="utf-8") as f:
        f.write(content)
    print("OK: dotenv agregado a server.js")

# Crear el archivo .env con la clave (si no existe ya, no lo sobreescribimos
# por si el usuario ya tenia algo ahi de otra sesion)
import os
path_env = r"C:\Users\hanse\Downloads\railway_dashboard\.env"
linea_env = 'YOUTUBE_API_KEY=AIzaSyCnvYmEePkUpdGm4lc7wcRuKnYAXojq07Y\n'

if os.path.exists(path_env):
    with open(path_env, encoding="utf-8") as f:
        env_actual = f.read()
    if "YOUTUBE_API_KEY" in env_actual:
        print("AVISO: .env ya existe y ya tiene YOUTUBE_API_KEY, no se modifico")
    else:
        with open(path_env, "a", encoding="utf-8") as f:
            f.write(linea_env)
        print("OK: YOUTUBE_API_KEY agregada al .env existente")
else:
    with open(path_env, "w", encoding="utf-8") as f:
        f.write(linea_env)
    print("OK: .env creado con YOUTUBE_API_KEY")
