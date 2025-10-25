"""
The Everything SDK provides a DLL and Lib interface to Everything over IPC.
Everything is required to run in the background.

documentation   : https://www.voidtools.com/support/everything/sdk/
dependency (SDK): https://www.voidtools.com/Everything-SDK.zip
"""
import ctypes
import datetime
import struct
import win32api
from dataclasses import dataclass
from enum import IntEnum, IntFlag
from pathlib import Path
from typing import Dict, Iterable, Iterator


class Request(IntFlag):
    """Flags for requesting specific file information."""
    FILE_NAME = 0x00000001
    PATH = 0x00000002
    FULL_PATH_AND_FILE_NAME = 0x00000004
    EXTENSION = 0x00000008
    SIZE = 0x00000010
    DATE_CREATED = 0x00000020
    DATE_MODIFIED = 0x00000040
    DATE_ACCESSED = 0x00000080
    ATTRIBUTES = 0x00000100
    FILE_LIST_FILE_NAME = 0x00000200
    RUN_COUNT = 0x00000400
    DATE_RUN = 0x00000800
    DATE_RECENTLY_CHANGED = 0x00001000
    HIGHLIGHTED_FILE_NAME = 0x00002000
    HIGHLIGHTED_PATH = 0x00004000
    HIGHLIGHTED_FULL_PATH_AND_FILE_NAME = 0x00008000

    DEFAULT = FULL_PATH_AND_FILE_NAME | SIZE | DATE_MODIFIED
    ALL = (
            FILE_NAME | PATH | FULL_PATH_AND_FILE_NAME | EXTENSION | SIZE |
            DATE_CREATED | DATE_MODIFIED | DATE_ACCESSED | ATTRIBUTES |
            FILE_LIST_FILE_NAME | RUN_COUNT | DATE_RUN | DATE_RECENTLY_CHANGED |
            HIGHLIGHTED_FILE_NAME | HIGHLIGHTED_PATH | HIGHLIGHTED_FULL_PATH_AND_FILE_NAME
    )


class FileAttribute(IntFlag):
    """Windows file attributes constants."""
    READONLY = 0x00000001
    HIDDEN = 0x00000002
    SYSTEM = 0x00000004
    DIRECTORY = 0x00000010
    ARCHIVE = 0x00000020
    DEVICE = 0x00000040
    NORMAL = 0x00000080
    TEMPORARY = 0x00000100
    SPARSE_FILE = 0x00000200
    REPARSE_POINT = 0x00000400
    COMPRESSED = 0x00000800
    OFFLINE = 0x00001000
    NOT_CONTENT_INDEXED = 0x00002000
    ENCRYPTED = 0x00004000


class Sort(IntEnum):
    """Sort types for query results."""
    NAME_ASCENDING = 1
    NAME_DESCENDING = 2
    PATH_ASCENDING = 3
    PATH_DESCENDING = 4
    SIZE_ASCENDING = 5
    SIZE_DESCENDING = 6
    EXTENSION_ASCENDING = 7
    EXTENSION_DESCENDING = 8
    TYPE_NAME_ASCENDING = 9
    TYPE_NAME_DESCENDING = 10
    DATE_CREATED_ASCENDING = 11
    DATE_CREATED_DESCENDING = 12
    DATE_MODIFIED_ASCENDING = 13
    DATE_MODIFIED_DESCENDING = 14
    ATTRIBUTES_ASCENDING = 15
    ATTRIBUTES_DESCENDING = 16
    FILE_LIST_FILENAME_ASCENDING = 17
    FILE_LIST_FILENAME_DESCENDING = 18
    RUN_COUNT_ASCENDING = 19
    RUN_COUNT_DESCENDING = 20
    DATE_RECENTLY_CHANGED_ASCENDING = 21
    DATE_RECENTLY_CHANGED_DESCENDING = 22
    DATE_ACCESSED_ASCENDING = 23
    DATE_ACCESSED_DESCENDING = 24
    DATE_RUN_ASCENDING = 25
    DATE_RUN_DESCENDING = 26


class EverythingError(IntEnum):
    """Error codes from Everything_GetLastError."""
    OK = 0
    MEMORY = 1
    IPC = 2
    REGISTERCLASSEX = 3
    CREATEWINDOW = 4
    CREATETHREAD = 5
    INVALIDINDEX = 6
    INVALIDCALL = 7


