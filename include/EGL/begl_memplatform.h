/*=============================================================================
Broadcom Proprietary and Confidential. (c)2014 Broadcom.
All rights reserved.
=============================================================================*/

#ifndef __BEGL_MEMPLATFORM_H__
#define __BEGL_MEMPLATFORM_H__

#include <stdlib.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum
{
   BEGL_MemCacheLineSize,
   BEGL_MemLargestBlock,
   BEGL_MemFree,
   BEGL_MemPrintHeapData,
   BEGL_MemPagetablePhysAddr,
   BEGL_MemMmuMaxVirtAddr,
   BEGL_MemMmuUnsecureBinTranslation,
   BEGL_MemMmuSecureBinTranslation,
   BEGL_MemPlatformToken,
} BEGL_MemInfoType;

/* These must match gmem usage flags */
typedef enum
{
   BEGL_USAGE_CPU_READ     = 1 << 0,
   BEGL_USAGE_CPU_WRITE    = 1 << 1,
   BEGL_USAGE_V3D_READ     = 1 << 2,
   BEGL_USAGE_V3D_WRITE    = 1 << 3,
   BEGL_USAGE_COHERENT     = 1 << 5,
   BEGL_USAGE_HINT_DYNAMIC = 1 << 6,
   BEGL_USAGE_SECURE       = 1 << 7,
} BEGL_MemAllocFlags;

typedef void *BEGL_MemHandle;

typedef struct BEGL_MemoryInterface
{
   BEGL_MemHandle (*Alloc)(void *context, size_t numBytes, size_t alignment, uint32_t flags, const char *desc);
   void           (*Free)(void *context, BEGL_MemHandle h);
   void          *(*Map)(void *context, BEGL_MemHandle h, size_t offset, size_t length, uint32_t usage_flags);
   void           (*Unmap)(void *context, BEGL_MemHandle h, void *cpu_ptr, size_t length);
   uint32_t       (*Lock)(void *context, BEGL_MemHandle h);
   void           (*Unlock)(void *context, BEGL_MemHandle h);
   void           (*FlushCache)(void *context, BEGL_MemHandle h, void *pCached, size_t numBytes);
   uint64_t       (*GetInfo)(void *context, BEGL_MemInfoType type);

   /*
    * Optional entrypoint to create a wrapper handle to manage a MMU pagetable
    * mapping for externally allocated physically contiguous memory ranges
    */
   BEGL_MemHandle (*WrapExternal)(void *context, uint64_t physaddr, size_t length, const char *desc);

   void           *context;
} BEGL_MemoryInterface;


extern void BEGL_RegisterMemoryInterface(BEGL_MemoryInterface *iface);

typedef void (*PFN_BEGL_RegisterMemoryInterface)(BEGL_MemoryInterface *);

#ifdef __cplusplus
}
#endif

#endif
