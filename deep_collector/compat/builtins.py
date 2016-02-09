
try:
    from cStringIO import StringIO
except ImportError:
    # Python 3.x
    from io import StringIO


try:
    basestring = basestring
except:
    # Python 3.x
    basestring = (str, bytes)
