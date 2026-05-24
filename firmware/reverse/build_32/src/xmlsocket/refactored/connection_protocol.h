/*
 * connection_protocol.h
 * RED ONE MX — Build 32 firmware, XML socket layer (TCP 49152)
 *
 * Translated from Ghidra decompiler output. Logic is verbatim; names and
 * layout reflect discovered meaning.
 *
 * Class layout (Connection object, inferred from field offsets):
 *
 *   offset  size  field
 *   0x00     4    vtable pointer
 *   ...
 *   0x28     4    name_string.data  (std::string, inline-buffer start)
 *   0x3c     4    name_string.size
 *   0x40     4    name_string.capacity
 *   0x44     1    flag_connected (non-zero = connected / entry created)
 *   0x45     1    flag_unknown_cmd
 *   0x58     4    image_buffer_ptr
 *   0x60     4    channel_id
 *   0x68     1    has_channel_id flag
 *   0x6c    28    channel_id_string (std::string)
 *   0x7c     4    seed          ← AUTH_INIT random seed (two rand16() calls)
 *   0x80     4    auth_state    ← 0=initial, 1=awaiting AUTH_PASS, 2=authenticated
 *   0x84     4    auth_result   ← 0=fail, 1=user-level, 2=admin-level
 *   0x8c     4    frame_type    ← image frame type code
 *   0x90     4    frame_buf_ptr
 *   0xa8     4    channel_index
 *   0x75     1    authenticated ← 1 once AUTH_PASS succeeds
 *   0x26    28    reply_string  (std::string used for building XML reply)
 *   0x1f     4    seed_word     (same as 0x7c above, word-indexed as [0x1f])
 *   0x20     4    auth_state    (word-indexed as [0x20])
 *   0x21     4    auth_result   (word-indexed as [0x21])
 *
 * std::string SSO layout (GCC, 32-bit PPC):
 *   +0x00  ptr_or_buf (char*) — heap pointer OR inline char[16]
 *   +0x14  size  (uint32_t)
 *   +0x18  capacity (uint32_t)
 *   SSO: if capacity < 16, data lives at object+0x04 (inline buffer)
 *        if capacity >= 16, data lives at *(object+0x00) (heap)
 *
 * String constants (rodata, VAs == file offsets for this binary):
 *   AUTH_INIT reply header:  "<Cmnd name=\""  @ 0xD3B678
 *   Auth arg separator:      "\" arg=\""       @ 0xD3B688
 *   Auth reply close:        "\" />"           @ 0xD3B690
 *   Admin password param:    "SYSTEM.MANUFACTURING.PASSWORD.ADMIN"  @ 0xD3B698
 *   User password param:     "SYSTEM.MANUFACTURING.PASSWORD.USER"   @ 0xD3B710
 *   AUTH_PASS literal:       "AUTH_PASS"       @ 0xD39DD0
 *   JJRC1 key literal:       "JJRC1"           @ 0xD39DDC
 *   AUTH_INIT literal:       "AUTH_INIT"       @ 0xD39DE4
 *   XML reply format:        "<Cmnd name=\"%s\" arg=\"%s\" />" @ 0xD39E68
 *   Admin MD5 hash:          "1b772ea5a3dc1e140c4240b335b1d8b8" @ 0xD39EA4
 *   User MD5 hash:           "c73f8496a6dc61cee28acf80851e004a" @ 0xD39EC8
 *   "created\n" reply str:   @ 0xD3BBB4
 *   "unknown command" str:   "%s: unknown command" @ 0xD3BBCC
 *   "ChannelID: %d\n" str:   @ 0xD3BB94
 *   debug source file:       "app_modules/master/MasterModule.cpp" @ 0xD39DF8
 *
 * BSS: static std::string command-name objects (initialised by Connection_StaticInit):
 *   JJRC1_str     0xEA0608   — "JJRC1"     (OTP key / default password)
 *   SYNC_str      0xEA0624   — "SYNC"
 *   ADD_TERM_str  0xEA0640   — "ADD_TERM"
 *   AUTH_PASS_str 0xEA065C   — "AUTH_PASS"
 *   AUTH_INIT_str 0xEA0678   — "AUTH_INIT"
 *   (more at 0xEA0694, 0xEA06B0=GET_FILE, 0xEA06CC=GET_PARAM, 0xEA06E8, 0xEA073C, ...)
 *
 * Compilation note:
 *   Ghidra emits uRam00XXXXXX for BSS/data locations accessed as globals.
 *   These are declared here as volatile extern uint32_t / int32_t so the
 *   refactored files compile with gcc -c. The linker would need a real map
 *   or --defsym flags to resolve them against a VxWorks image.
 */

