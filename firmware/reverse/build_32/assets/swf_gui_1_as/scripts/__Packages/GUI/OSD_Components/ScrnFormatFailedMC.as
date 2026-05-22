class GUI.OSD_Components.ScrnFormatFailedMC extends GUI.OSD_Components.FullScreenMC
{
   var __ERR_LINE1;
   var __ERR_LINE2;
   function ScrnFormatFailedMC()
   {
      super();
   }
   function SetErrorString(errLine1, errLine2)
   {
      this.__ERR_LINE1.text = errLine1;
      this.__ERR_LINE2.text = errLine2;
   }
}
