/*
 * uart.c -- Xilinx UART Lite (XUartLite) driver decompilation
 *
 * RED ONE MX firmware build 32, r1mx reverse engineering project.
 *
 * The camera's serial console uses a Xilinx UART Lite IP core at MMIO
 * base 0x40600000 (UART_LITE_BASE), connected through the Virtex-4 FPGA
 * fabric.  VxWorks uses two UART cores:
 *   - Xilinx UART Lite (XUartLite) at 0x40600000  -- debug console
 *   - NS16550-compatible (XUartNs550) at a second address -- optional
 *
 * Source file names embedded in the binary (symtab region 0xD24A80):
 *   xuartlite.c, xuartlite_sinit.c, xuartlite_intr.c,
 *   xuartlite_selftest.c, xuartlite_stats.c, xuartlite_sio_adapter.c,
 *   uartns550.c, uartns550_format.c, uartns550_intr.c,
 *   uartns550_options.c, uartns550_stats.c, uartns550_selftest.c
 *
 * Decompilation methodology:
 *   - Ghidra 12.0.4 analysis of software.bin (PPC405BE, base 0x0)
 *   - Cross-referenced against public Xilinx EDK 10.1 XUartLite driver
 *     (Apache 2.0 licence) -- the source structure is identical to
 *     what Ghidra produces, confirming register offsets and logic.
 *   - MMIO access: XUartLite_ReadReg / XUartLite_WriteReg are macros
 *     that expand to lwz/stw instructions on PPC.
 *
 * Compiler: gcc-powerpc-linux-gnu -mcpu=405 -mbig-endian -O2
 *           (original: Wind River Diab on Windows, same output expected
 *            for these simple leaf functions)
 */

#include <stdint.h>

/* -------------------------------------------------------------------------
 * MMIO base addresses
 * ------------------------------------------------------------------------- */
#define UART_LITE_BASE      0x40600000U   /* Xilinx UART Lite -- debug console  */
#define UART_NS550_BASE     0x40800000U   /* NS16550 core (if populated)         */

/* -------------------------------------------------------------------------
 * Xilinx UART Lite register offsets  (from xuartlite_l.h)
 * ------------------------------------------------------------------------- */
#define XUL_RX_FIFO_OFFSET          0x00U  /* Receive FIFO (read)                */
#define XUL_TX_FIFO_OFFSET          0x04U  /* Transmit FIFO (write)              */
#define XUL_STATUS_REG_OFFSET       0x08U  /* Status register (read-only)        */
#define XUL_CONTROL_REG_OFFSET      0x0CU  /* Control register (write)           */

/* Status register bit masks */
#define XUL_SR_PARITY_ERROR         0x80U  /* Parity error detected              */
#define XUL_SR_FRAMING_ERROR        0x40U  /* Framing error detected             */
#define XUL_SR_OVERRUN_ERROR        0x20U  /* Receive FIFO overrun               */
#define XUL_SR_INTR_ENABLED         0x10U  /* Interrupts enabled                 */
#define XUL_SR_TX_FIFO_FULL         0x08U  /* Transmit FIFO full                 */
#define XUL_SR_TX_FIFO_EMPTY        0x04U  /* Transmit FIFO empty                */
#define XUL_SR_RX_FIFO_FULL         0x02U  /* Receive FIFO full                  */
#define XUL_SR_RX_FIFO_VALID_DATA   0x01U  /* Receive FIFO has data              */

/* Control register bit masks */
#define XUL_CR_ENABLE_INTR          0x10U  /* Enable interrupt output            */
#define XUL_CR_FIFO_TX_RESET        0x01U  /* Reset transmit FIFO                */
#define XUL_CR_FIFO_RX_RESET        0x02U  /* Reset receive FIFO                 */

/* -------------------------------------------------------------------------
 * MMIO access helpers
 * These expand to single lwz / stw instructions on PPC405.
 * ------------------------------------------------------------------------- */
static inline uint32_t XUartLite_ReadReg(uint32_t base, uint32_t offset)
{
    return *(volatile uint32_t *)(base + offset);
}

static inline void XUartLite_WriteReg(uint32_t base, uint32_t offset, uint32_t val)
{
    *(volatile uint32_t *)(base + offset) = val;
}

