"""
The Everything SDK provides a DLL and Lib interface to Everything over IPC.
Everything is required to run in the background.

documentation   : https://www.voidtools.com/support/everything/sdk/
dependency (SDK): https://www.voidtools.com/Everything-SDK.zip
"""
import ctypes
import datetime
import os
import struct
import win32api
from functools import reduce
from typing import List, Iterable, Dict

# defines flag
REQUEST_FILE_NAME = 0x00000001
REQUEST_PATH = 0x00000002
REQUEST_FULL_PATH_AND_FILE_NAME = 0x00000004
REQUEST_EXTENSION = 0x00000008
REQUEST_SIZE = 0x00000010
REQUEST_DATE_CREATED = 0x00000020
REQUEST_DATE_MODIFIED = 0x00000040
REQUEST_DATE_ACCESSED = 0x00000080
REQUEST_ATTRIBUTES = 0x00000100
REQUEST_FILE_LIST_FILE_NAME = 0x00000200
REQUEST_RUN_COUNT = 0x00000400
REQUEST_DATE_RUN = 0x00000800
REQUEST_DATE_RECENTLY_CHANGED = 0x00001000
REQUEST_HIGHLIGHTED_FILE_NAME = 0x00002000
REQUEST_HIGHLIGHTED_PATH = 0x00004000
REQUEST_HIGHLIGHTED_FULL_PATH_AND_FILE_NAME = 0x00008000

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

SORT_NAME_ASCENDING = 1
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

# return values from Everything_GetLastError
OK = 0  # no error
ERROR_MEMORY = 1  # out of memory
ERROR_IPC = 2  # IPC not available
ERROR_REGISTERCLASSEX = 3  # RegisterClassEx failed
ERROR_CREATEWINDOW = 4  # CreateWindow failed
ERROR_CREATETHREAD = 5  # CreateThread failed
ERROR_INVALIDINDEX = 6  # Invalid result index (must be >= 0 and < numResults)
ERROR_INVALIDCALL = 7  # Call Everything_Query before getting results

# see more: https://en.wikipedia.org/wiki/File_attribute
_ATTRIBUTES = (
    (FILE_ATTRIBUTE_ENCRYPTED, 'E'),
    (FILE_ATTRIBUTE_NOT_CONTENT_INDEXED, 'I'),
    (FILE_ATTRIBUTE_OFFLINE, 'O'),
    (FILE_ATTRIBUTE_COMPRESSED, 'C'),
    (FILE_ATTRIBUTE_REPARSE_POINT, 'L'),
    (FILE_ATTRIBUTE_SPARSE_FILE, 'P'),
    (FILE_ATTRIBUTE_TEMPORARY, 'T'),
    (FILE_ATTRIBUTE_NORMAL, 'N'),
    (FILE_ATTRIBUTE_DEVICE, 'D'),
    (FILE_ATTRIBUTE_ARCHIVE, 'A'),
    (FILE_ATTRIBUTE_DIRECTORY, 'D'),
    (FILE_ATTRIBUTE_SYSTEM, 'S'),
    (FILE_ATTRIBUTE_HIDDEN, 'H'),
    (FILE_ATTRIBUTE_READONLY, 'R'),
)

_SUPPORTED_FLAGS = (
    REQUEST_HIGHLIGHTED_FULL_PATH_AND_FILE_NAME,
    REQUEST_HIGHLIGHTED_PATH,
    REQUEST_HIGHLIGHTED_FILE_NAME,
    REQUEST_DATE_RECENTLY_CHANGED,
    REQUEST_DATE_RUN,
    REQUEST_RUN_COUNT,
    REQUEST_FILE_LIST_FILE_NAME,
    REQUEST_ATTRIBUTES,
    REQUEST_DATE_ACCESSED,
    REQUEST_DATE_MODIFIED,
    REQUEST_DATE_CREATED,
    REQUEST_SIZE,
    REQUEST_EXTENSION,
    REQUEST_FULL_PATH_AND_FILE_NAME,
    REQUEST_PATH,
    REQUEST_FILE_NAME
)

