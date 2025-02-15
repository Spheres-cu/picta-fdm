# Picta-FDM

![GitHub Release](https://img.shields.io/github/v/release/Spheres-cu/picta-fdm)
![GitHub License](https://img.shields.io/github/license/Spheres-cu/picta-fdm)
![GitHub Repo stars](https://img.shields.io/github/stars/Spheres-cu/picta-fdm)

<picture>
  <img src="plugin/logo.png" alt="Picta FDM" width="128px" height="128px">
</picture>

Provides support for downloading videos from [www.picta.cu](https://picta.cu) it is a Add-on for [Free download Manager](https://www.freedownloadmanager.org/).

Based on the plugin [Elephant](https://github.com/meowcateatrat/elephant) and [picta-dl](https://github.com/oleksis/picta-dl) video downloader for Picta.cu

## Install

1. Download the latest [release](https://github.com/Spheres-cu/picta-fdm/releases/latest).

2. Create the configuration file (*config*) for picta-dl (if yt-dlp folder don't exists you must create it):

    *On  Windows:*

    ```text
    %AppData%\yt-dlp\config
    ```

    *On Linux:*

    ```text
    ~/.config/yt-dlp/config
    ```

    - *And the config file must be have:*

    ```text
    #User and password
    -u <your_picta_user>
    -p <your_picta_password>
    ```

3. Install the picta-fdm.fda using from plugin menu: *install from file* option in Free Download Manager.

## Requirements

1. Python 3.9 or above
   - If you don't have Python installed in your system Free Download Manager get you the option for install it.
2. Free Download Manager version 6.26.0.6069 or above.
