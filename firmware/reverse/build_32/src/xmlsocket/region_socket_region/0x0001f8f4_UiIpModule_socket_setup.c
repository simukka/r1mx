/* 0x0001f8f4  UiIpModule_socket_setup  size=628 bytes */


undefined4 UiIpModule_socket_setup(int param_1)

{
  bool bVar1;
  int iVar2;
  undefined4 uVar3;
  uint uVar4;
  int iVar5;
  undefined4 uVar6;
  int iVar7;
  
  iVar2 = param_1 * 0x430;
  uVar3 = 0;
  if (param_1 != 1) {
    FUN_0000a07c(*(undefined4 *)(iVar2 + 0x108ea30),0xc);
    FUN_005b1edc(1);
    FUN_0000a07c(*(undefined4 *)(iVar2 + 0x108ea30),8);
    bVar1 = false;
    uVar3 = FUN_0000a05c(*(undefined4 *)(iVar2 + 0x108ea28));
    *(undefined4 *)(iVar2 + 0x108e9f8) = uVar3;
    FUN_005b1edc(1);
    iVar7 = 0;
    if (0 < *(int *)(iVar2 + 0x108e9dc)) {
      do {
        uVar4 = FUN_0000a05c(*(undefined4 *)(iVar2 + 0x108ea2c));
        if ((uVar4 & 0x80) == 0) {
          bVar1 = true;
          break;
        }
        iVar5 = FUN_00009518();
        FUN_005b1edc(iVar5 / 10);
        iVar7 = iVar7 + 100;
      } while (iVar7 < *(int *)(iVar2 + 0x108e9dc));
    }
    if (2 < iRam00e107b4) {
      uVar3 = FUN_0000a05c(*(undefined4 *)(iVar2 + 0x108ea2c));
      uVar6 = FUN_0000a05c(*(undefined4 *)(iVar2 + 0x108ea28));
      FUN_00443f20(0xd35488,iVar7,uVar3,uVar6,0,0,0);
    }
    if (bVar1) {
      if (4 < iRam00e107b4) {
        FUN_00443f20(0xd354dc,0,0,0,0,0,0);
      }
      if (pcRam00e10728 != reset_vector) {
        (*pcRam00e10728)(param_1);
      }
      if (4 < iRam00e107b4) {
        FUN_00443f20(0xd354bc,0,0,0,0,0,0);
      }
      FUN_005ab588(iVar2 + 0x108e8f8,0,0);
      if (6 < iRam00e107b4) {
        FUN_00443f20(0xd35478,0,0,0,0,0,0);
      }
      uVar3 = 0;
    }
    else if (iRam00e107b4 < 9) {
      uVar3 = 0xffffffff;
    }
    else {
      uVar3 = FUN_0000a05c(*(undefined4 *)(iVar2 + 0x108ea2c));
      uVar6 = FUN_0000a05c(*(undefined4 *)(iVar2 + 0x108ea28));
      FUN_00443f20(0xd35508,uVar3,uVar6,0,0,0,0);
      uVar3 = 0xffffffff;
    }
  }
  return uVar3;
}

