Quick start
===========

cached
------


.. ipython:: python

    from module_utilities import cached

    class Example:
        @cached.prop
        def aprop(self):
            print('setting prop')
            return ['aprop']
        @cached.meth
        def ameth(self, x=1):
            print('seeting ameth')
            return [x]
        @cached.clear
        def method_that_clears(self):
            pass

    x = Example()
    print(x.aprop)
    print(x.aprop)

    print(x.ameth(1))
    print(x.ameth(x=1))

    x.method_that_clears()

    print(x.aprop)



.. ipython:: python

    from module_utilities.docfiller import DocFiller

    d = DocFiller.from_docstring(
        """
        Parameters
        ----------
        x : int
            x param
        y : int
            y param
        z0 | z : int
            z int param
        z1 | z : float
            z float param

        Returns
        -------
        output0 | output : int
            Integer output.
        output1 | output : float
            Float output
        """,
        combine_keys='parameters'
    )

    def func(x, y, z):
        """
        Parameters
        ----------
        {x}
        {y}
        {z0}
        Returns
        --------
        {returns.output0}
        """
        return x + y + z

    func = d()(func)

    print(func.__doc__)



