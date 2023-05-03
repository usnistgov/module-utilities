---
jupytext:
  text_representation:
    format_name: myst
kernelspec:
  display_name: Python 3
  name: python3
---

<!-- markdownlint-disable MD041 -->

# Quick start

## Cached

```{code-cell} ipython3

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

```

## docfiller

```{code-cell} ipython3


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

```

```{code-cell} ipython3
@d.assign_keys(z='z0', out='returns.output0')()
def func1(x, y, z):
    """
    Parameters
    ----------
    {x}
    {y}
    {z}

    Returns
    -------
    {out}
    """
    pass

print(func1.__doc__)
```

```{code-cell} ipython3

@d.assign_keys(z='z1', out='returns.output1')(func1)
def func2(x, y, z):
    pass

print(func2.__doc__)
```