DEFAULT_FLAGS: int = (
        REQUEST_FULL_PATH_AND_FILE_NAME
        | REQUEST_SIZE
        | REQUEST_DATE_MODIFIED
)

ALL_FLAGS: int = reduce(lambda x, y: x | y, _SUPPORTED_FLAGS)

# convert a windows FILETIME to a python datetime
# https://stackoverflow.com/questions/39481221/convert-datetime-back-to-windows-64-bit-filetime
WINDOWS_TICKS = int(1 / 10 ** -7)  # 10,000,000 (100 nanoseconds or .1 microseconds)
WINDOWS_EPOCH = datetime.datetime.strptime('1601-01-01 00:00:00', '%Y-%m-%d %H:%M:%S')
POSIX_EPOCH = datetime.datetime.strptime('1970-01-01 00:00:00', '%Y-%m-%d %H:%M:%S')
EPOCH_DIFF = (POSIX_EPOCH - WINDOWS_EPOCH).total_seconds()  # 11644473600.0
WINDOWS_TICKS_TO_POSIX_EPOCH = EPOCH_DIFF * WINDOWS_TICKS  # 116444736000000000.0


class Error(BaseException):
    def __init__(self, error_info):
        super().__init__(self)
        self.error_info = error_info

    def __str__(self):
        return self.error_info

    __repr__ = __str__