/* -------------------------------------------------------------------------
 * XUartLite instance structure  (from xuartlite.h)
 *
 * The Ghidra decompiler identifies field access at the following struct
 * offsets inside several UART Lite driver functions:
 *   +0x00  uint32_t RegBaseAddress   -- MMIO base (0x40600000)
 *   +0x04  uint32_t IsReady          -- initialisation sentinel
 *   +0x18  void (*RecvHandler)(...)  -- receive callback
 *   +0x1C  void *RecvCallBackRef     -- receive callback argument
 *   +0x20  void (*SendHandler)(...)  -- transmit callback
 *   +0x24  void *SendCallBackRef     -- transmit callback argument
 *   +0x28  uint32_t TotalSentCount   -- running transmit byte count
 *   +0x2C  uint32_t TotalReceivedCount -- running receive byte count
 *   +0x30  uint32_t TotalErrorCount  -- running error count
 * ------------------------------------------------------------------------- */
typedef struct {
    uint32_t  RegBaseAddress;
    uint32_t  IsReady;
    uint8_t  *SendBufferPtr;
    uint32_t  SendBufferLength;
    uint8_t  *ReceiveBufferPtr;
    uint32_t  ReceiveBufferLength;
    void    (*RecvHandler)(void *ref, uint32_t EventData);
    void     *RecvCallBackRef;
    void    (*SendHandler)(void *ref, uint32_t EventData);
    void     *SendCallBackRef;
    uint32_t  TotalSentCount;
    uint32_t  TotalReceivedCount;
    uint32_t  TotalErrorCount;
} XUartLite;

/* -------------------------------------------------------------------------
 * XUartLite_Config -- configuration entry (one per device in ConfigTable)
 *
 * The XUartLite_ConfigTable (confirmed present in binary, base address
 * 0x40600000 found at file offset 0xCC3DA4 in a packed config table)
 * contains at minimum: {DeviceId, BaseAddress, BaudRate, UseParity, ...}
 * ------------------------------------------------------------------------- */
typedef struct {
    uint16_t  DeviceId;
    uint32_t  RegBaseAddr;
    uint32_t  BaudRate;
    int       UseParity;
    int       OddParity;
    int       DataBits;
} XUartLite_Config;

/* The static config table (XUartLite_ConfigTable) is a linker-generated
 * array initialised from BSP parameters.  One entry covers the debug UART:
 *
 *   XUartLite_Config XUartLite_ConfigTable[] = {
 *       { 0, UART_LITE_BASE, 115200, 0, 0, 8 },   // device 0
 *   };
 *
 * DeviceId=0 maps to the boot console at 0x40600000.
 */

/* -------------------------------------------------------------------------
 * XUartLite_LookupConfig -- find config by DeviceId
 * (no exact binary address confirmed via symtab; deduced from call pattern)
 * ------------------------------------------------------------------------- */
XUartLite_Config *XUartLite_LookupConfig(uint16_t DeviceId);  /* extern */

/* -------------------------------------------------------------------------
 * XUartLite_CfgInitialize
 * Initialises the driver instance from a config entry.
 * ------------------------------------------------------------------------- */
int XUartLite_CfgInitialize(XUartLite *InstancePtr,
                             XUartLite_Config *Config,
                             uint32_t EffectiveAddr)
{
    InstancePtr->RegBaseAddress = EffectiveAddr;
    InstancePtr->IsReady        = 0x11111111U;  /* VxWorks "initialised" sentinel */

    /* Reset both FIFOs */
    XUartLite_WriteReg(EffectiveAddr, XUL_CONTROL_REG_OFFSET,
                       XUL_CR_FIFO_TX_RESET | XUL_CR_FIFO_RX_RESET);
    XUartLite_WriteReg(EffectiveAddr, XUL_CONTROL_REG_OFFSET, 0);

    return 0; /* XST_SUCCESS */
}

/* -------------------------------------------------------------------------
 * XUartLite_Initialize
 * Convenience wrapper: look up config and call CfgInitialize.
 * ------------------------------------------------------------------------- */
int XUartLite_Initialize(XUartLite *InstancePtr, uint16_t DeviceId)
{
    XUartLite_Config *cfg = XUartLite_LookupConfig(DeviceId);
    if (cfg == 0)
        return 1; /* XST_DEVICE_NOT_FOUND */
    return XUartLite_CfgInitialize(InstancePtr, cfg, cfg->RegBaseAddr);
}

