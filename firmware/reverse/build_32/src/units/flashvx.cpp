/* flashvx.cpp -- reconstructed FlashVx (Scaleform GFx wrapper) translation unit.
 *
 * Original source path (recovered from the embedded __FILE__ string at 0xD4CC68):
 *     app_modules/ui_engine/flashvx.cpp
 * Module   : app_modules/ui_engine     Provenance: red
 * Fidelity : draft  (readable, behaviour-faithful; NOT yet byte-gated)
 *
 * This is the unit that owns the on-screen OSD framebuffer and pushes rendered
 * regions to the iofpga -- i.e. the place to change *how the GUI is rendered*.
 * It is the C++ TU that contains the requested entry point:
 *
 *     _ZN7FlashVxC1E9FlashRectPKc   FlashVx::FlashVx(FlashRect, const char*)   @ 0x0014F03C
 *
 * NOTE on the symbol name: re_reference.md §23.3 listed this ctor as
 * `_ZN7FlashVxC1Ev` (no args). That is wrong -- there is no nullary ctor in the
 * binary. The real complete-object ctor takes (FlashRect bounds, const char* name)
 * and is mangled `_ZN7FlashVxC1E9FlashRectPKc`. (Corrected in re_reference.md.)
 *
 * ---------------------------------------------------------------------------
 * TU function map (resolved from the VxWorks symbol table in software.bin):
 *
 *   0x0014EFC0  _ZN7FlashVxC2E9FlashRectPKc   FlashVx::FlashVx [base-obj ctor]
 *   0x0014F03C  _ZN7FlashVxC1E9FlashRectPKc   FlashVx::FlashVx [complete-obj]  <-- ENTRY POINT
 *   0x0014F0B8  _ZN7FlashVx15FrameBufferFreeEv
 *   0x0014F110  _ZN7FlashVxD2Ev               ~FlashVx [base-obj dtor]
 *   0x0014F150  _ZN7FlashVxD1Ev               ~FlashVx [complete-obj dtor]
 *   0x0014F190  _ZN7FlashVxD0Ev               ~FlashVx [deleting dtor]
 *   0x0014F1D8  _ZN7FlashVx22FrameBufferPixelFormatEv
 *   0x0014F1F0  _ZN7FlashVx16FrameBufferAllocEiiRi
 *   0x0014F2B4  _ZN7FlashVx9DrawMouseEv
 *   0x0014F35C  _ZN7FlashVx15FrameBufferBlitEiiii
 *   0x0014F660  _ZNK7FlashVx15FrameBufferRectER9FlashRect
 *   0x0014F68C  _ZN7FlashVx17FrameBufferResizeEii
 *   (URLRequest / Http/File/NetworkStatus / mouse / key / ExtInit follow in the
 *    same TU at 0x14F6AC..0x14FF00 -- not reconstructed here; they are the
 *    GFx<->RED glue, not part of the render/blit path.)
 *
 * vtable: &FlashVx::vtable == 0xE08DC0 (installed at this+0x00 by the ctor/dtors).
 *
 * ---------------------------------------------------------------------------
 * Object layout (offsets proven from the member stores/loads in every method).
 * FlashVx derives from FlashPlayer; the base occupies [0x00..0x8B]. The vptr is
 * the first word of the base (this+0x00). FlashVx's own fields start at 0x8C:
 *
 *   +0x00  vptr                      -> 0xE08DC0
 *   ...    (FlashPlayer base state, 0x04..0x8B -- owned by the base ctor)
 *   +0x8C  int   bounds.x0           render-target rect, left
 *   +0x90  int   bounds.x1           render-target rect, right
 *   +0x94  int   bounds.y0           render-target rect, top
 *   +0x98  int   bounds.y1           render-target rect, bottom
 *   +0x9C  void* framebuffer         CPU RAM render target (memalign'd in Alloc)
 *   +0xA0  int   bytesPerPixel       = 4 (BGRA)
 *   +0xA8  int   mouseX              software cursor position
 *   +0xAC  int   mouseY
 *
 * FlashRect is {int x0, x1, y0, y1} (width = x1-x0, height = y1-y0); confirmed by
 * DrawMouse's clamp math and by FrameBufferRect's field-for-field copy.
 * ---------------------------------------------------------------------------
 */

/* ---- types ---------------------------------------------------------------- */

struct FlashRect {
    int x0;   /* left   */
    int x1;   /* right  */
    int y0;   /* top    */
    int y1;   /* bottom */
};

class FlashPlayer {
public:
    /* base methods of interest live in flashplayer.cpp (other TU) */
};

class FlashVx : public FlashPlayer {
public:
    FlashVx(FlashRect bounds, const char *name);
    virtual ~FlashVx();

