[English](README.md) | Español

# Groovn

Una app de escritorio para puntuar, reseñar y explorar álbumes de música, al estilo de Letterboxd pero para música.

## Contexto

Proyecto personal (otoño de 2025).

## Funcionalidades

- Registro e inicio de sesión con usuario, email y contraseña.
- Añadir un álbum con título, artista, género, fecha de lanzamiento, una nota de 1 a 5, una reseña y la URL de la portada.
- Ver los álbumes como tarjetas con su portada.
- Buscar mientras escribes, filtrar por género y ordenar por artista (A–Z o Z–A), por nota o por fecha de lanzamiento.

## Cómo funciona

Una interfaz en Tkinter se conecta a una base de datos MySQL local llamada `groovnapp`, con dos tablas: `users` y `reviews`. Cada reseña pertenece a un usuario. Las portadas se descargan desde su URL con `requests` y se muestran con Pillow.

Es un proyecto de aprendizaje. Las contraseñas se guardan en texto plano y las credenciales de la base de datos están escritas en el código para un MySQL local, así que no lo uses con cuentas reales.

## Cómo ejecutarlo

Necesitas un servidor MySQL local con usuario `root` y contraseña `root`, o cambiar la conexión en `main.py` y `test-connection.py`.

```bash
git clone https://github.com/lucasavila23/groovn.git
cd groovn
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python test-connection.py   # crea la base de datos y las tablas
python main.py
```

## Tecnologías

Python, Tkinter, MySQL (mysql-connector-python), Pillow, requests.

## Licencia

MIT. Consulta [LICENSE](LICENSE).

## Autor

Lucas Avila Manotas · [LinkedIn](https://www.linkedin.com/in/lucas-avila23)
