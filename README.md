# Picta-FDM

[![en readme](https://img.shields.io/badge/readme-en-red?logo=readme&logoColor=red&label=readme)](https://github.com/Spheres-cu/picta-fdm#picta-fdm)
[![es leeme](https://img.shields.io/badge/readme-es-brightgreen?logo=readme&logoColor=brightgreen&label=leeme)](https://github.com/Spheres-cu/picta-fdm/blob/main/README.es.md#picta-fdm)

![GitHub Release](https://img.shields.io/github/v/release/Spheres-cu/picta-fdm?logo=refinedgithub&logoColor=FFFFFF)
![GitHub Downloads (all assets, all releases)(https://img.shields.io/badge/downloads-green?logo=github&logoColor=1f1f23&labelColor=fbfbfb&color=brightblue)](https://img.shields.io/github/downloads/Spheres-cu/picta-fdm/total)
![GitHub License](https://img.shields.io/github/license/Spheres-cu/picta-fdm)
![GitHub Repo stars](https://img.shields.io/github/stars/Spheres-cu/picta-fdm)

![Picta-fdm Logo](https://github.com/Spheres-cu/picta-fdm/blob/main/.pictures/logo-miniaturas.png?raw=true)

Provides support for downloading videos from [www.picta.cu](https://picta.cu) and [Youtube](https://www.youtube.com) it is a Add-on for [Free download Manager](https://www.freedownloadmanager.org/).

Based on [picta-dl](https://github.com/oleksis/picta-dl) video downloader for Picta.cu and [yt-dlp](https://github.com/yt-dlp/yt-dlp)

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
    # User and password
    -u <your_picta_user>
    -p <your_picta_password>
    ```

   **<ins>Important note!</ins>**

   if you configured a *.netrc* credential please **remove it from config file** due to a Security vulnerability [CVE-2026-26331](https://nvd.nist.gov/vuln/detail/CVE-2026-26331) is no longer recommended.

3. Install the picta-fdm.fda using from plugin menu: *install from file* option in Free Download Manager.

## Requirements

1. Python 3.10 or above
   > If you don't have Python installed in your system Free Download Manager get you the option for install it.

2. Free Download Manager latest version

3. A JavaScript runtime: [Deno](https://docs.deno.com/runtime)

   > If you don't have already installed Deno in your system Free Download Manager get you the option for install it.

## Usage

1. Enter to [www.picta.cu](https://www.picta.cu) with your account
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

### HTTP Error 404: Not Found

Some media playlist can have error like "Not Found". This can be because the content of the media was erase or for some error  when was uploaded to [www.picta.cu](https://www.picta.cu). That case you will see a error message: "Error HTTP Error 404: Not Found"

![Picta-fdm troubleshooting](https://github.com/Spheres-cu/picta-fdm/blob/main/.pictures/HTTP_Error_404_Not_Found.png?raw=true)

### Plugin signature troubleshooting

If get some error based in the plugin signature you can activate the dev mode, this mode permit the execution of the plugin without the API 9 restrinction.

![Picta-fdm dev mode](https://github.com/Spheres-cu/picta-fdm/blob/main/.pictures/dev_mode_en.png?raw=true)

### Allow add-ons use browser cookies (for YT downloads)

Sometimes you can get HTTP Error 403 or 429 from Youtube because the requests rate limit or overuse of the amount of downloads without a user account, but if you activate the option of "Allow add-ons to use web browser cookies" in the add-ons section you can avoid that's problem, but be careferul with the rate limit and amount of download  because your account in YT can be bloqued for certain time or permanent.

For the use of the web browser cookies don't work well in chromium-based browser in Windows so I recommend use firefox instead.

With Linux in almost any web browser work that's feature: brave, firefox, chrome, chromium, edge, opera, safari, vivaldi, whale.
