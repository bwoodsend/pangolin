.. py:currentmodule:: pangolin

===============
:class:`Palmer`
===============

.. autoclass:: Palmer

    .. automethod:: __init__

    .. autoattribute:: arch_type
    .. autoattribute:: side
    .. autoattribute:: index
    .. autoattribute:: sub_index
    .. autoattribute:: primary
    .. autoattribute:: species

    .. autoattribute:: kind
    .. autoattribute:: KINDS
    .. autoattribute:: jaw_type
    .. automethod:: match

    .. autoattribute:: pangolin.Palmer.regex
        :annotation:

        The compiled regex :ref:`re.Pattern <re-objects>` used
        to parse palmers from strings.
        :ref:`Regex matches <match-objects>` derived from this pattern may be
        passed directly to :meth:`__init__`::

            >>> text = "The LL5 is more distal than the LL3."

            # Extract all palmers from a piece of text.
            >>> [Palmer(match) for match in Palmer.regex.finditer(text)]
            [Palmer('LL5'), Palmer('LL3')]

            # Find/replace all palmers swapping left and right.
            >>> Palmer.regex.sub(lambda m: str(-Palmer(m)), text)
            'The LR5 is more distal than the LR3.'

            # Find/replace all palmers, converting to upper teeth.
            >>> Palmer.regex.sub(lambda m: str(Palmer(m).with_(arch_type="U")), text)
            'The UL5 is more distal than the UL3.'

            # Find/replace all palmers, converting to equivalent baby teeth.
            >>> Palmer.regex.sub(lambda m: str(Palmer(m).with_(primary=True)), text)
            'The LLE is more distal than the LLC.'

    .. autoattribute:: quadrant
    .. automethod:: to_FDI
    .. automethod:: to_symbol
    .. automethod:: to_universal
    .. automethod:: with_
