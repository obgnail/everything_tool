import ctypes
import datetime
import struct
import win32api

# defines
EVERYTHING_REQUEST_FILE_NAME = 0x00000001  # ✓
EVERYTHING_REQUEST_PATH = 0x00000002  # ✓
EVERYTHING_REQUEST_FULL_PATH_AND_FILE_NAME = 0x00000004
EVERYTHING_REQUEST_EXTENSION = 0x00000008  # ✓
EVERYTHING_REQUEST_SIZE = 0x00000010  # ✓
EVERYTHING_REQUEST_DATE_CREATED = 0x00000020  # ✓
EVERYTHING_REQUEST_DATE_MODIFIED = 0x00000040  # ✓
EVERYTHING_REQUEST_DATE_ACCESSED = 0x00000080  # ✓
EVERYTHING_REQUEST_ATTRIBUTES = 0x00000100
EVERYTHING_REQUEST_FILE_LIST_FILE_NAME = 0x00000200  # ✓
EVERYTHING_REQUEST_RUN_COUNT = 0x00000400  # ✓
EVERYTHING_REQUEST_DATE_RUN = 0x00000800
EVERYTHING_REQUEST_DATE_RECENTLY_CHANGED = 0x00001000
EVERYTHING_REQUEST_HIGHLIGHTED_FILE_NAME = 0x00002000  # ✓
EVERYTHING_REQUEST_HIGHLIGHTED_PATH = 0x00004000  # ✓
EVERYTHING_REQUEST_HIGHLIGHTED_FULL_PATH_AND_FILE_NAME = 0x00008000  # ✓

# 排序状态映射
EVERYTHING_SORT_NAME_ASCENDING = 1
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

# convert a windows FILETIME to a python datetime
# https://stackoverflow.com/questions/39481221/convert-datetime-back-to-windows-64-bit-filetime
WINDOWS_TICKS = int(1 / 10 ** -7)  # 10,000,000 (100 nanoseconds or .1 microseconds)
WINDOWS_EPOCH = datetime.datetime.strptime('1601-01-01 00:00:00', '%Y-%m-%d %H:%M:%S')
POSIX_EPOCH = datetime.datetime.strptime('1970-01-01 00:00:00', '%Y-%m-%d %H:%M:%S')
EPOCH_DIFF = (POSIX_EPOCH - WINDOWS_EPOCH).total_seconds()  # 11644473600.0
WINDOWS_TICKS_TO_POSIX_EPOCH = EPOCH_DIFF * WINDOWS_TICKS  # 116444736000000000.0

default_flags = (
        EVERYTHING_REQUEST_FILE_NAME
        | EVERYTHING_REQUEST_PATH
        | EVERYTHING_REQUEST_SIZE
        | EVERYTHING_REQUEST_DATE_CREATED
        | EVERYTHING_REQUEST_DATE_MODIFIED
        | EVERYTHING_REQUEST_DATE_ACCESSED
        | EVERYTHING_REQUEST_EXTENSION
        | EVERYTHING_REQUEST_RUN_COUNT
        | EVERYTHING_REQUEST_HIGHLIGHTED_FILE_NAME
        | EVERYTHING_REQUEST_HIGHLIGHTED_PATH
        | EVERYTHING_REQUEST_HIGHLIGHTED_FULL_PATH_AND_FILE_NAME
        | EVERYTHING_REQUEST_FILE_LIST_FILE_NAME
)


