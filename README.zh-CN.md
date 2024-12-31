# Everything Tool

[English](https://github.com/obgnail/everything_tool/blob/master/README.md) | 简体中文


`Everything Tool` 是一个适用于 Python 的 SDK，用于与 Windows 下的文件查找软件 `Everything` 进行通讯。



## 环境要求

本项目使用 IPC 与 `Everything` 通讯，需要下载完整版的 `Everything` 软件。精简版的 `Everything` 不支持 IPC，点击[这里](https://www.voidtools.com/zh-cn/downloads/)下载完整版。 请确保 `Everything` 在后台运行。



## 示例

```python
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
```



## 搜索语法

`Everything Tool` 支持所有 `Everything` 语法。有关详细的搜索语法，请参考 `Everything` 的帮助文档。以下是一些常见功能：

- 操作符
- 通配符
- 宏
- 修饰符
- 函数
- 函数语法
- 大小语法
- 大小常数
- 日期语法
- 日期常数
- 属性常数



## Search 函数及其派生函数

`Everything Tool` 提供了一系列搜索函数，以下是 `search` 函数及其派生函数的定义和说明：

```python
def search(
        self,
        keyword: str,
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
    Everything 搜索文件
    :param keyword: 搜索关键字，支持所有 Everything 搜索语法
    :param match_path: 匹配路径
    :param match_case: 区分大小写
    :param whole_word: 全字匹配
    :param regex: 使用正则表达式
    :param offset: 偏移量
    :param limit: 最大数目，<0 则查询所有
    :param flags: 查询字段
    :param sort: 排序
    :return: 记录字典的生成器
    """
    pass

def search_in_located(self, path, keywords='', **kwargs):
    """搜索路径下文件"""
    return self.search(f'{path} {keywords}', **kwargs)

def search_folder(self, keywords='', **kwargs):
    """搜索文件夹"""
    return self.search(f'folder: {keywords}', **kwargs)

def search_ext(self, ext, keywords='', **kwargs):
    """搜索扩展名称"""
    return self.search(f'ext:{ext} {keywords}', **kwargs)

def search_audio(self, keywords='', **kwargs):
    """搜索音频文件"""
    return self.search_ext(f'{self.audio_ext} {keywords}', **kwargs)

def search_compressed(self, keywords='', **kwargs):
    """搜索压缩文件"""
    return self.search_ext(f'{self.compressed_ext} {keywords}', **kwargs)

def search_doc(self, keywords='', **kwargs):
    """搜索文档"""
    return self.search_ext(f'{self.doc_ext} {keywords}', **kwargs)

def search_exe(self, keywords='', **kwargs):
    """搜索可执行文件"""
    return self.search_ext(f'{self.exe_ext} {keywords}', **kwargs)

def search_pic(self, keywords='', **kwargs):
    """搜索图片"""
    return self.search_ext(f'{self.pic_ext} {keywords}', **kwargs)

def search_video(self, keywords='', **kwargs):
    """搜索视频"""
    return self.search_ext(f'{self.video_ext} {keywords}', **kwargs)
```



## 支持查询的字段

`Everything Tool` 支持 `Everything` 的全部查询字段。以下是一些常见字段：

```python
REQUEST_FILE_NAME = 0x00000001  # 文件名
REQUEST_PATH = 0x00000002  # 不含文件的路径
REQUEST_FULL_PATH_AND_FILE_NAME = 0x00000004  # 包含文件名的路径
REQUEST_EXTENSION = 0x00000008  # 拓展名
REQUEST_SIZE = 0x00000010  # 大小(byte)
REQUEST_DATE_CREATED = 0x00000020  # 创建时间
REQUEST_DATE_MODIFIED = 0x00000040  # 修改时间
REQUEST_DATE_ACCESSED = 0x00000080  # 访问时间
REQUEST_ATTRIBUTES = 0x00000100  # 属性
REQUEST_FILE_LIST_FILE_NAME = 0x00000200  # 文件列表名
REQUEST_RUN_COUNT = 0x00000400  # 运行次数
REQUEST_DATE_RUN = 0x00000800  # 最近打开时间
REQUEST_DATE_RECENTLY_CHANGED = 0x00001000  # 最近修改时间
REQUEST_HIGHLIGHTED_FILE_NAME = 0x00002000  # 文件名(高亮关键字)
REQUEST_HIGHLIGHTED_PATH = 0x00004000  # 不含文件的路径(高亮关键字)
REQUEST_HIGHLIGHTED_FULL_PATH_AND_FILE_NAME = 0x00008000  # 包含文件名的路径(高亮关键字)
```

默认查询的字段：

```python
DEFAULT_FLAGS = (
        REQUEST_FULL_PATH_AND_FILE_NAME
        | REQUEST_SIZE
        | REQUEST_DATE_MODIFIED
)
```



## 支持查询的文件属性

```python
# see more: https://learn.microsoft.com/en-us/windows/win32/fileio/file-attribute-constants
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



## 支持的排序

```python
SORT_NAME_ASCENDING = 1 # default
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

