import ctypes
import datetime
import struct

# defines
EVERYTHING_REQUEST_FILE_NAME = 0x00000001
EVERYTHING_REQUEST_PATH = 0x00000002
EVERYTHING_REQUEST_FULL_PATH_AND_FILE_NAME = 0x00000004
EVERYTHING_REQUEST_EXTENSION = 0x00000008
EVERYTHING_REQUEST_SIZE = 0x00000010
EVERYTHING_REQUEST_DATE_CREATED = 0x00000020
EVERYTHING_REQUEST_DATE_MODIFIED = 0x00000040
EVERYTHING_REQUEST_DATE_ACCESSED = 0x00000080
EVERYTHING_REQUEST_ATTRIBUTES = 0x00000100
EVERYTHING_REQUEST_FILE_LIST_FILE_NAME = 0x00000200
EVERYTHING_REQUEST_RUN_COUNT = 0x00000400
EVERYTHING_REQUEST_DATE_RUN = 0x00000800
EVERYTHING_REQUEST_DATE_RECENTLY_CHANGED = 0x00001000
EVERYTHING_REQUEST_HIGHLIGHTED_FILE_NAME = 0x00002000
EVERYTHING_REQUEST_HIGHLIGHTED_PATH = 0x00004000
EVERYTHING_REQUEST_HIGHLIGHTED_FULL_PATH_AND_FILE_NAME = 0x00008000

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

everything_dll_path = './dll/Everything64.dll'

# dll imports
everything_dll = ctypes.WinDLL(everything_dll_path)

everything_dll.Everything_GetResultDateCreated.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_ulonglong)]
everything_dll.Everything_GetResultDateModified.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_ulonglong)]
everything_dll.Everything_GetResultSize.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_ulonglong)]
everything_dll.Everything_GetResultFileNameW.argtypes = [ctypes.c_int]
everything_dll.Everything_GetResultFileNameW.restype = ctypes.c_wchar_p
everything_dll.Everything_GetResultExtensionW.restype = ctypes.c_wchar_p

# convert a windows FILETIME to a python datetime
# https://stackoverflow.com/questions/39481221/convert-datetime-back-to-windows-64-bit-filetime
WINDOWS_TICKS = int(1 / 10 ** -7)  # 10,000,000 (100 nanoseconds or .1 microseconds)
WINDOWS_EPOCH = datetime.datetime.strptime('1601-01-01 00:00:00', '%Y-%m-%d %H:%M:%S')
POSIX_EPOCH = datetime.datetime.strptime('1970-01-01 00:00:00', '%Y-%m-%d %H:%M:%S')
EPOCH_DIFF = (POSIX_EPOCH - WINDOWS_EPOCH).total_seconds()  # 11644473600.0
WINDOWS_TICKS_TO_POSIX_EPOCH = EPOCH_DIFF * WINDOWS_TICKS  # 116444736000000000.0


def get_time(filetime):
    """Convert windows filetime winticks to python datetime.datetime."""
    winticks = struct.unpack('<Q', filetime)[0]
    if winticks == 18446744073709551615:
        return None
    microsecs = (winticks - WINDOWS_TICKS_TO_POSIX_EPOCH) / WINDOWS_TICKS
    return datetime.datetime.fromtimestamp(microsecs)


def version():
    major_version = everything_dll.Everything_GetMajorVersion()
    minor_version = everything_dll.Everything_GetMinorVersion()
    revision = everything_dll.Everything_GetRevision()
    build_number = everything_dll.Everything_GetBuildNumber()
    version_string = f'{major_version}.{minor_version}.{revision}.{build_number}'
    return version_string


def file_type(is_file, is_folder, is_volume):
    if is_file == 1:
        return 'file'
    elif is_folder == 1:
        return 'folder'
    elif is_volume == 1:
        return 'volume'
    return 'unknown'


