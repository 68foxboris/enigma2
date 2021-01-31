/*=============================================================================
Broadcom Proprietary and Confidential. (c)2012 Broadcom.
All rights reserved.

Project  :  khronos
Module   :  Broadcom GLES extensions header

FILE DESCRIPTION
Extensions which we invented. Included by gl_public_api.h (used in the driver).
If applications want to use these they must include this file explicitly.
=============================================================================*/

#ifndef GL3EXT_BRCM_H
#define GL3EXT_BRCM_H

#ifdef __cplusplus
extern "C" {
#endif

#ifndef GL_APIENTRYP
#   define GL_APIENTRYP GL_APIENTRY*
#endif

/*  http://www.opengl.org/registry/api/enum.spec                              */
/*                                                                            */
/*  If an extension is experimental, allocate temporary enum values in the    */
/*  range 0x6000-0x8000 during development work.  When the vendor commits to  */
/*  releasing the extension, allocate permanent enum values (see link).       */

/* Expose "mirror once" texture wrap mode */
#ifndef GL_BRCM_mirror_clamp_to_edge
#define GL_BRCM_mirror_clamp_to_edge 1
#endif
#if GL_BRCM_mirror_clamp_to_edge
#define GL_MIRROR_CLAMP_TO_EDGE_BRCM   0x8743 /* wrap mode */
#endif

/* Expose unorm16/snorm16 texture types */
#ifndef GL_BRCM_texture_norm16
#define GL_BRCM_texture_norm16 1
#endif
#if GL_BRCM_texture_norm16
#define GL_R16_BRCM                   0x822A
#define GL_RG16_BRCM                  0x822C
#define GL_RGBA16_BRCM                0x805B
#define GL_R16_SNORM_BRCM             0x8F98
#define GL_RG16_SNORM_BRCM            0x8F99
#define GL_RGBA16_SNORM_BRCM          0x8F9B
#endif

#ifndef GL_BRCM_texture_1D
#define GL_BRCM_texture_1D 1
#endif
#if GL_BRCM_texture_1D
#define GL_TEXTURE_1D_BRCM               0x7930
#define GL_TEXTURE_1D_ARRAY_BRCM         0x7931
#define GL_SAMPLER_1D_BRCM               0x7932
#define GL_SAMPLER_1D_ARRAY_BRCM         0x7933
#define GL_INT_SAMPLER_1D_BRCM           0x7934
#define GL_INT_SAMPLER_1D_ARRAY_BRCM     0x7935
#define GL_UNSIGNED_INT_SAMPLER_1D_BRCM        0x7936
#define GL_UNSIGNED_INT_SAMPLER_1D_ARRAY_BRCM  0x7937
#define GL_TEXTURE_BINDING_1D_BRCM       0x7938
#define GL_TEXTURE_BINDING_1D_ARRAY_BRCM 0x7939

#ifdef GL_GLEXT_PROTOTYPES
GL_APICALL void GL_APIENTRY glTexImage1DBRCM (GLenum target, GLint level, GLint internalformat, GLsizei width, GLint border, GLenum format, GLenum type, const GLvoid* pixels);
#endif
typedef void   (GL_APIENTRYP PFNGLTEXIMAGE1DBRCMPROC) (GLenum target, GLint level, GLint internalformat, GLsizei width, GLint border, GLenum format, GLenum type, const GLvoid* pixels);
#endif /* GL_BRCM_texture_1D */

#ifndef GL_BRCM_polygon_mode
#define GL_BRCM_polygon_mode 1
#endif
#if GL_BRCM_polygon_mode
#define GL_FILL_BRCM    0x1B02 // These share values with the non-BRCM versions in gl3.h
#define GL_LINE_BRCM    0x1B01
#define GL_POINT_BRCM   0x1B00
#ifdef GL_GLEXT_PROTOTYPES
GL_APICALL void GL_APIENTRY glPolygonModeBRCM(GLenum mode);
#endif
#endif /* GL_BRCM_polygon_mode */

/* Like https://www.opengl.org/registry/specs/EXT/provoking_vertex.txt */
#ifndef GL_BRCM_provoking_vertex
# define GL_BRCM_provoking_vertex 1
#endif
#if GL_BRCM_provoking_vertex
#define GL_FIRST_VERTEX_CONVENTION_BRCM   0x8E4D
#define GL_LAST_VERTEX_CONVENTION_BRCM    0x8E4E
#define GL_PROVOKING_VERTEX_BRCM          0x8E4F
typedef void (GL_APIENTRYP PFNGLPROVOKINGVERTEXBRCMPROC)(GLenum mode);
#ifdef GL_GLEXT_PROTOTYPES
GL_APICALL void GL_APIENTRY glProvokingVertexBRCM(GLenum mode);
#endif
#endif /* GL_BRCM_provoking_vertex */

#ifndef GL_BRCM_texture_unnormalised_coords
# define GL_BRCM_texture_unnormalised_coords 1
#endif
#if GL_BRCM_texture_unnormalised_coords
#define GL_TEXTURE_UNNORMALISED_COORDS_BRCM 0x7940
#endif /*GL_BRCM_texture_unnormalised_coords */

#ifdef __cplusplus
}
#endif

#endif
