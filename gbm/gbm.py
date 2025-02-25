from __future__ import annotations

import os
from contextlib import contextmanager
import gbm.capi.gbm as gb

class GbmError(Exception):
    pass

class GbmBufferObject:
    def __init__(self, bo_ptr, parent: GbmDevice | GbmSurface, destroy_on_close: bool):
        if not bo_ptr:
            raise GbmError('Failed to create GBM buffer object')
        self._bo = bo_ptr
        self._parent = parent
        self._closed = False
        self.destroy_on_close = destroy_on_close

    @property
    def width(self) -> int:
        return gb.gbm_bo_get_width(self._bo)

    @property
    def height(self) -> int:
        return gb.gbm_bo_get_height(self._bo)

    @property
    def stride(self) -> int:
        return gb.gbm_bo_get_stride(self._bo)

    @property
    def format(self) -> int:
        return gb.gbm_bo_get_format(self._bo)

    @property
    def handle(self) -> int:
        return gb.gbm_bo_get_handle(self._bo).u32

    def get_fd(self) -> int:
        """Get the file descriptor for the buffer object. The caller is responsible for closing the FD."""
        fd = gb.gbm_bo_get_fd(self._bo)
        if fd < 0:
            raise GbmError('Failed to get buffer FD')
        return fd

    @contextmanager
    def fd(self):
        """Context manager for the buffer object's file descriptor."""
        fd = self.get_fd()
        try:
            yield fd
        finally:
            os.close(fd)

    def close(self):
        if not self._closed and self._bo and self.destroy_on_close:
            gb.gbm_bo_destroy(self._bo)
        self._closed = True

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __del__(self):
        self.close()

class GbmSurface:
    def __init__(self, surface, parent: GbmDevice):
        self._surface = surface
        self._parent = parent
        self._current_bo = None
        self._closed = False

    @property
    def handle(self):
        return self._surface

    def lock_front_buffer(self) -> GbmBufferObject:
        bo = gb.gbm_surface_lock_front_buffer(self._surface)
        if not bo:
            raise GbmError('Failed to lock front buffer')
        self._current_bo = GbmBufferObject(bo, self, destroy_on_close=False)
        return self._current_bo

    def release_buffer(self, bo: GbmBufferObject):
        if bo._parent is not self:
            raise GbmError('Buffer object does not belong to this surface')
        gb.gbm_surface_release_buffer(self._surface, bo._bo)
        if bo is self._current_bo:
            self._current_bo = None

    @property
    def has_free_buffers(self) -> bool:
        return bool(gb.gbm_surface_has_free_buffers(self._surface))

    def close(self):
        if not self._closed and self._surface:
            gb.gbm_surface_destroy(self._surface)
            self._closed = True

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __del__(self):
        self.close()

class GbmDevice:
    def __init__(self, fd: int):
        self._device = gb.gbm_create_device(fd)
        if not self._device:
            raise GbmError('Failed to create GBM device')
        self._fd = fd
        self._closed = False

    @property
    def fd(self) -> int:
        return self._fd

    @property
    def handle(self):
        return self._device

    @property
    def backend_name(self) -> str:
        return gb.gbm_device_get_backend_name(self._device)

    def is_format_supported(self, format: int, flags: int) -> bool:
        return gb.gbm_device_is_format_supported(self._device, format, flags)

    def get_format_modifier_plane_count(self, format: int, modifier: int) -> int:
        return gb.gbm_device_get_format_modifier_plane_count(self._device, format, modifier)

    def create_buffer_object(self, width: int, height: int, format: int, flags: int) -> GbmBufferObject:
        bo = gb.gbm_bo_create(self._device, width, height, format, flags)
        if not bo:
            raise GbmError('Failed to create GBM buffer object')
        return GbmBufferObject(bo, self, destroy_on_close=True)

    def create_buffer_object_with_modifiers(self, width: int, height: int, format: int, modifiers: list[int]) -> GbmBufferObject:
        count = len(modifiers)
        mod_array = (gb.ctypes.c_uint64 * count)(*modifiers)

        bo = gb.gbm_bo_create_with_modifiers(self._device, width, height, format, mod_array, count)
        if not bo:
            raise GbmError('Failed to create GBM buffer object with modifiers')
        return GbmBufferObject(bo, self, destroy_on_close=True)

    def create_surface(self, width: int, height: int, format: int, flags: int) -> GbmSurface:
        surface = gb.gbm_surface_create(self._device, width, height, format, flags)
        if not surface:
            raise GbmError('Failed to create GBM surface')
        return GbmSurface(surface, self)

    def close(self):
        if not self._closed and self._device:
            gb.gbm_device_destroy(self._device)
            self._closed = True

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __del__(self):
        self.close()

# Re-export format and flag constants
GBM_FORMAT_XRGB8888 = gb.GBM_BO_FORMAT_XRGB8888
GBM_FORMAT_ARGB8888 = gb.GBM_BO_FORMAT_ARGB8888

GBM_BO_USE_SCANOUT = gb.GBM_BO_USE_SCANOUT
GBM_BO_USE_CURSOR = gb.GBM_BO_USE_CURSOR
GBM_BO_USE_RENDERING = gb.GBM_BO_USE_RENDERING
GBM_BO_USE_WRITE = gb.GBM_BO_USE_WRITE
GBM_BO_USE_LINEAR = gb.GBM_BO_USE_LINEAR
GBM_BO_USE_PROTECTED = gb.GBM_BO_USE_PROTECTED
GBM_BO_USE_FRONT_RENDERING = gb.GBM_BO_USE_FRONT_RENDERING
