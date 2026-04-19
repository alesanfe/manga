# Manga Downloader

Manga Downloader es una aplicación web completa desarrollada con Django que permite descargar capítulos de manga desde my.ninemanga.com, convertirlos automáticamente a formato PDF y ofrecer una API REST para gestionar todas las descargas. La aplicación incluye una interfaz de usuario moderna basada en Black Dashboard, junto con utilidades robustas para poblar la base de datos y crear índices de búsqueda eficientes.

Este proyecto ha sido diseñado para ser fácil de desplegar y mantener, ofreciendo flexibilidad tanto para usuarios finales que deseen descargar manga como para desarrolladores que quieran extender la funcionalidad. La aplicación soporta múltiples bases de datos (SQLite, MySQL y PostgreSQL) y puede desplegarse fácilmente usando Docker Compose.

## Características Principales

La aplicación ofrece un conjunto completo de funcionalidades orientadas a la descarga y gestión de manga. Puedes descargar capítulos individuales, rangos de capítulos o series completas de manga con un solo clic. Cada capítulo se descarga y se convierte automáticamente a formato PDF de alta calidad, lo que facilita su lectura en cualquier dispositivo.

Para desarrolladores, la API REST proporcionada permite integrar la funcionalidad de descarga en otras aplicaciones o automatizar procesos mediante programación. El sistema de scraping, basado en BeautifulSoup y Selenium, extrae tanto las imágenes como los metadatos de los mangas, asegurando que tengas información completa sobre cada serie.

La aplicación está preparada para diferentes entornos de despliegue, desde desarrollo local hasta producción en servidores, con soporte para múltiples sistemas de bases de datos y una configuración modular que facilita la personalización según tus necesidades.

## Tecnologías Utilizadas

Este proyecto está construido sobre tecnologías modernas y robustas. Utiliza Python 3.8 o superior como lenguaje principal, con Django 3.2.x como framework web. Para la API REST se implementa Django REST Framework, que proporciona herramientas poderosas para crear endpoints web estandarizados y bien documentados.

El scraping de contenido se realiza mediante BeautifulSoup4 y lxml para el análisis de HTML, complementado con Selenium para sitios web que requieren JavaScript. La generación de PDFs se implementa con ReportLab, una librería robusta que produce documentos de alta calidad. Para entornos de producción, la aplicación puede servir con Gunicorn como servidor WSGI y Nginx como servidor proxy inverso.

## Requisitos Previos

Para ejecutar este proyecto necesitas tener Python 3.8 o superior instalado en tu sistema. Si planeas utilizar Selenium para scraping avanzado, también necesitarás tener Chrome o Chromium instalado junto con su correspondiente ChromeDriver compatible con la versión del navegador.

Aunque es posible ejecutar el proyecto sin Docker, se recomienda encarecidamente tener Docker y Docker Compose instalados para obtener un entorno de despliegue reproducible y simplificado. Docker asegura que todas las dependencias estén correctamente configuradas y que el entorno sea consistente entre diferentes máquinas.

## Inicio Rápido con Docker (Recomendado)

La forma más sencilla de poner en marcha la aplicación es utilizando Docker, que automatiza todo el proceso de configuración y garantiza un entorno consistente. Comienza clonando el repositorio en tu máquina local:

```powershell
git clone https://github.com/alesanfe/manga.git
cd manga
```

El proyecto ahora organiza todas las configuraciones de Docker bajo la carpeta `docker/`, con subcarpetas específicas por entorno: `docker/base/` para la configuración base, `docker/dev/` para desarrollo con recarga automática, y `docker/prod/` para producción. También se incluyen `docker/nginx/` con la configuración de Nginx, `docker/gunicorn-cfg.py` para Gunicorn, y `docker/Dockerfile`. Cada carpeta tiene su propio archivo `docker-compose.yml` y `.env`. Antes de levantar los servicios, puedes editar los archivos `.env` correspondientes en cada carpeta:

Opciones para levantar el proyecto:

- Levantar en modo desarrollo (compose base, orientado a entorno con nginx + gunicorn):

