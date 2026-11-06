FicImage (aka FicImageScript)
=============================

.. image:: /logo.png
   :alt: Logo
   :width: 128
   :height: 128
   :align: center

Enhance your FicHub files with images.

Explore the repo: https://github.com/Jemeni11/FicImage

.. contents:: Table of Contents
   :depth: 1
   :backlinks: top

Introduction
------------

|PyPI Downloads|

FicImage (aka FicImageScript due to naming issues on PyPI) is a tool for
inserting missing images into FicHub files.

It scans the file for image placeholders, downloads the images, and
replaces the placeholders with the actual images.

.. note::

   Only supports EPUB and zipped HTML. PDF/MOBI support is not planned
   (see `Why no PDF/MOBI support?`_).

Features
--------

- Scans FicHub files for image placeholders and replaces them with actual images
- Supports batch processing with the ``--recursive`` flag
- Handles image downloading and basic processing using Pillow
- Supports JPEG, PNG, GIF, WEBP, and SVG (within EPUB 3.3 spec limits)
- Optional image compression for JPEG, PNG and non-animated WEBP
- Customizable via ``ficimage.json`` config file (supports image format,
  compression, max size, zipped html handling)
- Verbose mode for troubleshooting
- Leaves placeholders untouched if an image can't be downloaded
- Avoids breaking animated images (minimal processing on GIFs/WEBPs)

Installation
------------

From PyPI (Recommended)
~~~~~~~~~~~~~~~~~~~~~~~

.. code:: shell

   pip install FicImageScript

From GitHub Releases
~~~~~~~~~~~~~~~~~~~~

1. Download the latest release from the `FicImage GitHub Releases page
   <https://github.com/Jemeni11/FicImage/releases>`__.

2. Depending on your preference, choose one of the following installation
   methods:

   - Using the Wheel File:

     .. code:: shell

        pip install FicImageScript-<version>-py3-none-any.whl

   - Using the Source Tarball File:

     .. code:: shell

        pip install FicImageScript-<version>.tar.gz

   Replace ``<version>`` with the actual version number of the release.

Usage
-----

After installation, run FicImage with the following command:

.. code:: shell

   ficimage -p path/to/file

Where ``path/to/file`` is the path to the FicHub file you want to add images to.

Run ``ficimage -h`` to see all available options:

.. code:: shell

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

Examples
~~~~~~~~

- **Update a single file:**

  .. code:: shell

     ficimage -p path/to/file.epub

- **Update all files in a directory and its subdirectories:**

  .. code:: shell

     ficimage -r path/to/directory

- **Use a custom configuration file:**

  .. code:: shell

     ficimage -p path/to/file.epub -c path/to/ficimage.json

- **Enable verbose output for troubleshooting:**

  .. code:: shell

     ficimage -p path/to/file.epub -V

- **Combine recursive + verbose:**

  .. code:: shell

     ficimage -r path/to/directory -V

- **Zipped HTML with embedded images:**

  .. code:: shell

     ficimage -p path/to/file.zip -c path/to/ficimage.json

  Ensure your ``ficimage.json`` has ``"zip_embed_images": true`` to embed
  images as base64 in the HTML.

- **Check for updates:**

  .. code:: shell

     ficimage -u

- **Show credits and support information:**

  .. code:: shell

     ficimage --credits

- **Display the current version:**

  .. code:: shell

     ficimage -v

Image Support
-------------

FicHub EPUBs are **EPUB 3.3** files, which support these
`image formats <https://www.w3.org/TR/epub-33/#sec-core-media-types>`__ only:

- **JPEG**
- **PNG**
- **GIF**
- **WEBP**
- **SVG**

FicImage handles them as follows:

- **Non-animated images**: Converted to WEBP by default (configurable)
- **Animated GIF/WEBP**: |warning| Currently unsupported (processing breaks
  animations, so FicImage skips converting/compressing them)
- **SVG**: Saved as-is (compression not supported)

If an image download fails, the placeholder URL is left unchanged.
Image processing is powered by `Pillow <https://pillow.readthedocs.io/en/stable/index.html>`__.

**Compression behavior:**

- FicImage tries to compress images below ``max_image_size`` (see
  `Configuration Options`_), but this is not a hard guarantee
- Very small targets (e.g., 1KB) may fail; aim for 100KB+ for reliable results
- Compression may reduce image quality

Configuration
-------------

FicImage uses a **JSON configuration file** (``ficimage.json``) to customize
settings.

FicImage checks for a configuration file in the given directory path. If no
directory path is given, FicImage checks the current directory and then the
Operating System's home directory.

The configuration file contains the following options:

Configuration Options
~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1

   * - Key
     - Type
     - Description
   * - ``compress_images``
     - boolean
     - Whether to compress images (non-animated WEBP/JPEG/PNG only)
   * - ``default_image_format``
     - string
     - Default format for converted images (non-animated WEBP/JPEG/PNG only)
       (case-insensitive).
   * - ``max_image_size``
     - integer
     - Maximum image size in bytes (triggers compression if exceeded)
   * - ``zip_embed_images``
     - boolean
     - When processing zipped HTML: embed images as base64 in the HTML
       instead of writing files to images/

``zip_embed_images`` (Zipped HTML only)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Controls how FicImage stores images when the input is **zipped HTML**.

