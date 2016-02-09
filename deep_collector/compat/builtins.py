
try:
    from cStringIO import StringIO
except ImportError:
    # Python 3.x
    from io import StringIO
