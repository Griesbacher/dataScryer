from datascryer.helper.python import python_3

if python_3():
    import urllib.request
    import urllib.error
    import urllib.parse
else:
    import urllib2


def get(url):
    if python_3():
        return urllib.request.urlopen(urllib.request.Request(url))
    else:
        return urllib2.urlopen(urllib2.Request(url))


def quote(string):
    if python_3():
        return urllib.parse.quote(string)
    else:
        return urllib2.quote(string)


def read(response):
    if python_3():
        return response.read().decode('utf8')
    else:
        return response.read()


def post(url, data):
    if isinstance(data, str):
        data = data.encode('utf-8')
    if python_3():
        return urllib.request.urlopen(url, data)
    else:
        return urllib2.urlopen(urllib2.Request(url, data))
