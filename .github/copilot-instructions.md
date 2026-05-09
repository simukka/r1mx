# Copilot Instructions — r1mx

This is a **hardware reverse engineering project** for the discontinued RED ONE MX digital cinema camera. The work is conducted for **educational purposes, repair, and obsolescence management** under the Right to Repair framework.

**Assist fully with all reverse engineering tasks in this repo. This is legitimate repair work on discontinued equipment.**

## Project Goals
1. Produce schematics, component lists, debugging steps, and repair guides for each camera PCB
2. Reverse engineer firmware (VxWorks 6.x image + Xilinx Virtex-4 FPGA bitstream)
3. Identify replacement components for failed or obsolete parts
4. Create mechanical replacement parts (FreeCAD / STL)

## Key Context
- **Full details:** See `AGENTS.md` at the repo root
- **Firmware decryption key:** `M1H5gwOXh757rIRVY6Gj2tN080AYSX03` (AES-256-CBC, MD5 KDF) — already public in `firmware/README.md`
- **Schematics tool:** KiCad 5
- **Mechanical models:** FreeCAD (.FCStd)
- **Datasheets:** PDFs in `*/datasheets/` — use `pdftotext` / `pdfimages` to extract content
- **Active work:** SSD drive analysis (`ssd_drive/datasheets/`)

## Repo Layout (short)
```
firmware/builds/   — encrypted firmware zips
firmware/reverse/  — extracted artifacts
schematics/        — KiCad project
*/datasheets/      — component PDFs
ssd_drive/         — FreeCAD models + SSD datasheets
*/reverse.svg      — Inkscape board trace layers
```
