# Coding conventions

## Code formatting

There are no explicit code formatting conventions since we use `ruff` to enforce a format.

## Docstring format

We use the [NumPy docstring format](https://www.sphinx-doc.org/en/master/usage/extensions/example_numpy.html).
We use `sphinx-autodocs-typehints` to automatically insert type hints into the docstrings.
Our format thus deviates from the default NumPy example given by the link above.
Docstrings should therefore be laid out as follows, including spacing and punctuation:

```python

def foo(x: int, y: float) -> float:
    """Short description.

    Long description.

    With multiple paragraphs.

    Warning
    -------
    Be careful!

    Parameters
    ----------
    x:
        First input.
    y:
        Second input.

    Returns
    -------
    :
        The result.

    Raises
    ------
    ValueError
        If the input is bad.
    IndexError
        If some lookup failed.

    See Also
    --------
    scitacean.bar:
        A bit less foo.

    Examples
    --------
    This is how to use it:

      >>> foo(1, 2)
      3

    And also:

      >>> foo(1, 3)
      6
    """
```

The order of sections is fixed as shown in the example.

- **Short description** (*required*) A single sentence describing the purpose of the function / class.
- **Long description** (*optional*) One or more paragraphs of detailed explanations.
  Can include additional sections like `Warning` or `Hint`.
- **Parameters** (*required for functions*) List of all function arguments including their name but not their type.
  Listing arguments like this can seem ridiculous if the explanation is as devoid of content as in the example.
  But it is still required in order for sphinx to show the types.
- **Returns** (*required for functions*) Description of the return value.
  Required for the same reason as the parameter list.

  For a single return value, neither a name nor type should be given.
  But a colon is required as in the example above in order to produce proper formatting.

  For multiple return values, to produce proper formatting,
  both name and type must be given even though the latter repeats the type annotation:

  ```python

  """
  Returns
  -------
  n: int
      The first return value.
  z: float
      The second return value.
  """
  ```

- **Raises** (*optional*) We generally do not document what exceptions can be raised from a function.
  But if there are some important cases, this section can list those exceptions with an explanation
  of when the exception is raised.
  The exception type is required.
  Note that there are no colons here.
- **See Also** (*optional*) List of related functions and/or classes.
  The function/class name should include the module it is in but without reST markup.
  For simple cases, the explanation can be left out.
  In this case, the colon should be omitted as well and multiple entries must be separated by commas.
- **Examples** (*optional*) Example code given using `>>>` as the Python prompt.
  May include text before, after, and between code blocks.
  Note the spacing in the example.

Some functions can be sufficiently described by a single sentence.
In this case, the 'Parameters' and 'Returns' sections may be omitted and the docstring should be laid out on a single line.
If it does not fit on a single line, it is too complicated.
For example

```python
def bar(self) -> int:
    """Returns the number of dimensions."""
```

Note that the argument types are not shown in the rendered documentation.
