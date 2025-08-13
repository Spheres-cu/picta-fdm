# Picta-FDM

[![en readme](https://img.shields.io/badge/readme-en-red?logo=readme&logoColor=red&label=readme)](https://github.com/Spheres-cu/picta-fdm#picta-fdm)
[![es leeme](https://img.shields.io/badge/readme-es-brightgreen?logo=readme&logoColor=brightgreen&label=leeme)](https://github.com/Spheres-cu/picta-fdm/blob/main/README.es.md#picta-fdm)

![GitHub Release](https://img.shields.io/github/v/release/Spheres-cu/picta-fdm?logo=refinedgithub&logoColor=FFFFFF)
![GitHub Downloads (all assets, all releases)(https://img.shields.io/badge/downloads-green?logo=github&logoColor=1f1f23&labelColor=fbfbfb&color=brightblue)](https://img.shields.io/github/downloads/Spheres-cu/picta-fdm/total?logo=artifacthub)
![GitHub License](https://img.shields.io/github/license/Spheres-cu/picta-fdm)
![GitHub Repo stars](https://img.shields.io/github/stars/Spheres-cu/picta-fdm)

![Picta-fdm Logo](https://github.com/Spheres-cu/picta-fdm/blob/main/.pictures/logo-miniaturas.png?raw=true)

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
2. Free Download Manager version 6.29.1.6392 or above.

## Usage

1. Enter to <https://www.picta.cu> with your account
2. Search for the content you wish to download.
3. Copy a link of the video of your choose.
4. Paste the link in to FDM.
5. Select what to download and where in the download windows of FDM.

Enjoy it !

![Picta-fdm usage](https://github.com/Spheres-cu/picta-fdm/blob/main/.pictures/usage_01.png?raw=true)

![Picta-fdm usage](https://github.com/Spheres-cu/picta-fdm/blob/main/.pictures/usage_02.png?raw=true)

![Picta-fdm usage](https://github.com/Spheres-cu/picta-fdm/blob/main/.pictures/usage_03.png?raw=true)

## Screenshots

![Picta-fdm screenshots](https://github.com/Spheres-cu/picta-fdm/blob/main/.pictures/00_download_playlist.png?raw=true)

![Picta-fdm screenshots](https://github.com/Spheres-cu/picta-fdm/blob/main/.pictures/01_download_playlist.png?raw=true)

![Picta-fdm screenshots](https://github.com/Spheres-cu/picta-fdm/blob/main/.pictures/02_download_playlist.png?raw=true)

## Troubleshooting

### Unsupported format

There is a problem with the FDM API when downloading audio/video that is in fragments format since it has no support for this type of download.

Some playlist contains media with fragments format (audio/video in parts) this type of format haven't  support in FDM API and you will see an error of "Unsupported format", this problem is in the FDM team TODO list .

You may download the other media in the playlists without problema except for this kind.

![Picta-fdm troubleshooting](https://github.com/Spheres-cu/picta-fdm/blob/main/.pictures/Unsupported_format.png?raw=true)