```powershell
docker-compose -f docker/base/docker-compose.yml up -d --build
```

- Levantar el entorno de desarrollo con recarga automática (recomendado para programar):

Este flujo usa `docker/dev/docker-compose.yml` y ejecuta `python manage.py runserver` dentro del contenedor; además monta el código del host para que los cambios se apliquen inmediatamente.

```powershell
make dev-up
# o
docker-compose -f docker/dev/docker-compose.yml up -d --build
```

Accede a la app de desarrollo en http://localhost:8000. Cuando termines, detén y elimina volúmenes con:

```powershell
make dev-down
# o
docker-compose -f docker/dev/docker-compose.yml down -v
```

- Levantar en modo producción (no monta código host):

```powershell
make deploy
# o
docker-compose -f docker/prod/docker-compose.yml up -d --build
```

Notas sobre persistencia y poblado de la BD
------------------------------------------------
La configuración de docker utiliza volúmenes nombrados para persistir datos y archivos estáticos/media:

- `mysql_data` — datos de MySQL
- `static_volume` / `static_volume_dev` — destino de `collectstatic`
- `media_volume` / `media_volume_dev` — archivos subidos (media)

Para poblar la base de datos hay dos opciones:

- Ejecutar el servicio one-shot `populate-db` (usa el fixture `data/initial_data.json` si existe o ejecuta el script de scraping):

```powershell
make populate-db
# o
docker-compose -f docker/base/docker-compose.yml run --rm populate-db
```

- Habilitar poblado automático al arranque: añade `POPULATE_DB=true` en tu `.env`. El entrypoint intentará primero `manage.py loaddata data/initial_data.json` y, si no existe, ejecutará el script de populado.

Healthchecks y endpoints
-------------------------
La aplicación expone un endpoint simple de salud en `/health/` que devuelve JSON {"status":"ok"}. Los healthchecks de los contenedores usan este endpoint para verificar que la app esté lista.

Variables de entorno por entorno
--------------------------------
Se han incluido plantillas de `.env` específicas para cada entorno en `docker/envs/`:

- `docker/envs/.env.dev.example` — ejemplo para desarrollo (usa `DEBUG=True`, `POPULATE_DB=true`).
- `docker/envs/.env.prod.example` — ejemplo para producción (usa `DEBUG=False`).

Puedes instalar la plantilla adecuada en la raíz como `.env` usando los targets del `Makefile`:

```powershell
make env-dev   # copia docker/envs/.env.dev.example -> .env
make env-prod  # copia docker/envs/.env.prod.example -> .env
```

Los targets `make dev-up` y `make deploy` copian automáticamente la plantilla correspondiente en `.env` antes de arrancar los servicios.


Uso avanzado con Docker
-----------------------
Si necesitas ejecutar acciones adicionales (poblar la BD o levantar una configuración de producción), hay utilidades incluidas:

- Levantar en modo desarrollo (recomendado para desarrollo local):

```powershell
docker-compose -f docker/base/docker-compose.yml up -d --build
```

Desarrollo con recarga automática (recomendado)
------------------------------------------------
Para que el contenedor de desarrollo actualice automáticamente el código cuando programes, usa la configuración de desarrollo incluida. Esta configuración ejecuta `python manage.py runserver` dentro del contenedor y monta el código desde tu equipo, por lo que los cambios se recargan automáticamente.

Desde la raíz del proyecto:

```powershell
make dev-up
# o
docker-compose -f docker/dev/docker-compose.yml up -d --build
```

La aplicación quedará disponible en http://localhost:8000 y se recargará cuando guardes cambios en el código.

Para detener el entorno de desarrollo y eliminar volúmenes asociados:

```powershell
make dev-down
# o
docker-compose -f docker/dev/docker-compose.yml down -v
```


- Poblar la base de datos manualmente (servicio one-shot):

```powershell
# Correr el servicio `populate-db` que cargará `data/initial_data.json` si existe
# o ejecutará el script de población por scraping (puede tardar).
docker-compose -f docker/base/docker-compose.yml run --rm populate-db
```

