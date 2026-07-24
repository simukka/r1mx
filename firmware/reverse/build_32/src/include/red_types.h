/* red_types.h -- RED-specific structs recovered during reconstruction, shared across
 * units so clangd resolves them consistently. Editor aid only (see vx_types.h); the
 * byte-exact build does not use this header.
 */
#ifndef R1MX_RED_TYPES_H
#define R1MX_RED_TYPES_H

#include "vx_types.h"

/* FlashVx bounding rectangle: {left, right, top, bottom} (width = x1-x0, height =
 * y1-y0). Recovered from app_modules/ui_engine/flashvx.cpp (DrawMouse clamp math +
 * FrameBufferRect's field-for-field copy). */
struct FlashRect {
    int x0;   /* left   */
    int x1;   /* right  */
    int y0;   /* top    */
    int y1;   /* bottom */
};

#endif /* R1MX_RED_TYPES_H */