/* -------------------------------------------------------------------------
 * XUartLite_ResetFifos
 * Resets both receive and transmit FIFOs.
 * Called from VxWorks SIO adapter DevInit.
 * ------------------------------------------------------------------------- */
void XUartLite_ResetFifos(XUartLite *InstancePtr)
{
    XUartLite_WriteReg(InstancePtr->RegBaseAddress, XUL_CONTROL_REG_OFFSET,
                       XUL_CR_FIFO_TX_RESET | XUL_CR_FIFO_RX_RESET);
    XUartLite_WriteReg(InstancePtr->RegBaseAddress, XUL_CONTROL_REG_OFFSET, 0);
}

/* -------------------------------------------------------------------------
 * XUartLite_IsSending
 * Returns non-zero if a transmit is in progress (TX FIFO not empty).
 * ------------------------------------------------------------------------- */
int XUartLite_IsSending(XUartLite *InstancePtr)
{
    uint32_t status = XUartLite_ReadReg(InstancePtr->RegBaseAddress,
                                        XUL_STATUS_REG_OFFSET);
    return !(status & XUL_SR_TX_FIFO_EMPTY);
}

/* -------------------------------------------------------------------------
 * XUartLite_SendByte  (leaf -- single stw instruction after inline)
 * Writes one byte to the TX FIFO.  Caller must ensure FIFO is not full.
 * ------------------------------------------------------------------------- */
void XUartLite_SendByte(uint32_t BaseAddress, uint8_t Data)
{
    XUartLite_WriteReg(BaseAddress, XUL_TX_FIFO_OFFSET, (uint32_t)Data);
}

/* -------------------------------------------------------------------------
 * XUartLite_RecvByte  (leaf -- single lwz instruction after inline)
 * Reads one byte from the RX FIFO.  Caller must ensure FIFO has data.
 * ------------------------------------------------------------------------- */
uint8_t XUartLite_RecvByte(uint32_t BaseAddress)
{
    return (uint8_t)XUartLite_ReadReg(BaseAddress, XUL_RX_FIFO_OFFSET);
}

/* -------------------------------------------------------------------------
 * XUartLite_EnableInterrupt
 * Sets the enable-interrupt bit in the control register.
 *
 * Binary note: Ghidra labels 0x3E5418 as this function but that address
 * is mid-function inside a larger VxWorks SIO interrupt registration
 * handler.  The simple MMIO version below is the logical equivalent.
 * ------------------------------------------------------------------------- */
void XUartLite_EnableInterrupt(XUartLite *InstancePtr)
{
    XUartLite_WriteReg(InstancePtr->RegBaseAddress,
                       XUL_CONTROL_REG_OFFSET, XUL_CR_ENABLE_INTR);
}

/* -------------------------------------------------------------------------
 * XUartLite_DisableInterrupt
 * Clears the enable-interrupt bit in the control register.
 * ------------------------------------------------------------------------- */
void XUartLite_DisableInterrupt(XUartLite *InstancePtr)
{
    XUartLite_WriteReg(InstancePtr->RegBaseAddress,
                       XUL_CONTROL_REG_OFFSET, 0);
}

/* -------------------------------------------------------------------------
 * XUartLite_Send  (non-blocking DMA-style transfer)
 * Starts sending NumBytes from BufferPtr.  Returns number of bytes placed
 * into the TX FIFO (may be less than NumBytes if FIFO fills up).
 * ------------------------------------------------------------------------- */
uint32_t XUartLite_Send(XUartLite *InstancePtr,
                        const uint8_t *BufferPtr,
                        uint32_t NumBytes)
{
    uint32_t SentCount = 0;
    uint32_t Status;

    while (SentCount < NumBytes) {
        Status = XUartLite_ReadReg(InstancePtr->RegBaseAddress,
                                   XUL_STATUS_REG_OFFSET);
        if (Status & XUL_SR_TX_FIFO_FULL)
            break;
        XUartLite_SendByte(InstancePtr->RegBaseAddress, BufferPtr[SentCount]);
        SentCount++;
    }
    InstancePtr->TotalSentCount += SentCount;
    return SentCount;
}

/* -------------------------------------------------------------------------
 * XUartLite_Recv  (non-blocking)
 * Drains the RX FIFO into BufferPtr.  Returns number of bytes received.
 * ------------------------------------------------------------------------- */
