# Products.ZAlchemyConnector

[![PyPI version](https://badge.fury.io/py/Products.ZAlchemyConnector.svg)](https://badge.fury.io/py/Products.ZAlchemyConnector)

ZAlchemyConnector is a generic database adapter connector and text query wrapper for [Zope] using [SQLAlchemy].
The DA part of this product is basically a wrapper around [z3c.sqlalchemy], which provides easy to use integration with Zope transactions.
The text query wrapper part, works similarly to ZSQLMethods, but using SQLAlchemy syntax on SQL text for binding and replacing variables.

#### Why use this product?
 - If you already use SQL files and do not want to change everything to ORM.
     - This product offers the object Query, which executes text SQL querys over SQLAlchemy.
- If  you do not want to create and DA and save it on ZODB.
    - This product offers the object Wrapper, which allow you to create a database adapter inside another Zope product.

## Requirements
* z3c.sqlalchemy > 1.5.1
* SQLAlchemy >= 0.5.5
* zope.sqlalchemy >= 1.2.0
* zope.component
* zope.interface
* zope.schema
* zope.testing

## Installation
Using pip:
```sh
pip install Products.ZAlchemyConnector
```
## How to use
There's two ways to use this product, first is using the database adapter and second is using the Query object.

### Wrapper
This is an example product using the wrapper class as the database adapter.
```Python
from Products.ZAlchemyConnector.Wrapper import Wrapper
from OFS.SimpleItem import SimpleItem

class Example(SimpleItem):
    meta_type = "Example"

    def __init__(self, id, DBUrl):
        self.id = id
        self.DBUrl = DBUrl
        self.wrapper = None
        self.CreateWrapper()

    def CreateWrapper(self):
        self.wrapper = Wrapper(
            id="wrapper", dsn=self.DBUrl,
            engine_options=(("isolation_level", "REPEATABLE READ"),
                            ("encoding", "8859")))

   [...]
```
Let's go over the code, this time with explanations.
So, the code above, basically creates a Zope Product named Example, which can be written on ZODB.
The attributes ``wrapper`` and ``DBUrl`` are the most important for our example.
 - ``wrapper`` - Stores the instance from the class Wrapper which we imported.
 - ``DBUrl`` - Stores the url location for your database. This url should be formatted according to [SQLAlchemy engine] url specifications.
 
 Now that we have the url, we can call the ``CreateWrapper`` method, which will create an instance of the ``Wrapper`` class and put it in ``self.wrapper``.
 The ``Wrapper`` class receives three parameters:
 
 - ``id`` - This is the ID of the instance. This is useful in case of error, since this ID is used by [SiteErrorLog] product.
 - ``dsn`` - This is the url we have stored in the ``DBUrl`` attribute.
 - ``engine_options`` - This receives other [SQLAlchemy engine] configurations.

After creating this instance, we can now access this wrapper from anywhere inside the ``Example`` product. Here's an example on how to run a query using it:
```Python
from Products.ZAlchemyConnector.Wrapper import Wrapper
from OFS.SimpleItem import SimpleItem
from zope.sqlalchemy import mark_changed

class Example(SimpleItem):
[...]
    def RunTestExample(self):
        session = self.wrapper.get_wrapper().session
        mark_changed(session)
        response = session.execute("Select * from example")
        print(response.fetchall())
```
As you can see on the ``RunTestExample`` method, you just need to use the convenience function ``get_wrapper()`` to get access to the SQLAlchemy ``session`` and execute whatever query you want on the database.

### Query
The ``Query`` class should be used with the ``Wrapper`` class of this product. The query object basically does everything we did inside the ``RunTestExample`` method behind the scene. 
The code bellow is the rewritten version of ``RunTestExample``, but this time it's using the ``Query`` class 

```Python
from Products.ZAlchemyConnector.Wrapper import Wrapper
from Products.ZAlchemyConnector.Query import Query
from OFS.SimpleItem import SimpleItem

class Example(SimpleItem):
[...]
    def RunTestExample(self):
        _select = Query(
            id="select", get_wrapper=self.wrapper.get_wrapper,
            template="Select * from example")

        print(_select())
```
Another reason you should use the ``Query`` class is that it tries to enforce the types of the parameter you pass to the query, as shown bellow. 
```Python
from Products.ZAlchemyConnector.Wrapper import Wrapper
from Products.ZAlchemyConnector.Query import Query
from OFS.SimpleItem import SimpleItem

class Example(SimpleItem):
[...]
    def RunTestExampleWithParams(self):
        _select = Query(
            id="select_with_params",
            get_wrapper=self.wrapper.get_wrapper,
            template="Select * from example where id_example = :id_example",
            arguments=[{"type": "int", "key": "id_example"}])

        print(_select(id_example=5))
```
In the ``arguments`` parameter, you can pass a ``list`` of ``dicts`` with the configuration for each argument for your query. 

In the example code, we are telling the ``Query`` object it will receive a parameter named ``id_example`` and that this parameter should be an ``int``.

Behind the scenes, the ``Query`` object will bind the ``key`` received with the ``type`` informed and the variable inside our template.

Next, when we make the call for the variable (``_select(id_example=5)``), the ``Query`` class will try to enforce the type we told it on the ``arguments`` parameter. In this case, it'll force the ``id_example`` to be an ``int``.
If this fails, the object will throw an ``QueryTypeError`` exception.

Another way it can fail is if you feed an parameter you haven't configured on the ``arguments`` parameter. In this case it will throw an ``QueryParamaterError`` exception.

Otherwise, after the line ``print(_select(id_example=5))``, it'll print the results of the query.
The results are stored in the object ``Results``, which is a subclass of ``UserList`` and each line returned from the query is a ``NamedTuple``, which allows the access to theirs values using the name of the columns as an attribute. E.g. ``_select[0].id_example``.

#### Query parameters

 - ``id`` - ID of the instance, useful for debugging. (Required)
 - ``get_wrapper`` - Receives the function ``get_wrapper`` from the instance of ``Wrapper``. (Required)
 - ``template`` - Receives the SQL string we will run. (Required)
 - ``max_rows`` - Max number of rows to return, if set to ``0`` it will return everything. Defaults to ``0``
 - ``arguments`` - List of dictionaries with the arguments used for the template. Defaults to ``None``
 
#### Arguments configuration
 - ``type`` - The type to be enforced on the key. There are 3 enforceable,  ``int``, ``string`` and ``float``. (Required)
 - ``key`` - Name of the parameter and what will be replaced in the template. (Required)
 - ``multiple`` - If set to ``True``, it's going to be transformed in a ``Tuple`` with elements of the ``type`` informed. Defaults to ``False``.

## Author
Products.ZAlchemyConnector was written by Gabriel Diniz Gisoldo for SoftRH, S&atilde;o Paulo, Brazil.

## License
Products.ZAlchemyConnector is licensed under the MIT license. See LICENSE

[z3c.sqlalchemy]: https://github.com/zopefoundation/z3c.sqlalchemy "z3c.sqlalchemy"
[SQLAlchemy]: https://www.sqlalchemy.org/ "SQLAlchemy"
[Zope]: https://zope.readthedocs.io "Zope"
[SQLAlchemy engine]: https://docs.sqlalchemy.org/en/13/core/engines.html#sqlalchemy.create_engine "Url for SQLAlchemy engine"
[SiteErrorLog]: https://github.com/zopefoundation/Products.SiteErrorLog "Products.SiteErrorLog"
