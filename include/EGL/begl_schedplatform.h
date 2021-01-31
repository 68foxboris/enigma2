/*=============================================================================
Broadcom Proprietary and Confidential. (c)2014 Broadcom.
All rights reserved.
=============================================================================*/

#ifndef __BEGL_SCHEDINTERFACE_H__
#define __BEGL_SCHEDINTERFACE_H__

#include <EGL/begl_memplatform.h>
#include <stdbool.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum
{
   BEGL_SchedSuccess,
   BEGL_SchedFail
} BEGL_SchedStatus;

typedef enum
{
   BEGL_FenceSignaled,
   BEGL_FenceTimeout
} BEGL_FenceStatus;

typedef enum
{
   BEGL_CtrAcquire   = 0,
   BEGL_CtrRelease   = 1,
   BEGL_CtrStart     = 2,
   BEGL_CtrStop      = 3
} BEGL_SchedCounterState;

typedef enum
{
   BEGL_EventAcquire = 0,
   BEGL_EventRelease = 1,
   BEGL_EventStart   = 2,
   BEGL_EventStop    = 3
} BEGL_SchedEventState;

/* Forwards declare types used in interface */
struct bcm_sched_job;
struct bcm_sched_complete;
struct bcm_sched_query_response;
struct bcm_sched_dependencies;
struct v3d_idents;
struct bcm_sched_counter_group_desc;
struct bcm_sched_counter;
struct bcm_sched_group_counter_selector;
struct bcm_sched_event_track_desc;
struct bcm_sched_event_desc;
struct bcm_sched_event_field_desc;

typedef struct BEGL_SchedInterface
{
   void              *(*Open)(void *context);
   void               (*Close)(void *context, void *session);
   BEGL_SchedStatus   (*QueueJobs)(void *context, void *session, const struct bcm_sched_job *job, unsigned num_jobs);
   BEGL_SchedStatus   (*QueueBinRender)(void *context, void *session, const struct bcm_sched_job *bin, const struct bcm_sched_job *render);
   BEGL_SchedStatus   (*PollComplete)(void *context, void *session, struct bcm_sched_complete *complete);
   BEGL_SchedStatus   (*Query)(void *context, void *session, const struct bcm_sched_dependencies *completed_deps, const struct bcm_sched_dependencies *finalized_deps, struct bcm_sched_query_response *response);
   int                (*MakeFenceForJobs)(void *session, const struct bcm_sched_dependencies *completed_deps, const struct bcm_sched_dependencies *finalised_deps, bool force_create);
   int                (*MakeFenceForAnyNonFinalizedJob)(void *session);
   void               (*MakeFence)(void *context, int *fence);
   BEGL_SchedStatus   (*KeepFence)(void *context, int fence);
   void               (*WaitFence)(void *context, int fence);
   BEGL_FenceStatus   (*WaitFenceTimeout)(void *context, int fence, uint32_t timeoutms);
   void               (*SignalFence)(void *context, int fence);
   void               (*CloseFence)(void *context, int fence);
   void               (*GetInfo)(void *context, void *session, struct v3d_idents *info);

   void               (*RegisterUpdateOldestNFID)(void *context, void *session, void (*update)(uint64_t));

   /* Performance counters */
   void               (*GetPerfNumCounterGroups)(void *context, void *session, uint32_t *numGroups);
   BEGL_SchedStatus   (*GetPerfCounterGroupInfo)(void *context, void *session, uint32_t group, struct bcm_sched_counter_group_desc *desc);
   BEGL_SchedStatus   (*SetPerfCounting)(void *context, void *session, BEGL_SchedCounterState state);
   BEGL_SchedStatus   (*ChoosePerfCounters)(void *context, void *session, const struct bcm_sched_group_counter_selector *selector);
   uint32_t           (*GetPerfCounterData)(void *context, void *session, struct bcm_sched_counter  *counters, uint32_t max_counters, uint32_t reset_counts);

   /* Event timeline */
   void               (*GetEventCounts)(void *context, void *session, uint32_t *numTracks, uint32_t *numEvents);
   BEGL_SchedStatus   (*GetEventTrackInfo)(void *context, void *session, uint32_t track, struct bcm_sched_event_track_desc *track_desc);
   BEGL_SchedStatus   (*GetEventInfo)(void *context, void *session, uint32_t event, struct bcm_sched_event_desc *event_desc);
   BEGL_SchedStatus   (*GetEventDataFieldInfo)(void *context, void *session, uint32_t event, uint32_t field, struct bcm_sched_event_field_desc *field_desc);
   BEGL_SchedStatus   (*SetEventCollection)(void *context, void *session, BEGL_SchedEventState state);
   uint32_t           (*GetEventData)(void *context, void *session, uint32_t event_buffer_bytes, void *event_buffer, uint32_t *overflowed, uint64_t *timebase_us);

   void               (*SetMMUContext)(void *context, uint64_t physAddr, uint32_t maxVirtAddr, int64_t unsecureBinTranslation, int64_t secureBinTranslation, uint64_t platformToken);

   bool               (*ExplicitSync)(void *context);

   void                 *context;
   BEGL_MemoryInterface *memIface;

} BEGL_SchedInterface;


extern void BEGL_RegisterSchedInterface(BEGL_SchedInterface *iface);

typedef void (*PFN_BEGL_RegisterSchedInterface)(BEGL_SchedInterface *);

#ifdef __cplusplus
}
#endif

#endif /* _BEGL_SCHEDINTERFACE */
