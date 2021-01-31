/*=============================================================================
Broadcom Proprietary and Confidential. (c)2014 Broadcom.
All rights reserved.

Project  :  khronos
Module   :  Broadcom EGL extensions header

FILE DESCRIPTION
Extensions which we invented. If applications want to use these they must
include this file explicitly.
=============================================================================*/

#ifndef __eglext_brcm_h_
#define __eglext_brcm_h_

#ifdef __cplusplus
extern "C" {
#endif

#include <EGL/eglplatform.h>

#if KHRONOS_SUPPORT_INT64

typedef khronos_uint64_t EGLuint64BRCM;

/*  EGL_BRCM_performance_counters */
#ifndef EGL_BRCM_performance_counters
#define EGL_BRCM_performance_counters 1

#define EGL_ACQUIRE_COUNTERS_BRCM         0x33C0
#define EGL_RELEASE_COUNTERS_BRCM         0x33C1
#define EGL_START_COUNTERS_BRCM           0x33C2
#define EGL_STOP_COUNTERS_BRCM            0x33C3
#define EGL_NUM_COUNTER_GROUPS_BRCM       0x33C4
#define EGL_MAX_COUNTER_STRING_LEN_BRCM   0x33C5

   typedef EGLint     (EGLAPIENTRYP PFNEGLGETPERFCOUNTERCONSTANTBRCMPROC) (EGLenum pname);
   typedef EGLBoolean (EGLAPIENTRYP PFNEGLGETPERFCOUNTERGROUPINFOBRCMPROC) (EGLint group, EGLint nameStrSize, char *groupNameStr, EGLint *numCounters, EGLint *maxActiveCounters);
   typedef EGLBoolean (EGLAPIENTRYP PFNEGLGETPERFCOUNTERINFOBRCMPROC) (EGLint group, EGLint counter, EGLuint64BRCM *minValue, EGLuint64BRCM *maxValue, EGLuint64BRCM *denominator, EGLint nameStrSize, char *nameStr, EGLint unitStrSize, char *unitStr);
   typedef EGLBoolean (EGLAPIENTRYP PFNEGLSETPERFCOUNTINGBRCMPROC) (EGLenum pname);
   typedef EGLBoolean (EGLAPIENTRYP PFNEGLCHOOSEPERFCOUNTERSBRCMPROC) (EGLBoolean enable, EGLint group, EGLint numCounters, EGLint *counterList);
   typedef EGLBoolean (EGLAPIENTRYP PFNEGLGETPERFCOUNTERDATABRCMPROC) (EGLint dataBufferBytes, void *data, EGLint *bytesWritten, EGLBoolean resetCounters);

#ifdef GL_GLEXT_PROTOTYPES
   EGLAPI EGLint     EGLAPIENTRY eglGetPerfCounterConstantBRCM(EGLenum pname);
   EGLAPI EGLBoolean EGLAPIENTRY eglGetPerfCounterGroupInfoBRCM(EGLint group, EGLint nameStrSize, char *groupNameStr, EGLint *numCounters, EGLint *maxActiveCounters);
   EGLAPI EGLBoolean EGLAPIENTRY eglGetPerfCounterInfoBRCM(EGLint group, EGLint counter, EGLuint64BRCM *minValue, EGLuint64BRCM *maxValue, EGLuint64BRCM *denominator, EGLint nameStrSize, char *nameStr, EGLint unitStrSize, char *unitStr);
   EGLAPI EGLBoolean EGLAPIENTRY eglSetPerfCountingBRCM(EGLenum pname);
   EGLAPI EGLBoolean EGLAPIENTRY eglChoosePerfCountersBRCM(EGLBoolean enable, EGLint group, EGLint numCounters, EGLint *counterList);
   EGLAPI EGLBoolean EGLAPIENTRY eglGetPerfCounterDataBRCM(EGLint dataBufferBytes, void *data, EGLint *bytesWritten, EGLBoolean resetCounters);
#endif

#endif /* EGL_BRCM_performance_counters */

/*  EGL_BRCM_event_monitor */

#ifndef EGL_BRCM_event_monitor
#define EGL_BRCM_event_monitor 1

#define EGL_ACQUIRE_EVENTS_BRCM           0x33D0
#define EGL_RELEASE_EVENTS_BRCM           0x33D1
#define EGL_START_EVENTS_BRCM             0x33D2
#define EGL_STOP_EVENTS_BRCM              0x33D3
#define EGL_NUM_EVENT_TRACKS_BRCM         0x33D4
#define EGL_NUM_EVENTS_BRCM               0x33D5
#define EGL_MAX_EVENT_STRING_LEN_BRCM     0x33D6

   typedef EGLint     (EGLAPIENTRYP PFNEGLGETEVENTCONSTANTBRCMPROC) (EGLenum pname);
   typedef EGLBoolean (EGLAPIENTRYP PFNEGLGETEVENTTRACKINFOBRCMPROC) (EGLint track, EGLint nameStrSize, char *trackNameStr);
   typedef EGLBoolean (EGLAPIENTRYP PFNEGLGETEVENTINFOBRCMPROC) (EGLint event, EGLint nameStrSize, char *nameStr, EGLint *numDataFields);
   typedef EGLBoolean (EGLAPIENTRYP PFNEGLGETEVENTDATAFIELDINFOBRCMPROC) (EGLint event, EGLint field, EGLint nameStrSize, char *nameStr, EGLBoolean *isSigned, EGLint *numBytes);
   typedef EGLBoolean (EGLAPIENTRYP PFNEGLSETEVENTCOLLECTIONBRCMPROC) (EGLenum pname);
   typedef EGLBoolean (EGLAPIENTRYP PFNEGLGETEVENTDATABRCMPROC) (EGLint dataBufferBytes, void *data, EGLint *bytesWritten, EGLBoolean *overflowed, EGLuint64BRCM *timebase);

#ifdef GL_GLEXT_PROTOTYPES
   EGLAPI EGLint     EGLAPIENTRY eglGetEventConstantBRCM(EGLenum pname);
   EGLAPI EGLBoolean EGLAPIENTRY eglGetEventTrackInfoBRCM(EGLint track, EGLint nameStrSize, char *trackNameStr);
   EGLAPI EGLBoolean EGLAPIENTRY eglGetEventInfoBRCM(EGLint event, EGLint nameStrSize, char *nameStr, EGLint *numDataFields);
   EGLAPI EGLBoolean EGLAPIENTRY eglGetEventDataFieldInfoBRCM(EGLint event, EGLint field, EGLint nameStrSize, char *nameStr, EGLBoolean *isSigned, EGLint *numBytes);
   EGLAPI EGLBoolean EGLAPIENTRY eglSetEventCollectionBRCM(EGLenum pname);
   EGLAPI EGLBoolean EGLAPIENTRY eglGetEventDataBRCM(EGLint dataBufferBytes, void *data, EGLint *bytesWritten, EGLBoolean *overflowed, EGLuint64BRCM *timebase);
#endif

#endif /* EGL_BRCM_event_monitor */

#endif /* KHRONOS_SUPPORT_INT64 */

#ifndef EGL_BRCM_gl_framebuffer_image
#define EGL_BRCM_gl_framebuffer_image              1
#define EGL_GL_FRAMEBUFFER_BRCM                    0x70B9
#define EGL_GL_FRAMEBUFFER_TARGET_BRCM             0x70BA
#define EGL_GL_FRAMEBUFFER_ATTACHMENT_BRCM         0x70BB
#define EGL_GL_FRAMEBUFFER_CONVERT_TO_COLOR_BRCM   0x70BC
#define EGL_GL_FRAMEBUFFER_CONVERT_TO_UIF          0x70BD
#endif

#ifndef EGL_BRCM_platform_nexus
#define EGL_BRCM_platform_nexus 1
#define EGL_PLATFORM_NEXUS_BRCM                    0x32F0
#endif /* EGL_BRCM_platform_nexus */

#ifdef __cplusplus
}
#endif

#endif