uint32_t XUartLite_Recv(XUartLite *InstancePtr,
                        uint8_t *BufferPtr,
                        uint32_t NumBytes)
{
    uint32_t RecvCount = 0;
    uint32_t Status;

    while (RecvCount < NumBytes) {
        Status = XUartLite_ReadReg(InstancePtr->RegBaseAddress,
                                   XUL_STATUS_REG_OFFSET);
        if (!(Status & XUL_SR_RX_FIFO_VALID_DATA))
            break;
        BufferPtr[RecvCount] = XUartLite_RecvByte(InstancePtr->RegBaseAddress);
        RecvCount++;
    }
    InstancePtr->TotalReceivedCount += RecvCount;
    return RecvCount;
}

/* -------------------------------------------------------------------------
 * XUartLite_InterruptHandler
 * Top-level ISR registered with VxWorks.  Dispatches to send/recv handlers.
 * Confirmed present in binary via symtab name at 0xDF79AC.
 * ------------------------------------------------------------------------- */
void XUartLite_InterruptHandler(XUartLite *InstancePtr)
{
    uint32_t Status = XUartLite_ReadReg(InstancePtr->RegBaseAddress,
                                        XUL_STATUS_REG_OFFSET);

    if (Status & (XUL_SR_RX_FIFO_VALID_DATA | XUL_SR_RX_FIFO_FULL)) {
        /* Drain RX FIFO */
        if (InstancePtr->ReceiveBufferPtr && InstancePtr->ReceiveBufferLength > 0) {
            uint32_t n = XUartLite_Recv(InstancePtr,
                                        InstancePtr->ReceiveBufferPtr,
                                        InstancePtr->ReceiveBufferLength);
            InstancePtr->ReceiveBufferPtr    += n;
            InstancePtr->ReceiveBufferLength -= n;
            if (InstancePtr->ReceiveBufferLength == 0 && InstancePtr->RecvHandler)
                InstancePtr->RecvHandler(InstancePtr->RecvCallBackRef, n);
        }
    }

    if (!(Status & XUL_SR_TX_FIFO_FULL)) {
        /* Drain send buffer into TX FIFO */
        if (InstancePtr->SendBufferPtr && InstancePtr->SendBufferLength > 0) {
            uint32_t n = XUartLite_Send(InstancePtr,
                                        InstancePtr->SendBufferPtr,
                                        InstancePtr->SendBufferLength);
            InstancePtr->SendBufferPtr    += n;
            InstancePtr->SendBufferLength -= n;
            if (InstancePtr->SendBufferLength == 0 && InstancePtr->SendHandler)
                InstancePtr->SendHandler(InstancePtr->SendCallBackRef, n);
        }
    }

    /* Error reporting */
    if (Status & (XUL_SR_PARITY_ERROR | XUL_SR_FRAMING_ERROR | XUL_SR_OVERRUN_ERROR))
        InstancePtr->TotalErrorCount++;
}

/* -------------------------------------------------------------------------
 * dsp_crossover_init  (formerly mislabelled "uart_init" at 0x1C18DC)
 *
 * This function was incorrectly identified as a UART initialiser.
 * Ghidra decompiler output shows it is a DSP/audio crossover filter
 * initialisation function operating entirely in IEEE 754 single-precision
 * floating point:
 *   - Constants: 1.0f (0x3F800000), 0.25f (0x3E800000), 0.1f (0x3DCCCCCD)
 *   - Calls to FUN_00374be4 (fp_multiply), FUN_00374e00 (fp_add),
 *     FUN_00374be8 (fp_multiply_variant), FUN_00377ff8 (fp_compare)
 *   - Computes filter coefficients (Butterworth/biquad crossover banks)
 *     for the camera's stereo audio pipeline.
 *
 * The UART Lite MMIO base 0x40600000 == 3.5f in IEEE 754.  The "lis r4,
 * 0x4060" at 0x1C1A0C is loading the float constant 3.5f, NOT a pointer.
 *
 * extern declaration -- decompiled body lives in audio_dsp.c (TODO).
 * ------------------------------------------------------------------------- */
extern void dsp_crossover_init(float *coeff_table,
                               float  sample_rate,
                               float  crossover_freq,
                               float  gain,
                               uint32_t num_channels,
                               int    num_bands);