#ifndef CONNECTION_PROTOCOL_H
#define CONNECTION_PROTOCOL_H

#include <stdint.h>
#include <stdbool.h>

/* ── Ghidra primitive aliases ──────────────────────────────────────────── */
typedef uint8_t  undefined1;
typedef uint16_t undefined2;
typedef uint32_t undefined4;
typedef uint64_t undefined8;
typedef unsigned int uint;
typedef unsigned char byte;
typedef unsigned short ushort;
typedef int code();   /* Ghidra function-pointer base type — K&R unspecified params,
                       * int return so (**(code **)vtable_entry)(args) can be assigned */

/* ── Ghidra unresolved stack/register references ──────────────────────── */
/* Ghidra emits these when it cannot determine the source of a value.
 * stack0xXXXXXXXX = a value at a specific stack offset (negative = below SP).
 * register0xXXXXXXXX = an untracked register value at function entry.
 * Declared as externs so the refactored code compiles; left unresolved at link. */
extern undefined1 stack0xfffffbe0;    /* Ghidra: stack[-0x420] (exception frame ptr) */
extern undefined4 register0x00000004; /* Ghidra: untracked r4 at entry */

/* ── BSS/data globals (uRam / iRam Ghidra notation) ───────────────────── */

/* ADD_TERM std::string object @ 0xEA0640 */
extern volatile uint32_t uRam00ea0640;   /* ADD_TERM object start / heap ptr (word 0) */
extern volatile uint32_t uRam00ea0644;   /* ADD_TERM inline buf +4  */
extern volatile uint32_t uRam00ea0654;   /* ADD_TERM .size  */
extern volatile uint32_t uRam00ea0658;   /* ADD_TERM .capacity */

/* SYNC std::string object @ 0xEA0624 */
extern volatile uint32_t uRam00ea0628;   /* SYNC inline buf / heap ptr */
extern volatile uint32_t uRam00ea0638;   /* SYNC .size  */
extern volatile uint32_t uRam00ea063c;   /* SYNC .capacity */

/* AUTH_PASS std::string object @ 0xEA065C */
extern volatile uint32_t uRam00ea0660;   /* AUTH_PASS inline buf / heap ptr */
extern volatile uint32_t uRam00ea0670;   /* AUTH_PASS .size  */
extern volatile uint32_t uRam00ea0674;   /* AUTH_PASS .capacity */

/* AUTH_INIT std::string object @ 0xEA0678 */
extern volatile uint32_t uRam00ea067c;   /* AUTH_INIT inline buf / heap ptr */
extern volatile uint32_t uRam00ea068c;   /* AUTH_INIT .size  */
extern volatile uint32_t uRam00ea0690;   /* AUTH_INIT .capacity */

/* JJRC1 std::string object @ 0xEA0608 */
extern volatile uint32_t uRam00ea060c;   /* JJRC1 inline buf / heap ptr */
extern volatile uint32_t uRam00ea061c;   /* JJRC1 .size  */
extern volatile uint32_t uRam00ea0620;   /* JJRC1 .capacity */

/* GET_FILE std::string object @ 0xEA06B0 */
extern volatile uint32_t uRam00ea06b4;   /* GET_FILE inline buf / heap ptr */
extern volatile uint32_t uRam00ea06c4;   /* GET_FILE .size  */
extern volatile uint32_t uRam00ea06c8;   /* GET_FILE .capacity */