- Levantar en modo producción (sin bind-mounts; usa `docker/prod/docker-compose.yml`):

```powershell
docker-compose -f docker/prod/docker-compose.yml up -d --build
```

Nota: en producción es recomendable no montar el código desde el host y gestionar las variables de entorno mediante el entorno del orquestador o un secreto.

## Inicio Rápido para Desarrollo Local

Si prefieres ejecutar el proyecto directamente en tu máquina sin utilizar Docker, puedes seguir este proceso de configuración manual. Primero, crea y activa un entorno virtual de Python para aislar las dependencias del proyecto:

`````powershell
python -m venv venv
venv\Scripts\activate
```

Con el entorno virtual activado, instala todas las dependencias necesarias del proyecto especificadas en el archivo `requirements.txt`:

`````powershell
pip install -r requirements.txt
```

El siguiente paso es configurar las variables de entorno. Al igual que con Docker, copia el archivo de ejemplo a `.env` y edítalo con tus configuraciones específicas. Luego, aplica las migraciones de la base de datos para crear la estructura necesaria:

`````powershell
python manage.py makemigrations
python manage.py migrate
```

Si deseas tener datos de ejemplo para probar la aplicación, puedes ejecutar el script de poblado de la base de datos. Este paso es opcional pero recomendado para familiarizarte con la funcionalidad:

`````powershell
python -c "from utils.db_populate import populate_mangas; populate_mangas()"
```

Finalmente, inicia el servidor de desarrollo de Django:

`````powershell
python manage.py runserver
```

La aplicación estará disponible en http://127.0.0.1:8000 y podrás acceder a todas sus funcionalidades desde tu navegador.

## Configuración de Variables de Entorno

El proyecto utiliza variables de entorno para gestionar la configuración de manera segura y flexible. Encontrarás archivos de ejemplo en `docker/envs/.env.dev.example` y `docker/envs/.env.prod.example` que debes copiar a `.env` y personalizar según tu entorno. Entre las variables más importantes destacan la clave secreta de Django (SECRET_KEY), que es esencial para la seguridad de la aplicación, y el modo de depuración (DEBUG), que debe establecerse en False en entornos de producción.

Para la configuración de la base de datos, puedes elegir entre SQLite, MySQL o PostgreSQL mediante la variable DB_ENGINE. Según tu elección, necesitarás proporcionar las credenciales correspondientes incluyendo el nombre de la base de datos, usuario, contraseña, host y puerto. Además, puedes configurar el host o URL de producción mediante la variable SERVER si necesitas especificar un dominio particular.

## Uso de la API REST

La aplicación proporciona una API REST completa que permite integrar la funcionalidad de descarga en otras aplicaciones o automatizar procesos. Para obtener documentación detallada sobre todos los endpoints disponibles, parámetros y ejemplos de uso, consulta el archivo [docs/API.md](docs/API.md).

El endpoint principal para descargar mangas es POST /api/manga/download/, que acepta solicitudes con el nombre del manga y una lista de capítulos a descargar. Este endpoint es muy flexible: puedes descargar todos los capítulos de una serie enviando una lista vacía, un capítulo específico enviando un solo número, o un rango de capítulos enviando el inicio y fin del rango.

Aquí tienes un ejemplo de cómo utilizar este endpoint mediante curl:

```bash
curl -X POST http://127.0.0.1:8000/api/manga/download/ \
  -H "Content-Type: application/json" \
  -d '{"manga_name": "nombre-del-manga", "chapters": [1,10]}' --output descarga.zip
```

El parámetro manga_name debe corresponder al identificador o nombre utilizado por my.ninemanga.com. El parámetro chapters es una lista de números que indica qué capítulos descargar: una lista vacía descarga todos los capítulos disponibles, un solo elemento descarga ese capítulo específico, y dos elementos descargan el rango desde el primer número hasta el segundo.

Como respuesta, la API genera un archivo ZIP que contiene los PDFs de todos los capítulos solicitados, listo para ser descargado y utilizado.

