class GUI.OSD_Components.ScrnFacCalApplyInProgMC extends GUI.OSD_Components.FullScreenMC
{
   var __factoryCalState;
   function ScrnFacCalApplyInProgMC()
   {
      super();
      this.NewProgressBar(500);
   }
   function SetStateString(state)
   {
      this.__factoryCalState.text = state;
   }
}
