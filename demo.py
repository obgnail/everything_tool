import everything_tool as et


def search():
    try:
        with et.EverythingTool() as tool:

            version = tool.version()
            print(f'everything version: {version}')

            keywords = 'tel'  # 搜索关键词
            flags = et.EVERYTHING_REQUEST_FILE_NAME | et.EVERYTHING_REQUEST_SIZE  # 查询文件名和文件大小
            sort = et.EVERYTHING_SORT_SIZE_DESCENDING  # 搜索结果以大小降序排列
            for file in tool.search_ext(keywords=keywords, ext=['exe', 'msi'], flags=flags, sort=sort):
                print(file)

    except (AttributeError, et.EverythingError) as e:
        print('error:', e)


if __name__ == '__main__':
    search()