## Notas Importantes sobre Scraping y Selenium

El sistema de scraping de la aplicación utiliza Selenium para sitios web que requieren ejecución de JavaScript. Si planeas utilizar Selenium localmente en tu entorno de desarrollo, es necesario que instales Chrome o Chromium junto con su correspondiente ChromeDriver. Es crucial que la versión de ChromeDriver sea compatible con la versión del navegador que tienes instalada, de lo contrario el scraping no funcionará correctamente.

Los scrapers están específicamente orientados a my.ninemanga.com, lo que significa que los selectores y la lógica de extracción de datos están adaptados a la estructura HTML de ese sitio en particular. Es importante tener en cuenta que el HTML de los sitios web puede cambiar con el tiempo, lo que podría causar que los scrapers dejen de funcionar. Si detectas fallos en el scraping, te recomiendo revisar los selectores CSS y XPath en el archivo `utils/manga_services.py` y en los módulos correspondientes del app `apps/manga`.

## Documentación del Proyecto

El proyecto cuenta con una documentación completa y organizada en la carpeta `docs/` que cubre todos los aspectos de la aplicación, desde el uso hasta el desarrollo. Esta documentación está diseñada para ayudarte tanto si eres un usuario final que desea utilizar la aplicación como si eres un desarrollador que quiere contribuir al proyecto.

Para usuarios finales, el archivo [USER_MANUAL.md](docs/USER_MANUAL.md) proporciona una guía detallada sobre cómo navegar y utilizar la interfaz web, incluyendo instrucciones para buscar manga, filtrar resultados, gestionar descargas y solucionar problemas comunes. Este manual está escrito pensando en usuarios que no tienen conocimientos técnicos profundos.

Si necesitas información sobre la API REST para integraciones o automatización, el archivo [API.md](docs/API.md) contiene la documentación completa de todos los endpoints disponibles, incluyendo parámetros, ejemplos de uso en diferentes lenguajes de programación y códigos de error. Este documento es esencial para desarrolladores que deseen consumir la API programáticamente.

Para desarrolladores que deseen contribuir al proyecto o modificar el código, el archivo [DEVELOPMENT.md](docs/DEVELOPMENT.md) ofrece una guía completa de desarrollo. Este documento cubre la configuración del entorno de desarrollo, el flujo de trabajo recomendado, los estándares de código del proyecto, cómo escribir pruebas, y mejores prácticas para mantener la calidad del código.

Si necesitas entender la estructura interna del proyecto, el archivo [PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md) proporciona un mapa detallado de todos los directorios y archivos del proyecto, explicando el propósito de cada componente y cómo se organizan las diferentes partes de la aplicación. Este documento es particularmente útil para nuevos desarrolladores que se están familiarizando con el códigobase.

El archivo [CHANGELOG.md](docs/CHANGELOG.md) mantiene un registro histórico de todas las versiones del proyecto y los cambios introducidos en cada una, lo que es útil para rastrear la evolución del software y entender qué características se han añadido o modificado en cada versión.

Finalmente, el archivo [LICENSE.md](docs/LICENSE.md) contiene los términos de licencia bajo los cuales se distribuye el proyecto, actualmente bajo la licencia MIT, que permite un uso flexible del código tanto para proyectos personales como comerciales.

## Estructura del Proyecto

El proyecto sigue una estructura organizada que separa claramente las diferentes responsabilidades de la aplicación. El directorio `core/` contiene la configuración central de Django, incluyendo los archivos de configuración modular (settings), la configuración WSGI para despliegue y el enrutamiento principal de URLs.

Las aplicaciones Django principales se encuentran en el directorio `apps/`, que incluye tres aplicaciones fundamentales: `authentication` para la gestión de usuarios y autenticación, `home` para la página principal y funcionalidades generales, y `manga` que contiene toda la lógica específica relacionada con la descarga y gestión de manga.

