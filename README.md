# Picta-FDM

<picture>
  <img src="plugin/logo.png" alt="Picta FDM" width="256px" height="256px">
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
2. Free Download Manager version 6.25.2.xxx or above.
