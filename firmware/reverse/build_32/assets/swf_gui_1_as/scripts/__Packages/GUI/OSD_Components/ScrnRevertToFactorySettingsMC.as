class GUI.OSD_Components.ScrnRevertToFactorySettingsMC extends GUI.OSD_Components.FullScreenMC
{
   var __gpdb;
   function ScrnRevertToFactorySettingsMC()
   {
      super();
      _global.VxDebug("...........................................................................CTOR ScrnRevertToFactorySettingsMC()");
      this.__gpdb = _global.gpdb;
      this._visible = false;
   }
   function Activate()
   {
      super.Activate();
      _global.VxLog("ScrnRevertToFactorySettingsMC::Activate()");
      this._visible = true;
   }
}
