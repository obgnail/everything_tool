# Everything Tool

[English](https://github.com/obgnail/everything_tool/blob/master/README.md) | 简体中文

`Everything Tool` 是一个类型安全的 Python SDK，专为与 Windows 平台上的文件搜索软件 `Everything` 互动而设计。它提供了一个清晰的、面向对象的 API，让您能完全发挥 Everything 的即时搜索能力。

---

## 环境要求

本项目通过 IPC (Inter-Process Communication) 与 `Everything` 通信。因此，您必须安装**完整版**的 `Everything` 软件，并确保其在后台运行。精简版不支持 IPC 功能。

- **下载 Everything**：您可以从 [官方网站](https://www.voidtools.com/zh-cn/downloads/) 下载。

---

## 使用示例

以下是一个基本示例，展示如何使用 `Everything Tool` 查找系统中最近修改的 5 个 Python 文件。

```python
from everything_tool import Client, Request, Sort, SDKError

try:
    # 客户端必须在 'with' 语句中使用，以确保资源被正确管理。
    with Client() as client:
        print(f"Everything 版本: {client.version()}")

        # 1. 使用 Request 枚举来定义需要查询的字段。
        search_flags = (
            Request.FULL_PATH_AND_FILE_NAME | 
            Request.SIZE | 
            Request.DATE_MODIFIED
        )

        # 2. 使用清晰、可读的参数执行搜索。
        results = client.search(
            keywords="*.py", 
            limit=5, 
            flags=search_flags, 
            sort=Sort.DATE_MODIFIED_DESCENDING
        )

        print("\n找到最近修改的 5 个 Python 文件：")
        
        # 3. 返回结果是结构化的 SearchResult 对象。
        for item in results:
            size_kb = f"{item.size / 1024:.2f} KB" if item.size is not None else "N/A"
            print(f"- 路径: {item.full_path}")
            print(f"  大小: {size_kb}")
            print(f"  修改时间: {item.modified_time}")

except FileNotFoundError as e:
    print(f"错误：找不到 Everything64.dll。请确保它位于正确的路径。\n{e}")
except SDKError as e:
    # 捕获特定的 SDK 错误，例如 'Everything' 服务未运行。
    print(f"发生 SDK 错误: {e}")
```

---

## 核心特性

### 类型安全的枚举 (Enums)
本 SDK 使用 `Enum` 类（如 `Request`, `Sort`, `FileAttribute`）来取代原始的整数常量。这不仅提升了代码的可读性，还能让静态分析工具和 IDE 在运行前就捕获到类型错误，从而避免潜在的 bug。

### 结构化的返回结果 (`SearchResult` 数据类)
搜索方法会返回一个 `SearchResult` 对象的迭代器。这是一个只读的 `dataclass`，允许您通过属性（例如 `result.full_path`）来访问结果。相比传统的字典，它更为健壮和可预测，并能获得 IDE 的完整自动补全支持。

---

## API 概览

### 核心搜索方法
这是所有查询的基础函数，其他便捷的封装方法都基于此函数构建。

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

### 便捷的封装方法
针对常见的搜索场景，我们提供了一系列便捷的方法：
- `search_in_located(path, keywords, **kwargs)`: 在特定路径下搜索。
- `search_folder(keywords, **kwargs)`: 仅搜索文件夹。
- `search_ext(extensions, keywords, **kwargs)`: 根据一个或多个扩展名进行搜索。
- `search_audio(keywords, **kwargs)`: 搜索常见的音频文件。
- `search_video(keywords, **kwargs)`: 搜索常见的视频文件。
- `search_image(keywords, **kwargs)`: 搜索常见的图片文件。
- `search_doc(keywords, **kwargs)`: 搜索常见的文档文件。

---

## 参考

### 请求字段 (`Request`)
使用这些枚举成员来指定您希望返回结果包含哪些数据。默认值为 `Request.DEFAULT`。

| 成员                                  | 说明                                           |
| ------------------------------------- | ---------------------------------------------- |
| `FILE_NAME`                           | 仅文件名称                                     |
| `PATH`                                | 不含文件名称的路径                             |
| `FULL_PATH_AND_FILE_NAME`             | 包含文件名称的完整路径                         |
| `EXTENSION`                           | 扩展名                                         |
| `SIZE`                                | 文件大小 (单位：字节)                          |
| `DATE_CREATED`                        | 创建日期                                       |
| `DATE_MODIFIED`                       | 最后修改日期                                   |
| `DATE_ACCESSED`                       | 最后访问日期                                   |
| `ATTRIBUTES`                          | 文件属性 (例如：只读、隐藏)                    |
| `RUN_COUNT`                           | 文件的运行次数                                 |
| `DATE_RUN`                            | 上次运行的日期                                 |
| `DATE_RECENTLY_CHANGED`               | 最近变更的日期                                 |
| `HIGHLIGHTED_FILE_NAME`               | 高亮关键字的文件名称                           |
| `HIGHLIGHTED_PATH`                    | 高亮关键字的路径                               |
| `HIGHLIGHTED_FULL_PATH_AND_FILE_NAME` | 高亮关键字的完整路径和文件名称                 |
| `DEFAULT`                             | `FULL_PATH_AND_FILE_NAME`, `SIZE`, `DATE_MODIFIED` 的组合 |
| `ALL`                                 | 包含所有可用请求字段的组合                     |

### 排序方式 (`Sort`)
使用这些枚举成员来控制搜索结果的排序顺序。默认值为 `Sort.NAME_ASCENDING`。

| 成员                        | 说明                 |
| ----------------------------- | -------------------- |
| `NAME_ASCENDING` / `DESCENDING` | 按文件名称排序       |
| `PATH_ASCENDING` / `DESCENDING` | 按路径排序           |
| `SIZE_ASCENDING` / `DESCENDING` | 按大小排序           |
| `EXTENSION_ASCENDING` / `DESCENDING` | 按扩展名排序         |
| `DATE_CREATED_ASCENDING` / `DESCENDING` | 按创建日期排序       |
| `DATE_MODIFIED_ASCENDING` / `DESCENDING` | 按修改日期排序       |
| ...以及更多                   | (详见代码中的 `Sort` 枚举) |

### 文件属性 (`FileAttribute`)
这些枚举成员代表 Windows 的文件属性。

| 成员                  | 说明                           |
| ----------------------- | ------------------------------ |
| `READONLY`              | 文件为只读。                   |
| `HIDDEN`                | 文件为隐藏。                   |
| `SYSTEM`                | 文件为系统文件。               |
| `DIRECTORY`             | 项目为文件夹。                 |
| `ARCHIVE`               | 文件已标记为存档。             |
| `COMPRESSED`            | 文件被压缩。                   |
| `ENCRYPTED`             | 文件被加密。                   |
| `REPARSE_POINT`         | 文件具有关联的重新分析点。     |

---

## 搜索语法

本 SDK 支持完整的 `Everything` 搜索语法。若要进行高级查询，请参考 `Everything` 应用程序内的官方文档（帮助 -> 搜索语法）。这包括：
- 运算符 (`!`, `|`, ` `)
- 通配符 (`*`, `?`)
- 修饰符 (`file:`, `folder:`, `ext:`)
- 函数 (`dm:`, `size:`, `attrib:`)
- 以及更多高级功能。
