import sys
import os
import errno
import ctypes
import struct
import time
import platform
import threading

from .future import Future

_HAS_TIMERFD = False
if platform.system() == "Linux":
    try:
        from .timerfd import *
        _HAS_TIMERFD = True
    except (AttributeError, OSError):
        pass

class Thread(Future):
    def __init__(self, target = None, name = None, args = (), kwargs = None):
        super().__init__()
        self.__target = target
        self.__args = args
        self.__kwargs = {} if kwargs is None else kwargs
        self.__thread = threading.Thread(target=self.__ThreadFunc, name=name, daemon=True)

    def Start(self):
        return self.__thread.start()
    
    def GetId(self):
        return self.__thread.ident
    
    def GetNativeId(self):
        return self.__thread.native_id

    def __ThreadFunc(self):
        value = None
        try:
            value = self.__target(*self.__args, **self.__kwargs)
            self.Ready(value)
        except:
            info = sys.exc_info() 
            self.Fail(f"[Thread] target func raise exception: name={info[0].__name__}, args={str(info[1].args)}")

class RecurrentThread(Thread):
    def __init__(self, interval: float = 1.0, target = None, name = None, args = (), kwargs = None):
        self.__quit = False
        self.__inter = interval
        self.__loopTarget = target
        self.__loopArgs = args
        self.__loopKwargs = {} if kwargs is None else kwargs

        if interval is None or interval <= 0.0:
            super().__init__(target=self.__LoopFunc_0, name=name)
        else:
            super().__init__(target=self.__LoopFunc, name=name)

    def Wait(self, timeout: float = None):
        self.__quit = True
        super().Wait(timeout)

    def __LoopFunc(self):
        if _HAS_TIMERFD:
            self.__LoopFunc_timerfd()
        else:
            self.__LoopFunc_sleep()

    def __LoopFunc_timerfd(self):
        # clock type CLOCK_MONOTONIC = 1
        tfd = timerfd_create(1, 0)
        spec = itimerspec.from_seconds(self.__inter, self.__inter)
        timerfd_settime(tfd, 0, ctypes.byref(spec), None)

        while not self.__quit:
            try:
                self.__loopTarget(*self.__loopArgs, **self.__loopKwargs)
            except:
                info = sys.exc_info()
                print(f"[RecurrentThread] target func raise exception: name={info[0].__name__}, args={str(info[1].args)}")

            try:
                buf = os.read(tfd, 8)
            except OSError as e:
                if e.errno != errno.EAGAIN:
                    raise e

        os.close(tfd)

    def __LoopFunc_sleep(self):
        while not self.__quit:
            step_start = time.perf_counter()
            try:
                self.__loopTarget(*self.__loopArgs, **self.__loopKwargs)
            except:
                info = sys.exc_info()
                print(f"[RecurrentThread] target func raise exception: name={info[0].__name__}, args={str(info[1].args)}")

            elapsed = time.perf_counter() - step_start
            remaining = self.__inter - elapsed
            if remaining > 0:
                time.sleep(remaining)
    
    def __LoopFunc_0(self):
        while not self.__quit:
            try:
                self.__loopTarget(*self.__args, **self.__kwargs)
            except:
                info = sys.exc_info() 
                print(f"[RecurrentThread] target func raise exception: name={info[0].__name__}, args={str(info[1].args)}")

