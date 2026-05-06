# Build 13 v1.8.8 "Sundance"
The first build that I have been able to scrap from the Internet. Any build
before this might be a beta/alpha build.

It does not seem to have encryption that was later introduced.

## Tools used
* Wayback machine
* Binwalk

## Reverse engineering
Unzipping the `Upgrade_build 13.zip` we can first see some metadat:

```
-rwxrwxrwx 1 simukka simukka 6675813 jan.  24  2008  build_13_ops_guide_v1.8.8.pdf
-rwxrwxrwx 1 simukka simukka    3456 jan.  18  2008 'build_13_red_one_v1.8.8_readme .txt'
```

This build or zip was created around January 2008. 

### SundanceBootable.bin
VxWorks is a proprietary RTOS developed by Wind River Systems. It includes a 
custom [Linux Kernel](https://docs.windriver.com/bundle/Wind_River_Linux_Kernel_and_BSP_Developers_Guide_8.0_1/page/fuy1554300103283.html).

Interpreting the version `"VxWorks WIND kernel version "2.10"` is challenging.
Either this is version 2.10 of VxWorks WIND or the Linux kernel is version 2.10.
Looking at the Linux kernel release notes for 2008, we can see the following:

```
The latest snapshot for the stable Linux kernel tree is:  	2.6.26-rc6-git2 	2008-06-14 07:01 UTC 	B 	V 	  	C
The latest 2.4 version of the Linux kernel is:  	2.4.36.6 	2008-06-06 16:27 UTC 	F 	V 	  	C 	Changelog
The latest 2.2 version of the Linux kernel is:  	2.2.26 	2004-02-25 00:28 UTC 	F 	V 	  	  	Changelog 
```

And if we cross reference the [Windriver website](https://web.archive.org/web/20080512034830/http://www.windriver.com/products/vxworks/) (circa-2008) we can assume the Kernel Version
is 2.4 or 2.6 and "2.10" is referencing the version of the Wind platform:


| Product | Platform Release | Kernel Version | Release Date |
| --- | --- | --- | --- |
Wind River Linux | 2.0 | 2.6.21 | 15 Dec 2007 |
Wind River Linux | 3.0.1 | 2.6.27.2114 | Sep 2009 |


`binwalk SundanceBootable.bin`

```
DECIMAL       HEXADECIMAL     DESCRIPTION
--------------------------------------------------------------------------------
4096428       0x3E81AC        Copyright string: "Copyright Wind River Systems, Inc., 1984-2006"
4521448       0x44FDE8        VxWorks WIND kernel version "2.10"
5151716       0x4E9BE4        XML document, version: "1.0"
5190636       0x4F33EC        gzip compressed data, from Unix, last modified: 1970-01-01 00:00:00 (null date)
6685296       0x660270        Uncompressed Adobe Flash SWF file, Version 7, File size (header included) 2846522
6802401       0x67CBE1        JPEG image data, JFIF standard 1.02
6802431       0x67CBFF        TIFF image data, big-endian, offset of first image directory: 8
6802733       0x67CD2D        JPEG image data, JFIF standard 1.02
6810319       0x67EACF        JPEG image data, JFIF standard 1.02
6831989       0x683F75        Copyright string: "Copyright (c) 1998 Hewlett-Packard Company"
7033591       0x6B52F7        Zlib compressed data, best compression
...
```

```
634729        0x9AF69         bix header, header size: 64 bytes, header CRC: 0x306350, created: 
1988-02-16 09:38:08, image size: 16810370 bytes, Data Address: 0x21010051, Entry Point: 0x80008105, data CRC: 0x84020242, image name: ""
```

### Resources
* https://www.uio.no/studier/emner/matnat/fys/FYS4220/h11/undervisningsmateriale/laboppgaver-rt/
* https://support2.windriver.com/index.php?page=other-downloads&dw_search_product=66&dw_search_product_version=344&order_by=content_modified_date&order_way=asc#list
