# Picta-FDM

[![en readme](https://img.shields.io/badge/readme-en-red?logo=readme&logoColor=red&label=readme)](https://github.com/Spheres-cu/picta-fdm#picta-fdm)
[![es leeme](https://img.shields.io/badge/readme-es-brightgreen?logo=readme&logoColor=brightgreen&label=leeme)](https://github.com/Spheres-cu/picta-fdm/blob/main/README.es.md#picta-fdm)

![GitHub Release](https://img.shields.io/github/v/release/Spheres-cu/picta-fdm?logo=refinedgithub&logoColor=FFFFFF)
![GitHub Downloads (all assets, all releases)(https://img.shields.io/badge/descargas-green?logo=github&logoColor=1f1f23&labelColor=fbfbfb&color=brightblue)](https://img.shields.io/github/downloads/Spheres-cu/picta-fdm/total)
![GitHub License](https://img.shields.io/github/license/Spheres-cu/picta-fdm)
![GitHub Repo stars](https://img.shields.io/github/stars/Spheres-cu/picta-fdm)

![Picta-fdm Logo](https://github.com/Spheres-cu/picta-fdm/blob/main/.pictures/logo-miniaturas.png?raw=true)

Proporciona soporte para descargar videos de [www.picta.cu](https://picta.cu) es un complemento para [Free download Manager](https://www.freedownloadmanager.org/).

Basado en el complemento [Elephant](https://github.com/meowcateatrat/elephant) y [picta-dl](https://github.com/oleksis/picta-dl)  descargador de videos para Picta.cu

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
    #User and password
    -u <tu_usuario_de_picta>
    -p <tu_contraseña_de_picta>
    ```

3. Instale picta-fdm.fda desde el menú *Complementos* de FDM con la opción: *Instalar complemento desde archivo*.

## Requisitos

1. Python 3.9 o superior

    - Si no tiene Python instalado en su sistema, Free Download Manager le da la opción de instalarlo.

2. Free Download Manager versión 6.29.1.6392 o superior.

## Forma de Uso

1. Ingrese a [www.picta.cu](https://www.picta.cu) con su cuenta.

2. Busque el contenido que desea descargar.

3. Copie un enlace del video de su elección.

4. Pegue el enlace a FDM.

5. Seleccione los archivos a descargar y dónde descargarlos.

Disfrútala!

![Picta-fdm usage](https://github.com/Spheres-cu/picta-fdm/blob/main/.pictures/usage_01.png?raw=true)

![Picta-fdm usage](https://github.com/Spheres-cu/picta-fdm/blob/main/.pictures/usage_02.png?raw=true)

![Picta-fdm usage](https://github.com/Spheres-cu/picta-fdm/blob/main/.pictures/usage_03.png?raw=true)

## Capturas de pantalla

![Picta-fdm screenshots](https://github.com/Spheres-cu/picta-fdm/blob/main/.pictures/00_download_playlist.png?raw=true)

![Picta-fdm screenshots](https://github.com/Spheres-cu/picta-fdm/blob/main/.pictures/01_download_playlist.png?raw=true)

![Picta-fdm screenshots](https://github.com/Spheres-cu/picta-fdm/blob/main/.pictures/02_download_playlist.png?raw=true)

## Solución de problemas

### Formato no compatible

Hay un problema con la API FDM al descargar audio/video que se encuentra en formato de fragmentos, ya que no tiene soporte para este tipo de descarga.

Algunas listas de reproducción contienen medios con formato de fragmentos (audio/video en partes) Este tipo de formato no es compatible con la API FDM y verá un error de "formato no compatible", este problema está en la lista de TODO del equipo FDM.

Puede descargar los otros medios en las listas de reproducción sin problemas, excepto para este tipo.

![Picta-fdm troubleshooting](https://github.com/Spheres-cu/picta-fdm/blob/main/.pictures/Unsupported_format.png?raw=true)