La lógica de negocio y las utilidades reutilizables se encuentran en el directorio `utils/`. Aquí puedes encontrar `manga_services.py` con los servicios de descarga de manga, `db_populate.py` para poblar la base de datos con datos iniciales, e `index_creator.py` para crear índices de búsqueda eficientes.

Los archivos estáticos (CSS, JavaScript, imágenes) y las plantillas HTML se encuentran en los directorios `static/` y `templates/` respectivamente, siguiendo las mejores prácticas de Django para mantener el frontend organizado. Finalmente, los archivos de configuración para despliegue se organizan en `docker/` con subcarpetas específicas: `docker/base/docker-compose.yml` para configuración base, `docker/dev/docker-compose.yml` para desarrollo con recarga automática, `docker/prod/docker-compose.yml` para producción, `docker/Dockerfile`, `docker/nginx/` con la configuración de Nginx y `docker/gunicorn-cfg.py` para la configuración de Gunicorn.

## Scripts y Tareas Útiles

El proyecto incluye varios scripts y comandos que facilitan tareas comunes de desarrollo y mantenimiento. Para poblar la base de datos con datos de ejemplo, puedes ejecutar el script de poblado que carga información de manga y crea los índices de búsqueda necesarios:

`````powershell
python -c "from utils.db_populate import populate_mangas; populate_mangas()"
```

Cuando realices cambios en los modelos de la base de datos durante el desarrollo, necesitarás crear y aplicar las migraciones correspondientes. Django proporciona comandos para gestionar este proceso de manera sencilla:

`````powershell
python manage.py makemigrations
python manage.py migrate
```

Si el proyecto incluye pruebas configuradas con pytest o el framework de pruebas de Django, puedes ejecutarlas para verificar que todo funcione correctamente antes de realizar cambios importantes:

`````powershell
python manage.py test
```

## Comandos Útiles para Desarrolladores

Para el desarrollo del proyecto, es recomendable instalar tanto las dependencias de producción como las herramientas de desarrollo. Esto incluye formateadores de código, linters y herramientas de testing que ayudan a mantener la calidad del código:

`````powershell
pip install -r requirements.txt -r requirements-dev.txt
```

El proyecto utiliza pre-commit hooks para asegurar que el código cumpla con los estándares de calidad antes de cada commit. Estos hooks ejecutan automáticamente el formateo de código, la organización de imports y el linting. Para instalarlos en tu repositorio local:

`````powershell
pre-commit install
```

Si tienes GNU Make disponible en tu entorno (en Windows puedes usar WSL o ejecutar los comandos manualmente), el proyecto incluye un Makefile con comandos simplificados para tareas comunes. Estos comandos facilitan la ejecución de operaciones frecuentes:

`````powershell
make install   # instala dependencias
make lint      # corre isort, black, flake8
make test      # ejecuta pytest
```

## Buenas Prácticas y Recomendaciones

Al trabajar con este proyecto, es importante seguir ciertas buenas prácticas para garantizar la seguridad y la calidad del código. En entornos de producción, siempre debes mantener la variable `DEBUG` establecida en False y proporcionar una `SECRET_KEY` segura y generada aleatoriamente. Nunca uses la clave secreta por defecto en producción.

Es fundamental no guardar credenciales ni información sensible en el repositorio. En su lugar, utiliza variables de entorno o servicios de gestión de secretos. Esto incluye contraseñas de bases de datos, claves de API y cualquier otra información sensible que pueda comprometer la seguridad del sistema.

Antes de realizar un despliegue a producción, es recomendable ejecutar escaneos de dependencias para identificar posibles vulnerabilidades de seguridad. Herramientas como safety, pip-audit o Snyk pueden ayudarte a detectar paquetes con vulnerabilidades conocidas y actualizarlos a versiones seguras.

Para mantener la calidad del código a lo largo del tiempo, considera añadir cobertura de tests y ejecutar linters (flake8, isort, black) en tu pipeline de integración continua. Esto asegura que cualquier cambio que se introduzca cumpla con los estándares del proyecto y no rompa funcionalidades existentes.

## Cómo Contribuir

