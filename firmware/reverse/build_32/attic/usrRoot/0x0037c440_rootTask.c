/* 0x0037c440  rootTask  size=4 bytes */


void thunk_FUN_0037c290(undefined4 param_1)

{
  bool bVar1;
  code *pcVar2;
  int iVar3;
  int unaff_r26;
  undefined4 unaff_r29;
  int unaff_r30;
  undefined4 unaff_r31;
  uint in_stack_00000034;
  code *in_stack_00000038;
  undefined4 in_stack_0000003c;
  undefined4 in_stack_00000044;
  
  if ((*(uint *)(*(int *)(unaff_r30 + -0x3c20) + 0x98) & 2) != 0) {
    in_stack_00000034 = in_stack_00000034 & 0xffffffe3;
  }
  *(undefined4 *)(*(int *)(unaff_r30 + -0x3c20) + 0x278) = param_1;
  if ((in_stack_00000034 & 1) != 0) {
    (*in_stack_00000038)(in_stack_0000003c,unaff_r31);
  }
  if (((in_stack_00000034 & 2) != 0) && ((in_stack_00000034 & 8) == 0)) {
    if (pcRam00e27068 != reset_vector) {
      (*pcRam00e27068)(*(undefined4 *)(unaff_r30 + -0x3c20),unaff_r31,in_stack_00000044,unaff_r29);
    }
    if (pcRam00e27064 != reset_vector) {
      (*pcRam00e27064)(*(undefined4 *)(unaff_r30 + -0x3c20),unaff_r31,in_stack_00000044,unaff_r29);
    }
  }
  if ((in_stack_00000034 & 0x1c) != 0) {
    *(undefined4 *)(*(int *)(unaff_r26 + -0x3c20) + 0x26c) = unaff_r31;
    if ((in_stack_00000034 & 8) == 0) {
      if ((in_stack_00000034 & 0x10) == 0) {
        if ((in_stack_00000034 & 4) == 0) goto LAB_0037c32c;
        FUN_0036fd0c();
        FUN_005b1a30();
        iVar3 = iRam00e9c3e0;
        *(uint *)(iRam00e9c3e0 + 0x268) = *(uint *)(iRam00e9c3e0 + 0x268) | 8;
        FUN_005b13ac(iVar3);
        iVar3 = iRam00e9c3e0;
      }
      else {
        FUN_0036fd0c();
        FUN_005b1a30();
        iVar3 = iRam00e9c3e0;
        pcVar2 = pcRam00e9c030;
        bVar1 = pcRam00e9c030 != reset_vector;
        *(uint *)(iRam00e9c3e0 + 0x268) = *(uint *)(iRam00e9c3e0 + 0x268) | 8;
        if (bVar1) {
          (*pcVar2)(*(undefined4 *)(iVar3 + 0x94));
          iVar3 = iRam00e9c3e0;
        }
      }
      *(uint *)(iVar3 + 0x268) = *(uint *)(iVar3 + 0x268) & 0xfffffff7;
    }
    else {
      if (pcRam00e2707c != reset_vector) {
        (*pcRam00e2707c)(unaff_r31,in_stack_00000044,in_stack_00000034 & 2);
      }
      if ((pcRam00e9c4b8 != reset_vector) && (iVar3 = (*pcRam00e9c4b8)(), iVar3 != 0)) {
        FUN_0036fd0c();
        FUN_005b1a30();
        return;
      }
    }
  }
LAB_0037c32c:
  *(uint *)(*(int *)(unaff_r26 + -0x3c20) + 0x268) =
       *(uint *)(*(int *)(unaff_r26 + -0x3c20) + 0x268) | 2;
  FUN_0037d87c();
  puRam00fbfa64 = (undefined4 *)FUN_005bb138(unaff_r31);
  uRam00fbfa68 = *puRam00fbfa64;
  FUN_0036c134(puRam00fbfa64,0x7fe00008,*(undefined4 *)(*(int *)(unaff_r26 + -0x3c20) + 0x94));
  uRam00fbfa5c = FUN_005bb114(unaff_r31);
  FUN_0036fd0c();
  FUN_005b1a30();
  return;
}