- ``false`` (default): FicImage saves images as real files and writes them
  into the output ZIP under ``images/``, then updates the HTML to reference
  ``images/<filename>``. This makes it easy to browse/copy image files, but
  you'll usually need to extract the ZIP to view the HTML with its images.

- ``true``: FicImage embeds each image directly into the HTML as a base64
  ``data:`` URI, so the HTML becomes self-contained (no separate image files
  needed). This is handy for sharing a single HTML file and for conversion
  workflows that prefer everything inline.

Trade-offs:

- Embedding increases output size (base64 encoding adds ~33% overhead).
- Embedded images are harder to extract than "normal" image files.

Default Configuration
~~~~~~~~~~~~~~~~~~~~~

If no configuration file is found, FicImage will use the following default
settings:

.. code:: json

   {
     "compress_images": true,
     "default_image_format": "WEBP",
     "max_image_size": 100000,
     "zip_embed_images": false
   }

Why no PDF/MOBI support?
-------------------------

TL;DR: PDF and MOBI support is not planned. Use an EPUB source and convert
with Calibre instead.

I originally planned to support PDF and MOBI, but after testing, I realized
that both formats have limitations that make them unsuitable for this tool:

- PDF: While PDFs can contain images, they are not designed for reflowable
  text and often have complex layouts. Extracting and replacing images in
  PDFs is non-trivial and would require a different approach than what
  FicImage currently uses. The best I could do was for each image, I'd have
  to insert a new page with the image. The images could not be inserted in
  the middle of the text, which is a dealbreaker for me. I want to keep the
  images in their original context. Also, adding PDF support increased the
  size of this by a lot loll (Admittedly, I could have made that an
  optional dependency, but I didn't want to do that either).
- MOBI: I couldn't find a python lib for this, and I didn't want to write
  one from scratch. It also doesn't support images as well as EPUB (and
  Zipped HTML) does.

Really, you're better off using an EPUB source and converting it to PDF or
MOBI with a tool like `Calibre <https://calibre-ebook.com/>`__. This way,
you can use FicImage to add images to the EPUB, then convert it to your
desired format.

Planned Features
----------------

- ☐ **Caching** – Avoid re-downloading the same image multiple times across
  chapters or files
- ☐ **Concurrency** – Download multiple images at once to speed things up
  (with proper race condition handling)
- ☐ **Better aspect ratio handling** – Resize images while preserving their
  original proportions more reliably
- ☐ **Improved WebP usage** – Convert static JPEGs and PNGs to WebP for
  better performance, instead of only using WebP for animated images
- ☐ **Tests** – Start writing tests (sigh)

Why did I build this?
---------------------

.. note::

   FicHub is a growing set of accessibility tools for reading fanfiction.

`FicHub <https://fichub.net/>`__ is great, it really is. But after one too
many times of copying image links to open in my browser, I had to find an
alternative. Building this tool wasn't my first thought. I initially found
`leech.py <https://github.com/kemayo/leech>`__, but its image support was
still a work in progress. After discovering a
`PR <https://github.com/kemayo/leech/pull/84>`__ that added basic image
support, I expanded on that code, which eventually became the core of what
we now call FicImage.

The project wouldn't be where it is today without Iris (FicHub's creator),
who helped with the finishing touches by fixing a major bug that prevented
v1 from working properly. She also suggested making it a proper package and
at the time, I hadn't even considered that.

So thank you to Iris for both creating FicHub and helping with this
project. Without FicHub, this tool obviously wouldn't exist (lol).

Check out FicHub:
`Website <https://fichub.net/>`__ ✦
`GitHub <https://github.com/FicHub/fichub.net>`__ ✦
`Discord <https://discord.gg/sByBAhX>`__

Also, I've built other fanfiction tools like
`FicRadar <https://github.com/Jemeni11/FicRadar/>`__,
`TalesTrove <https://github.com/Jemeni11/TalesTrove>`__ and contributed to
`WebToEpub <https://github.com/dteviot/WebToEpub>`__ and
`Leech.py <https://github.com/kemayo/leech>`__.

Contributing
------------

Fork the repo and get started!

Wait a minute, who are you?
---------------------------

`FicImage <https://pypi.org/project/FicImageScript/>`__ was built by
Emmanuel Jemeni, a Frontend Developer with a passion for Python.

You can find me on various platforms:

- `LinkedIn <https://www.linkedin.com/in/emmanuel-jemeni>`__
- `GitHub <https://github.com/Jemeni11>`__
- `BlueSky <https://bsky.app/profile/jemeni11.bsky.social>`__
- `Twitter <https://twitter.com/Jemeni11_>`__

If you'd like, you can support me on
`GitHub Sponsors <https://github.com/sponsors/Jemeni11/>`__ or
`Buy Me A Coffee <https://www.buymeacoffee.com/jemeni11>`__.

License
-------

`MIT LICENSE <https://github.com/Jemeni11/FicImage/blob/main/LICENSE>`__

Changelog
---------

`Changelog <https://github.com/Jemeni11/FicImage/blob/main/CHANGELOG.md>`__


.. |PyPI Downloads| image:: https://static.pepy.tech/personalized-badge/ficimagescript?period=total&units=NONE&left_color=GREY&right_color=BLUE&left_text=PyPI+downloads
   :alt: PyPI Downloads
   :target: https://pepy.tech/projects/ficimagescript

.. |warning| unicode:: U+26A0 U+FE0F