Las contribuciones al proyecto son bienvenidas y apreciadas. Si deseas colaborar, el proceso es sencillo y sigue las mejores prácticas de desarrollo open source. Comienza haciendo un fork del repositorio a tu cuenta personal de GitHub. Esto te dará una copia independiente donde puedes trabajar sin afectar el proyecto original.

Una vez tengas tu fork, crea una rama descriptiva para tu trabajo. Es recomendable usar un nombre que describa claramente qué funcionalidad estás implementando o qué problema estás solucionando, como `feature/mi-nueva-funcionalidad` o `bugfix/corregir-error-especifico`:

`````powershell
git checkout -b feature/mi-feature
```

Al realizar cambios, es importante que añadas pruebas para verificar que tu código funciona correctamente y que no rompe funcionalidades existentes. También documenta tus cambios, ya sea en el código mediante comentarios o en la documentación del proyecto si introduces nuevas características visibles para los usuarios.

Cuando tu trabajo esté completo, haz un pull request al repositorio original. Describe claramente los cambios que has realizado, incluyendo un resumen de la funcionalidad, instrucciones sobre cómo probarlo localmente y los tests que has añadido. Esto facilita que los mantenedores del proyecto revisen y aprueben tu contribución.

## Seguridad y Privacidad

La seguridad es una prioridad en este proyecto. Es fundamental que nunca incluyas claves, contraseñas ni ninguna credencial sensible en tus commits al repositorio. Este tipo de información debe manejarse siempre mediante variables de entorno o servicios de gestión de secretos.

Al revisar o proponer cambios, presta especial atención a cualquier modificación que afecte a dependencias nativas o que implique ejecución de código remoto. Estos tipos de cambios pueden tener implicaciones de seguridad significativas y deben ser revisados cuidadosamente antes de ser integrados.

Si descubres una vulnerabilidad de seguridad en el proyecto, por favor repórtala de manera responsable siguiendo las directrices de seguridad del proyecto, en lugar de hacerla pública inmediatamente.

## Licencia

Este proyecto está licenciado bajo la licencia MIT, que es una licencia permisiva que permite un uso flexible del código tanto para proyectos personales como comerciales. Para detalles completos sobre los términos de la licencia, consulta el archivo [docs/LICENSE.md](docs/LICENSE.md).

La licencia MIT te permite usar, copiar, modificar, fusionar, publicar, distribuir, sublicenciar y/o vender copias del software, sujeto a las siguientes condiciones: el aviso de copyright y el aviso de permiso deben incluirse en todas las copias o porciones sustanciales del software.

## Contacto y Créditos

El autor y mantenedor original del proyecto es Ales Anfe, y el repositorio original está disponible en https://github.com/alesanfe/manga. La interfaz de usuario se basa en Black Dashboard Django, un tema desarrollado por Creative Tim que proporciona una base moderna y atractiva para aplicaciones web.

Si necesitas asistencia adicional o tienes preguntas sobre el proyecto, no dudes en contactar a través de los canales oficiales del repositorio. La comunidad de usuarios y desarrolladores puede ser una gran fuente de ayuda y conocimiento.

Si estás interesado en mejoras adicionales como una revisión completa del código, un informe de seguridad profesional, o la implementación de integración continua con GitHub Actions, puedo ayudarte a preparar estas mejoras. Simplemente indícame qué aspecto prefieres priorizar y lo desarrollaré según tus necesidades.


## Automatizaci�n del Setup en Windows

Para facilitar la configuraci�n del entorno de desarrollo en sistemas Windows, hemos a�adido un script de PowerShell que automatiza todo el proceso de configuraci�n inicial. Este script, ubicado en scripts/setup_dev.ps1, realiza todas las tareas necesarias para poner en marcha el proyecto de manera r�pida y sencilla.

Para utilizar el script, navega al directorio del proyecto y ejec�talo con PowerShell:

```powershell
cd C:\Users\alex0\PycharmProjects\manga
.\scripts/setup_dev.ps1
```

