/*=============================================================================
Broadcom Proprietary and Confidential. (c)2016 Broadcom.
All rights reserved.

Project  :  khronos
Module   :  Wayland EGL extensions header

FILE DESCRIPTION
Wayland EGL extensions.

IMPORTANT NOTE
The EGL_WL_bind_wayland_display extension is essential for the server-side
Wayland to access client-side buffers but it's NOT present in the Khronos
registry, therefore it's not included with the standard eglext.h file
auto-generated from the registry and released by the Khronos group.

This file is a (hopefully) temporary workaround necessary until the
WL_bind_wayland_display extension finally lands in the Khronos registry.
A slightly modified eglext.h temporarily includes this file and that's the only
modification to the eglext.h.
=============================================================================*/

#ifndef __eglext_wayland_h_
#define __eglext_wayland_h_

#include "eglplatform.h"

#ifdef __cplusplus
extern "C" {
#endif

#ifndef EGL_WL_bind_wayland_display
#define EGL_WL_bind_wayland_display 1

#define EGL_WAYLAND_BUFFER_WL       0x31D5 /* eglCreateImageKHR target */
#define EGL_WAYLAND_PLANE_WL        0x31D6 /* eglCreateImageKHR target */

#define EGL_WAYLAND_Y_INVERTED_WL   0x31DB /* eglQueryWaylandBufferWL attribute */

#define EGL_TEXTURE_Y_U_V_WL        0x31D7
#define EGL_TEXTURE_Y_UV_WL         0x31D8
#define EGL_TEXTURE_Y_XUXV_WL       0x31D9

struct wl_display;
struct wl_resource;

typedef EGLBoolean (EGLAPIENTRYP PFNEGLBINDWAYLANDDISPLAYWL) (EGLDisplay dpy, struct wl_display *display);
typedef EGLBoolean (EGLAPIENTRYP PFNEGLUNBINDWAYLANDDISPLAYWL) (EGLDisplay dpy, struct wl_display *display);
typedef EGLBoolean (EGLAPIENTRYP PFNEGLQUERYWAYLANDBUFFERWL) (
  EGLDisplay          dpy,
  struct wl_resource *buffer,
  EGLint              attribute,
  EGLint             *value);
  #ifdef EGL_EGLEXT_PROTOTYPES
EGLAPI EGLBoolean EGLAPIENTRY eglBindWaylandDisplayWL(
  EGLDisplay         dpy,
  struct wl_display *display);
EGLAPI EGLBoolean EGLAPIENTRY eglUnbindWaylandDisplayWL(
  EGLDisplay         dpy,
  struct wl_display *display);

EGLAPI EGLBoolean EGLAPIENTRY eglQueryWaylandBufferWL(
  EGLDisplay          dpy,
  struct wl_resource *buffer,
  EGLint              attribute,
  EGLint             *value);
  #endif
#endif

#ifdef __cplusplus
}
#endif

#endif
