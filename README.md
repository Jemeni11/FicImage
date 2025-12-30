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
- [Installation](#installation)
  - [From PyPI (Recommended)](#from-pypi-recommended)
  - [From GitHub Releases](#from-github-releases)
- [Usage](#usage)
  - [Examples](#examples)
- [Image Support](#image-support)
- [Configuration](#configuration)
  - [Configuration Options](#configuration-options)
  - [`zip_embed_images` (Zipped HTML only)](#zip_embed_images-zipped-html-only)
  - [Default Configuration](#default-configuration)
- [Planned Features](#planned-features)
- [Why did I build this?](#why-did-i-build-this)
- [Contributing](#contributing)
- [Wait a minute, who are you?](#wait-a-minute-who-are-you)
- [License](#license)
- [Changelog](#changelog)

## Introduction

[![PyPI Downloads](https://static.pepy.tech/personalized-badge/ficimagescript?period=total&units=NONE&left_color=GREY&right_color=BLUE&left_text=PyPI+downloads)](https://pepy.tech/projects/ficimagescript)

FicImage (aka FicImageScript due to naming issues on PyPI) is a tool for inserting missing images into FicHub files.

It scans the file for image placeholders, downloads the images, and replaces the placeholders with the actual images.

> [!NOTE]
>
> Currently supports EPUB and zipped HTML. PDF/MOBI support is planned (see [Planned Features](#planned-features)).

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Features

- Scans FicHub files for image placeholders and replaces them with actual images
- Supports batch processing with the `--recursive` flag
- Handles image downloading and basic processing using Pillow
- Supports JPEG, PNG, GIF, WEBP, and SVG (within EPUB 3.3 spec limits)
- Optional image compression for JPEG, PNG and non-animated WEBP
- Customizable via `ficimage.json` config file (supports image format, compression, max size, zipped html handling)
- Verbose mode for troubleshooting
- Leaves placeholders untouched if an image can’t be downloaded
- Avoids breaking animated images (minimal processing on GIFs/WEBPs)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Installation

### From PyPI (Recommended)

```shell
pip install FicImageScript
```

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

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Usage

After installation, run FicImage with the following command:

```shell
ficimage -p path/to/file
```

Where `path/to/file` is the path to the FicHub file you want to add images to.

Run `ficimage -h` to see all available options:

```shell
usage: ficimage [-h] [-p PATH] [-c CONFIG_FILE_PATH] [-V] [-v] [-r RECURSIVE] [-u] [--credits]

Update a FicHub file with images.

options:
  -h, --help                show this help message and exit
  -p, --path PATH           The path to the FicHub file.
  -c, --config_file_path CONFIG_FILE_PATH
                            The path to the ficimage.json file.
  -V, --verbose             Enable verbose output
  -v, --version             Prints out the current version and quits.
  -r, --recursive RECURSIVE
                            This will update all files in the directory path given and its subdirectories.
  -u, --update              Check if a new version is available.
  --credits                 Show credits and support information

Made with ❤️ by @Jemeni11 | Run --credits to learn more & show support
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Examples

- **Update a single file:**

  ```shell
  ficimage -p path/to/file.epub
  ```

- **Update all files in a directory and its subdirectories:**

  ```shell
  ficimage -r path/to/directory
  ```

- **Use a custom configuration file:**

  ```shell
  ficimage -p path/to/file.epub -c path/to/ficimage.json
  ```

- **Enable verbose output for troubleshooting:**

  ```shell
  ficimage -p path/to/file.epub -V
  ```

- **Combine recursive + verbose:**

  ```shell
  ficimage -r path/to/directory -V
  ```

- **Zipped HTML with embedded images:**

  ```shell
  ficimage -p path/to/file.zip -c path/to/ficimage.json
  ```

  Ensure your `ficimage.json` has `"zip_embed_images": true` to embed images as base64 in the HTML.

- **Check for updates:**

  ```shell
  ficimage -u
  ```

- **Show credits and support information:**

  ```shell
  ficimage --credits
  ```

- **Display the current version:**

  ```shell
  ficimage -v
  ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Image Support

FicHub EPUBs are **EPUB 3.3** files, which support
these [image formats](https://www.w3.org/TR/epub-33/#sec-core-media-types) only:

- **JPEG**
- **PNG**
- **GIF**
- **WEBP**
- **SVG**

FicImage handles them as follows:

- **Non-animated images**: Converted to WEBP by default (configurable)
- **Animated GIF/WEBP**: ⚠️ Currently unsupported (processing breaks animations, so FicImage skips converting/compressing them)
- **SVG**: Saved as-is (compression not supported)

If an image download fails, the placeholder URL is left unchanged.
Image processing is powered by [Pillow](https://pillow.readthedocs.io/en/stable/index.html)

**Compression behavior:**

- FicImage tries to compress images below `max_image_size` [(see Configuration Options for more info)](#configuration-options), but this is not a hard guarantee
- Very small targets (e.g., 1KB) may fail; aim for 100KB+ for reliable results
- Compression may reduce image quality

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Configuration

FicImage uses a **JSON configuration file** (`ficimage.json`) to customize settings.

FicImage checks for a configuration file in the given directory path. If no directory path is given, FicImage checks the current directory and then the Operating System's home directory.

The configuration file contains the following options:

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Configuration Options

| Key                    | Type    | Description                                                                                         |
| ---------------------- | ------- | --------------------------------------------------------------------------------------------------- |
| `compress_images`      | boolean | Whether to compress images (non-animated WEBP/JPEG/PNG only)                                        |
| `default_image_format` | string  | Default format for converted images (non-animated WEBP/JPEG/PNG only) (case-insensitive).           |
| `max_image_size`       | integer | Maximum image size in bytes (triggers compression if exceeded)                                      |
| `zip_embed_images`     | boolean | When processing zipped HTML: embed images as base64 in the HTML instead of writing files to images/ |

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### `zip_embed_images` (Zipped HTML only)

Controls how FicImage stores images when the input is **zipped HTML**.

- `false` (default): FicImage saves images as real files and writes them into the output ZIP under `images/`, then
  updates the HTML to reference `images/<filename>`. This makes it easy to browse/copy image files, but you’ll usually
  need to extract the ZIP to view the HTML with its images.

- `true`: FicImage embeds each image directly into the HTML as a base64 `data:` URI, so the HTML becomes
  self-contained (no separate image files needed). This is handy for sharing a single HTML file and for conversion
  workflows that prefer everything inline.

Trade-offs:

- Embedding increases output size (base64 encoding adds ~33% overhead).
- Embedded images are harder to extract than "normal" image files.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Default Configuration

If no configuration file is found, FicImage will use the following default settings:

```json
{
  "compress_images": true,
  "default_image_format": "WEBP",
  "max_image_size": 100000,
  "zip_embed_images": false
}
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Planned Features

- [ ] **Caching** – Avoid re-downloading the same image multiple times across chapters or files
- [ ] **Concurrency** – Download multiple images at once to speed things up (with proper race condition handling)
- [ ] **Better aspect ratio handling** – Resize images while preserving their original proportions more reliably
- [ ] **Broader format support** – Add support for other FicHub formats like MOBI and PDF
- [ ] **Improved WebP usage** – Convert static JPEGs and PNGs to WebP for better performance, instead of only using WebP for animated images
- [ ] **Tests** – Start writing tests (sigh)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Why did I build this?

> [!NOTE]
>
> FicHub is a growing set of accessibility tools for reading fanfiction.

[FicHub](https://fichub.net/) is great, it really is. But after one too many times of copying image links to open in my
browser, I had to find an alternative. Building this tool wasn't my first thought. I initially
found [leech.py](https://github.com/kemayo/leech), but its image support was still a work in progress. After discovering
a [PR](https://github.com/kemayo/leech/pull/84) that added basic image support, I expanded on that code, which
eventually became the core of what we now call FicImage.

The project wouldn't be where it is today without Iris (FicHub's creator), who helped with the finishing touches by
fixing a major bug that prevented v1 from working properly. She also suggested making it a proper package and at the
time,
I hadn't even considered that.

So thank you to Iris for both creating FicHub and helping with this project. Without FicHub, this tool obviously
wouldn't exist (lol).

Check out FicHub:
[Website](https://fichub.net/) ✦ [GitHub](https://github.com/FicHub/fichub.net)
✦ [Discord](https://discord.gg/sByBAhX)

Also, I’ve built other fanfiction tools like [FicRadar](https://github.com/Jemeni11/FicRadar/),
[TalesTrove](https://github.com/Jemeni11/TalesTrove) and contributed to
[WebToEpub](https://github.com/dteviot/WebToEpub) and [Leech.py](https://github.com/kemayo/leech).

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Contributing

Fork the repo and get started!

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Wait a minute, who are you?

[FicImage](https://pypi.org/project/FicImageScript/) was built by Emmanuel Jemeni, a Frontend Developer with a passion
for Python.

You can find me on various platforms:

- [LinkedIn](https://www.linkedin.com/in/emmanuel-jemeni)
- [GitHub](https://github.com/Jemeni11)
- [BlueSky](https://bsky.app/profile/jemeni11.bsky.social)
- [Twitter](https://twitter.com/Jemeni11_)

If you'd like, you can support me on [GitHub Sponsors](https://github.com/sponsors/Jemeni11/)
or [Buy Me A Coffee](https://www.buymeacoffee.com/jemeni11).

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## License

[MIT LICENSE](/LICENSE)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Changelog

[Changelog](/CHANGELOG.md)

<p align="right">(<a href="#readme-top">back to top</a>)</p>