class Client:
    def __init__(self, dll_path=''):
        if not dll_path:
            dir_path = os.path.abspath(os.path.dirname(__file__))
            dll_path = os.path.join(dir_path, 'dll', 'Everything64.dll')
        self.dll_path = dll_path
        self.process_name = 'Everything.exe'
        self.dll = None
        self.error: [Error, None] = None
        self.buffers: Dict = {}
        self.flag_func_map: Dict = {}

        self.audio_ext = ('aac;ac3;aif;aifc;aiff;au;cda;dts;fla;flac;it;m1a;m2a;m3u;m4a;mid;midi;'
                          'mka;mod;mp2;mp3;mpa;ogg;ra;rmi;spc;rmi;snd;umx;voc;wav;wma;xm')
        self.compressed_ext = ('7z;ace;arj;bz2;cab;gz;gzip;jar;r00;r01;r02;r03;r04;r05;r06;r07;r08;'
                               'r09;r10;r11;r12;r13;r14;r15;r16;r17;r18;r19;r20;r21;r22;r23;r24;'
                               'r25;r26;r27;r28;r29;rar;tar;tgz;z;zip')
        self.doc_ext = ('ahk;ass;asm;c;cfg;chm;cpp;css;csv;cxx;doc;docm;docx;dot;dotm;dotx;go;h;hpp;'
                        'htm;html;hxx;ini;java;json;js;log;lua;lrc;md;mdb;mht;mhtml;odt;pdf;potx;potm;'
                        'ppam;ppsm;ppsx;pps;ppt;pptm;pptx;py;rtf;sh;sldm;sldx;sql;thmx;toml;txt;vsd;'
                        'vtt;wpd;wps;wri;xlam;xls;xlsb;xlsm;xlsx;xltm;xltx;xml;yml;yaml')
        self.exe_ext = 'bat;cmd;exe;msi;msp;scr'
        self.pic_ext = 'ani;bmp;gif;ico;jpe;jpeg;jpg;pcx;png;psd;svg;tga;tif;tiff;webp;wmf'
        self.video_ext = ('3g2;3gp;3gp2;3gpp;amr;amv;asf;avi;bdmv;bik;d2v;divx;drc;dsa;dsm;dss;dsv;'
                          'evo;f4v;flc;fli;flic;flv;hdmov;ifo;ivf;m1v;m2p;m2t;m2ts;m2v;m4b;m4p;m4v;'
                          'mkv;mp2v;mp4;mp4v;mpe;mpeg;mpg;mpls;mpv2;mpv4;mov;mts;ogm;ogv;pss;pva;'
                          'qt;ram;ratdvd;rm;rmm;rmvb;roq;rpm;smil;smk;swf;tp;tpr;ts;vob;vp6;webm;'
                          'wm;wmp;wmv')

    def __enter__(self):
        self.dll = ctypes.WinDLL(self.dll_path)  # dll imports

        if not self.is_running():
            raise self.error

        self._create_buffers()
        self._define_ctypes()
        self._create_flag_map()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        win32api.FreeLibrary(self.dll._handle)

    @staticmethod
    def _get_time(filetime) -> [datetime.datetime, None]:
        """Convert windows filetime winticks to python datetime.datetime."""
        win_ticks = struct.unpack('<Q', filetime)[0]
        if win_ticks == 18446744073709551615:
            return None
        microseconds = (win_ticks - WINDOWS_TICKS_TO_POSIX_EPOCH) / WINDOWS_TICKS
        return datetime.datetime.fromtimestamp(microseconds)

    @staticmethod
    def _flags_int_2_list(flags_num: int) -> List[int]:
        remain = flags_num
        search_flags = []
        for i in range(0, len(_SUPPORTED_FLAGS)):
            if remain == 0:
                break

            value = _SUPPORTED_FLAGS[i]
            if remain >= value:
                remain -= value
                search_flags.append(value)

        if remain != 0:
            raise AttributeError(f"error flags: {flags_num}")

        return search_flags

    def _create_buffers(self) -> None:
        buffers = {
            'full_path': ctypes.create_unicode_buffer(260),
            'size': ctypes.c_ulonglong(1),
            'accessed_time': ctypes.c_ulonglong(1),
            'created_time': ctypes.c_ulonglong(1),
            'modified_time': ctypes.c_ulonglong(1),
            'recently_changed': ctypes.c_ulonglong(1),
            'date_run': ctypes.c_ulonglong(1),
        }
        self.buffers = buffers

    def _create_flag_map(self) -> None:
        flag_list = _SUPPORTED_FLAGS

        key_list = ('highlighted_full_path', 'highlighted_path',
                    'highlighted_name', 'recently_changed',
                    'date_run', 'run_count',
                    'file_list_file_name', 'attributes',
                    'accessed_time', 'modified_time',
                    'created_time', 'size',
                    'extension', 'full_path',
                    'path', 'name')

        func_list = (self._get_flag_highlighted_full_path, self._get_flag_highlighted_path,
                     self._get_flag_highlighted_name, self._get_flag_recently_changed,
                     self._get_flag_date_run, self._get_flag_run_count,
                     self._get_flag_file_list_file_name, self._get_flag_attributes,
                     self._get_flag_accessed_time, self._get_flag_modified_time,
                     self._get_flag_created_time, self._get_flag_size,
                     self._get_flag_extension, self._get_flag_full_path,
                     self._get_flag_path, self._get_flag_name)

        d = {flag: (key, func) for flag, key, func in zip(flag_list, key_list, func_list)}
        self.flag_func_map = d

    def _define_ctypes(self) -> None:
        self.dll.Everything_GetResultDateCreated.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_ulonglong)]

        self.dll.Everything_GetResultDateModified.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_ulonglong)]

        self.dll.Everything_GetResultDateAccessed.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_ulonglong)]

        self.dll.Everything_GetResultSize.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_ulonglong)]

        self.dll.Everything_GetResultExtensionW.restype = ctypes.c_wchar_p

        self.dll.Everything_GetResultDateRecentlyChanged.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_ulonglong)]

        self.dll.Everything_GetResultDateRun.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_ulonglong)]

        self.dll.Everything_GetResultFileNameW.argtypes = [ctypes.c_int]
        self.dll.Everything_GetResultFileNameW.restype = ctypes.c_wchar_p

        self.dll.Everything_GetResultPathW.argtypes = [ctypes.c_int]
        self.dll.Everything_GetResultPathW.restype = ctypes.c_wchar_p

        self.dll.Everything_GetResultRunCount.argtypes = [ctypes.c_int]
        self.dll.Everything_GetResultRunCount.restype = ctypes.c_int

        self.dll.Everything_GetResultHighlightedFileNameW.argtypes = [ctypes.c_int]
        self.dll.Everything_GetResultHighlightedFileNameW.restype = ctypes.c_wchar_p

        self.dll.Everything_GetResultHighlightedPathW.argtypes = [ctypes.c_int]
        self.dll.Everything_GetResultHighlightedPathW.restype = ctypes.c_wchar_p

        self.dll.Everything_GetResultHighlightedFullPathAndFileNameW.argtypes = [ctypes.c_int]
        self.dll.Everything_GetResultHighlightedFullPathAndFileNameW.restype = ctypes.c_wchar_p

        self.dll.Everything_GetResultFileListFileNameW.argtypes = [ctypes.c_int]
        self.dll.Everything_GetResultFileListFileNameW.restype = ctypes.c_wchar_p

        self.dll.Everything_GetResultAttributes.argtypes = [ctypes.c_int]
        self.dll.Everything_GetResultAttributes.restype = ctypes.POINTER(ctypes.c_ulonglong)

    def _setup(self, keywords, math_path, math_case, whole_word,
               regex, offset, limit, flags, sort) -> None:
        self.dll.Everything_Reset()
        self.dll.Everything_SetSearchW(keywords)
        self.dll.Everything_SetMatchPath(math_path)
        self.dll.Everything_SetMatchCase(math_case)
        self.dll.Everything_SetMatchWholeWord(whole_word)
        self.dll.Everything_SetRegex(regex)
        self.dll.Everything_SetRequestFlags(flags)
        self.dll.Everything_SetSort(sort)
        if offset > 0:
            self.dll.Everything_SetOffset(offset)
        if limit > 0:
            self.dll.Everything_SetMax(limit)

    def _get_flag_name(self, idx) -> str:
        name = self.dll.Everything_GetResultFileNameW(idx)
        return name

    def _get_flag_path(self, idx) -> str:
        file_path = self.dll.Everything_GetResultPathW(idx)
        return file_path

    def _get_flag_full_path(self, idx) -> str:
        name = self.buffers['full_path']
        self.dll.Everything_GetResultFullPathNameW(idx, name, 260)
        return ctypes.wstring_at(name)

    def _get_flag_type(self, idx) -> str:
        if self.dll.Everything_IsFileResult(idx) == 1:
            return 'file'
        elif self.dll.Everything_IsFolderResult(idx) == 1:
            return 'folder'
        elif self.dll.Everything_IsVolumeResult(idx) == 1:
            return 'volume'
        else:
            return 'unknown'

    def _get_flag_size(self, idx) -> int:
        size = self.buffers['size']
        self.dll.Everything_GetResultSize(idx, size)
        return size.value

    def _get_flag_extension(self, idx) -> str:
        ext = self.dll.Everything_GetResultExtensionW(idx)
        return ext

    def _get_flag_run_count(self, idx) -> int:
        run_count = self.dll.Everything_GetResultRunCount(idx)  # returns 0 if unavailable
        return run_count

    def _get_flag_attributes(self, idx) -> str:
        attr = self.dll.Everything_GetResultAttributes(idx)
        attr_num = struct.unpack('<Q', attr)[0]

        remain = attr_num
        attr_names = ''
        for i in range(0, len(_ATTRIBUTES)):
            if remain == 0:
                break

            num, name = _ATTRIBUTES[i]
            if remain >= num:
                remain -= num
                attr_names += name

        if remain != 0:
            raise AttributeError(f"error attr: {attr_num}")

        attr_names = attr_names[::-1]
        return attr_names

    def _get_flag_file_list_file_name(self, idx) -> str:
        file_list_file_name = self.dll.Everything_GetResultFileListFileNameW(idx)
        return file_list_file_name

    def _get_flag_accessed_time(self, idx) -> datetime.datetime:
        time_accessed = self.buffers['accessed_time']
        self.dll.Everything_GetResultDateAccessed(idx, time_accessed)
        return self._get_time(time_accessed)

    def _get_flag_created_time(self, idx) -> datetime.datetime:
        time_created = self.buffers['created_time']
        self.dll.Everything_GetResultDateCreated(idx, time_created)
        return self._get_time(time_created)

    def _get_flag_modified_time(self, idx) -> datetime.datetime:
        modified_time = self.buffers['modified_time']
        self.dll.Everything_GetResultDateModified(idx, modified_time)
        return self._get_time(modified_time)

    def _get_flag_recently_changed(self, idx) -> datetime.datetime:
        recently_changed = self.buffers['recently_changed']
        self.dll.Everything_GetResultDateRecentlyChanged(idx, recently_changed)
        return self._get_time(recently_changed)

    def _get_flag_date_run(self, idx) -> datetime.datetime:
        date_run = self.buffers['date_run']
        self.dll.Everything_GetResultDateRun(idx, date_run)
        return self._get_time(date_run)

    def _get_flag_highlighted_name(self, idx) -> str:
        highlight_name = self.dll.Everything_GetResultHighlightedFileNameW(idx)
        return highlight_name

    def _get_flag_highlighted_path(self, idx) -> str:
        highlight_path = self.dll.Everything_GetResultHighlightedPathW(idx)
        return highlight_path

    def _get_flag_highlighted_full_path(self, idx) -> str:
        highlight_full_path = self.dll.Everything_GetResultHighlightedFullPathAndFileNameW(idx)
        return highlight_full_path

    def _execute_search(self) -> int:
        self.dll.Everything_QueryW(1)  # execute the query
        result_num = self.dll.Everything_GetNumResults()  # get the number of results
        return result_num

    def is_running(self) -> bool:
        _ = self.version()
        err = self.get_last_error()
        if err is not None:
            self.error = err
            return False
        return True

    def version(self) -> str:
        major_version = self.dll.Everything_GetMajorVersion()
        minor_version = self.dll.Everything_GetMinorVersion()
        revision = self.dll.Everything_GetRevision()
        build_number = self.dll.Everything_GetBuildNumber()
        version_string = f'{major_version}.{minor_version}.{revision}.{build_number}'
        return version_string

    def get_last_error(self) -> [Error, None]:
        error = self.dll.Everything_GetLastError()

        if error == OK:
            return None
        elif error == ERROR_MEMORY:
            error_info = "out of memory"
        elif error == ERROR_IPC:
            error_info = "IPC not available"
        elif error == ERROR_REGISTERCLASSEX:
            error_info = "register classEx failed"
        elif error == ERROR_CREATEWINDOW:
            error_info = "create window failed"
        elif error == ERROR_CREATETHREAD:
            error_info = "create thread failed"
        elif error == ERROR_INVALIDINDEX:
            error_info = "invalid result index (must be >= 0 and < numResults)"
        elif error == ERROR_INVALIDCALL:
            error_info = "call everything query before getting results"
        else:
            error_info = "unknown error"

        return Error(error_info)

    def _flags_adapter(self, flags: [int, Iterable[int]]) -> [int, list[int]]:
        if isinstance(flags, int):
            return flags, self._flags_int_2_list(flags)
        elif isinstance(flags, Iterable):
            return reduce(lambda x, y: x | y, flags), list(flags)
        else:
            raise AttributeError('arg flags must be int/Iterable[int]')

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

        flag_num, flag_list = self._flags_adapter(flags)
        self._setup(keywords, math_path, math_case, whole_word, regex, offset, limit, flag_num, sort)
        result_num = self._execute_search()

        for idx in range(result_num):
            data = {}
            for flag in flag_list:
                key, func = self.flag_func_map[flag]
                if func is not None:
                    data[key] = func(idx)

            yield data

    def search_in_located(self, path: str, keywords='', **kwargs):
        """Search files in a specific path"""
        return self.search(f'{path} {keywords}', **kwargs)

    def search_folder(self, keywords='', **kwargs):
        """Search folders"""
        return self.search(f'folder: {keywords}', **kwargs)

    def search_ext(self, ext: [str, Iterable[str]], keywords='', **kwargs):
        """Search by file extension"""
        if isinstance(ext, Iterable):
            ext = ';'.join(ext)
        ext = ext.replace('.', '')
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

    def exit(self) -> None:
        """exit everything"""
        self.dll.Everything_Exit()


if __name__ == '__main__':
    try:
        with Client() as client:
            print("everything version:\t", client.version())
            result = client.search("*.zip")
            print("*.zip:\t", len(list(result)))
    except (AttributeError, Error) as e:
        print(e)
