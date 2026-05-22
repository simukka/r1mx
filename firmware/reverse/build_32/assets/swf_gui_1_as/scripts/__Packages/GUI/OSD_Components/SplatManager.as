class GUI.OSD_Components.SplatManager
{
   var __gpdb;
   static var __manager;
   var __splatAllowed = false;
   var __showAudioSplat = false;
   var __showMeterSplat = false;
   function SplatManager()
   {
      _global.VxDebug("...........................................................................CTOR SplatManager()");
      GUI.OSD_Components.SplatManager.__manager = this;
      this.__gpdb = _global.gpdb;
   }
   static function GetManager()
   {
      if(GUI.OSD_Components.SplatManager.__manager === undefined)
      {
         _global.VxError("SplatManager::GetManager() called before being instantiated");
      }
      return GUI.OSD_Components.SplatManager.__manager;
   }
   function AllowSplat(allowSplat)
   {
      this.__splatAllowed = allowSplat;
      if(allowSplat)
      {
         if(this.__showAudioSplat)
         {
            _global.VxDebug("                   SplatManager::AllowSplat(" + allowSplat + ") Turning ON Volume");
            _global.VxEnableVolumeRendering(true);
         }
         if(this.__showMeterSplat)
         {
            _global.VxDebug("                   SplatManager::AllowSplat(" + allowSplat + ") Turning ON IA");
            _global.VxEnableImageAnalysisRendering(false);
            _global.VxEnableImageAnalysisRendering(true);
         }
      }
      else
      {
         _global.VxDebug("                   SplatManager::AllowSplat(" + allowSplat + ") Turning OFF IA and Volume");
         _global.VxEnableImageAnalysisRendering(false);
         _global.VxEnableVolumeRendering(false);
      }
   }
   function ShowAudioSplat(show)
   {
      this.__showAudioSplat = show;
      GUI.OSD_Components.GadgetManager.GetManager().ShowVolumeMeter(show);
      _global.VxDebug("                   SplatManager::ShowAudioSplat(" + show + ")");
      if(this.__splatAllowed)
      {
         _global.VxDebug("                   SplatManager::ShowAudioSplat(" + show + ") Turning " + (!show ? "OFF" : "ON") + " Volume");
         _global.VxEnableVolumeRendering(show);
      }
   }
   function ShowMeterSplat(show)
   {
      this.__showMeterSplat = show;
      _global.VxDebug("                   SplatManager::ShowMeterSplat(" + show + ")");
      if(this.__splatAllowed)
      {
         _global.VxDebug("                   SplatManager::ShowMeterSplat(" + show + ") Turning " + (!show ? "OFF" : "ON") + " IA Meters");
         if(show)
         {
            _global.VxEnableImageAnalysisRendering(false);
         }
         _global.VxEnableImageAnalysisRendering(show);
         if(!show)
         {
            _global.VxForceRedraw();
         }
      }
   }
}
