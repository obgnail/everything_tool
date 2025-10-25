import everything_tool as et


def search():
    try:
        with et.Client() as client:
            print(f"Everything version: {client.version()}")

            print("\nSearching for first 5 '*.py' files, sorted by modified date:")
            search_flags = et.Request.FULL_PATH_AND_FILE_NAME | et.Request.SIZE | et.Request.DATE_MODIFIED
            results = client.search(
                "*.py",
                limit=5,
                flags=search_flags,
                sort=et.Sort.DATE_MODIFIED_DESCENDING
            )
            for item in results:
                size_kb = f"{item.size / 1024:.2f} KB" if item.size is not None else "N/A"
                print(f"- Path: {item.full_path}")
                print(f"  Size: {size_kb}")
                print(f"  Modified: {item.modified_time}")

    except FileNotFoundError:
        print("Error: Everything64.dll not found. Please place it in the correct directory.")
    except et.SDKError as e:
        print(f"An SDK error occurred: {e}")


if __name__ == '__main__':
    search()
