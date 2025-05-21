from abc import ABC, abstractmethod


class PluginAPI(ABC):
    @abstractmethod
    def _call_api(self, *args, **kwargs): ...

    def call_api(self, *args, **kwargs):
        return self._call_api(*args, **kwargs)