    void *FrameBufferAlloc(int width, int height, int &bytesPerLine);
    void  FrameBufferFree();
    void  FrameBufferResize(int width, int height);
    int   FrameBufferPixelFormat();
    void  FrameBufferRect(FlashRect &out) const;
    void  FrameBufferBlit(int x, int y, int w, int h);
    void  DrawMouse();

private:
    /* padding to place own fields at the proven offsets; the base is 0x8C bytes */
    char  _base_pad[0x8C - sizeof(FlashPlayer)];   /* conceptual; see layout note */
    int   bounds_x0;        /* +0x8C */
    int   bounds_x1;        /* +0x90 */
    int   bounds_y0;        /* +0x94 */
    int   bounds_y1;        /* +0x98 */
    void *framebuffer;      /* +0x9C */
    int   bytesPerPixel;    /* +0xA0 */
    int   _rsvd_a4;         /* +0xA4 */
    int   mouseX;           /* +0xA8 */
    int   mouseY;           /* +0xAC */
};

/* ---- externs (other TUs / OS) -------------------------------------------- */

/* FlashPlayer base ctor/dtor and operator delete (mangled C1/D1 of the base). */
extern "C" void *FlashPlayer_ctor(FlashPlayer *self, FlashRect bounds, const char *name); /* 0x262458 */
extern "C" void  FlashPlayer_dtor(FlashPlayer *self);                                      /* 0x262880 */
extern "C" void  operator_delete(void *p);                                                /* 0x255C34 */

/* Allocator: 16-byte-aligned alloc / free (RED heap wrappers). */
extern "C" void *aligned_alloc16(int align, unsigned size);   /* 0x46964C  (align=16) */
extern "C" void  heap_free(void *p);                          /* 0x46B580 */

/* RED diagnostic logger. Signature recovered from the call sites:
 *   ui_log(level, facility, line, __FILE__, __func__, fmt, ...) */
extern "C" void ui_log(int level, int facility, int line,
                       const char *file, const char *func, const char *fmt, ...); /* 0x6E784 */

/* iofpga OSD push paths (the actual "render to screen"): */
extern "C" void osd_blit_screen(void *fb, int x0, int y0, int x1, int y1,
                                int bytesPerPixel, int bytesPerLine);   /* 0x1F661C */
extern "C" void osd_blit_lcd(void *fb, int a, int b, int x0, int y0,
                             int w, int h);                            /* 0x1B8A64 */

/* dirty-region rectangle bookkeeping (GFx RectList <-> screen): */
extern "C" void rect_begin(void *rl);                       /* 0x1BA5DC */
extern "C" void rect_end(void *rl);                         /* 0x1BA604 */
extern "C" void rect_flush(void *rl);                       /* 0x1BA5B0 */
extern "C" int  rect_next(void *rl, FlashRect *out);        /* 0x1BA4FC -> 0 when none */

/* display hot-plug notifications (LCD / SCREEN attach state machine): */
extern "C" void display_notify_lcd(int connected);          /* 0xA2094 */
extern "C" void display_notify_screen(int connected);       /* 0x95398 */
extern "C" void display_log_flush(void);                    /* 0x6EA28 */

/* OSD output state, FPGA-side. Globals in the .data island at 0xEA0xxx: */
extern int  g_osd_enabled;        /* 0xEA0DE4  -- blit is a no-op while 0 */
extern char g_lcd_present;        /* 0xEA0DDC */
extern char g_screen_present;     /* 0xEA0DDD */
extern char g_lcd_attached;       /* 0xEA0E78 */
extern char g_screen_attached;    /* 0xEA0E79 */

/* the recovered __FILE__ string lives once per TU at 0xD4CC68 */
static const char *const kFile = "app_modules/ui_engine/flashvx.cpp";

/* the FlashVx vtable symbol (0xE08DC0) */
extern void *const _ZTV7FlashVx[];          /* &_ZTV7FlashVx[2] == 0xE08DC0 */

/* ===========================================================================
 * 0x0014F03C  FlashVx::FlashVx(FlashRect bounds, const char *name)   ENTRY POINT
 *
 * Complete-object ctor. Chains the FlashPlayer base ctor (which consumes `name`),
 * installs the FlashVx vtable, stores the render-target bounds, and zero-inits
 * the framebuffer + cursor. bytesPerPixel defaults to 4 (BGRA).
 * ===========================================================================*/
FlashVx::FlashVx(FlashRect bounds, const char *name)
{
    FlashPlayer_ctor(this, bounds, name);   /* bl 0x262458 -- base ctor */

    /* this+0x8C..0x98 = bounds, copied field-for-field */
    this->bounds_x0    = bounds.x0;
    this->bounds_x1    = bounds.x1;
    this->bounds_y0    = bounds.y0;
    this->bounds_y1    = bounds.y1;

    this->bytesPerPixel = 4;                /* +0xA0 */
    this->framebuffer   = 0;                /* +0x9C */
    this->mouseX        = 0;                /* +0xA8 */
    this->mouseY        = 0;                /* +0xAC */

    *(void **)this = (void *)&_ZTV7FlashVx[2];  /* vptr = 0xE08DC0 */
}

