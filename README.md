# Everything Tool 

English | [简体中文](https://github.com/obgnail/everything_tool/blob/master/README.zh-CN.md)

`Everything Tool` is a Python SDK designed to interface with the `Everything` file search software for Windows. 



## Requirements

This project uses IPC to communicate with `Everything`. You need to download the full version of `Everything` software. The lite version does not support IPC. Click [here](https://www.voidtools.com/en-us/downloads/) to download the full version. Ensure that `Everything` is running in the background.



## Usage Example

Here is a basic example demonstrating how to use `Everything Tool` to search for files:

```python
import everything_tool as et

def search():
    try:
        with et.Client() as client:
            print(f'Everything version: {client.version()}')

            flags = et.REQUEST_FILE_NAME | et.REQUEST_SIZE
            sort = et.SORT_SIZE_DESCENDING
            limit = 2
            for file in client.search_ext(keywords='py', ext=['exe', 'msi'], flags=flags, sort=sort, limit=limit):
                print(file)
    except (AttributeError, et.Error) as e:
        print('Error:', e)

if __name__ == '__main__':
    search()
```



## Search Syntax

`Everything Tool` supports all `Everything` search syntax. Refer to `Everything`’s help documentation for detailed search syntax. Below are some common features:

- Operators
- Wildcards
- Macros
- Modifiers
- Functions
- Function syntax
- Size syntax
- Size constants
- Date syntax
- Date constants
- Property constants



## Search Function and Its Derivatives

`Everything Tool` provides a series of search functions. Here is the definition and description of the `search` function and its derivatives:

```python
def search(
    self,
    keywords: str,
    math_path: bool = False,
    math_case: bool = False,
    whole_word: bool = False,
    regex: bool = False,
    offset: int = 0,
    limit: int = -1,
    flags: [int, Iterable[int]] = DEFAULT_FLAGS,
    sort: int = SORT_NAME_ASCENDING
) -> Iterable[Dict]:
    """
    Search files using Everything
    :param keywords: Search keyword, supports all Everything search syntax
    :param math_path: Match path
    :param math_case: Case sensitive
    :param whole_word: Whole word match
    :param regex: Use regular expression
    :param offset: Offset
    :param limit: Maximum number, <0 means search all
    :param flags: Query fields
    :param sort: Sort order
    :return: Generator of record dictionaries
    """
    pass

def search_in_located(self, path, keywords='', **kwargs):
    """Search files in a specific path"""
    return self.search(f'{path} {keywords}', **kwargs)

def search_folder(self, keywords='', **kwargs):
    """Search folders"""
    return self.search(f'folder: {keywords}', **kwargs)

def search_ext(self, ext, keywords='', **kwargs):
    """Search by file extension"""
    return self.search(f'ext:{ext} {keywords}', **kwargs)

def search_audio(self, keywords='', **kwargs):
    """Search audio files"""
    return self.search_ext(f'{self.audio_ext} {keywords}', **kwargs)

def search_compressed(self, keywords='', **kwargs):
    """Search compressed files"""
    return self.search_ext(f'{self.compressed_ext} {keywords}', **kwargs)

def search_doc(self, keywords='', **kwargs):
    """Search documents"""
    return self.search_ext(f'{self.doc_ext} {keywords}', **kwargs)

def search_exe(self, keywords='', **kwargs):
    """Search executable files"""
    return self.search_ext(f'{self.exe_ext} {keywords}', **kwargs)

def search_pic(self, keywords='', **kwargs):
    """Search image files"""
    return self.search_ext(f'{self.pic_ext} {keywords}', **kwargs)

def search_video(self, keywords='', **kwargs):
    """Search video files"""
    return self.search_ext(f'{self.video_ext} {keywords}', **kwargs)
```



## Supported Query Fields

`Everything Tool` supports all query fields from `Everything`. Here are some common fields:

```python
REQUEST_FILE_NAME = 0x00000001  # File name
REQUEST_PATH = 0x00000002  # Path without file name
REQUEST_FULL_PATH_AND_FILE_NAME = 0x00000004  # Full path with file name
REQUEST_EXTENSION = 0x00000008  # Extension
REQUEST_SIZE = 0x00000010  # Size (byte)
REQUEST_DATE_CREATED = 0x00000020  # Creation date
REQUEST_DATE_MODIFIED = 0x00000040  # Modified date
REQUEST_DATE_ACCESSED = 0x00000080  # Accessed date
REQUEST_ATTRIBUTES = 0x00000100  # Attributes
REQUEST_FILE_LIST_FILE_NAME = 0x00000200  # File list name
REQUEST_RUN_COUNT = 0x00000400  # Run count
REQUEST_DATE_RUN = 0x00000800  # Last run date
REQUEST_DATE_RECENTLY_CHANGED = 0x00001000  # Recently changed date
REQUEST_HIGHLIGHTED_FILE_NAME = 0x00002000  # Highlighted file name
REQUEST_HIGHLIGHTED_PATH = 0x00004000  # Highlighted path without file name
REQUEST_HIGHLIGHTED_FULL_PATH_AND_FILE_NAME = 0x00008000  # Highlighted full path with file name
```

Default query fields:

```python
DEFAULT_FLAGS = (
        REQUEST_FULL_PATH_AND_FILE_NAME
        | REQUEST_SIZE
        | REQUEST_DATE_MODIFIED
)
```



## Supported File Attributes

Here are the supported file attributes:

```python
# See more: https://learn.microsoft.com/en-us/windows/win32/fileio/file-attribute-constants
FILE_ATTRIBUTE_READONLY = 0x00000001
FILE_ATTRIBUTE_HIDDEN = 0x00000002
FILE_ATTRIBUTE_SYSTEM = 0x00000004
FILE_ATTRIBUTE_DIRECTORY = 0x00000010
FILE_ATTRIBUTE_ARCHIVE = 0x00000020
FILE_ATTRIBUTE_DEVICE = 0x00000040
FILE_ATTRIBUTE_NORMAL = 0x00000080
FILE_ATTRIBUTE_TEMPORARY = 0x00000100
FILE_ATTRIBUTE_SPARSE_FILE = 0x00000200
FILE_ATTRIBUTE_REPARSE_POINT = 0x00000400
FILE_ATTRIBUTE_COMPRESSED = 0x00000800
FILE_ATTRIBUTE_OFFLINE = 0x00001000
FILE_ATTRIBUTE_NOT_CONTENT_INDEXED = 0x00002000
FILE_ATTRIBUTE_ENCRYPTED = 0x00004000
```



## Supported Sort Orders

Here are the supported sort orders:

```python
SORT_NAME_ASCENDING = 1  # Default
SORT_NAME_DESCENDING = 2
SORT_PATH_ASCENDING = 3
SORT_PATH_DESCENDING = 4
SORT_SIZE_ASCENDING = 5
SORT_SIZE_DESCENDING = 6
SORT_EXTENSION_ASCENDING = 7
SORT_EXTENSION_DESCENDING = 8
SORT_TYPE_NAME_ASCENDING = 9
SORT_TYPE_NAME_DESCENDING = 10
SORT_DATE_CREATED_ASCENDING = 11
SORT_DATE_CREATED_DESCENDING = 12
SORT_DATE_MODIFIED_ASCENDING = 13
SORT_DATE_MODIFIED_DESCENDING = 14
SORT_ATTRIBUTES_ASCENDING = 15
SORT_ATTRIBUTES_DESCENDING = 16
SORT_FILE_LIST_FILENAME_ASCENDING = 17
SORT_FILE_LIST_FILENAME_DESCENDING = 18
SORT_RUN_COUNT_ASCENDING = 19
SORT_RUN_COUNT_DESCENDING = 20
SORT_DATE_RECENTLY_CHANGED_ASCENDING = 21
SORT_DATE_RECENTLY_CHANGED_DESCENDING = 22
SORT_DATE_ACCESSED_ASCENDING = 23
SORT_DATE_ACCESSED_DESCENDING = 24
SORT_DATE_RUN_ASCENDING = 25
SORT_DATE_RUN_DESCENDING = 26
```

