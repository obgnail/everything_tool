import everything

if __name__ == '__main__':
    # version = everything.version()
    # print(version)

    result = everything.search("RJ*")
    a = list(result)
    print(a)

    # result = everything.search_audio("RJ*")
    # a = list(result)
    # print(a)