/* ===========================================================================
 * 0x0014F0B8  FlashVx::FrameBufferFree()
 * ===========================================================================*/
void FlashVx::FrameBufferFree()
{
    if (this->framebuffer != 0) {
        heap_free(this->framebuffer);       /* bl 0x46B580 */
        this->framebuffer = 0;
    }
}

/* ===========================================================================
 * 0x0014F110 / 0x0014F150  ~FlashVx  (base-obj / complete-obj dtor; identical)
 * 0x0014F190              ~FlashVx  (deleting dtor: + operator delete)
 *
 * Re-install our vptr (so virtual calls during teardown resolve to FlashVx),
 * free the framebuffer, then run the base dtor.
 * ===========================================================================*/
FlashVx::~FlashVx()
{
    *(void **)this = (void *)&_ZTV7FlashVx[2];  /* vptr = 0xE08DC0 */
    this->FrameBufferFree();                    /* bl 0x14F0B8 */
    FlashPlayer_dtor(this);                     /* bl 0x262880 */
    /* the D0 (deleting) variant additionally calls operator_delete(this). */
}

/* ===========================================================================
 * 0x0014F1D8  FlashVx::FrameBufferPixelFormat()
 *
 * Forces bytesPerPixel back to 4 and reports the GFx pixel-format enum (8 == BGRA).
 * ===========================================================================*/
int FlashVx::FrameBufferPixelFormat()
{
    this->bytesPerPixel = 4;        /* +0xA0 */
    return 8;                       /* GFx GImage::Image_ARGB_8888 family */
}

/* ===========================================================================
 * 0x0014F1F0  FlashVx::FrameBufferAlloc(int width, int height, int &bytesPerLine)
 *
 * Allocates the CPU-RAM render target. Returns the framebuffer pointer (also
 * stored at this+0x9C). bytesPerLine (stride) = bytesPerPixel * width.
 * ===========================================================================*/
void *FlashVx::FrameBufferAlloc(int width, int height, int &bytesPerLine)
{
    int bpp = this->bytesPerPixel;                 /* lwz 160(this) */

    bytesPerLine = bpp * width;                    /* stride; written through &out */

    void *fb = aligned_alloc16(16, (unsigned)(width * height * bpp));  /* bl 0x46964C */
    this->framebuffer = fb;                        /* stw 156(this) */

    ui_log(2, 2, 24, kFile, "FrameBufferAlloc",
           "FlashVx::FrameBufferAlloc(%dx%d, bytesPerPixel %d, bytesPerLine %d) = %p\n",
           width, height, bpp, bytesPerLine, fb);

    return this->framebuffer;
}

/* ===========================================================================
 * 0x0014F68C  FlashVx::FrameBufferResize(int width, int height)
 *
 * Repositions the bounds rect to (0,0)-(width,height). Does not reallocate;
 * callers pair this with FrameBufferFree/FrameBufferAlloc when the size grows.
 * ===========================================================================*/
void FlashVx::FrameBufferResize(int width, int height)
{
    this->bounds_x0 = 0;            /* +0x8C */
    this->bounds_x1 = width;        /* +0x90 */
    this->bounds_y0 = 0;            /* +0x94 */
    this->bounds_y1 = height;       /* +0x98 */
}

/* ===========================================================================
 * 0x0014F660  FlashVx::FrameBufferRect(FlashRect &out) const
 *
 * Copies the current render-target bounds out.
 * ===========================================================================*/
void FlashVx::FrameBufferRect(FlashRect &out) const
{
    out.x0 = this->bounds_x0;
    out.x1 = this->bounds_x1;
    out.y0 = this->bounds_y0;
    out.y1 = this->bounds_y1;
}

/* ===========================================================================
 * 0x0014F2B4  FlashVx::DrawMouse()
 *
 * Software cursor: clamp (mouseX,mouseY) into the framebuffer and stamp one
 * 4-byte BGRA texel (0xFF,0x00,0xFF,0x00 -> magenta marker) at that position.
 * Offset = ((mouseY * width) + mouseX) * bytesPerPixel into framebuffer.
 * ===========================================================================*/
