# Everything Tool

Everything SDK for python。

## 运行环境

本项目使用 everything IPC 通讯，需要[下载](https://www.voidtools.com/zh-cn/downloads/)完整版的 everything 软件。精讲版的 everything 不支持 IPC。



## Demo

```python
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

# {'modified_time': datetime.datetime(2019, 12, 7, 17, 31, 7, 336120), 'size': 18446744073709551615, 'full_path': 'C:\\Windows\\WinSxS\\amd64_system.io.compression.zipfile_b77a5c561934e089_4.0.15805.0_none_f6cd5d82d8d3e7bd'}
# {'modified_time': datetime.datetime(2022, 11, 19, 16, 41, 41, 568549), 'size': 18446744073709551615, 'full_path': 'D:\\Java\\legal\\jdk.zipfs'}
# {'modified_time': datetime.datetime(2021, 11, 4, 2, 43, 3, 485258), 'size': 18446744073709551615, 'full_path': 'D:\\software\\CLion 2021.2.3\\jbr\\legal\\jdk.zipfs'}

# {'attributes': 'A', 'name': 'v0.0.0-20210805182204-aaa1db679c0d.mod'}
# {'attributes': 'A', 'name': 'WahWahWaaah.mp3'}
```



## 搜索语法

Everything Tool 支持所有 everything 语法，通过 everything 的帮助获得搜索语法，具体有以下功能：

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

```python
def search(
        self,
        keyword,
        math_path=False,
        math_case=False,
        whole_world=False,
        regex=False,
        offset=0,
        limit=-1,
        flags=DEFAULT_FLAGS,
        sort_type=EVERYTHING_SORT_NAME_ASCENDING
):
    """
    everything搜索文件
    :param keyword: 搜索关键字,支持通配符
    :param math_path: 匹配路径
    :param math_case: 区分大小写
    :param whole_world: 全字匹配
    :param regex: 使用正则表达式
    :param offset: 偏移量
    :param limit: 最多几条
    :param flags: 查询字段
    :param sort_type: 排序
    :return:
    """
    ...
```

```python
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

支持 everything 全部的查询字段

```python
EVERYTHING_REQUEST_FILE_NAME = 0x00000001  # 文件名
EVERYTHING_REQUEST_PATH = 0x00000002  # 不含文件的路径
EVERYTHING_REQUEST_FULL_PATH_AND_FILE_NAME = 0x00000004  # 包含文件名的路径
EVERYTHING_REQUEST_EXTENSION = 0x00000008  # 拓展名
EVERYTHING_REQUEST_SIZE = 0x00000010  # 大小(byte)
EVERYTHING_REQUEST_DATE_CREATED = 0x00000020  # 创建时间
EVERYTHING_REQUEST_DATE_MODIFIED = 0x00000040  # 修改时间
EVERYTHING_REQUEST_DATE_ACCESSED = 0x00000080  # 访问时间
EVERYTHING_REQUEST_ATTRIBUTES = 0x00000100  # 属性
EVERYTHING_REQUEST_FILE_LIST_FILE_NAME = 0x00000200  # 文件列表名
EVERYTHING_REQUEST_RUN_COUNT = 0x00000400  # 运行次数
EVERYTHING_REQUEST_DATE_RUN = 0x00000800  # 最近打开时间
EVERYTHING_REQUEST_DATE_RECENTLY_CHANGED = 0x00001000  # 最近修改时间
EVERYTHING_REQUEST_HIGHLIGHTED_FILE_NAME = 0x00002000  # 文件名(高亮关键字)
EVERYTHING_REQUEST_HIGHLIGHTED_PATH = 0x00004000  # 不含文件的路径(高亮关键字)
EVERYTHING_REQUEST_HIGHLIGHTED_FULL_PATH_AND_FILE_NAME = 0x00008000  # 包含文件名的路径(高亮关键字)
```



## 默认查询的字段

```python
DEFAULT_FLAGS = (
        EVERYTHING_REQUEST_FULL_PATH_AND_FILE_NAME
        | EVERYTHING_REQUEST_SIZE
        | EVERYTHING_REQUEST_DATE_MODIFIED
)
```



## 文件属性

```python
# see more: https://learn.microsoft.com/en-us/windows/win32/fileio/file-attribute-constants
EVERYTHING_FILE_ATTRIBUTE_READONLY = 0x00000001
EVERYTHING_FILE_ATTRIBUTE_HIDDEN = 0x00000002
EVERYTHING_FILE_ATTRIBUTE_SYSTEM = 0x00000004
EVERYTHING_FILE_ATTRIBUTE_DIRECTORY = 0x00000010
EVERYTHING_FILE_ATTRIBUTE_ARCHIVE = 0x00000020
EVERYTHING_FILE_ATTRIBUTE_DEVICE = 0x00000040
EVERYTHING_FILE_ATTRIBUTE_NORMAL = 0x00000080
EVERYTHING_FILE_ATTRIBUTE_TEMPORARY = 0x00000100
EVERYTHING_FILE_ATTRIBUTE_SPARSE_FILE = 0x00000200
EVERYTHING_FILE_ATTRIBUTE_REPARSE_POINT = 0x00000400
EVERYTHING_FILE_ATTRIBUTE_COMPRESSED = 0x00000800
EVERYTHING_FILE_ATTRIBUTE_OFFLINE = 0x00001000
EVERYTHING_FILE_ATTRIBUTE_NOT_CONTENT_INDEXED = 0x00002000
EVERYTHING_FILE_ATTRIBUTE_ENCRYPTED = 0x00004000
```



## 排序

```python
EVERYTHING_SORT_NAME_ASCENDING = 1 # default value
EVERYTHING_SORT_NAME_DESCENDING = 2
EVERYTHING_SORT_PATH_ASCENDING = 3
EVERYTHING_SORT_PATH_DESCENDING = 4
EVERYTHING_SORT_SIZE_ASCENDING = 5
EVERYTHING_SORT_SIZE_DESCENDING = 6
EVERYTHING_SORT_EXTENSION_ASCENDING = 7
EVERYTHING_SORT_EXTENSION_DESCENDING = 8
EVERYTHING_SORT_TYPE_NAME_ASCENDING = 9
EVERYTHING_SORT_TYPE_NAME_DESCENDING = 10
EVERYTHING_SORT_DATE_CREATED_ASCENDING = 11
EVERYTHING_SORT_DATE_CREATED_DESCENDING = 12
EVERYTHING_SORT_DATE_MODIFIED_ASCENDING = 13
EVERYTHING_SORT_DATE_MODIFIED_DESCENDING = 14
EVERYTHING_SORT_ATTRIBUTES_ASCENDING = 15
EVERYTHING_SORT_ATTRIBUTES_DESCENDING = 16
EVERYTHING_SORT_FILE_LIST_FILENAME_ASCENDING = 17
EVERYTHING_SORT_FILE_LIST_FILENAME_DESCENDING = 18
EVERYTHING_SORT_RUN_COUNT_ASCENDING = 19
EVERYTHING_SORT_RUN_COUNT_DESCENDING = 20
EVERYTHING_SORT_DATE_RECENTLY_CHANGED_ASCENDING = 21
EVERYTHING_SORT_DATE_RECENTLY_CHANGED_DESCENDING = 22
EVERYTHING_SORT_DATE_ACCESSED_ASCENDING = 23
EVERYTHING_SORT_DATE_ACCESSED_DESCENDING = 24
EVERYTHING_SORT_DATE_RUN_ASCENDING = 25
EVERYTHING_SORT_DATE_RUN_DESCENDING = 26
```

