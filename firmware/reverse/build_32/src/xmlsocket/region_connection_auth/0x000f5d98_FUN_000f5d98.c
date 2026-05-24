/* 0x000f5d98  FUN_000f5d98  size=144 bytes */


void FUN_000f5d98(int param_1)

{
  char cVar1;
  
  FUN_000f5d84();
  if (*(char *)(param_1 + 0x6c) != '\0') {
    *(undefined1 *)(param_1 + 0x6d) = 1;
    cVar1 = *(char *)(param_1 + 0x6c);
    while (cVar1 != '\0') {
      FUN_001d9a58(10);
      cVar1 = *(char *)(param_1 + 0x6c);
    }
  }
  if (*(char *)(param_1 + 0x60) != '\0') {
    *(undefined1 *)(param_1 + 0x60) = 0;
    FUN_003598fc(0);
    return;
  }
  return;
}