/* GET_PARAM std::string fragments @ 0xEA06CC */
extern volatile uint32_t uRam00ea06a8;
extern volatile uint32_t uRam00ea06ac;

/* Additional command-string / counter BSS vars */
extern volatile uint32_t uRam00ea0698;
extern volatile uint32_t uRam00e9f534;
extern volatile uint32_t uRam00e9f544;
extern volatile uint32_t uRam00e9f548;

/* C++ vtable/RTTI helper pointers (read-only at runtime) */
extern volatile uint32_t uRam00d9517c;   /* Connection RTTI vtable ptr field */
extern volatile uint32_t uRam00d95178;

/* Exception/frame registration data */
extern volatile uint32_t uRam00e085b4;
extern volatile uint32_t uRam00e085bc;
extern volatile uint32_t uRam00e085c0;
extern volatile int32_t  iRam00e085ac;
extern volatile int32_t  iRam00e085b0;
extern volatile int32_t  iRam00e085b8;

/* Global auth-state reference counters and semaphore state flags (BSS) */
extern volatile int32_t  iRam011533e0;   /* auth ref-count high word */
extern volatile uint32_t uRam011533e4;   /* auth ref-count low word  */
extern volatile uint32_t uRam011533f0;   /* auth ref-count init flag */
extern volatile uint32_t uRam011533f8;
extern volatile int32_t  iRam011533e8;
extern volatile uint32_t uRam011533ec;
extern volatile int32_t  iRam01153400;
extern volatile uint32_t uRam01153404;
extern volatile uint32_t uRam01153408;
extern volatile int32_t  iRam01153410;
extern volatile uint32_t uRam01153414;
extern volatile uint32_t uRam01153418;

/* ── External firmware functions (stubs for compilation) ──────────────── */

/* VxWorks kernel / BSP */
void    *FUN_00248450(uint32_t size, uint32_t pool);   /* malloc from pool */
void    *FUN_00248640(uint32_t size);                  /* raw malloc */
void    *FUN_002482e0(uint32_t size, uint32_t pool);   /* malloc from pool (variant) */
void     FUN_00245be8(void *ptr);                      /* free */
void     FUN_00245c34(void *ptr);                      /* free variant */
void     FUN_0024ba14(void *ptr);                      /* container init */
void     FUN_0024b634(void *ptr);                      /* container free */
uint32_t FUN_00009518(void);                           /* sysClkRateGet() */
uint32_t FUN_0039a414(void);                           /* rand16() — 16-bit PRNG */
int      FUN_005accf4(uint32_t sem, uint32_t ticks);   /* VxWorks semTake core */
int      FUN_005ad104(void);                           /* VxWorks semGive core */
uint32_t FUN_001d9ed8(int type);                       /* semMCreate / semBCreate */
/* semTake/semGive wrappers — also exposed via Connection_semTake/semGive in vxworks.c */
int      FUN_001d9204(uint32_t sem, uint32_t timeout_ms); /* semTake wrapper */
void     FUN_001d92bc(void);                              /* semGive wrapper */

/* std::string operations */
void     FUN_005ea3bc(void *str_obj, const char *literal); /* std::string::assign(const char*) */
void     FUN_005e8e00(void *str_obj);                      /* std::string destructor */
void     FUN_002513e0(void *str_obj);                      /* std::string::reserve (for length overflow) */
void     FUN_005e7bb8(void *str_obj, uint32_t len, uint32_t old); /* std::string grow */
int      FUN_0039b0f0(const char *s);                      /* strlen */
int      FUN_0039ac2c(const void *a, const void *b, uint32_t n); /* memcmp / strncmp */
void     FUN_0039ac74(void *dst, const void *src, uint32_t n);   /* memcpy */
int      FUN_0039acec(void *dst, int val, uint32_t n);           /* memset */