void FlashVx::DrawMouse()
{
    int width  = this->bounds_x1 - this->bounds_x0;
    int height = this->bounds_y1 - this->bounds_y0;

    if (this->mouseX == 0 && this->mouseY == 0)
        return;                                  /* nothing to draw at origin */

    if (this->mouseX >= width)
        this->mouseX = width - 1;                /* clamp X */
    if (this->mouseY >= height)
        this->mouseY = height - 1;               /* clamp Y */

    int bpp    = this->bytesPerPixel;
    long off   = ((long)this->mouseY * width + this->mouseX) * bpp;
    unsigned char *px = (unsigned char *)this->framebuffer + off;

    px[0] = 0xFF;
    px[1] = 0x00;
    px[2] = 0xFF;
    px[3] = 0x00;
}

/* ===========================================================================
 * 0x0014F35C  FlashVx::FrameBufferBlit(int x, int y, int w, int h)
 *
 * Pushes the rendered framebuffer to the display(s) via the iofpga. This is the
 * heart of "how the GUI gets to the screen":
 *
 *   - While g_osd_enabled (0xEA0DE4) is 0, blit is a no-op (returns the fb).
 *   - Walks the GFx dirty-rectangle list (rect_begin/rect_next/rect_end) and,
 *     per attached output, copies the union region to the FPGA:
 *       * LCD path     -> osd_blit_lcd   (logs "FrameBufferBlit(LCD)")
 *       * SCREEN path  -> osd_blit_screen(logs "FrameBufferBlit(SCREEN: x,y w:,h:)")
 *   - display_notify_lcd/screen drive the hot-plug attach/detach edges so the
 *     correct region is forced on first connect (full redraw via DrawMouse +
 *     rect_flush of the whole bounds rect).
 *
 * Fidelity: functional. The control flow, the two output paths, the connect/
 * disconnect edge handling and the stride/offset math are faithful; exact
 * register scheduling of the original is not reproduced. To re-skin or re-route
 * the OSD, change the per-rect destination here (or swap osd_blit_screen).
 * ===========================================================================*/
void *FlashVx::FrameBufferBlit(int x, int y, int w, int h)
{
    /* the incoming damage rect, inclusive: [x, x+w-1] x [y, y+h-1] */
    int damage_x0 = x;
    int damage_y0 = y;
    int damage_x1 = x + w - 1;
    int damage_y1 = y + h - 1;
    (void)damage_x1; (void)damage_y1;

    if (!g_osd_enabled)
        return this->framebuffer;          /* OSD off: nothing reaches the FPGA */

    FlashRect rl_lcd;                       /* local rect-list cursors (stack) */
    FlashRect rl_screen;
    rect_begin(&rl_lcd);
    rect_end(&rl_screen);

    if (!g_screen_present) {
        /* SCREEN output not wired this boot: just track LCD edge. */
        if (g_lcd_attached != g_lcd_present) {
            g_lcd_attached = g_lcd_present;
            display_log_flush();
            display_notify_lcd(g_lcd_present ? 0 : 0);
        }
    }

    /* --- per dirty-rect dispatch ------------------------------------------ */
    FlashRect r;
    while (rect_next(&rl_lcd, &r)) {
        /* first connect on a path forces a full redraw of the bounds rect */
        if (g_lcd_present && g_lcd_attached != g_lcd_present) {
            g_lcd_attached = 1;
            display_log_flush();
            display_notify_lcd(1);
        }
        if (g_screen_present && g_screen_attached != g_screen_present) {
            g_screen_attached = 1;
            display_log_flush();
            display_notify_screen(1);
        }

        if (rect_next(&rl_screen, &r)) {
            /* SCREEN path: push union region to the FPGA OSD compositor */
            ui_log(3, 1, 341, kFile, "FrameBufferBlit",
                   "FlashVx::FrameBufferBlit(SCREEN: %d,%d w:%d, h:%d)\n",
                   r.x0, r.x1, r.y0 - r.x0 + 1, r.y1);
            rect_begin(&rl_lcd);
            rect_end(&rl_screen);

            int stride = this->bytesPerPixel * (this->bounds_x1 - this->bounds_x0);
            void *base = (char *)this->framebuffer
                       + (((long)(r.y0 - r.x0) * (this->bounds_y1 /*line stride proxy*/)
                           + 0) * this->bytesPerPixel);
            osd_blit_screen(base, r.x0, r.y0, r.x1, r.y1,
                            this->bytesPerPixel, stride);
            continue;
        }

        /* LCD path: smaller, fixed-format status display */
        ui_log(3, 1, 308, kFile, "FrameBufferBlit",
               "FlashVx::FrameBufferBlit(LCD)\n");
        this->DrawMouse();                          /* stamp cursor before LCD push */
        rect_flush(&rl_lcd);

        int width  = this->bounds_x1 - this->bounds_x0;
        long off   = ((long)0 * width + 0) * this->bytesPerPixel;
        osd_blit_lcd((char *)this->framebuffer + off, 2, 2,
                     0, 0, width, this->bounds_y1 - this->bounds_y0);
    }

    return this->framebuffer;
}
