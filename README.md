# Everything Tool

English | [简体中文](https://github.com/obgnail/everything_tool/blob/master/README.zh-CN.md)

`Everything Tool` is a type-safe Python SDK designed to interface with the `Everything` file search software for Windows. It provides a clean, object-oriented API to harness the full power of Everything's instant search capabilities.



## Requirements

This project uses IPC (Inter-Process Communication) to communicate with `Everything`. Therefore, you must have the **full version** of the `Everything` software installed and running in the background. The Lite version does not support IPC.

- **Download Everything**: You can download it from the [official website](https://www.voidtools.com/en-us/downloads/).



## Usage Example

Here is a basic example demonstrating how to use `Everything Tool` to find the 5 most recently modified Python files on your system.

```python
from everything_tool import Client, Request, Sort, SDKError

try:
    # The client must be used within a 'with' statement to ensure resources are managed correctly.
    with Client() as client:
        print(f"Everything version: {client.version()}")

        # 1. Define which fields to retrieve using Request enums.
        search_flags = (
            Request.FULL_PATH_AND_FILE_NAME | 
            Request.SIZE | 
            Request.DATE_MODIFIED
        )

        # 2. Perform the search with clear, readable parameters.
        results = client.search(
            keywords="*.py", 
            limit=5, 
            flags=search_flags, 
            sort=Sort.DATE_MODIFIED_DESCENDING
        )

        print("\nFound the 5 most recently modified Python files:")
        
        # 3. The results are structured SearchResult objects.
        for item in results:
            size_kb = f"{item.size / 1024:.2f} KB" if item.size is not None else "N/A"
            print(f"- Path: {item.full_path}")
            print(f"  Size: {size_kb}")
            print(f"  Modified: {item.modified_time}")

except FileNotFoundError as e:
    print(f"Error: Could not find Everything64.dll. Please ensure it's in the correct path.\n{e}")
except SDKError as e:
    # Catch specific SDK errors, e.g., if 'Everything' is not running.
    print(f"An SDK error occurred: {e}")
```



## Key Features

### Type-Safe Enums
Instead of using raw integer constants, the SDK provides `Enum` classes for `Request`, `Sort`, and `FileAttribute`. This improves code readability and prevents bugs by allowing static analysis tools and IDEs to catch errors before runtime.

### Structured Results (`SearchResult` Dataclass)
The search methods return an iterator of `SearchResult` objects. This is a read-only `dataclass` that provides attribute-style access to results (e.g., `result.full_path`). It offers a more robust and predictable alternative to dictionaries, with full support for IDE autocompletion.



## API Overview

### Core Search Method
This is the main function for all queries. Convenience wrappers are built on top of it.

```python
def search(
    self,
    keywords: str,
    match_path: bool = False,
    match_case: bool = False,
    whole_word: bool = False,
    regex: bool = False,
    offset: int = 0,
    limit: int = -1,
    flags: Request = Request.DEFAULT,
    sort: Sort = Sort.NAME_ASCENDING
) -> Iterator[SearchResult]:
    ...
```

### Convenience Wrappers
For common search tasks, you can use these helpful methods:
- `search_in_located(path, keywords, **kwargs)`: Search within a specific folder.
- `search_folder(keywords, **kwargs)`: Search for folders only.
- `search_ext(extensions, keywords, **kwargs)`: Search by one or more file extensions.
- `search_audio(keywords, **kwargs)`: Search for common audio files.
- `search_video(keywords, **kwargs)`: Search for common video files.
- `search_image(keywords, **kwargs)`: Search for common image files.
- `search_doc(keywords, **kwargs)`: Search for common document files.



## Reference

### Request Fields (`Request`)
Use these enum members to specify which data fields to retrieve. The default is `Request.DEFAULT`.

| Member                                | Description                                      |
| ------------------------------------- | ------------------------------------------------ |
| `FILE_NAME`                           | File name only                                   |
| `PATH`                                | Path without the file name                       |
| `FULL_PATH_AND_FILE_NAME`             | Full path including the file name                |
| `EXTENSION`                           | File extension                                   |
| `SIZE`                                | File size in bytes                               |
| `DATE_CREATED`                        | Creation date                                    |
| `DATE_MODIFIED`                       | Last modified date                               |
| `DATE_ACCESSED`                       | Last accessed date                               |
| `ATTRIBUTES`                          | File attributes (e.g., Read-only, Hidden)        |
| `RUN_COUNT`                           | How many times the file has been run             |
| `DATE_RUN`                            | The date the file was last run                   |
| `DATE_RECENTLY_CHANGED`               | The date the file was recently changed           |
| `HIGHLIGHTED_FILE_NAME`               | Highlighted file name                            |
| `HIGHLIGHTED_PATH`                    | Highlighted path                                 |
| `HIGHLIGHTED_FULL_PATH_AND_FILE_NAME` | Highlighted full path and file name              |
| `DEFAULT`                             | A composite of `FULL_PATH_AND_FILE_NAME`, `SIZE`, and `DATE_MODIFIED` |
| `ALL`                                 | A composite of all available request flags       |

### Sort Orders (`Sort`)
Use these enum members to control the sort order of the results. The default is `Sort.NAME_ASCENDING`.

| Member                        | Description                   |
| ----------------------------- | ----------------------------- |
| `NAME_ASCENDING` / `DESCENDING` | Sort by file name             |
| `PATH_ASCENDING` / `DESCENDING` | Sort by path                  |
| `SIZE_ASCENDING` / `DESCENDING` | Sort by size                  |
| `EXTENSION_ASCENDING` / `DESCENDING` | Sort by extension             |
| `DATE_CREATED_ASCENDING` / `DESCENDING` | Sort by creation date         |
| `DATE_MODIFIED_ASCENDING` / `DESCENDING` | Sort by modified date         |
| ...and many more              | (See `Sort` enum in code for a full list) |

### File Attributes (`FileAttribute`)
These enum members represent Windows file attributes.

| Member                  | Description                               |
| ----------------------- | ----------------------------------------- |
| `READONLY`              | The file is read-only.                    |
| `HIDDEN`                | The file is hidden.                       |
| `SYSTEM`                | The file is a system file.                |
| `DIRECTORY`             | The item is a directory.                  |
| `ARCHIVE`               | The file is marked for archive.           |
| `COMPRESSED`            | The file is compressed.                   |
| `ENCRYPTED`             | The file is encrypted.                    |
| `REPARSE_POINT`         | The file has an associated reparse point. |



## Search Syntax

This SDK supports the complete `Everything` search syntax. For advanced queries, please refer to the official documentation within the `Everything` application (Help -> Search Syntax). This includes:
- Operators (`!`, `|`, ` `)
- Wildcards (`*`, `?`)
- Modifiers (`file:`, `folder:`, `ext:`)
- Functions (`dm:`, `size:`, `attrib:`)
- And much more.
