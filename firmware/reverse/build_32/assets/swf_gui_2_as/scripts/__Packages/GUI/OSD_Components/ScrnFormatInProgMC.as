class GUI.OSD_Components.ScrnFormatInProgMC extends GUI.OSD_Components.FullScreenMC
{
   var __FORMATTING_STR;
   function ScrnFormatInProgMC()
   {
      super();
      this.NewProgressBar(500);
   }
   function ShowFormatting(magType)
   {
      this.__FORMATTING_STR.text = "Formatting the " + magType + " digital magazine...";
   }
}
