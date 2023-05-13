import everything

if __name__ == '__main__':
    with everything.EverythingTool() as tool:
        if not tool:
            print('everything is not running')
        else:
            version = tool.version()
            print(version)

            result = tool.search("RJ*")
            print(len(list(result)))

            result = tool.search_audio("RJ*")
            for i in result:
                print(i)
