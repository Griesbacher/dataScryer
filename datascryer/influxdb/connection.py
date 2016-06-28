def gen_url(address, db, args, query_type):
    if not str.endswith(address, "/"):
        address += "/"
    return "%s%s?db=%s&%s" % (address, query_type, db, args)


def gen_clean_url(address, query_type):
    if not str.endswith(address, "/"):
        address += "/"
    return "%s%s" % (address, query_type)
