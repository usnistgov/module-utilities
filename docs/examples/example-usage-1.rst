Quick start
===========

cached
------


..
   .. ipython:: python

       from module_utilities import cached


       class Example:
           @cached.prop
           def aprop(self):
               print("setting prop")
               return ["aprop"]

           @cached.meth
           def ameth(self, x=1):
               print("seeting ameth")
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
           """,
           combine_keys="parameters",
       )


   .. ipython:: python

       @d()
       def func(x, y, z):
           """
           Parameters
           ----------
           {x}
           {y}
           {z0}
           """
           return x + y + z


       print(func.__doc__)


       @d.assign_keys(z="z0")()
       def func1(x, y, z):
           """
           Parameters
           ----------
           {x}
           {y}
           {z}
           """
           return x + y + z


       print(func1.__doc__)


       @d.assign_keys(z="z1")(func1)
       def func2(x, y, z):
           return x + y + z


       print(func2.__doc__)
