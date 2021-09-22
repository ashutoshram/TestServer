try:
    import asyncio as asyncio_
except ImportError:
    aio = None
else:
    # asyncio abbreviations --------------------------------------------
    class aio:
        @classmethod
        def loop (cls, func, *args, **karg):
            loop = asyncio_.get_event_loop ()
            loop.run_until_complete (func (*args, **karg))  
        
        @classmethod
        def wait (cls, futures, timeout = None):
            return asyncio_.wait (futures, timeout = timeout)
        
        @classmethod
        def submit (cls, func, *args, **karg):
            return asyncio_.ensure_future(func (*args, **karg)) # Future
        
        @classmethod
        async def map (cls, func, iterable):
            futures = [cls.submit (func,  item) for item in iterable]
            return await asyncio_.gather (*futures)
    
        @classmethod
        async def thread (cls, func, *args, **karg):
            loop = asyncio_.get_event_loop()  
            return await loop.run_in_executor (None, func, *args, **karg) # Future