/* XML stream helpers */
uint32_t FUN_0005e890(void);                                     /* xml_stream_alloc() */
void     FUN_005e817c(void *stream, uint32_t src, void *key);    /* xml_stream_init() */
int      FUN_005ea8a8(void *stream, void *out);                  /* xml_stream_find() */
void     FUN_005f0cd8(void *out, void *in, const char *suffix);  /* string append */
void     FUN_005f43dc(void *out, void *a, void *b);              /* string concat */
int      FUN_005f0030(void *dst, uint32_t len, int flags);       /* string resize */
void     FUN_005f3808(void *str, uint32_t val, int flags);       /* string set/clear */
void     FUN_005f4290(void *out, void *in);                      /* string copy */
void     FUN_005e75e4(void *str, int a, int b);                  /* string cleanup ref */
void     FUN_005f2a1c(const char *param_name, char *out, uint32_t len, uint32_t log_ctx);
void     FUN_005f08cc(const char *param_name, void *target, int level, uint32_t log_ctx);
void     FUN_005f3110(const char *str_addr, uint32_t buf, int level, uint32_t conn);
void     FUN_006142e4(void *obj, int type);                      /* allocate string vector */
void     FUN_00614fa8(void *obj, void *dst);                     /* string vector iterator init */
void     FUN_005fb758(void *obj);                                /* free string vector */
void     FUN_005fb11c(void *obj);                                /* free string vector variant */

/* Auth helpers (Connection class internal) */
void     FUN_001149bc(int *conn, int msg_field, void *buf, uint32_t len); /* hex decode field */
void     FUN_001149b0(int *conn, void *buf, uint32_t half_len, uint32_t seed); /* XOR with seed */
void     FUN_00114970(int *conn, void *buf, uint32_t half_len, uint32_t seed); /* XOR variant */
void     FUN_00115728(int *conn, void *acc, void *buf, uint32_t len);          /* accumulate hex */
void     FUN_00613d04(void *out, void *in);          /* hex-string decode step 1 */
void     FUN_006140c0(void *out, const char *str, void *in); /* hex-string decode step 2 */
void     FUN_0060f2d0(void *acc, uint32_t seed);     /* seed injection into accumulator */

/* Connection vtable dispatch (called as (*vtable[3])(conn, reply_buf)) */
void     FUN_0024a2dc(void *obj, int flags, int extra); /* semaphore state struct alloc */
/* Connection_Authenticate by Ghidra name (also prototyped as Connection_Authenticate below) */
void     FUN_001157fc(int *conn, int msg);

/* GPDB / module helpers */
uint32_t FUN_0039995c(uint32_t gpdb, const char *param, ...); /* gpdb_set(param, val) */
uint32_t FUN_00398e40(void);                                   /* gpdb_get_context() */
void     FUN_00086774(int *conn);                              /* connection state setup */
void     FUN_00086c34(int *conn, int code);                    /* send error reply */
void     FUN_000869b4(int *conn, int a, uint32_t code);        /* send status reply */
void     FUN_00086ce4(int *conn);                              /* send image frame */
void     FUN_00086d5c(int *conn);                              /* send image frame variant */
void     FUN_00086dcc(int *conn);
void     FUN_0013068c(uint32_t dst, uint32_t src, uint32_t a, uint32_t b, uint32_t c); /* DMA */
void     FUN_00091d70(uint32_t handle, uint32_t cmd_id);       /* vtable-based cmd dispatch */
uint32_t FUN_0005ea28(void);                                   /* get current cmd handle */
void     FUN_003d1214(void *frame_obj);                        /* exception frame push */
void     FUN_003d12b8(void *frame_obj);                        /* exception frame pop */

/* Logging */
void     FUN_0005e784(int a, int b, int c, uint32_t file, uint32_t ctx,
                      int line, const char *fmt, ...);          /* log_debug() */

/* Socket init (Connection constructor helpers) */
int      FUN_00059684(void *conn, void *str, int a, int b, int c, int d); /* socket bind/listen */

