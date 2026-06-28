class GUI.OSD_Components.GadgetManager
{
   var __activeGadget;
   var __activeGadgetName;
   var __gadgets;
   var __gpdb;
   var __mc;
   static var __manager;
   var __visible = false;
   var __imageAnalysisActive = false;
   function GadgetManager(parent)
   {
      _global.VxDebug("...........................................................................CTOR GadgetManager()");
      this.__mc = parent;
      this.__gpdb = _global.gpdb;
      GUI.OSD_Components.GadgetManager.__manager = this;
      this.__gadgets = new Object();
      this.__mc.attachMovie("PlaybackPanel","mcPlayback",this.__mc.getNextHighestDepth(),{_x:0,_y:0});
      this.__gadgets.PlaybackPanel = this.__mc.mcPlayback;
      this.__mc.attachMovie("Widget_VolumeMeter","mcGadgetVolume",this.__mc.getNextHighestDepth(),{_x:910,_y:790});
      this.__gadgets.Volume = this.__mc.mcGadgetVolume;
      this.__mc.attachMovie("ImageAnalysis","mcGadgetImageAnalysis",this.__mc.getNextHighestDepth());
      this.__gadgets.ImageAnalysis = this.__mc.mcGadgetImageAnalysis;
      GUI.OSD_Components.TabManager.GetManager();
   }
   static function GetManager()
   {
      if(GUI.OSD_Components.GadgetManager.__manager === undefined)
      {
         _global.VxError("GadgetManager::GetManager() Called before created");
      }
      return GUI.OSD_Components.GadgetManager.__manager;
   }
   function ShowGadget(show)
   {
      _global.VxDebug("GadgetManager::ShowGadget(" + show.toString() + ")");
      var _loc4_;
      if(!GUI.OSD_Components.TabManager.GetManager().IsGuiNavigationActive())
      {
         _loc4_ = this.__activeGadget;
         this.SelectGadget();
         this.__visible = show;
         if(_loc4_ != this.__activeGadget)
         {
            _loc4_.Activate(false);
            if(!GUI.OSD_Components.TabManager.GetManager().IsGuiNavigationActive())
            {
               this.__activeGadget.Activate(true);
            }
         }
      }
      _global.VxDebug("GadgetManager::ShowGadget(" + show.toString() + ") Forcing display of IA meter");
      this.__gadgets.ImageAnalysis.Activate(show);
   }
   function SelectGadget()
   {
      var _loc5_ = "IDLE" != this.__gpdb.paramGet("VIDEO.PLAYBACK.STATE");
      var _loc9_ = "Spot Exposure" == this.__gpdb.paramGet("GUI.SOFTKEY.IMAGE_ANALYSIS.HUD_METER");
      var _loc7_ = this.__gpdb.paramGetBoolean("GUI.SOFTKEY.IMAGE_ANALYSIS.ASSIST_METER_ENABLED");
      var _loc6_ = this.__gpdb.paramGetBoolean("VIDEO.RECORD.VARISPEED.ENABLED");
      var _loc4_ = this.__gpdb.paramGetBoolean("GUI.RECORD.TIMELAPSE.ENABLED");
      var _loc3_ = this.__gpdb.paramGetBoolean("IMAGE_ANALYSIS.MAGNIFICATION.ENABLE");
      var _loc8_ = !_loc4_ && !_loc6_ && !_loc3_;
      _global.VxDebug("GadgetManager::SelectGadget()      playbackActive: " + _loc5_);
      _global.VxDebug("GadgetManager::SelectGadget()          zoomActive: " + _loc3_);
      _global.VxDebug("GadgetManager::SelectGadget()      iaAssistActive: " + _loc7_);
      _global.VxDebug("GadgetManager::SelectGadget()         audioActive: " + _loc8_);
      if(_loc5_)
      {
         this.__activeGadget = this.__gadgets.PlaybackPanel;
         this.__activeGadgetName = "Playback";
      }
      else if(_loc7_ || _loc9_)
      {
         this.__activeGadget = this.__gadgets.ImageAnalysis;
         this.__activeGadgetName = "Image Analysis";
      }
      else if(_loc6_ || _loc4_)
      {
         this.__activeGadget = null;
         this.__activeGadgetName = "NULL (VS or TL)";
      }
      else if(_loc3_)
      {
         this.__activeGadget = null;
         this.__activeGadgetName = "NULL (Zoom)";
      }
      else if(_loc8_)
      {
         this.__activeGadget = null;
         this.__activeGadgetName = "NULL (Volume Meter)";
      }
      _global.VxDebug("GadgetManager::SelectGadget() new __activeGadget: " + this.__activeGadgetName);
   }
   function ShowVolumeMeter(show)
   {
      this.__gadgets.Volume.Activate(show);
      _global.VxDebug("GadgetManager::ShowVolumeMeter() VolumeMeter is visible: " + show);
   }
   function onInputEvent(name, value)
   {
      var _loc3_ = false;
      _global.VxDebug("..GadgetManager::onInputEvent(): " + name + "," + value);
      if(this.__activeGadget)
      {
         _loc3_ = this.__activeGadget.onInputEvent(name,value);
      }
      return _loc3_;
   }
}
