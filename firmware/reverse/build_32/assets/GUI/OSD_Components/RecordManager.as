class GUI.OSD_Components.RecordManager
{
   var __gpdb;
   static var __manager;
   var __isBusy = false;
   function RecordManager()
   {
      _global.VxDebug("...........................................................................CTOR RecordManager()");
      GUI.OSD_Components.RecordManager.__manager = this;
      this.__gpdb = _global.gpdb;
      this.AddCallbacks();
   }
   function AddCallbacks()
   {
      var _loc3_ = mx.utils.Delegate.create(this,this.Update);
      this.__gpdb.addCallback("GUI.RUN_STATE",_loc3_);
      this.__gpdb.addCallback("VIDEO.RECORD.REQUESTED",_loc3_);
      this.__gpdb.addCallback("VIDEO.RECORD.STATE",_loc3_);
      var _loc2_ = mx.utils.Delegate.create(this,this.HandleVariTimelapseUpdate);
      this.__gpdb.addCallback("GUI.RECORD.TIMELAPSE.ENABLED",_loc2_);
      this.__gpdb.addCallback("GUI.RECORD.TIMELAPSE.TRIGGER_MODE",_loc2_);
      this.__gpdb.addCallback("VIDEO.RECORD.VARISPEED.ENABLED",_loc2_);
      this.__gpdb.addCallback("VIDEO.RECORD.VARISPEED.RAMP.ENABLED",_loc2_);
      this.__gpdb.addCallback("VIDEO.RECORD.VARISPEED.RAMP.TRIGGER",_loc2_);
      this.__gpdb.addCallback("GUI.RECORD.VARISPEED.FRAME_RATE",_loc2_);
      this.__gpdb.addCallback("GUI.RECORD.VARISPEED.RAMP.END_FRAME_RATE",_loc2_);
   }
   function Update(name, value)
   {
      switch(name)
      {
         case "GUI.RUN_STATE":
            if(value == "GUI_STATE_3_INITIALIZE_GUI_STATE")
            {
               this.InitGuiSettings();
            }
            return;
         case "VIDEO.RECORD.REQUESTED":
            if(value == "true")
            {
               this.SelectivelyEnableMagnification(false);
               this.SetCameraBusy(true);
            }
            return;
         case "VIDEO.RECORD.STATE":
            switch(value)
            {
               case "ACTIVE":
                  if(!this.__gpdb.paramGetBoolean("VIDEO.RECORD.REQUESTED"))
                  {
                     _global.VxLog("ERROR! RecordManager::Update() RECORD_STATE==ACTIVE w/o being REQUESTED!");
                  }
                  break;
               case "IDLE":
                  this.SetCameraBusy(false);
                  if(this.__gpdb.paramGetBoolean("VIDEO.RECORD.REQUESTED"))
                  {
                     _global.VxError("ERROR! RecordManager::Update() RECORD_STATE==IDLE while RECORD_REQUESTED!");
                  }
                  this.PostRecordCleanup();
                  break;
               case "ERROR":
                  this.HandleRecordFailure();
                  this.PostRecordCleanup();
            }
            return;
         default:
            _global.VxError("RecordManager.Update() ERROR! Unknown parameter, \'" + name + "\'. Ignoring.");
            return;
      }
   }
   function InitGuiSettings()
   {
      this.RequestSystemFrameRate(this.__gpdb.paramGetNumber("PROJECT.MODE_MATRIX.FRAME_RATE"));
      this.InitGuiFromVideoRecordMode();
      var _loc2_ = this.__gpdb.paramGetNumber("VIDEO.RECORD.PRERECORD.DURATION");
      if(_loc2_ == 0)
      {
         this.__gpdb.paramSet("GUI.RECORD.PRERECORD.ENABLED",false);
      }
      else
      {
         this.__gpdb.paramSet("GUI.RECORD.PRERECORD.ENABLED",true);
         this.__gpdb.paramSet("GUI.RECORD.PRERECORD.DURATION",_loc2_);
      }
      this.SetSystemRecordParams();
   }
   function InitGuiFromVideoRecordMode()
   {
      var _loc7_ = this.__gpdb.paramGet("VIDEO.RECORD.MODE");
      var _loc3_;
      var _loc4_ = this.__gpdb.paramGetBoolean("VIDEO.RECORD.VARISPEED.RAMP.ENABLED");
      var _loc6_;
      var _loc5_;
      switch(_loc7_)
      {
         case "CONTINUOUS":
            if(this.__gpdb.paramGetBoolean("VIDEO.RECORD.VARISPEED.ENABLED"))
            {
               _loc3_ = "VARISPEED";
            }
            else
            {
               _loc3_ = "NORMAL";
            }
            break;
         case "TIMELAPSE":
            _loc3_ = "TIMELAPSE";
            this.__gpdb.paramSet("GUI.RECORD.TIMELAPSE.TRIGGER_MODE","INTERVAL");
            break;
         case "BURST":
            _loc3_ = "TIMELAPSE";
            this.__gpdb.paramSet("GUI.RECORD.TIMELAPSE.TRIGGER_MODE","ONE-SHOT");
            break;
         case "VARISPEED":
            _loc3_ = "VARISPEED";
            _global.VxError("RecordManager:InitGuiFromVideoRecordMode() GUI doesn\'t support the VIDEO.RECORD.MODE==\'VARISPEED\'. Yet.");
      }
      switch(_loc3_)
      {
         case "NORMAL":
            _loc6_ = false;
            _loc5_ = false;
            _loc4_ = false;
            break;
         case "VARISPEED":
            _loc6_ = true;
            _loc5_ = false;
            break;
         case "TIMELAPSE":
            _loc6_ = false;
            _loc5_ = true;
            _loc4_ = false;
      }
      this.__gpdb.paramSet("GUI.RECORD.TIMELAPSE.ENABLED",_loc5_);
      this.__gpdb.paramSet("VIDEO.RECORD.VARISPEED.ENABLED",_loc6_);
      this.__gpdb.paramSet("VIDEO.RECORD.VARISPEED.RAMP.ENABLED",_loc4_);
   }
   static function GetManager()
   {
      if(GUI.OSD_Components.RecordManager.__manager === undefined)
      {
         _global.VxError("ERROR! RecordManager::GetManager() called before being instantiated");
      }
      return GUI.OSD_Components.RecordManager.__manager;
   }
   function IsRecording()
   {
      return this.__isBusy;
   }
   function GuiRecordMode()
   {
      var _loc2_;
      if(this.__gpdb.paramGetBoolean("GUI.RECORD.TIMELAPSE.ENABLED"))
      {
         _loc2_ = "TIMELAPSE";
      }
      else if(this.__gpdb.paramGetBoolean("VIDEO.RECORD.VARISPEED.ENABLED"))
      {
         _loc2_ = "VARISPEED";
      }
      else
      {
         _loc2_ = "NORMAL";
      }
      return _loc2_;
   }
   function HandleRecordRequest()
   {
      var _loc3_ = this.__gpdb.paramGet("VIDEO.RECORD.STATE");
      var _loc4_;
      switch(_loc3_)
      {
         case "IDLE":
            if(!this.__isBusy)
            {
               this.__gpdb.paramSet("VIDEO.PLAYBACK.REQUESTED",false);
               this.SelectivelyEnableMagnification(false);
               if(this.__gpdb.paramGetBoolean("GUI.RECORD.PRERECORD.ENABLED") && this.__gpdb.paramGetBoolean("GUI.RECORD.PRERECORD.REQUESTED"))
               {
                  this.__gpdb.paramSet("GUI.RECORD.PRERECORD.REQUESTED",false);
                  _loc4_ = this.__gpdb.paramGetNumber("GUI.RECORD.PRERECORD.DURATION");
                  this.__gpdb.paramSet("VIDEO.RECORD.PRERECORD.DURATION",_loc4_);
               }
               else
               {
                  this.__gpdb.paramSet("VIDEO.RECORD.PRERECORD.DURATION",0);
               }
               this.__gpdb.paramSet("VIDEO.RECORD.REQUESTED",true);
            }
            return;
         case "PRERECORD":
            this.__gpdb.paramSet("VIDEO.RECORD.PRERECORD.RECORD_REQUESTED",true);
            return;
         case "ACTIVE":
            this.__gpdb.paramSet("VIDEO.RECORD.REQUESTED",false);
            this.__gpdb.paramSet("VIDEO.RECORD.PRERECORD.RECORD_REQUESTED",false);
            return;
         case "ERROR":
            _global.VxLog("RecordManager::HandleRecordRequest() Handling error. Ignoring RECORD toggle.");
            return;
         default:
            return;
      }
   }
   function HandlePreRecordRequest()
   {
      if(this.__gpdb.paramGetBoolean("GUI.RECORD.PRERECORD.ENABLED"))
      {
         _global.VxLog("RecordManager::HandlePreRecordRequest() Entering pre-record mode...");
         this.__gpdb.paramSet("GUI.RECORD.PRERECORD.REQUESTED",true);
         this.HandleRecordRequest();
      }
      else
      {
         _global.VxLog("RecordManager::HandlePreRecordRequest() Pre-record is not enabled. Ignoring keypress.");
      }
   }
   function HandleBurstRequest()
   {
      var _loc3_ = this.__gpdb.paramGet("VIDEO.RECORD.STATE");
      switch(_loc3_)
      {
         case "IDLE":
            if(!this.__isBusy)
            {
               _global.VxLog("RecordManager::HandleBurstRequest() Initiating BURST mode.");
               this.__gpdb.paramSet("VIDEO.PLAYBACK.REQUESTED",false);
               this.__gpdb.paramSet("GUI.RECORD.TIMELAPSE.TRIGGER_MODE","ONE-SHOT");
               this.__gpdb.paramSet("GUI.RECORD.TIMELAPSE.ENABLED",true);
               this.__gpdb.paramSet("VIDEO.RECORD.REQUESTED",true);
            }
            return;
         case "ACTIVE":
            _global.VxLog("RecordManager::HandleBurstRequest() Requesting BURST!");
            this.__gpdb.paramSet("VIDEO.RECORD.TIMELAPSE.BURST_TRIGGER",true);
            return;
         case "ERROR":
            return;
         default:
            return;
      }
   }
   function HandleRampRequest()
   {
      var _loc3_ = this.__gpdb.paramGet("VIDEO.RECORD.STATE");
      switch(_loc3_)
      {
         case "ACTIVE":
            _global.VxLog("RecordManager::HandleRampRequest() Requesting RAMP!");
            if(this.__gpdb.paramGetBoolean("VIDEO.RECORD.VARISPEED.ENABLED") && this.__gpdb.paramGetBoolean("VIDEO.RECORD.VARISPEED.RAMP.ENABLED"))
            {
               if("ON_EVENT" == this.__gpdb.paramGet("VIDEO.RECORD.VARISPEED.RAMP.TRIGGER"))
               {
                  this.__gpdb.paramSet("VIDEO.RECORD.VARISPEED.RAMP.ACTIVE","RAMP_1");
               }
               else
               {
                  _global.VxError("RecordManager::HandleRampRequest() TRIGGER not \'ON_EVENT\'. Ignoring request.");
               }
            }
            else
            {
               _global.VxError("RecordManager::HandleRampRequest() Ramping now enabled. Ignoring request.");
            }
            return;
         case "IDLE":
         case "ERROR":
            _global.VxError("RecordManager::HandleRampRequest() Not recording. Ignoring request.");
            return;
         default:
            return;
      }
   }
   function SetCameraBusy(isBusy)
   {
      this.__isBusy = isBusy;
      if(isBusy)
      {
         GUI.OSD_Components.MenuManager.GetManager().ExitMenuTree();
      }
   }
   function HandleVariTimelapseUpdate(name, value)
   {
      var _loc3_ = value == "true";
      switch(name)
      {
         case "GUI.RECORD.TIMELAPSE.ENABLED":
            if(_loc3_)
            {
               this.__gpdb.paramSet("VIDEO.RECORD.VARISPEED.ENABLED",false);
            }
            if("ACTIVE" == this.__gpdb.paramGet("VIDEO.RECORD.STATE"))
            {
               this.__gpdb.paramSet("GUI.RECORD.TIMELAPSE.ENABLED",!_loc3_);
               GUI.OSD_Components.ErrorManagerMC.GetManager().PopupErrorMessage("RECORDING LOCKOUT.","Feature not available while recording.");
            }
            break;
         case "GUI.RECORD.TIMELAPSE.TRIGGER_MODE":
            break;
         case "VIDEO.RECORD.VARISPEED.ENABLED":
            if(_loc3_)
            {
               this.__gpdb.paramSet("GUI.RECORD.TIMELAPSE.ENABLED",false);
            }
            if("ACTIVE" == this.__gpdb.paramGet("VIDEO.RECORD.STATE"))
            {
               this.__gpdb.paramSet("VIDEO.RECORD.VARISPEED.ENABLED",!_loc3_);
               GUI.OSD_Components.ErrorManagerMC.GetManager().PopupErrorMessage("RECORDING LOCKOUT.","Feature not available while recording.");
            }
            else if(!_loc3_)
            {
               this.__gpdb.paramSet("VIDEO.RECORD.VARISPEED.RAMP.ENABLED",false);
            }
            break;
         case "VIDEO.RECORD.VARISPEED.RAMP.ENABLED":
            if(_loc3_)
            {
               this.__gpdb.paramSet("VIDEO.RECORD.VARISPEED.ENABLED",true);
               this.ConfigureSysRampParams();
            }
            break;
         case "GUI.RECORD.VARISPEED.FRAME_RATE":
         case "VIDEO.RECORD.VARISPEED.RAMP.TRIGGER":
         case "GUI.RECORD.VARISPEED.RAMP.END_FRAME_RATE":
            this.ConfigureSysRampParams();
            break;
         default:
            _global.VxError("RecordManager.HandleVariTimelapseUpdate() ERROR! Unknown parameter, \'" + name + "\'. Ignoring.");
      }
      this.SetSystemRecordParams(name,value);
      GUI.OSD_Components.HudLowerMC.GetManager().RefreshDisplay();
   }
   function SetSystemRecordParams(name, value)
   {
      var _loc9_ = this.__gpdb.paramGet("VIDEO.RECORD.MODE");
      var _loc8_;
      var _loc2_;
      var _loc7_;
      var _loc5_;
      var _loc3_;
      var _loc4_;
      var _loc6_;
      if(!this.__gpdb.paramGetBoolean("SYSTEM.PROFILE.RESTORE.REQUESTED"))
      {
         _loc8_ = this.GuiRecordMode();
         _loc7_ = this.__gpdb.paramGetNumber("PROJECT.MODE_MATRIX.FRAME_RATE");
         switch(_loc8_)
         {
            case "NORMAL":
               _loc2_ = "CONTINUOUS";
               _loc4_ = false;
               _loc6_ = false;
               _loc3_ = true;
               _loc5_ = false;
               break;
            case "VARISPEED":
               _loc2_ = "CONTINUOUS";
               _loc4_ = true;
               _loc6_ = false;
               _loc3_ = false;
               _loc5_ = this.__gpdb.paramGetBoolean("VIDEO.RECORD.VARISPEED.RAMP.ENABLED");
               _loc7_ = this.__gpdb.paramGetNumber("GUI.RECORD.VARISPEED.FRAME_RATE");
               break;
            case "TIMELAPSE":
               switch(this.__gpdb.paramGet("GUI.RECORD.TIMELAPSE.TRIGGER_MODE"))
               {
                  case "INTERVAL":
                     _loc2_ = "TIMELAPSE";
                     break;
                  case "ONE-SHOT":
                     _loc2_ = "BURST";
               }
               _loc4_ = false;
               _loc6_ = true;
               _loc3_ = false;
               _loc5_ = false;
         }
         this.__gpdb.paramSet("VIDEO.RECORD.MODE",_loc2_);
         this.__gpdb.paramSet("VIDEO.RECORD.VARISPEED.ENABLED",_loc4_);
         this.__gpdb.paramSet("VIDEO.RECORD.VARISPEED.RAMP.ENABLED",_loc5_);
         this.__gpdb.paramSet("AUDIO.ENABLED",_loc3_);
         this.RequestSystemFrameRate(_loc7_);
         this.ConfigureSysRampParams();
      }
   }
   function ConfigureSysRampParams()
   {
      var _loc2_;
      var _loc3_;
      var _loc4_;
      if(this.__gpdb.paramGetBoolean("VIDEO.RECORD.VARISPEED.ENABLED"))
      {
         if(this.__gpdb.paramGetBoolean("VIDEO.RECORD.VARISPEED.RAMP.ENABLED"))
         {
            _loc2_ = this.__gpdb.paramGetNumber("VIDEO.RECORD.FRAME_RATE.REQUESTED");
            _loc3_ = this.__gpdb.paramGetNumber("GUI.RECORD.VARISPEED.RAMP.END_FRAME_RATE");
            _loc4_ = _loc3_ / _loc2_;
            this.__gpdb.paramSet("VIDEO.RECORD.VARISPEED.RAMP.RAMP_1.MULTIPLIER",_loc4_);
            if("ON_RECORD" == this.__gpdb.paramGet("VIDEO.RECORD.VARISPEED.RAMP.TRIGGER"))
            {
               this.__gpdb.paramSet("VIDEO.RECORD.VARISPEED.RAMP.ACTIVE","RAMP_1");
            }
            else
            {
               this.__gpdb.paramSet("VIDEO.RECORD.VARISPEED.RAMP.ACTIVE","NONE");
            }
         }
         else
         {
            this.__gpdb.paramSet("VIDEO.RECORD.VARISPEED.RAMP.ACTIVE","NONE");
         }
         this.RequestSystemFrameRate(this.__gpdb.paramGetNumber("GUI.RECORD.VARISPEED.FRAME_RATE"));
      }
      else
      {
         this.__gpdb.paramSet("VIDEO.RECORD.VARISPEED.RAMP.ACTIVE","NONE");
      }
   }
   function RequestSystemFrameRate(fps)
   {
      if(fps == undefined)
      {
         throw new Error("RecordManager::RequestSystemFrameRate() undefined frame rate");
      }
      this.__gpdb.paramSet("VIDEO.RECORD.FRAME_RATE.REQUESTED",fps);
   }
   function PostRecordCleanup()
   {
      if(this.__gpdb.paramGetBoolean("VIDEO.RECORD.VARISPEED.ENABLED"))
      {
         if(this.__gpdb.paramGetBoolean("VIDEO.RECORD.VARISPEED.RAMP.ENABLED"))
         {
            this.RequestSystemFrameRate(this.__gpdb.paramGetNumber("VIDEO.RECORD.FRAME_RATE.ACTUAL"));
            this.RequestSystemFrameRate(this.__gpdb.paramGetNumber("GUI.RECORD.VARISPEED.FRAME_RATE"));
            if("ON_RECORD" == this.__gpdb.paramGet("VIDEO.RECORD.VARISPEED.RAMP.TRIGGER"))
            {
               this.__gpdb.paramSet("VIDEO.RECORD.VARISPEED.RAMP.ACTIVE","RAMP_1");
            }
         }
      }
   }
   function HandleRecordFailure()
   {
      var _loc3_ = this.__gpdb.paramGet("SYSTEM.ERROR.RECORD");
      switch(_loc3_)
      {
         case "":
         case "NONE":
         case "CALCAPTURECOMPLETE":
         case "MEDIA_UNMOUNT_FAULT":
            break;
         default:
            if(!this.__gpdb.paramGetBoolean("VIDEO.RECORD.REQUESTED"))
            {
               _global.VxError("RecordManager::HandleRecordFailure() RECORD_STATE==ERROR while not RECORD_REQUESTED!");
            }
            GUI.OSD_Components.ErrorManagerMC.GetManager().PopupErrorMessage("Record Error:",_loc3_);
      }
      this.__gpdb.paramSet("VIDEO.RECORD.REQUESTED","false");
   }
   function SelectivelyEnableMagnification(enable)
   {
      var _loc4_;
      var _loc3_;
      if(enable)
      {
         _loc4_ = this.__gpdb.paramGetBoolean("VIDEO.RECORD.REQUESTED");
         _loc3_ = this.__gpdb.paramGetBoolean("VIDEO.PLAYBACK.REQUESTED");
         if(_loc3_)
         {
            enable = false;
         }
         else if(_loc4_)
         {
            enable = false;
         }
      }
      this.__gpdb.paramSet("IMAGE_ANALYSIS.MAGNIFICATION.ENABLE",enable);
      return enable;
   }
}
