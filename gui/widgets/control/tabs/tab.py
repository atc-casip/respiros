from abc import ABCMeta, abstractmethod

from gui.component import Component


class ControlTab(Component, metaclass=ABCMeta):
    """Base class for tabs in the control pane."""

    def __init__(self, app, title: str):
        super().__init__(app, visible=False)
        self.title = title

    @abstractmethod
    def lock(self):
        return

    @abstractmethod
    def unlock(self):
        return