class Constants:
    """A namespace for shared constants."""
    WINDOWS_TICKS = 10_000_000  # 100 nanoseconds
    WINDOWS_EPOCH = datetime.datetime(1601, 1, 1)
    POSIX_EPOCH = datetime.datetime(1970, 1, 1)
    EPOCH_DIFFERENCE = (POSIX_EPOCH - WINDOWS_EPOCH).total_seconds()
    WINDOWS_TICKS_TO_POSIX_EPOCH = EPOCH_DIFFERENCE * WINDOWS_TICKS
    INVALID_FILETIME = 2 ** 64 - 1
    MAX_PATH = 260

    ATTRIBUTE_MAP = {
        FileAttribute.READONLY: 'R',
        FileAttribute.HIDDEN: 'H',
        FileAttribute.SYSTEM: 'S',
        FileAttribute.DIRECTORY: 'D',
        FileAttribute.ARCHIVE: 'A',
        FileAttribute.DEVICE: 'D',
        FileAttribute.NORMAL: 'N',
        FileAttribute.TEMPORARY: 'T',
        FileAttribute.SPARSE_FILE: 'P',
        FileAttribute.REPARSE_POINT: 'L',
        FileAttribute.COMPRESSED: 'C',
        FileAttribute.OFFLINE: 'O',
        FileAttribute.NOT_CONTENT_INDEXED: 'I',
        FileAttribute.ENCRYPTED: 'E',
    }


class SDKError(Exception):
    """Custom exception for Everything SDK errors."""

    ERROR_MESSAGES = {
        EverythingError.MEMORY: "Out of memory",
        EverythingError.IPC: "IPC not available. Is 'Everything' running?",
        EverythingError.REGISTERCLASSEX: "RegisterClassEx failed",
        EverythingError.CREATEWINDOW: "CreateWindow failed",
        EverythingError.CREATETHREAD: "CreateThread failed",
        EverythingError.INVALIDINDEX: "Invalid result index",
        EverythingError.INVALIDCALL: "Invalid call. Did you call query() first?",
    }

    def __init__(self, error_code: EverythingError):
        self.error_code = error_code
        self.message = self.ERROR_MESSAGES.get(error_code, "An unknown error occurred")
        super().__init__(f"[{self.error_code.name}] {self.message}")


@dataclass(frozen=True)
class SearchResult:
    """A structured, read-only object for a single search result."""
    full_path: str | None = None
    path: str | None = None
    name: str | None = None
    extension: str | None = None
    size: int | None = None
    created_time: datetime.datetime | None = None
    modified_time: datetime.datetime | None = None
    accessed_time: datetime.datetime | None = None
    attributes: str | None = None
    run_count: int | None = None
    date_run: datetime.datetime | None = None
    recently_changed: datetime.datetime | None = None
    highlighted_full_path: str | None = None
    highlighted_path: str | None = None
    highlighted_name: str | None = None
    file_list_file_name: str | None = None


FileTypeGroups = {
    'AUDIO': {'m1a', 'dts', 'fla', 'mp3', 'xm', 'm2a', 'voc', 'cda', 'spc', 'snd', 'ac3', 'umx', 'mka', 'midi',
              'wma', 'm3u', 'mod', 'mid', 'wav', 'aac', 'mpa', 'it', 'ogg', 'rmi', 'aif', 'mp2', 'm4a', 'ra',
              'aiff', 'au', 'flac', 'aifc'},
    'VIDEO': {'m1v', 'mp2v', 'pss', 'mov', 'm4b', 'rm', 'vob', 'webm', '3gpp', 'roq', 'hdmov', 'tpr', 'evo', 'wmv',
              'qt', 'dss', 'swf', 'rpm', 'flv', 'mpe', 'ogm', 'tp', 'f4v', '3gp', 'wm', 'amv', 'dsv', 'mpeg', 'bik',
              'drc', 'ogv', 'ratdvd', 'mp4', 'asf', 'ts', 'wmp', 'ifo', '3g2', 'm2t', 'ivf', 'm2v', 'mp4v', 'rmvb',
              'avi', 'm2ts', 'mpv2', 'mpls', 'd2v', 'fli', 'bdmv', 'mpg', 'mkv', 'mpv4', 'flc', 'dsa', 'smil',
              'm4p', 'm4v', 'vp6', 'm2p', 'pva', 'mts', 'rmm', 'smk', 'divx', 'ram', 'flic', '3gp2', 'dsm', 'amr'},
    'IMAGE': {'wmf', 'gif', 'ico', 'tga', 'tif', 'jpe', 'ani', 'jpeg', 'bmp', 'jpg', 'pcx', 'psd', 'tiff', 'webp',
              'svg', 'png'},
    'DOC': {'doc', 'docx', 'pdf', 'txt', 'rtf', 'odt', 'xls', 'xlsx', 'ppt', 'pptx', 'md'},
}


