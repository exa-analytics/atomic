.. Copyright (c) 2015-2019, Exa Analytics Development Team
.. Distributed under the terms of the Apache License 2.0

.. _dev-label:

Development
#############

Environment
-----------
For a development ready installation::

    git clone https://github.com/exa-analytics/exatomic.git
    cd exatomic
    pip install -e .
    jupyter nbextension install --py --symlink --sys-prefix exatomic
    jupyter nbextension enable --py --sys-prefix exatomic

Note that this requires npm. On Windows, symlinks will not work but as a work-
around, extensions can be recompiled and reinstalled upon edits without the
need to reinstall the package.

Contributing
------------

Pull requests are welcome!
