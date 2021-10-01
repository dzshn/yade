# yade
Simple debug extension for d.py

## setup
There's no released package as of now, but using the repo should work:
* With [poetry](https://python-poetry.org/): `poetry add git+https://github.com/dzshn/yade#main`
* With pip: `pip install git+https://github.com/dzshn/yade`

## usage

On whatever bot you have, add this to the main script (e.g. on `__main__.py`, `bot.py` etc):

```python
bot.load_extension('yade')
```

Alternatively, to run this extension only, you can use `python -m yade [BOT_TOKEN]`.


## commands

TBD...
