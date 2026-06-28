class GUI.OSD_Components.ScrnWarnGenericMC extends GUI.OSD_Components.FullScreenMC
{
   var WARNING;
   function ScrnWarnGenericMC()
   {
      super();
   }
   function SetWarningText(warning)
   {
      this.WARNING.text = warning;
   }
}
