class GUI.OSD_Components.StatusBoxMC extends MovieClip
{
   function StatusBoxMC()
   {
      super();
      this.gotoAndStop("FRAME_GREEN");
   }
   function SetColor(color)
   {
      switch(color)
      {
         case "green":
            this.gotoAndStop("FRAME_GREEN");
            break;
         case "yellow":
            this.gotoAndStop("FRAME_YELLOW");
            break;
         case "red":
            this.gotoAndStop("FRAME_RED");
            break;
         case "grey":
            this.gotoAndStop("FRAME_GREY");
         default:
            return;
      }
   }
}
