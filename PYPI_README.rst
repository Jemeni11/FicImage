FicImage (aka FicImageScript)
=============================

FicImage is an application designed to enhance the reading experience of
FicHub epubs. With FicImage, users can easily add missing images to
their FicHub epubs, bringing the stories to life with vibrant visuals.
This user-friendly tool allows readers to fully immerse themselves in
their favorite fan fiction stories and enjoy them in a whole new way.

How to Use
----------

Installation with PIP
~~~~~~~~~~~~~~~~~~~~~

1. Install FicImage using ``pip install FicImageScript``.
2. After installation, run the program using
   ``ficimage -p path/to/epub -c path/to/ficimage/json`` where
   ``path/to/epub`` is the path to the **FicHub epub** you want to add
   images to and ``path/to/ficimage/json`` is the path to a file called
   **ficimage.json** . ficimage.json lets you configure FicImage. See
   more `in the configuration section below <#configuration>`__.

.. code:: shell

   (virt) nonso@HPEnvy:~/Documents/Code$ ficimage -h
    usage: main.py [-h] [-p PATH_TO_EPUB] [-c CONFIG_FILE_PATH] [-d] [-v] [-r RECURSIVE]

    Update a FicHub epub file with images.

    options:
      -h, --help            show this help message and exit
      -p PATH_TO_EPUB, --path_to_epub PATH_TO_EPUB
                            The path to the FicHub epub file.
      -c CONFIG_FILE_PATH, --config_file_path CONFIG_FILE_PATH
                            The path to the ficimage.json file.
      -d, --debug           Enable debug mode.
      -v, --version         Prints out the current version and quits
      -r RECURSIVE, --recursive RECURSIVE
                            This will update all files in the directory path given and its subdirectories
..

Image Support
~~~~~~~~~~~~~

`FicHub <https://fichub.net/>`__ creates EPUB 3.3 files, which means
that FicImage only save images in the following file format:

- JPEG
- PNG
- GIF
- WEBP
- SVG

See the `Core Media Types Section of the EPUB Version 3.3
Specification <https://www.w3.org/TR/epub-33/#sec-core-media-types>`__
for more information.

While FicImage can save SVG images, it can not compress them because
SVGs are not supported by Pillow.

FicImage uses
`Pillow <https://pillow.readthedocs.io/en/stable/index.html>`__ for
image manipulation and conversion.

By default, FicImage will try and save all non-animated images as JPEGs.

The only animated images that FicImage will save are GIFs and WEBPs.

FicImage does little to no processing on GIFs and WEBPs images. This is
to avoid breaking the animation.

If FicImage can not download an image, it leaves the image url paragraph
the same way it met it.

To configure image support, you will need to create a file called
``ficimage.json``. See the section below for more information.

Configuration
~~~~~~~~~~~~~

FicImage comes with a configuration file that allows you to customize
the program to your liking.

The configuration file is in the `JSON file
format <https://developer.mozilla.org/en-US/docs/Learn/JavaScript/Objects/JSON>`__
and contains the following options:

-  ``compress_images``: A boolean that tells FicImage whether to
   compress images. This is only supported for ``jpeg`` and ``png``
   images.
-  ``default_image_format``: A string that tells FicImage what default
   format to convert and save images in. This is only supported for
   ``jpeg`` and ``png`` images.
-  ``max_image_size``: An integer that tells FicImage the maximum size
   of an image in bytes. If an image is larger than this value, FicImage
   will compress it.

FicImage checks for a configuration file in the given directory path. If
no directory path is given, FicImage checks the current directory and
then the Operating System’s home directory.

If it does not find one, it uses the following defaults:

.. code:: json

   {
       "compress_images": true,
       "default_image_format": "JPEG",
       "max_image_size": 100000
   }

..

   Note: The ``compress_images`` key is a boolean and can only be
   ``true`` or ``false``. Booleans in JSON are written in lowercase.

   Note: If the ``default_image_format`` key does not exist, FicImage
   will default to ``jpeg``. The two image formats are ``jpeg`` and
   ``png``. The ``default_image_format`` key is case-insensitive.

..

   Note: The ``compress_images`` key tells FicImage to compress images.
   This is only supported for ``jpeg`` and ``png`` images. This also
   goes hand-in-hand with the ``max_image_size`` key. If the
   ``compress_images`` key is ``true`` but there’s no ``max_image_size``
   key, FicImage will compress the image to a size less than 1MB
   (1000000 bytes). If the ``max_image_size`` key is present, FicImage
   will compress the image to a size less than the value of the
   ``max_image_size`` key. The ``max_image_size`` key is in bytes.

   If ``compress_images`` is ``false``, FicImage will ignore the
   ``max_image_size`` key.

..

   Warning: Compressing images might make the image quality worse.

   Warning: ``max_image_size`` is not a hard limit. FicImage will try to
   compress the image to the size of the ``max_image_size`` key, but it
   might not be able to compress the image to the exact size of the
   ``max_image_size`` key.

..

   Warning: ``max_image_size`` should not be too small. For instance, if
   you set ``max_image_size`` to 1 000, FicImage will probably not be
   able to compress the image to 1 000 bytes (1 KB). If you set
   ``max_image_size`` to 1 000 000, FicImage will probably be able to
   compress the image to 1 000 000 bytes (1 MB).

   Warning: FicImage will not compress GIFs or WEBPs, that might damage
   the animation.

TODO
----

-  ☒ Improve logs
-  ☐ Conversion to other FicHub supported formats from ePub.
-  ☐ More testing

Contributing
------------

Fork `this repo <https://github.com/Jemeni11/FicImage>`__ and get
started!

Links
-----

-  Me

   `LinkedIn <https://www.linkedin.com/in/emmanuel-jemeni>`__ •
   `GitHub <https://github.com/Jemeni11>`__ •
   `Twitter <https://twitter.com/Jemeni11_>`__

-  FicHub

   `Website <https://fichub.net/>`__ •
   `GitHub <https://github.com/FicHub/fichub.net>`__ •
   `Discord <https://discord.gg/sByBAhX>`__

   Without FicHub, this project would (obviously lol) not exist.

   Thanks to `iris <https://github.com/iridescent-beacon>`__ for helping
   me with this project as well.