def search(
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
    # setup search
    everything_dll.Everything_Reset()  # 重置状态
    everything_dll.Everything_SetMatchPath(math_path)
    everything_dll.Everything_SetMatchCase(math_case)
    everything_dll.Everything_SetMatchWholeWord(whole_world)
    everything_dll.Everything_SetRegex(regex)
    everything_dll.Everything_SetOffset(offset)
    everything_dll.Everything_SetSort(sort_type)

    if limit > 0:
        everything_dll.Everything_SetMax(limit)

    everything_dll.Everything_SetSearchW(keyword)
    everything_dll.Everything_SetRequestFlags(
        EVERYTHING_REQUEST_FILE_NAME |
        EVERYTHING_REQUEST_PATH |
        EVERYTHING_REQUEST_SIZE |
        EVERYTHING_REQUEST_DATE_CREATED |
        EVERYTHING_REQUEST_DATE_MODIFIED |
        EVERYTHING_REQUEST_EXTENSION
    )

    # execute the query
    everything_dll.Everything_QueryW(1)

    # get the number of results
    num_results = everything_dll.Everything_GetNumResults()

    # create buffers
    filename = ctypes.create_unicode_buffer(260)
    date_created_time = ctypes.c_ulonglong(1)
    date_modified_filetime = ctypes.c_ulonglong(1)
    file_size = ctypes.c_ulonglong(1)

    for i in range(num_results):
        everything_dll.Everything_GetResultFullPathNameW(i, filename, 260)
        everything_dll.Everything_GetResultDateCreated(i, date_created_time)
        everything_dll.Everything_GetResultDateModified(i, date_modified_filetime)
        everything_dll.Everything_GetResultSize(i, file_size)

        ext = everything_dll.Everything_GetResultExtensionW(i)
        is_file = everything_dll.Everything_IsFileResult(i)
        is_folder = everything_dll.Everything_IsFolderResult(i)
        is_volume = everything_dll.Everything_IsVolumeResult(i)

        yield {
            'name': ctypes.wstring_at(filename),
            'type': file_type(is_file, is_folder, is_volume),
            'size': file_size.value,
            'ext': ext,
            'created_date': get_time(date_created_time),
            'modified_date': get_time(date_modified_filetime),
        }


def search_audio(keywords=''):
    """搜索音频文件"""
    return search(f'ext:aac;ac3;aif;aifc;aiff;au;cda;dts;fla;flac;it;m1a;m2a;m3u;m4a;mid;midi;mka;mod;mp2;mp3;mpa;'
                  f'ogg;ra;rmi;spc;rmi;snd;umx;voc;wav;wma;xm {keywords}')


def search_compressed(keywords=''):
    """搜索压缩文件"""
    return search(f'ext:7z;ace;arj;bz2;cab;gz;gzip;jar;r00;r01;r02;r03;r04;r05;r06;r07;r08;r09;r10;r11;r12;r13;r14;'
                  f'r15;r16;r17;r18;r19;r20;r21;r22;r23;r24;r25;r26;r27;r28;r29;rar;tar;tgz;z;zip {keywords}')


def search_doc(keywords=''):
    """搜索文档"""
    return search(f'ext:c;chm;cpp;csv;cxx;doc;docm;docx;dot;dotm;dotx;h;hpp;htm;html;hxx;ini;java;lua;mht;mhtml;'
                  f'odt;pdf;potx;potm;ppam;ppsm;ppsx;pps;ppt;pptm;pptx;rtf;sldm;sldx;thmx;txt;vsd;wpd;wps;wri;'
                  f'xlam;xls;xlsb;xlsm;xlsx;xltm;xltx;xml {keywords}')


def search_exe(keywords=''):
    """搜索可执行文件"""
    return search(f'ext:bat;cmd;exe;msi;msp;scr {keywords}')


def search_folder(keywords=''):
    """搜索文件夹"""
    return search(f'folder: {keywords}')


def search_pic(keywords=''):
    """搜索图片"""
    return search(f'ext:ani;bmp;gif;ico;jpe;jpeg;jpg;pcx;png;psd;tga;tif;tiff;webp;wmf {keywords}')


def search_video(keywords=''):
    """搜索视频"""
    return search(f'ext:3g2;3gp;3gp2;3gpp;amr;amv;asf;avi;bdmv;bik;d2v;divx;drc;dsa;dsm;dss;dsv;evo;f4v;flc;fli;'
                  f'flic;flv;hdmov;ifo;ivf;m1v;m2p;m2t;m2ts;m2v;m4b;m4p;m4v;mkv;mp2v;mp4;mp4v;mpe;mpeg;mpg;mpls;'
                  f'mpv2;mpv4;mov;mts;ogm;ogv;pss;pva;qt;ram;ratdvd;rm;rmm;rmvb;roq;rpm;smil;smk;swf;tp;tpr;ts;'
                  f'vob;vp6;webm;wm;wmp;wmv {keywords}')


def search_ext(ext, keywords=''):
    """搜索扩展名称"""
    return search(f'ext:{ext} {keywords}')


def search_in_located(path, keywords=''):
    """搜索路径下文件"""
    return search(f'{path} {keywords}')


def exit_everything():
    """ 执行退出客户端操作，会失去连接"""
    everything_dll.Everything_Exit()
    everything_dll.FreeLibrary()


if __name__ == '__main__':
    result = search("*.zip")
    print(len(list(result)))
