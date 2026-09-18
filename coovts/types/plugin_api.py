from abc import ABC, abstractmethod


# base API class for intellisense
class PluginAPI(ABC):
    @abstractmethod
    def _subscribe_event(self, *args, **kwargs): ...

    def subscribe_event(self, *args, **kwargs):
        return self._subscribe_event(*args, **kwargs)

    @abstractmethod
    async def _call_api(self, *args, **kwargs): ...

    def call_api(self, *args, **kwargs):
        return self._call_api(*args, **kwargs)
