class GUI.OSD_Components.WarningBoxMC extends MovieClip
{
   var __warningMessage;
   function WarningBoxMC()
   {
      super();
      this.__warningMessage.text = "hello";
      this._visible = false;
   }
   function Show(warning)
   {
      this.__warningMessage.text = "[" + warning + "]";
      this._visible = true;
   }
   function Hide()
   {
      this._visible = false;
   }
}
