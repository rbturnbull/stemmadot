================================================================
stemmadot
================================================================

.. start-badges

|testing badge| |coverage badge| |docs badge| |black badge|

.. |testing badge| image:: https://github.com/rbturnbull/stemmadot/actions/workflows/testing.yml/badge.svg
    :target: https://github.com/rbturnbull/stemmadot/actions

.. |docs badge| image:: https://github.com/rbturnbull/stemmadot/actions/workflows/docs.yml/badge.svg
    :target: https://rbturnbull.github.io/stemmadot
    
.. |black badge| image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black
    
.. |coverage badge| image:: https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/rbturnbull/7e847e177b0b427bfb0fe89bd2f6be5a/raw/coverage-badge.json
    :target: https://rbturnbull.github.io/stemmadot/coverage/

.. end-badges

.. start-quickstart

Visualization of STEMMA phylogenetic output.

STEMMA is a phylogenetic analysis tool for the study of textual traditions with contamination. 
It is available here: https://github.com/stemmatic/stemma
For more information about it, see Carslon's work:

    Carlson, Stephen C. *The Text of Galatians and Its History*. Wissenschaftliche Untersuchungen Zum Neuen Testament 385. Tübingen: Mohr Siebeck, 2015.

STEMMA input files can be generated from TEI XML using teiphy: https://github.com/jjmccollum/teiphy

For more information see: 
Joey McCollum and Robert Turnbull, "teiphy: A Python Package for Converting TEI XML Collations to NEXUS and Other Formats," JOSS 7.80 (2022): 4879, DOI: 10.21105/joss.04879.


Installation
==================================

Install using pip:

.. code-block:: bash

    pip install git+https://github.com/rbturnbull/stemmadot.git


Usage
==================================

Create the .STEM file using the `soln` executable from STEMMA.

Then run stemmadot:

.. code-block:: bash

    stemmadot <stemfile> <outputfile>

This will create a .dot file which can be visualized using Graphviz like in these examples:

.. code-block:: bash

    dot -Tpng <outputfile> -o <outputfile>.png
    dot -Tsvg <outputfile> -o <outputfile>.svg
    dot -Tpdf <outputfile> -o <outputfile>.pdf

You can reroot the tree using the ``--root`` option:

.. code-block:: bash

    stemmadot <stemfile> <outputfile> --root <root>

The root will be colored red by default and you can specify the color of other nodes using the ``--root-color`` option:

.. code-block:: bash

    stemmadot <stemfile> <outputfile> --root <root> --root-color <color>

Hypothetical nodes will be colored gray by default and you can specify the color of other nodes using the ``--hypothetical-node-color`` option:

.. code-block:: bash

    stemmadot <stemfile> <outputfile> --hypothetical-node-color <color>

You can specify other colors for nodes by creating a ``.toml`` file with regex patterns as keys and the corresponding colors as values. For example:

.. code-block:: toml

    # Lectionaries
    "L.*" = "blue"
    # 8079
    0150K = "red"
    2110K = "red"
    # 6209
    606K = "orange"
    1963K = "orange"
    1996K = "orange"
    1999K = "orange"
    2012K = "orange"

This is given to stemmadot using the ``--colors`` option:

.. code-block:: bash

    stemmadot <stemfile> <outputfile>

Edges representing mixutre (i.e. or 'contamination') will be colored red by default and you can specify the color of other edges using the ``--mixture-edge-color`` option.
Also, mixture with less than 33% will show in dotted lines and mixture with less than 66% will show in dashed lines. These can be changed with the ``--dotted`` and ``--dashed`` options respectively.

.. end-quickstart

Credits
==================================

.. start-credits

Robert Turnbull
For more information contact: <robert.turnbull@unimelb.edu.au>

STEMMA was created by Stephen Carlson (Australian Catholic University). If you use it, please cite Carlson's work:

    Carlson, Stephen C. *The Text of Galatians and Its History*. Wissenschaftliche Untersuchungen Zum Neuen Testament 385. Tübingen: Mohr Siebeck, 2015.

Help for this project came from Peter Montoro.

.. end-credits