class EverythingTool:
    def __init__(self, dll_path='./dll/Everything64.dll'):
        self.dll_path = dll_path
        self.process_name = 'Everything.exe'

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

        if not self.check_running():
            return None

        self.__define_ctypes()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        win32api.FreeLibrary(self.dll._handle)

    @staticmethod
    def __get_time(filetime):
        """Convert windows filetime winticks to python datetime.datetime."""
        winticks = struct.unpack('<Q', filetime)[0]
        if winticks == 18446744073709551615:
            return None
        microsecs = (winticks - WINDOWS_TICKS_TO_POSIX_EPOCH) / WINDOWS_TICKS
        return datetime.datetime.fromtimestamp(microsecs)

    @staticmethod
    def __get_file_type(is_file, is_folder, is_volume):
        if is_file == 1:
            return 'file'
        elif is_folder == 1:
            return 'folder'
        elif is_volume == 1:
            return 'volume'
        return 'unknown'

    def check_running(self):
        # import psutil
        # return any(process.name() == self.process_name for process in psutil.process_iter())
        return self.version() != '0.0.0.0'

    def version(self):
        major_version = self.dll.Everything_GetMajorVersion()
        minor_version = self.dll.Everything_GetMinorVersion()
        revision = self.dll.Everything_GetRevision()
        build_number = self.dll.Everything_GetBuildNumber()
        version_string = f'{major_version}.{minor_version}.{revision}.{build_number}'
        return version_string

    def __define_ctypes(self):
        self.dll.Everything_GetResultDateCreated.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_ulonglong)]

        self.dll.Everything_GetResultDateModified.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_ulonglong)]

        self.dll.Everything_GetResultDateAccessed.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_ulonglong)]

        self.dll.Everything_GetResultSize.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_ulonglong)]

        self.dll.Everything_GetResultExtensionW.restype = ctypes.c_wchar_p

        self.dll.Everything_GetResultFileNameW.argtypes = [ctypes.c_int]
        self.dll.Everything_GetResultFileNameW.restype = ctypes.c_wchar_p

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

    def __setup_search(self, keyword, math_path, math_case, whole_world, regex, offset, limit, sort_type):
        self.dll.Everything_Reset()  # 重置状态
        self.dll.Everything_SetMatchPath(math_path)
        self.dll.Everything_SetMatchCase(math_case)
        self.dll.Everything_SetMatchWholeWord(whole_world)
        self.dll.Everything_SetRegex(regex)
        self.dll.Everything_SetSort(sort_type)
        self.dll.Everything_SetSearchW(keyword)
        self.dll.Everything_SetRequestFlags(default_flags)
        self.dll.Everything_SetOffset(offset)
        if limit > 0:
            self.dll.Everything_SetMax(limit)

    def __execute_search(self):
        self.dll.Everything_QueryW(1)  # execute the query
        num_results = self.dll.Everything_GetNumResults()  # get the number of results
        return num_results

    def search(
            self,
            keyword,
            math_path=False,
            math_case=False,
            whole_world=False,
            regex=False,
            offset=0,
            limit=-1,
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
        :param sort_type: 排序
        :return:
        """

        # create buffers
        name = ctypes.create_unicode_buffer(260)
        size = ctypes.c_ulonglong(1)
        time_accessed = ctypes.c_ulonglong(1)
        time_created = ctypes.c_ulonglong(1)
        time_modified = ctypes.c_ulonglong(1)

        self.__setup_search(keyword, math_path, math_case, whole_world, regex, offset, limit, sort_type)
        num_results = self.__execute_search()

        for i in range(num_results):
            self.dll.Everything_GetResultFullPathNameW(i, name, 260)
            self.dll.Everything_GetResultSize(i, size)
            self.dll.Everything_GetResultDateAccessed(i, time_accessed)
            self.dll.Everything_GetResultDateCreated(i, time_created)
            self.dll.Everything_GetResultDateModified(i, time_modified)

            is_file = self.dll.Everything_IsFileResult(i)
            is_folder = self.dll.Everything_IsFolderResult(i)
            is_volume = self.dll.Everything_IsVolumeResult(i)
            extension = self.dll.Everything_GetResultExtensionW(i)
            run_count = self.dll.Everything_GetResultRunCount(i)  # returns 0 if unavailable
            result_file_list_file_name = self.dll.Everything_GetResultFileListFileNameW(i)
            highlight_name = self.dll.Everything_GetResultHighlightedFileNameW(i)
            highlight_path = self.dll.Everything_GetResultHighlightedPathW(i)
            highlight_name_path = self.dll.Everything_GetResultHighlightedFullPathAndFileNameW(i)

            yield {
                'name': ctypes.wstring_at(name),
                'type': self.__get_file_type(is_file, is_folder, is_volume),
                'size': size.value,
                'extension': extension,
                'run_count': run_count,
                'file_list_file_name': result_file_list_file_name,
                'accessed_time': self.__get_time(time_accessed),
                'created_time': self.__get_time(time_created),
                'modified_time': self.__get_time(time_modified),
                'highlighted_name': highlight_name,
                'highlighted_path': highlight_path,
                'highlighted_name_path': highlight_name_path,
            }

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

    def exit(self):
        """退出everything"""
        self.dll.Everything_Exit()


if __name__ == '__main__':
    with EverythingTool() as tool:
        if not tool:
            print('everything is not running')
        else:
            print("version:", tool.version())

            result = tool.search("*.zip")
            print("*.zip:", len(list(result)))

    print('-- done --')
