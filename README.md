<a id="readme-top"></a>

<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/Jemeni11/FicImage">
    <img src="/logo.png" alt="Logo" width="128" height="128">
  </a>

  <h1 align="center">FicImage</h1>

  <p align="center">
    Enhance your FicHub files with images.
    <br />
    <a href="https://github.com/Jemeni11/FicImage"><strong>Explore the repo »</strong></a>
  </p>
</div>

Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Planned Features](#planned-features)
- [Installation](#installation)
  - [From PyPI](#from-pypi)
  - [From GitHub Releases](#from-github-releases)
- [Usage](#usage)
- [Image Support](#image-support)
  - [Image Handling](#image-handling)
- [Configuration](#configuration)
  - [Configuration Options](#configuration-options)
  - [Default Configuration](#default-configuration)
  - [Notes](#notes)
- [Why did I build this?](#why-did-i-build-this)
- [Contributing](#contributing)
- [Wait a minute, who are you?](#wait-a-minute-who-are-you)
- [License](#license)
- [Changelog](#changelog)

## Introduction

![PyPI Downloads](https://static.pepy.tech/badge/ficimagescript)

FicImage (aka FicImageScript due to naming issues on PyPI) is a tool for inserting missing images into FicHub EPUBs.

It scans the file for image placeholders, downloads the images, and replaces the placeholders with the actual images.

Currently only supports EPUBs, with other formats planned.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Features

- Scans FicHub EPUB files for image placeholders and replaces them with actual images
- Supports batch processing with the `--recursive` flag
- Handles image downloading and basic processing using Pillow
- Supports JPEG, PNG, GIF, WEBP, and SVG (within EPUB 3.3 spec limits)
- Optional image compression for JPEG and PNG
- Customizable via `ficimage.json` config file (supports image format, compression, max size)
- Debug mode for troubleshooting
- Leaves placeholders untouched if an image can’t be downloaded
- Avoids breaking animated images (minimal processing on GIFs/WEBPs)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Planned Features

- **Caching** – Avoid re-downloading the same image multiple times across chapters or files
- **Concurrency** – Download multiple images at once to speed things up (with proper race condition handling)
- **Better aspect ratio handling** – Resize images while preserving their original proportions more reliably
- **Broader format support** – Add support for other FicHub formats like MOBI and PDF (Currently working on Zipped HTML)
- **Improved WebP usage** – Convert static JPEGs and PNGs to WebP for better performance, instead of only using WebP for
  animated images
- **Tests** – Start writing tests (sigh)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Installation

### From PyPI

1. Install FicImage using pip:

   ```shell
   pip install FicImageScript
   ```

2. After installation, run FicImage with the following command:

   ```shell
   ficimage -p path/to/epub -c path/to/ficimage/json
   ```

   - `path/to/epub`: Path to the FicHub EPUB you want to add images to.
   - `path/to/ficimage.json`: Path to your ficimage.json config file, where you can customize settings (
     see [Configuration](#configuration)).

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### From GitHub Releases

1. Download the latest release from the [FicImage GitHub Releases page](https://github.com/Jemeni11/FicImage/releases).

2. Depending on your preference, choose one of the following installation methods:

   - Using the Wheel File:

     ```shell
     pip install FicImageScript-<version>-py3-none-any.whl
     ```

   - Using the Source Tarball File:

     ```shell
     pip install FicImageScript-<version>.tar.gz
     ```

   Replace `<version>` with the actual version number of the release.

3. After installation, run FicImage using:

   ```shell
   python main.py -p path/to/epub -c path/to/ficimage/json
   ```

   - `path/to/epub`: Path to the FicHub EPUB you want to add images to.
   - `path/to/ficimage.json`: Path to your ficimage.json config file, where you can customize settings (
     see [Configuration](#configuration)).

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Usage

Run `ficimage -h` to see the available options:

```shell
(venv) nonso@Adell:~/Documents/Code$ ficimage -h
usage: main.py [-h] [-p PATH_TO_EPUB] [-c CONFIG_FILE_PATH] [-d] [-v] [-r RECURSIVE]

Update a FicHub epub file with images.

options:
  -h, --help                  Show this help message and exit.
  -p PATH_TO_EPUB,            The path to the FicHub epub file.
  --path_to_epub PATH_TO_EPUB
  -c CONFIG_FILE_PATH,        The path to the ficimage.json file.
  --config_file_path CONFIG_FILE_PATH
  -d, --debug                 Enable debug mode.
  -v, --version               Prints out the current version and quits.
  -r RECURSIVE,               This will update all files in the directory path given and its subdirectories.
  --recursive RECURSIVE
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Image Support

FicImage supports the following image formats for **FicHub EPUBs**:

- **JPEG**
- **PNG**
- **GIF**
- **WEBP**
- **SVG**

For more information, see the [Core Media Types Section of the EPUB Version 3.3 Specification](https://www.w3.org/TR/epub-33/#sec-core-media-types).

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Image Handling

- **Non-animated images**: FicImage will attempt to save all non-animated images as **JPEG** by default.
- **Animated images**: Only **GIFs** and **WEBPs** are supported, and FicImage does little to no processing on them to preserve the animation.
- **SVGs**: FicImage can save **SVG** images but **cannot compress** them since SVGs are not supported by [Pillow](https://pillow.readthedocs.io/en/stable/index.html).

If **FicImage** cannot download an image, it leaves the placeholder URL unchanged.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Configuration

FicImage uses a **JSON configuration file** (`ficimage.json`) to customize settings.

FicImage checks for a configuration file in the given directory path. If no directory
path is given, FicImage checks the current directory and then the Operating System's
home directory.

The configuration file contains the following options:

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Configuration Options

| Key                    | Type    | Description                                                             |
| ---------------------- | ------- | ----------------------------------------------------------------------- |
| `compress_images`      | boolean | Whether to compress images (JPEG/PNG only)                              |
| `default_image_format` | string  | Default format for converted images (JPEG/PNG only) (case-insensitive). |
| `max_image_size`       | integer | Maximum image size in bytes (triggers compression if exceeded)          |

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Default Configuration

If no configuration file is found, FicImage will use the following default settings:

```json
{
  "compress_images": true,
  "default_image_format": "JPEG",
  "max_image_size": 100000
}
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Notes

- **`compress_images`**:

  - If set to `true`, FicImage will try to compress images below **1MB** (unless a specific `max_image_size` is provided).
  - If set to `false`, **FicImage** ignores the `max_image_size` key.

- **`default_image_format`**:

  - If this key is missing, FicImage defaults to **JPEG**.

- **Compression Behavior**:

  - Compressing images might reduce the quality, especially if the image is compressed to a very small size (e.g., 1KB).
  - FicImage tries to compress the image to be smaller than the value specified in `max_image_size`, but **it’s not a hard limit**.

- **GIF and WEBP Compression**:
  - **FicImage** will **not** compress **GIF** or **WEBP** images to preserve the animation.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Why did I build this?

> [!NOTE]
>
> FicHub is a growing set of accessibility tools for reading fanfiction.

[FicHub](https://fichub.net/) is great - it really is. But after one too many times of copying image links to open in my browser, I had to find an alternative. Building this tool wasn't my first thought. I initially found [leech.py](https://github.com/kemayo/leech), but its image support was still a work in progress. After discovering a [PR](https://github.com/kemayo/leech/pull/84) that added basic image support, I expanded on that code, which eventually became the core of what we now call FicImage.

The project wouldn't be where it is today without Iris (FicHub's creator), who helped with the finishing touches by fixing a major bug that prevented v1 from working properly. She also suggested making it a proper package - something I hadn't even considered!

So thank you to Iris for both creating FicHub and helping with this project. Without FicHub, this tool obviously wouldn't exist (lol).

Check out FicHub:
[Website](https://fichub.net/) • [GitHub](https://github.com/FicHub/fichub.net) • [Discord](https://discord.gg/sByBAhX)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Contributing

Fork the repo and get started!

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Wait a minute, who are you?

[FicImage](https://pypi.org/project/FicImageScript/) was built by Emmanuel Jemeni, a Frontend Developer with a passion for Python.

You can find me on various platforms:

- [LinkedIn](https://www.linkedin.com/in/emmanuel-jemeni)
- [GitHub](https://github.com/Jemeni11)
- [Twitter](https://twitter.com/Jemeni11_)
- [BlueSky](https://bsky.app/profile/jemeni11.bsky.social)

If you'd like, you can support me on [GitHub Sponsors](https://github.com/sponsors/Jemeni11/) or [Buy Me A Coffee](https://www.buymeacoffee.com/jemeni11).

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## License

[MIT LICENSE](/LICENSE)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Changelog

[Changelog](/CHANGELOG.md)

<p align="right">(<a href="#readme-top">back to top</a>)</p>