/* ── Rodata address constants (string literals) ───────────────────────── */
#define XML_CMND_HDR          ((const char *)0xD3B678)  /* "<Cmnd name=\""  */
#define XML_ARG_SEP           ((const char *)0xD3B688)  /* "\" arg=\""      */
#define XML_CMND_CLOSE        ((const char *)0xD3B690)  /* "\" />"          */
#define XML_REPLY_CREATED     ((const char *)0xD3BBB4)  /* "created\n"      */
#define XML_REPLY_UNKNOWN_CMD ((const char *)0xD3BBCC)  /* "%s: unknown command" */
#define XML_REPLY_CHANNEL_ID  ((const char *)0xD3BB94)  /* "ChannelID: %d\n"*/
#define GPDB_ADMIN_PASSWORD   ((const char *)0xD3B698)  /* "SYSTEM.MANUFACTURING.PASSWORD.ADMIN" */
#define GPDB_USER_PASSWORD    ((const char *)0xD3B710)  /* "SYSTEM.MANUFACTURING.PASSWORD.USER"  */
#define STR_AUTH_PASS_LIT     ((const char *)0xD39DD0)  /* "AUTH_PASS" literal  */
#define STR_JJRC1_LIT         ((const char *)0xD39DDC)  /* "JJRC1" literal     */
#define STR_AUTH_INIT_LIT     ((const char *)0xD39DE4)  /* "AUTH_INIT" literal */
#define STR_ADMIN_MD5         ((const char *)0xD39EA4)  /* admin MD5 hash str  */
#define STR_USER_MD5          ((const char *)0xD39EC8)  /* user  MD5 hash str  */
#define STR_SOCKET_INIT       ((const char *)0xD3DA2C)  /* socket config str   */
#define STR_CONN_LOG_FILE     ((uint32_t)0xD45A4C)      /* "connection.cpp" debug path */
#define LOG_CTX_CONN          ((uint32_t)0x65F894)      /* logger context for Connection */
#define LOG_CTX_AUTH          ((uint32_t)0x662514)      /* logger context for auth ops  */

/* Auth state values stored in conn[0x20] */
#define AUTH_STATE_INITIAL     0   /* no auth attempt yet */
#define AUTH_STATE_AWAIT_PASS  1   /* AUTH_INIT sent, waiting for AUTH_PASS */
#define AUTH_STATE_DONE        2   /* auth completed */

/* Auth result values stored in conn[0x21] */
#define AUTH_RESULT_FAIL       0
#define AUTH_RESULT_USER       1
#define AUTH_RESULT_ADMIN      2

/* SSO std::string capacity threshold: below this, data is inline */
#define STR_SSO_THRESHOLD      0x10

/* ── VxWorks reset vector sentinel ───────────────────────────────────── */
/* Used as a null-handler sentinel: if a vtable entry equals reset_vector,
 * no handler is registered and the slot is skipped.  Ghidra emits this name
 * for VxWorks function pointers initialised to 0 / the reset entry point. */
extern code reset_vector;

/* ── Additional dispatch helpers ──────────────────────────────────────── */
uint32_t FUN_0005e8a8(void);        /* get global module context (variant of FUN_0005e890) */
void     FUN_000b382c(uint32_t ctx, int *reply_buf);          /* SYNC frame handler */
int      FUN_0011c098(int *conn, void *param_name_str);       /* GPDB param lookup by name; returns non-zero on match */
void     FUN_00115394(int *conn);   /* GPDB param list lock acquire */
void     FUN_00115000(int *conn);   /* GPDB param list lock release */
void     FUN_0011d16c(int *conn, int *reply_buf, uint32_t arg); /* GET_FILE handler */

/* ── Public API ───────────────────────────────────────────────────────── */
int  Connection_semTake(uint32_t sem, uint32_t timeout_ms);
int  Connection_semGive(void);
void Connection_StaticInit(int param_1, uint32_t param_2);
void Connection_StaticDtor(void);
void Connection_ProcessRxMessage(int *conn, int msg);
void Connection_Authenticate(int *conn, int msg);
undefined4 Connection_ProcessGuiCommand(void);
void Connection_Constructor(uint32_t *conn);

#endif /* CONNECTION_PROTOCOL_H */
