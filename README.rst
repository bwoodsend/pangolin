========
pangolin
========

..
    This site auto-generates the little python version badges from url.
    The required  format is:
    https://img.shields.io/badge/[text_block_1]-[text_block_2]-[html_named_color].svg

    It helps to pad with spaces. Characters need to be url escaped (can be done
    using urllib).

    from urllib.parse import quote
    "https://img.shields.io/badge/" + quote("python- {}-blue.svg".format(\
                " | ".join(["3.6", "3.7", "3.8", "3.9", "PyInstaller"])))

.. image::
    https://img.shields.io/badge/
    Python-%203.6%20%7C%203.7%20%7C%203.8%20%7C%203.9%20%7C%20PyInstaller-blue.svg

Tools for parsing and writing Dental Palmer notation.


* Free software: MIT license
* Documentation: https://pangolin.readthedocs.io.



Installation
------------

Releases are hosted on PyPI_. To install pangolin, run
the following in your terminal:

.. code-block:: console

    pip install pangolin

.. _PyPI: https://pypi.org/project/pangolin/


Quickstart
----------

Check out our `quickstart page on readthedocs
<https://pangolin.readthedocs.io/en/latest/quickstart.html>`_
to get started.


Credits
-------

This package was initially created with Cookiecutter_ and a fork of the
`audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
