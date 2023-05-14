import everything_tool

if __name__ == '__main__':
    with everything_tool.EverythingTool() as tool:
        if not tool:
            print('everything is not running')
        else:
            version = tool.version()
            print(f'version: {version}')

            for file in tool.search(".zip", limit=3):
                print(file)

            flags = (everything_tool.EVERYTHING_REQUEST_FILE_NAME
                     | everything_tool.EVERYTHING_REQUEST_ATTRIBUTES)
            for file in tool.search_audio('aaa', math_case=True, flags=flags):
                print(file)