class Client:
    def __init__(self, dll_path: str | Path | None = None):
        self.dll_path = str(dll_path or self._get_default_dll_path())
        self.dll: ctypes.WinDLL | None = None
        self._buffers: Dict[str, ctypes._SimpleCData] = {}
        self._flag_func_map: Dict[Request, tuple[str, callable]] = {}

    def __enter__(self):
        try:
            self.dll = ctypes.WinDLL(self.dll_path)
        except FileNotFoundError as err:
            raise FileNotFoundError(f"Could not find the Everything DLL at '{self.dll_path}'.") from err
        self._check_is_running()
        self._initialize_sdk()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.dll and self.dll._handle:
            win32api.FreeLibrary(self.dll._handle)
            self.dll = None

    def _check_is_running(self):
        """Checks if the Everything service is running by querying its version."""
        self.version()
        last_error = self.get_last_error()
        if last_error:
            raise last_error

    def _initialize_sdk(self):
        """Prepare buffers, ctypes definitions, and function mappings."""
        self._create_buffers()
        self._define_ctypes()
        self._create_flag_map()

    @staticmethod
    def _get_default_dll_path() -> Path:
        """Determines the default path for the Everything64.dll."""
        return Path(__file__).parent / "dll" / "Everything64.dll"

    @staticmethod
    def _filetime_to_datetime(filetime: ctypes.c_ulonglong) -> datetime.datetime | None:
        """Converts a Windows FILETIME structure to a Python datetime object."""
        win_ticks = struct.unpack('<Q', filetime)[0]
        if win_ticks == 0 or win_ticks == Constants.INVALID_FILETIME:
            return None
        microseconds = (win_ticks - Constants.WINDOWS_TICKS_TO_POSIX_EPOCH) / Constants.WINDOWS_TICKS
        return datetime.datetime.fromtimestamp(microseconds)

    def _create_buffers(self) -> None:
        """Pre-allocates ctypes buffers for performance."""
        self._buffers = {
            'full_path': ctypes.create_unicode_buffer(Constants.MAX_PATH),
            'size': ctypes.c_ulonglong(0),
            'accessed_time': ctypes.c_ulonglong(0),
            'created_time': ctypes.c_ulonglong(0),
            'modified_time': ctypes.c_ulonglong(0),
            'recently_changed': ctypes.c_ulonglong(0),
            'date_run': ctypes.c_ulonglong(0),
        }

    def _create_flag_map(self) -> None:
        """Maps RequestFlags to the corresponding result key and getter method."""
        self._flag_func_map = {
            Request.HIGHLIGHTED_FULL_PATH_AND_FILE_NAME: ('highlighted_full_path', self._get_highlighted_full_path),
            Request.HIGHLIGHTED_PATH: ('highlighted_path', self._get_highlighted_path),
            Request.HIGHLIGHTED_FILE_NAME: ('highlighted_name', self._get_highlighted_name),
            Request.DATE_RECENTLY_CHANGED: ('recently_changed', self._get_recently_changed),
            Request.DATE_RUN: ('date_run', self._get_date_run),
            Request.RUN_COUNT: ('run_count', self._get_run_count),
            Request.FILE_LIST_FILE_NAME: ('file_list_file_name', self._get_file_list_file_name),
            Request.ATTRIBUTES: ('attributes', self._get_attributes),
            Request.DATE_ACCESSED: ('accessed_time', self._get_accessed_time),
            Request.DATE_MODIFIED: ('modified_time', self._get_modified_time),
            Request.DATE_CREATED: ('created_time', self._get_created_time),
            Request.SIZE: ('size', self._get_size),
            Request.EXTENSION: ('extension', self._get_extension),
            Request.FULL_PATH_AND_FILE_NAME: ('full_path', self._get_full_path),
            Request.PATH: ('path', self._get_path),
            Request.FILE_NAME: ('name', self._get_name),
        }

    def _define_ctypes(self) -> None:
        """Define argument and return types for the DLL functions."""
        index = ctypes.c_int
        p_ulonglong = ctypes.POINTER(ctypes.c_ulonglong)
        return_strings = [
            "Everything_GetResultExtensionW", "Everything_GetResultFileNameW",
            "Everything_GetResultPathW", "Everything_GetResultHighlightedFileNameW",
            "Everything_GetResultHighlightedPathW", "Everything_GetResultHighlightedFullPathAndFileNameW",
            "Everything_GetResultFileListFileNameW"
        ]
        return_value_via_pointers = [
            "Everything_GetResultDateCreated", "Everything_GetResultDateModified",
            "Everything_GetResultDateAccessed", "Everything_GetResultSize",
            "Everything_GetResultDateRecentlyChanged", "Everything_GetResultDateRun"
        ]

        for func_name in return_strings:
            func = getattr(self.dll, func_name)
            func.argtypes = [index]
            func.restype = ctypes.c_wchar_p

        for func_name in return_value_via_pointers:
            func = getattr(self.dll, func_name)
            func.argtypes = [index, p_ulonglong]

        self.dll.Everything_GetResultRunCount.argtypes = [index]
        self.dll.Everything_GetResultRunCount.restype = ctypes.c_int

        self.dll.Everything_GetResultAttributes.argtypes = [index]
        self.dll.Everything_GetResultAttributes.restype = ctypes.POINTER(ctypes.c_ulonglong)

    def _setup_query(self, keywords, match_path, match_case, whole_word, regex, offset, limit, flags, sort) -> None:
        """Sets all query parameters before execution."""
        self.dll.Everything_Reset()
        self.dll.Everything_SetSearchW(keywords)
        self.dll.Everything_SetMatchPath(match_path)
        self.dll.Everything_SetMatchCase(match_case)
        self.dll.Everything_SetMatchWholeWord(whole_word)
        self.dll.Everything_SetRegex(regex)
        self.dll.Everything_SetRequestFlags(flags)
        self.dll.Everything_SetSort(sort)
        if offset > 0:
            self.dll.Everything_SetOffset(offset)
        if limit >= 0:
            self.dll.Everything_SetMax(limit)

    def _get_name(self, idx: int) -> str:
        return self.dll.Everything_GetResultFileNameW(idx)

    def _get_path(self, idx: int) -> str:
        return self.dll.Everything_GetResultPathW(idx)

    def _get_full_path(self, idx: int) -> str:
        buffer = self._buffers['full_path']
        self.dll.Everything_GetResultFullPathNameW(idx, buffer, Constants.MAX_PATH)
        return buffer.value

    def _get_size(self, idx: int) -> int:
        buffer = self._buffers['size']
        self.dll.Everything_GetResultSize(idx, buffer)
        return buffer.value

    def _get_extension(self, idx: int) -> str:
        return self.dll.Everything_GetResultExtensionW(idx)

    def _get_run_count(self, idx: int) -> int:
        return self.dll.Everything_GetResultRunCount(idx)

    def _get_attributes(self, idx: int) -> str:
        attr_ptr = self.dll.Everything_GetResultAttributes(idx)
        if not attr_ptr:
            return ""
        attr_int = struct.unpack('<Q', attr_ptr.contents)[0]
        attr_flags = FileAttribute(attr_int)
        return "".join(sorted(Constants.ATTRIBUTE_MAP[flag] for flag in Constants.ATTRIBUTE_MAP if flag in attr_flags))

    def _get_file_list_file_name(self, idx: int) -> str:
        return self.dll.Everything_GetResultFileListFileNameW(idx)

    def _get_accessed_time(self, idx: int) -> datetime.datetime | None:
        buffer = self._buffers['accessed_time']
        self.dll.Everything_GetResultDateAccessed(idx, buffer)
        return self._filetime_to_datetime(buffer)

    def _get_created_time(self, idx: int) -> datetime.datetime | None:
        buffer = self._buffers['created_time']
        self.dll.Everything_GetResultDateCreated(idx, buffer)
        return self._filetime_to_datetime(buffer)

    def _get_modified_time(self, idx: int) -> datetime.datetime | None:
        buffer = self._buffers['modified_time']
        self.dll.Everything_GetResultDateModified(idx, buffer)
        return self._filetime_to_datetime(buffer)

    def _get_recently_changed(self, idx: int) -> datetime.datetime | None:
        buffer = self._buffers['recently_changed']
        self.dll.Everything_GetResultDateRecentlyChanged(idx, buffer)
        return self._filetime_to_datetime(buffer)

    def _get_date_run(self, idx: int) -> datetime.datetime | None:
        buffer = self._buffers['date_run']
        self.dll.Everything_GetResultDateRun(idx, buffer)
        return self._filetime_to_datetime(buffer)

    def _get_highlighted_name(self, idx: int) -> str:
        return self.dll.Everything_GetResultHighlightedFileNameW(idx)

    def _get_highlighted_path(self, idx: int) -> str:
        return self.dll.Everything_GetResultHighlightedPathW(idx)

    def _get_highlighted_full_path(self, idx: int) -> str:
        return self.dll.Everything_GetResultHighlightedFullPathAndFileNameW(idx)

    def version(self) -> str:
        """Returns the version of the Everything instance."""
        major = self.dll.Everything_GetMajorVersion()
        minor = self.dll.Everything_GetMinorVersion()
        revision = self.dll.Everything_GetRevision()
        build = self.dll.Everything_GetBuildNumber()
        return f"{major}.{minor}.{revision}.{build}"

    def get_last_error(self) -> SDKError | None:
        """Checks for the last error and returns an exception object if found."""
        error_code_val = self.dll.Everything_GetLastError()
        if error_code_val == EverythingError.OK:
            return None
        return SDKError(EverythingError(error_code_val))

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
        """
        Performs a search query.

        :param keywords: Search query, supports Everything search syntax.
        :param match_path: Match path
        :param match_case: Case sensitive
        :param whole_word: Whole word match
        :param regex: Use regular expression
        :param offset: Offset
        :param limit: Maximum number, <0 means search all
        :param flags: A Request bitmask specifying which fields to retrieve.
        :param sort: A Sort enum member specifying the sort order.
        :return: An iterator yielding SearchResult objects.
        """
        self._setup_query(keywords, match_path, match_case, whole_word, regex, offset, limit, flags.value, sort.value)
        self.dll.Everything_QueryW(True)
        num_results = self.dll.Everything_GetNumResults()

        active_getters = {
            key: func
            for flag, (key, func) in self._flag_func_map.items()
            if flag in flags
        }

        for i in range(num_results):
            result_data = {key: getter(i) for key, getter in active_getters.items()}
            yield SearchResult(**result_data)

    def exit(self) -> None:
        """Requests the Everything service to exit."""
        self.dll.Everything_Exit()

    def search_in_located(self, path: str | Path, keywords: str = '', **kwargs) -> Iterator[SearchResult]:
        return self.search(f'path:"{path}" {keywords}', **kwargs)

    def search_folder(self, keywords: str = '', **kwargs) -> Iterator[SearchResult]:
        return self.search(f'folder: {keywords}', **kwargs)

    def search_ext(self, extensions: str | Iterable[str], keywords: str = '', **kwargs) -> Iterator[SearchResult]:
        if isinstance(extensions, str):
            ext_str = extensions.lstrip('.')
        else:
            ext_str = ";".join(ext.lstrip('.') for ext in extensions)
        return self.search(f'ext:{ext_str} {keywords}', **kwargs)

    def search_audio(self, keywords: str = '', **kwargs) -> Iterator[SearchResult]:
        return self.search_ext(FileTypeGroups['AUDIO'], keywords, **kwargs)

    def search_video(self, keywords: str = '', **kwargs) -> Iterator[SearchResult]:
        return self.search_ext(FileTypeGroups['VIDEO'], keywords, **kwargs)

    def search_image(self, keywords: str = '', **kwargs) -> Iterator[SearchResult]:
        return self.search_ext(FileTypeGroups['IMAGE'], keywords, **kwargs)

    def search_doc(self, keywords: str = '', **kwargs) -> Iterator[SearchResult]:
        return self.search_ext(FileTypeGroups['DOC'], keywords, **kwargs)
