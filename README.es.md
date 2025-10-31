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

    **~~NO recomendado~~**

    ```text
    #Usuario y contraseña
    -u <tu_usuario_picta>

    -p <tu_contraseña_picta>
    ```

    **Ó**

    **<ins>Recomendado</ins>**

    *Usar las credenciales de .netrc:*

    *Crear el archivo .netrc en ```%USERPROFILE%``` (Windows) y añadir:*

    ```text
    machine <extractor> login <usuario> password <contraseña>
    ```

    *Donde:*

    ```text
    - extractor = picta

    - login = tu usuario de picta

    - password = tu contraseña de picta
    ```

    *Y solamente añadir a config:*

    ```text
    --netrc
    ```

    *Este script puede crear el archivo con las credenciales:*

    ```bash
    @echo off
    setlocal enabledelayedexpansion

    set NETRC_FILE=%USERPROFILE%\.netrc

    echo Creando archivo .netrc en %USERPROFILE%
    echo.
    set /p "login=Entre login(usuario de picta): "

    for /f "delims=" %%p in ('powershell -Command "$password = Read-Host -AsSecureString 'Entre password'; $BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($password); [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)"') do set "password=%%p"

    set "password=!password: =!"
    set "password=!password: =!"

    echo|set /p="machine picta login !login! password !password!" > "%NETRC_FILE%"

    echo.
    echo El archivo .netrc ha sido creado satisfactoriamente en: %NETRC_FILE%
    echo.
    echo Contenido de .netrc:
    type "%NETRC_FILE%"

    set "password="
    ```

    *Crea un archivo, por ejemplo: "crear_archivo_netrc.cmd", pega el código anterior y ejecútalo en una consola de Windows.*

    *En Linux, el procedimiento es el mismo, pero en el archivo ```~/.netrc``` puedes crear las credenciales.*

3. Instale picta-fdm.fda desde el menú *Complementos* de FDM con la opción: *Instalar complemento desde archivo*.

## Requisitos

1. Python 3.10 o superior

    - Si no tiene Python instalado en su sistema, Free Download Manager le da la opción de instalarlo.

2. Free Download Manager versión 6.30.0.6459 o superior.

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

### Error HTTP 404: No encontrado

Algunas listas de reproducción multimedia pueden mostrar un error como "No encontrado". Esto puede deberse a que se borró el contenido o a algún error al subirlo a [www.picta.cu](https://www.picta.cu). En ese caso, verá el mensaje de error: "Error HTTP 404: No encontrado".

![Picta-fdm troubleshooting](https://github.com/Spheres-cu/picta-fdm/blob/main/.pictures/HTTP_Error_404_Not_Found.png?raw=true)
