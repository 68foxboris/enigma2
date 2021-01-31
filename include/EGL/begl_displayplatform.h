/*=============================================================================
Broadcom Proprietary and Confidential. (c)2014 Broadcom.
All rights reserved.

Project  :  khronos

FILE DESCRIPTION
Platform specific header for BCG's abstract platform support
=============================================================================*/

#ifndef __BEGL_DISPLAYPLATFORM_H__
#define __BEGL_DISPLAYPLATFORM_H__

#ifdef __cplusplus
extern "C"
{
#endif

#include <EGL/begl_memplatform.h>

#include <stdint.h>
#include <stdlib.h>

#ifndef __cplusplus
#include <stdbool.h>
#endif

/*****************************************************************************
 *****************************************************************************
 *****                       DISPLAY INTERFACE                           *****
 *****************************************************************************
 *****************************************************************************/

typedef enum
{
   BEGL_Success = 0,
   BEGL_Fail
} BEGL_Error;

typedef enum
{
   BEGL_Increment = 0,
   BEGL_Decrement
} BEGL_RefCountMode;

typedef enum
{
   BEGL_WindowInfoWidth = 1,
   BEGL_WindowInfoHeight = 2,
   BEGL_WindowInfoFormat = 4,
   BEGL_WindowInfoSwapChainCount = 8,
} BEGL_WindowInfoFlags;

typedef enum
{
   /* These formats are render target formats */
   BEGL_BufferFormat_eA8B8G8R8,
   BEGL_BufferFormat_eR8G8B8A8,
   BEGL_BufferFormat_eX8B8G8R8,
   BEGL_BufferFormat_eR8G8B8X8,
   BEGL_BufferFormat_eR5G6B5,

   BEGL_BufferFormat_eR4G4B4A4,
   BEGL_BufferFormat_eA4B4G4R4,
   BEGL_BufferFormat_eR4G4B4X4,
   BEGL_BufferFormat_eX4B4G4R4,

   BEGL_BufferFormat_eR5G5B5A1,
   BEGL_BufferFormat_eA1B5G5R5,
   BEGL_BufferFormat_eR5G5B5X1,
   BEGL_BufferFormat_eX1B5G5R5,

   /* non renderable input formats */
   BEGL_BufferFormat_eYV12,                  /* 3 planes layed out in Google format */
   BEGL_BufferFormat_eYUV422,                /* Single plane YUYV */

   /* renderable, but can only be used by the display and not re-read */
   BEGL_BufferFormat_eBSTC,

   /* Can be used to return back an invalid format */
   BEGL_BufferFormat_INVALID
} BEGL_BufferFormat;

typedef struct
{
   uint32_t            width;                 /* Visible width of window in pixels */
   uint32_t            height;                /* Visible height of window in pixels */
   uint32_t            swapchain_count;       /* Number of buffers in the swap chain, or 0 to take defaults from egl */
} BEGL_WindowInfo;

typedef struct BEGL_PixmapInfo
{
   uint32_t            width;                 /* Visible width of pixmap in pixels */
   uint32_t            height;                /* Visible height of pixmap in pixels */
   BEGL_BufferFormat   format;
} BEGL_PixmapInfo;

typedef struct BEGL_PixmapInfoEXT
{
   uint32_t            magic;
   uint32_t            width;                 /* Visible width of pixmap in pixels */
   uint32_t            height;                /* Visible height of pixmap in pixels */
   BEGL_BufferFormat   format;
   bool                secure;                /* Create pixmap in secure heap */
} BEGL_PixmapInfoEXT;

typedef struct
{
   uint32_t            width;                 /* Visible width of surface in pixels                   */
   uint32_t            height;                /* Visible height of surface in pixels                  */
   uint32_t            pitchBytes;            /* Bytes per row                                        */
   uint64_t            physicalOffset;        /* Physical address                                     */
   void                *cachedAddr;           /* Cached address mapping                               */
   uint32_t            byteSize;              /* Size of buffer in bytes                              */
   BEGL_BufferFormat   format;
} BEGL_SurfaceInfo;

typedef struct BEGL_DisplayInterface
{
   /* Context pointer - opaque to the 3d driver code, but passed out in all function pointer calls.
    * Prevents the client code needing to perform context lookups. */
   void *context;

   /* Called to determine current size of the window referenced by the opaque window handle.
    * Also fills in the number of pre-allocated swap-chain buffers, which must be > 0.
    * Set to the number of buffers in your pre-allocated chain. See BufferGet().
    * This is needed by EGL in order to know the size of a native 'window'. */
   BEGL_Error (*WindowGetInfo)(void *context, void *opaqueNativeWindow, BEGL_WindowInfoFlags flags, BEGL_WindowInfo *info);

   BEGL_Error (*SurfaceGetInfo)(void *context, void *opaqueNativeSurface, BEGL_SurfaceInfo *info);
   BEGL_Error (*SurfaceChangeRefCount)(void *context, void *opaqueNativeSurface, BEGL_RefCountMode inOrDec);
   BEGL_Error (*SurfaceVerifyImageTarget)(void *context, void *opaqueNativeSurface, uint32_t eglTarget);

   /* Return the next render buffer surface in the swap chain (in opaqueNativeSurface)
    * with a fence to wait on before accesing the buffer surface.
    * A surface obtained this way must be returned to the display system with a call to
    * DisplaySurface or CancelSurface.
    * All these 3 functions must be implemented;
    */
   BEGL_Error (*GetNextSurface)(void *context, void *opaqueNativeWindow, BEGL_BufferFormat format,
                               BEGL_BufferFormat *actualFormat, void **opaqueNativeSurface, bool secure, int *fence);

   BEGL_Error (*DisplaySurface)(void *context, void *nativeWindow, void *nativeSurface, int fence);

   BEGL_Error (*CancelSurface)(void *context, void *nativeWindow, void *nativeSurface, int fence);

   void (*SetSwapInterval)(void *context, void *nativeWindow, int interval);

   bool  (*PlatformSupported)(void *context, uint32_t platform);

   bool  (*SetDefaultDisplay)(void *context, void *display);

   void *(*GetDefaultDisplay)(void *context);

   void *(*WindowPlatformStateCreate)(void *context, void *nativeWindow);

   BEGL_Error (*WindowPlatformStateDestroy)(void *context, void *windowState);

   BEGL_Error (*GetNativeFormat)(void *context, BEGL_BufferFormat format, uint32_t *nativeformat);

   const char *(*GetClientExtensions)(void *context);
   const char *(*GetDisplayExtensions)(void *context);

   bool (*BindWaylandDisplay)(void *context, void *egl_display, void *wl_display);

   bool (*UnbindWaylandDisplay)(void *context, void *egl_display, void *wl_display);

   bool (*QueryBuffer)(void *context, void *display, void* buffer, int32_t attribute, int32_t *value);

} BEGL_DisplayInterface;

extern void BEGL_RegisterDisplayInterface(BEGL_DisplayInterface *iface);
extern void BEGL_PlatformAboutToShutdown(void);

typedef void (*PFN_BEGL_RegisterDisplayInterface)(BEGL_DisplayInterface *);
typedef void (*PFN_BEGL_PlatformAboutToShutdown)(void);

#ifdef __cplusplus
}
#endif

#endif /* __BEGL_DISPLAYPLATFORM_H__ */
