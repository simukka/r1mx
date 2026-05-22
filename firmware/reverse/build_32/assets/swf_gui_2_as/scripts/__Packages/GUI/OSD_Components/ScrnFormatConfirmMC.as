class GUI.OSD_Components.ScrnFormatConfirmMC extends GUI.OSD_Components.FullScreenMC
{
   var __NUM_CLIPS_STR;
   function ScrnFormatConfirmMC()
   {
      super();
   }
   function SetFormatSubScreen(numClips)
   {
      if(numClips == 1)
      {
         this.__NUM_CLIPS_STR.text = "The magazine currently contains one clip.";
      }
      else
      {
         this.__NUM_CLIPS_STR.text = "The magazine currently contains " + numClips + " clips.";
      }
   }
}
