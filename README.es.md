# Picta-FDM

[![en readme](https://img.shields.io/badge/readme-en-red?logo=readme&logoColor=red&label=readme)](https://github.com/Spheres-cu/picta-fdm#picta-fdm)
[![es leeme](https://img.shields.io/badge/readme-es-brightgreen?logo=readme&logoColor=brightgreen&label=leeme)](https://github.com/Spheres-cu/picta-fdm/blob/main/README.es.md#picta-fdm)

![GitHub Release](https://img.shields.io/github/v/release/Spheres-cu/picta-fdm?logo=refinedgithub&logoColor=FFFFFF)
![GitHub Downloads (all assets, all releases)(https://img.shields.io/badge/descargas-green?logo=github&logoColor=1f1f23&labelColor=fbfbfb&color=brightblue)](https://img.shields.io/github/downloads/Spheres-cu/picta-fdm/total)
![GitHub License](https://img.shields.io/github/license/Spheres-cu/picta-fdm)
![GitHub Repo stars](https://img.shields.io/github/stars/Spheres-cu/picta-fdm)

![Picta-fdm Logo](https://github.com/Spheres-cu/picta-fdm/blob/main/.pictures/logo-miniaturas.png?raw=true)

Proporciona soporte para descargar videos de [www.picta.cu](https://picta.cu) y [Youtube](https://www.youtube.com) es un complemento para [Free download Manager](https://www.freedownloadmanager.org/).

Basado en [picta-dl](https://github.com/oleksis/picta-dl) descargador de videos para Picta.cu y [yt-dlp](https://github.com/yt-dlp/yt-dlp)

## Instalación

1. Descargue el último lanzamiento [release](https://github.com/Spheres-cu/picta-fdm/releases/latest).

2. Cree el archivo de configuración (config) para PICTA-DL (si la carpeta YT-DLP no existe, debe crearlo):

    *En Windows:*

    ```text
    %AppData%\yt-dlp\config
    ```

    *En Linux:*

    ```text
    ~/.config/yt-dlp/config
    ```

    - *Y el archivo de configuración debe tener:*

    ```text
    # Usuario y contraseña
    -u <tu_usuario_picta>

    -p <tu_contraseña_picta>
    ```

    **<ins>¡Nota importante!</ins>**

    Si configuró una credencial *.netrc*, **elimínela del archivo de configuración** debido a una vulnerabilidad de seguridad [CVE-2026-26331](https://nvd.nist.gov/vuln/detail/CVE-2026-26331) ya no se recomienda.

3. Instale picta-fdm.fda desde el menú *Complementos* de FDM con la opción: *Instalar complemento desde archivo*.

## Requisitos

1. Python 3.10 o superior

    > Si no tiene Python instalado en su sistema, Free Download Manager le da la opción de instalarlo.

2. Free Download Manager la última versión.

3. Un entorno de ejecución de JavaScript: [Deno](https://docs.deno.com/runtime)

    > Si aún no tiene instalado Deno en su sistema, Free Download Manager le brinda la opción de instalarlo.

## Forma de Uso

1. Ingrese a [www.picta.cu](https://www.picta.cu) con su cuenta.

2. Busque el contenido que desea descargar.

3. Copie un enlace del video de su elección.

4. Pegue el enlace a FDM.

5. Seleccione los archivos a descargar y dónde descargarlos.

### Descargas opcionales

Desde la versión 1.1.4, puedes descargar listas de reproducción personales y resultados de búsqueda:

#### Para descargar una lista de reproducción personal, primero debes crear una

- Desde la página del vídeo:

1. Haz clic en los tres puntos de la esquina inferior derecha.
2. Haz clic en `Agregar lista de reproducción`. Crea una nueva si no existe y agrega el video.\
![Picta-fdm usage](https://github.com/Spheres-cu/picta-fdm/blob/main/.pictures/add_playlist.png?raw=true)
3. Una vez que hayas agregado todos los videos que deseas, ve a `Mis listas` en tu perfil, en la esquina superior derecha.
4. Reproduce alguno de los videos de tu lista de reproducción y copia la URL de la barra de direcciones del navegador.\
![Picta-fdm usage](https://github.com/Spheres-cu/picta-fdm/blob/main/.pictures/run_playlist.png?raw=true)
5. Pega la URL copiada en FDM.

#### Para descargar resultados de búsqueda

1. Crea una URL con este formato: `https://www.picta.cu/search/<consulta>`, donde `consulta` es tu parámetro de búsqueda.
2. Pega la URL creada en FDM.

**Ej. URLs de búsqueda:**

```texto
"https://www.picta.cu/search/*House of the Dragon S01*"
"https://www.picta.cu/search/smallville"
"https://picta.cu/search/*The Long Halloween*"
"https://www.picta.cu/search/*The last of us S0*"
"https://www.picta.cu/search/*What if* 3x"
"https://www.picta.cu/search/*Super Mario La pelicula"
"https://www.picta.cu/search/*Superman*"
```

Verás una lista de reproducción de vídeos de tu búsqueda anterior.

Disfrútala!

![Picta-fdm usage](https://github.com/Spheres-cu/picta-fdm/blob/main/.pictures/usage_01.png?raw=true)

![Picta-fdm usage](https://github.com/Spheres-cu/picta-fdm/blob/main/.pictures/usage_02.png?raw=true)

![Picta-fdm usage](https://github.com/Spheres-cu/picta-fdm/blob/main/.pictures/usage_03.png?raw=true)

## Capturas de pantalla

![Picta-fdm screenshots](https://github.com/Spheres-cu/picta-fdm/blob/main/.pictures/00_download_playlist.png?raw=true)

![Picta-fdm screenshots](https://github.com/Spheres-cu/picta-fdm/blob/main/.pictures/01_download_playlist.png?raw=true)

![Picta-fdm screenshots](https://github.com/Spheres-cu/picta-fdm/blob/main/.pictures/02_download_playlist.png?raw=true)

## Solución de problemas

### Error HTTP 404: No encontrado

Algunas listas de reproducción multimedia pueden mostrar un error como "No encontrado". Esto puede deberse a que se borró el contenido o a algún error al subirlo a [www.picta.cu](https://www.picta.cu). En ese caso, verá el mensaje de error: "Error HTTP 404: No encontrado".

![Picta-fdm troubleshooting](https://github.com/Spheres-cu/picta-fdm/blob/main/.pictures/HTTP_Error_404_Not_Found.png?raw=true)

### Solución de problemas con la firma del plugin

Si recibe algún error basado en la firma del complemento, puede activar el modo de desarrollo, este modo permite la ejecución del complemento sin la restricción de la API 9.

![Picta-fdm dev mode](https://github.com/Spheres-cu/picta-fdm/blob/main/.pictures/dev_mode.png?raw=true)

### Permitir que los complementos utilicen cookies del navegador (para descargas de YouTube)

A veces puedes obtener el error HTTP 403 0 429 de Youtube debido al sobre paso del límite de solicitudes para descargar sin una cuenta de usuario, pero si activas la opción de "Permitir que los complementos utilicen cookies del navegador web" en la sección de complementos puedes evitar ese problema, pero ten cuidado con el límite de solicitudes y la cantidad de descarga porque tu cuenta en YT puede ser bloqueada por un tiempo determinado o permanente.

El uso de cookies del navegador web no funciona bien en los navegadores basados ​​en Chrome en Windows, por lo que recomiendo utilizar Firefox en su lugar.

Con Linux, esta característica funciona en casi cualquier navegador web: Brave, Firefox, Chrome, Chrome, Edge, Opera, Safari, Vivaldi, Whale.
