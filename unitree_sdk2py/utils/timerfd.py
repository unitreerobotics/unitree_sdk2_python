import math
import ctypes
import platform

"""声明计时通用接口，主要为兼容windows平台和linux的文件描述符,在python3.13 os会支持但现在还没release.."""
class Timer:
    
    """
    参数：
    time: 首次运行等待时间，秒.First Wait Time, second.
    period: 周期等待时间, 秒.Period Wait Time, second.
    """
    def __init__(self, time :float, period :float):
        pass
    
    """
    阻塞等待,会在下方根据平台重写
    """
    def blockWait(self):
        pass
    
    """
    关闭句柄
    """
    def close(self):
        pass


# build platform compatible
if platform.system() == "Windows":
    from ctypes import wintypes
    kernel32 = ctypes.windll.kernel32
    INFINITE=wintypes.DWORD(-1)
    PTIMERAPCROUTINE  = ctypes.WINFUNCTYPE(None, wintypes.LPVOID, wintypes.DWORD, wintypes.DWORD)
    @PTIMERAPCROUTINE
    def timer_callback(arg, timer_low, timer_high):
        pass
    # 重写Timer方法
    def Timer_init(self, time :float, period :float):
        self.handle = kernel32.CreateWaitableTimerW(None, True, None)
        due_time = wintypes.LARGE_INTEGER(-int(time * 10000000)) # 秒转100纳秒
        period = int(period*1000) # 秒转毫秒
        # https://learn.microsoft.com/zh-cn/windows/win32/api/synchapi/nf-synchapi-setwaitabletimer
        if not kernel32.SetWaitableTimer(self.handle, ctypes.byref(due_time), period, timer_callback, 0, True):
            raise OSError("Failed to set waitable timer.")
    def Timer_blockWait(self):
        kernel32.WaitForSingleObject(self.handle, INFINITE)
    def Timer_close(self):
        kernel32.CancelWaitableTimer(self.handle)
        kernel32.CloseHandle(self.handle)
    Timer.__init__ = Timer_init
    Timer.blockWait = Timer_blockWait
    Timer.close = Timer_close
    
elif platform.system() == "Linux":
    
    from .clib_lookup import CLIBLookup

    class timespec(ctypes.Structure):
        _fields_ = [("sec", ctypes.c_long), ("nsec", ctypes.c_long)]
        __slots__ = [name for name,type in _fields_]

        @classmethod
        def from_seconds(cls, secs):
            c = cls()
            c.seconds = secs
            return c
        
        @property
        def seconds(self):
            return self.sec + self.nsec / 1000000000

        @seconds.setter
        def seconds(self, secs):
            x, y = math.modf(secs)
            self.sec = int(y)
            self.nsec = int(x * 1000000000)


    class itimerspec(ctypes.Structure):
        _fields_ = [("interval", timespec),("value", timespec)]
        __slots__ = [name for name,type in _fields_]
        
        @classmethod
        def from_seconds(cls, interval, value):
            spec = cls()
            spec.interval.seconds = interval
            spec.value.seconds = value
            return spec


    # function timerfd_create
    timerfd_create = CLIBLookup("timerfd_create", ctypes.c_int, (ctypes.c_long, ctypes.c_int))

    # function timerfd_settime
    timerfd_settime_linux = CLIBLookup("timerfd_settime", ctypes.c_int, (ctypes.c_int, ctypes.c_int, ctypes.POINTER(itimerspec), ctypes.POINTER(itimerspec)))

    def timerfd_settime(handle,interval,value):
        spec = itimerspec.from_seconds(interval, value)
        timerfd_settime_linux(handle, 0, spec, None)

    # function timerfd_gettime
    timerfd_gettime = CLIBLookup("timerfd_gettime", ctypes.c_int, (ctypes.c_int, ctypes.POINTER(itimerspec)))
    # 重写Timer方法
    import os
    def Timer_init(self, time :float, period :float):
        self.handle = timerfd_create(1, 0)
        spec = itimerspec.from_seconds(period, time)
        timerfd_settime_linux(self.handle, 0, spec, None)
    def Timer_blockWait(self):
        os.read(self.handle,8)
    def Timer_close(self):
        os.close(self.handle)
    Timer.__init__ = Timer_init
    Timer.blockWait = Timer_blockWait
    Timer.close = Timer_close