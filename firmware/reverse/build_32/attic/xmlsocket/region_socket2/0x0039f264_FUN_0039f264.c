/* 0x0039f264  FUN_0039f264  size=144 bytes */


int FUN_0039f264(undefined4 param_1,undefined4 param_2)

{
  int iVar1;
  
  if (pcRam010cf3e4 == reset_vector) {
    pcRam010cf3e4 = (code *)0x469fd0;
  }
  FUN_005accf4(uRam010cf3e0,0xffffffff);
  iVar1 = (*pcRam010cf3e4)(param_1,param_2);
  if (iVar1 != 0) {
    iRam010cf3f4 = iRam010cf3f4 + 1;
  }
  FUN_005ad104(uRam010cf3e0);
  return iVar1;
}

