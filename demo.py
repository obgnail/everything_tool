import everything_tool

if __name__ == '__main__':
    try:
        with everything_tool.EverythingTool() as tool:
            version = tool.version()
            print(f'version: {version}')

            for file in tool.search(".zip", limit=3):
                print(file)

            flags = (everything_tool.EVERYTHING_REQUEST_FILE_NAME
                     | everything_tool.EVERYTHING_REQUEST_ATTRIBUTES)
            for file in tool.search_audio('aaa', math_case=True, flags=flags):
                print(file)
    except (AttributeError, everything_tool.EverythingError) as e:
        print('error:', e)
