import everything_tool

if __name__ == '__main__':
    with everything_tool.EverythingTool() as tool:
        if not tool:
            print('everything is not running')
        else:
            version = tool.version()
            print(version)

            # result = tool.search("RJ*")
            # print(len(list(result)))

            result = tool.search("*.zip")
            for i in result:
                print(i)
