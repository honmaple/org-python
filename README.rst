    :Author: jianglin

.. contents::

1 org-python
------------

An orgmode parser for converting orgmode to html based on python.

.. image:: https://img.shields.io/badge/pypi-v0.2.0-brightgreen.svg
    :target: https://pypi.python.org/pypi/org-python
.. image:: https://img.shields.io/badge/python-3-brightgreen.svg
    :target: https://python.org
.. image:: https://img.shields.io/badge/license-BSD-blue.svg
    :target: LICENSE

1.1 quickstart
~~~~~~~~~~~~~~

.. code:: sh

    pip install org-python

.. code:: python

    from orgpython import org_to_html

    text = '''* heading
    - list1
    - list2
    - list3
      - list4
    - list5

      | th1-1  | th1-2  | th1-3  |
      |--------+--------+--------|
      | row1-1 | row1-2 | row1-3 |
      | row2-1 | row2-2 | row2-3 |
      | row3-1 | row3-2 | row3-3 |
    '''
    print(org_to_html(text,offset=0))

1.2 feature
~~~~~~~~~~~

- ☑ toc

- ☑ heading

  ::

      * headind 1
      ** headind 2
      *** headind 3
      **** headind 4
      ***** headind 5
      ****** headind 6

- ☑ unordered\_list

  ::

      - list
      - list
        - list
          + list
        - list

- ☑ ordered\_list

  ::

      1. list
      2. list
      3. list

- ☑ bold

  ::

      *bold*

- ☑ italic

  ::

      **italic**

- ☑ underlined

  ::

      _italic_

- ☑ code

  ::

      =code=

- ☑ delete

  ::

      +delete+

- ☑ image

  ::

      [[src][alt]]

- ☑ link

  ::

      [[href][text]]

- ☑ begin\_example

- ☑ begin\_src

- ☑ begin\_quote

- ☑ table

  ::

      | th1-1  | th1-2  | th1-3  |
      |--------+--------+--------|
      | row1-1 | row1-2 | row1-3 |
      | row2-1 | row2-2 | row2-3 |
      | row3-1 | row3-2 | row3-3 |
