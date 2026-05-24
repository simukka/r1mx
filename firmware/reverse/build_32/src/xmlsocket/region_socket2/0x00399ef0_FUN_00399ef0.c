/* 0x00399ef0  FUN_00399ef0  size=208 bytes */


void FUN_00399ef0(undefined1 *param_1,int param_2,int param_3,code *param_4)

{
  undefined1 uVar1;
  undefined1 *puVar2;
  undefined1 *puVar3;
  undefined1 *puVar4;
  int iVar5;
  undefined1 *puVar6;
  undefined1 *puVar7;
  
  puVar6 = param_1 + param_3;
  do {
    puVar7 = puVar6;
    if (param_1 + param_2 * param_3 <= puVar6) {
      return;
    }
    do {
      puVar7 = puVar7 + -param_3;
      if (puVar7 < param_1) break;
      iVar5 = (*param_4)(puVar6,puVar7);
    } while (iVar5 < 0);
    iVar5 = param_3;
    if (puVar7 + param_3 == puVar6) {
      puVar6 = puVar6 + param_3;
    }
    else {
      for (; iVar5 != 0; iVar5 = iVar5 + -1) {
        uVar1 = *puVar6;
        puVar4 = puVar6 + -param_3;
        puVar3 = puVar6;
        while (puVar2 = puVar4, puVar7 + param_3 <= puVar2) {
          *puVar3 = *puVar2;
          puVar3 = puVar2;
          puVar4 = puVar2 + -param_3;
        }
        *puVar3 = uVar1;
        puVar6 = puVar6 + 1;
      }
    }
  } while( true );
}

