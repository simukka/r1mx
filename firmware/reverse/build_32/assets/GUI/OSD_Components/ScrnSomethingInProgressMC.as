class GUI.OSD_Components.ScrnSomethingInProgressMC extends GUI.OSD_Components.FullScreenMC
{
   var NewProgressBar;
   var __MESSAGE;
   function ScrnSomethingInProgressMC()
   {
      super();
      this.NewProgressBar(500);
   }
   function SetText(message)
   {
      this.__MESSAGE.text = message;
   }
}
