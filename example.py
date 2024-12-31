import everything_tool as et


def search():
    try:
        with et.Client() as client:
            print(f'everything version: {client.version()}')

            flags = et.REQUEST_FILE_NAME | et.REQUEST_SIZE
            sort = et.SORT_SIZE_DESCENDING
            limit = 2
            for file in client.search_ext(keywords='py', ext=['exe', 'msi'], flags=flags, sort=sort, limit=limit):
                print(file)
    except (AttributeError, et.Error) as e:
        print('error:', e)


if __name__ == '__main__':
    search()
