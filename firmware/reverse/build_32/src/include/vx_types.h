/* vx_types.h -- minimal VxWorks / RED base types for clangd / IntelliSense.
 *
 * These are NOT the real Wind River headers (those live in the toolchain container and
 * drive the byte-for-bit build). They exist only so the reconstructed units type-check
 * and navigate cleanly in an editor. The byte-exact build uses the original ccppc with
 * its own headers, never this file.
 */
#ifndef R1MX_VX_TYPES_H
#define R1MX_VX_TYPES_H

typedef int             STATUS;
typedef int             BOOL;

typedef unsigned char   UINT8;
typedef unsigned short  UINT16;
typedef unsigned int    UINT32;
typedef signed char     INT8;
typedef short           INT16;
typedef int             INT32;

typedef unsigned char   UCHAR;
typedef unsigned short  USHORT;
typedef unsigned int    UINT;
typedef unsigned long   ULONG;

#ifndef NULL
#define NULL ((void *)0)
#endif

#define OK     0
#define ERROR  (-1)
#define TRUE   1
#define FALSE  0

#endif /* R1MX_VX_TYPES_H */
