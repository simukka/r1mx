class GUI.OSD_Components.UserGuideManager
{
   var __gpdb;
   var __scrn;
   static var __manager;
   function UserGuideManager()
   {
      _global.VxDebug("...........................................................................CTOR UserGuideManager()");
      GUI.OSD_Components.UserGuideManager.__manager = this;
      this.__gpdb = _global.gpdb;
      this.__scrn = new Object();
      this.__scrn.SetReticleWidthMC = GUI.OSD_Components.ScreenMgrMC.GetManager().AttachScreen("SetReticleWidthMC","Set Reticle Width");
   }
   static function GetManager()
   {
      if(GUI.OSD_Components.UserGuideManager.__manager === undefined)
      {
         _global.VxError("UserGuideManager::GetManager(): ERROR! Called before created.");
      }
      return GUI.OSD_Components.UserGuideManager.__manager;
   }
   function CustomizeIt(type)
   {
      _global.VxLog("UserGuideManager::CustomizeIt(): ...");
      this.__scrn.SetReticleWidthMC.Activate(type);
   }
}
