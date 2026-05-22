class GUI.OSD_Components.HudLowerMC extends MovieClip
{
   var __gpdb;
   var __show;
   var TIMELAPSE;
   var VARISPEED;
   var MAGNIFY;
   static var __manager;
   function HudLowerMC()
   {
      super();
      _global.VxDebug("...........................................................................CTOR HudLowerMC()");
      this.__gpdb = _global.gpdb;
      GUI.OSD_Components.HudLowerMC.__manager = this;
      this.InitLowerHUD();
      this.AddGpdbCallbacks();
   }
   function InitLowerHUD()
   {
      this.__show = !this.__gpdb.paramGetBoolean("GUI.OSD.SHOW.LOWER_HUD");
      this.Show(!this.__show);
   }
   function AddGpdbCallbacks()
   {
      var _loc2_ = mx.utils.Delegate.create(this,this.Update);
      this.__gpdb.addCallback("GUI.OSD.SHOW.LOWER_HUD",_loc2_);
      this.__gpdb.addCallback("VIDEO.PLAYBACK.STATE",_loc2_);
      this.__gpdb.addCallback("IMAGE_ANALYSIS.MAGNIFICATION.ENABLE",_loc2_);
      this.__gpdb.addCallback("GUI.SOFTKEY.IMAGE_ANALYSIS.ASSIST_METER_ENABLED",_loc2_);
   }
   function Update(name, value)
   {
      _global.VxDebug("HudLowerMC::Update(" + name + ", \'" + value + "\')");
      switch(name)
      {
         case "GUI.OSD.SHOW.LOWER_HUD":
            this.Show("true" == value);
            break;
         case "IMAGE_ANALYSIS.MAGNIFICATION.ENABLE":
         case "GUI.SOFTKEY.IMAGE_ANALYSIS.ASSIST_METER_ENABLED":
         case "VIDEO.PLAYBACK.STATE":
            this.RefreshDisplay();
      }
   }
   static function GetManager()
   {
      if(GUI.OSD_Components.HudLowerMC.__manager === undefined)
      {
         _global.VxError("HudLowerMC::GetManager() called before being instantiated");
      }
      return GUI.OSD_Components.HudLowerMC.__manager;
   }
   function RefreshDisplay()
   {
      this.Show(this.__show);
   }
   function Show(show)
   {
      var _loc4_ = this.__gpdb.paramGetBoolean("GUI.OSD.SHOW.LOWER_HUD");
      show &= _loc4_;
      _global.VxDebug("HudLowerMC::Show(show:" + show + "), __show: " + this.__show + ", enabled: " + _loc4_);
      if(!GUI.OSD_Components.TabManager.GetManager().IsGuiNavigationActive())
      {
         this.__show = show;
         if(show)
         {
            if(this.__gpdb.paramGetBoolean("GUI.SOFTKEY.IMAGE_ANALYSIS.ASSIST_METER_ENABLED") && "Focus Assist Overlay" != this.__gpdb.paramGet("GUI.SOFTKEY.IMAGE_ANALYSIS.ASSIST_METER"))
            {
               _global.VxDebug("HudLowerMC::Show()   FULL-WIDTH GRAPH");
               GUI.OSD_Components.GadgetManager.GetManager().ShowGadget(true);
               this.ManageAudioSplat(false);
               this._visible = false;
            }
            else
            {
               _global.VxDebug("HudLowerMC::Show()   Normal HUD");
               this._visible = true;
               this.ManageAudioSplat(true);
               GUI.OSD_Components.GadgetManager.GetManager().ShowGadget(true);
            }
         }
         else
         {
            _global.VxDebug("HudLowerMC::Show()   Hide HUD");
            GUI.OSD_Components.GadgetManager.GetManager().ShowGadget(false);
            this.ManageAudioSplat(false);
            this._visible = false;
         }
      }
      else
      {
         _global.VxDebug("HudLowerMC::Show(" + show + ") ...IGNORED because menu is active");
      }
   }
   function ManageAudioSplat(show)
   {
      if(show)
      {
         if("IDLE" != this.__gpdb.paramGet("VIDEO.PLAYBACK.STATE"))
         {
            _global.VxDebug("HudLowerMC::ManageAudioSplat(" + show + "): PLAYBACK");
            this.TIMELAPSE._visible = false;
            this.VARISPEED._visible = false;
            GUI.OSD_Components.SplatManager.GetManager().ShowAudioSplat(true);
         }
         else if(this.__gpdb.paramGetBoolean("IMAGE_ANALYSIS.MAGNIFICATION.ENABLE"))
         {
            _global.VxDebug("HudLowerMC::ManageAudioSplat(" + show + "): MAGNIFICATION");
            this.TIMELAPSE._visible = false;
            this.VARISPEED._visible = false;
            this.MAGNIFY._visible = true;
            GUI.OSD_Components.SplatManager.GetManager().ShowAudioSplat(false);
         }
         else if(this.__gpdb.paramGetBoolean("VIDEO.RECORD.VARISPEED.ENABLED"))
         {
            _global.VxDebug("HudLowerMC::ManageAudioSplat(" + show + "): VARISPEED");
            this.TIMELAPSE._visible = false;
            this.VARISPEED._visible = true;
            this.MAGNIFY._visible = false;
            GUI.OSD_Components.SplatManager.GetManager().ShowAudioSplat(false);
         }
         else if(this.__gpdb.paramGetBoolean("GUI.RECORD.TIMELAPSE.ENABLED"))
         {
            _global.VxDebug("HudLowerMC::ManageAudioSplat(" + show + "): TIMELAPSE");
            this.TIMELAPSE._visible = true;
            this.VARISPEED._visible = false;
            this.MAGNIFY._visible = false;
            GUI.OSD_Components.SplatManager.GetManager().ShowAudioSplat(false);
         }
         else
         {
            _global.VxDebug("HudLowerMC::ManageAudioSplat(" + show + "): VOLUME METER");
            this.TIMELAPSE._visible = false;
            this.VARISPEED._visible = false;
            this.MAGNIFY._visible = false;
            GUI.OSD_Components.SplatManager.GetManager().ShowAudioSplat(true);
         }
      }
      else
      {
         this.TIMELAPSE._visible = false;
         this.VARISPEED._visible = false;
         this.MAGNIFY._visible = false;
         GUI.OSD_Components.SplatManager.GetManager().ShowAudioSplat(false);
      }
   }
}