El script tambi�n acepta un par�metro opcional -Populate que, cuando se incluye, carga autom�ticamente datos de ejemplo en la base de datos despu�s de la configuraci�n. Esto es particularmente �til si deseas tener el proyecto listo para probar inmediatamente con datos de muestra:

```powershell
.\scripts/setup_dev.ps1 -Populate
```

## Escaneo de Seguridad y Gesti�n de Secretos

Mantener la seguridad del proyecto es fundamental, por lo que se recomienda ejecutar chequeos regulares antes de realizar despliegues o subir cambios importantes al repositorio. Estos chequeos ayudan a identificar vulnerabilidades en las dependencias y secretos que puedan haber sido comprometidos inadvertidamente.

Para comprobar vulnerabilidades en las dependencias del proyecto, puedes utilizar la herramienta safety. Esta herramienta analiza las dependencias instaladas y las compara con una base de datos de vulnerabilidades conocidas:

```powershell
pip install safety
safety check --full-report
```

Otra pr�ctica recomendada es escanear el historial de Git en busca de secretos que puedan haber sido comprometidos accidentalmente. La herramienta detect-secrets es excelente para este prop�sito, ya que puede identificar patrones comunes de secretos como claves de API, tokens y contrase�as:

```powershell
pip install detect-secrets
detect-secrets scan > .secrets.baseline
```

Una vez creado el archivo baseline, puedes auditar el historial para verificar si hay secretos comprometidos:

```powershell
detect-secrets audit .secrets.baseline
```

## Estructura Modular de Configuraci�n

Para mantener el proyecto organizado y seguro, recomendamos separar la configuraci�n de Django en m�dulos distintos seg�n el entorno. El proyecto actualmente implementa esta estructura con core/settings/base.py para la configuraci�n compartida, core/settings/local.py para el entorno de desarrollo local y core/settings/production.py para el entorno de producci�n.

Esta separaci�n permite tener configuraciones espec�ficas para cada entorno sin comprometer la seguridad. Es recomendable utilizar librer�as como django-environ o python-dotenv para cargar las variables de entorno desde el archivo .env de manera segura y centralizada.

Aqu� tienes un ejemplo de c�mo estructurar la configuraci�n utilizando django-environ:

```python
import environ

env = environ.Env(
    DEBUG=(bool, False)
)
environ.Env.read_env()  # lee .env

SECRET_KEY = env('DJANGO_SECRET_KEY')
DEBUG = env('DEBUG')
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['127.0.0.1'])

# DATABASE
DATABASES = {
    'default': env.db('DATABASE_URL', default='sqlite:///db.sqlite3')
}
```

## Archivos y Mejoras Recientes

El proyecto ha recibido varias mejoras recientes para mejorar su organizaci�n y seguridad. Se han a�adido archivos de documentaci�n y configuraci�n que facilitan tanto el desarrollo como el despliegue del proyecto.

Entre los archivos a�adidos recientemente se incluyen gu�as de seguridad y contribuci�n, as� como scripts de automatizaci�n. Estos archivos proporcionan directrices claras para mantener la calidad y seguridad del c�digo a lo largo del tiempo.

## Pr�ximos Pasos Recomendados

Hay varias mejoras que podr�an implementarse para llevar el proyecto al siguiente nivel. Una de las mejoras m�s importantes ser�a refactorizar completamente la configuraci�n de settings para utilizar django-environ de manera consistente en todos los entornos. Esto proporcionar�a una gesti�n m�s robusta y segura de las variables de entorno.

Otra recomendaci�n importante es ejecutar un escaneo completo de secretos en todo el repositorio para identificar y limpiar cualquier credencial o informaci�n sensible que pueda haber sido comprometida inadvertidamente. Esto es especialmente importante en proyectos que han tenido m�ltiples colaboradores.

Finalmente, considerar la implementaci�n de integraci�n continua mediante GitHub Actions podr�a automatizar significativamente el proceso de construcci�n y despliegue. Esto incluir�a jobs para construir im�genes Docker, ejecutar pruebas autom�ticamente y publicar nuevas versiones de manera consistente.
