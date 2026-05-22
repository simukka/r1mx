class GUI.OSD_Components.GpioManager
{
   var __gpdb;
   var __AUTOWBdelay;
   var __AUTOWBdelay1;
   static var __manager;
   function GpioManager()
   {
      _global.VxDebug("...........................................................................CTOR GpioManager()");
      GUI.OSD_Components.GpioManager.__manager = this;
      this.__gpdb = _global.gpdb;
      this.FlagRecordActive(false);
      this.AddCallbacks();
   }
   static function GetManager()
   {
      if(GUI.OSD_Components.GpioManager.__manager === undefined)
      {
         _global.VxError("GpioManager::GetManager() called before being instantiated");
      }
      return GUI.OSD_Components.GpioManager.__manager;
   }
   function AddCallbacks()
   {
      var _loc2_ = mx.utils.Delegate.create(this,this.Update);
      this.__gpdb.addCallback("SYSTEM.DEV.GPIO.SETTING.INPUT_1",_loc2_);
      this.__gpdb.addCallback("SYSTEM.DEV.GPIO.SETTING.INPUT_2",_loc2_);
      this.__gpdb.addCallback("SYSTEM.DEV.GPIO.CONFIG.INPUT_1.POLARITY",_loc2_);
      this.__gpdb.addCallback("SYSTEM.DEV.GPIO.CONFIG.INPUT_2.POLARITY",_loc2_);
      this.__gpdb.addCallback("SYSTEM.DEV.GPIO.CONFIG.OUTPUT_1.POLARITY",_loc2_);
      this.__gpdb.addCallback("SYSTEM.DEV.GPIO.CONFIG.OUTPUT_2.POLARITY",_loc2_);
      this.__gpdb.addCallback("VIDEO.PLAYBACK.REQUESTED",_loc2_);
      this.__gpdb.addCallback("GUI.PAINT.WHITE_BALANCE.AUTO",_loc2_);
      this.__gpdb.addCallback("VIDEO.RECORD.ACK",_loc2_);
   }
   function Update(name, value)
   {
      switch(name)
      {
         case "SYSTEM.DEV.GPIO.SETTING.INPUT_1":
            this.HandleGpio(1,value == "true");
            break;
         case "SYSTEM.DEV.GPIO.SETTING.INPUT_2":
            this.HandleGpio(2,value == "true");
            break;
         case "SYSTEM.DEV.GPIO.CONFIG.INPUT_1.POLARITY":
         case "SYSTEM.DEV.GPIO.CONFIG.INPUT_2.POLARITY":
            break;
         case "SYSTEM.DEV.GPIO.CONFIG.OUTPUT_1.POLARITY":
         case "SYSTEM.DEV.GPIO.CONFIG.OUTPUT_2.POLARITY":
            this.FlagRecordActive("true" == this.__gpdb.paramGet("VIDEO.RECORD.ACK"));
            break;
         case "VIDEO.RECORD.ACK":
            this.FlagRecordActive(value == "true");
            break;
         case "VIDEO.PLAYBACK.REQUESTED":
            this.FlagPlaybackActive(value == "true");
            break;
         case "GUI.PAINT.WHITE_BALANCE.AUTO":
            this.FlagPlaybackActive(value == "true");
      }
   }
   function HandleGpio(channel, trigger)
   {
      if(trigger)
      {
         var _loc3_ = "NONE";
         switch(channel)
         {
            case 1:
               _loc3_ = this.__gpdb.paramGet("SYSTEM.DEV.GPIO.CONFIG.INPUT_1.MAPPED_FUNCTION");
               break;
            case 2:
               _loc3_ = this.__gpdb.paramGet("SYSTEM.DEV.GPIO.CONFIG.INPUT_2.MAPPED_FUNCTION");
               break;
            default:
               _loc3_ = "NONE";
         }
         switch(_loc3_)
         {
            case "NONE":
               _global.VxError("GpioManager::HandleGpio(" + channel + ", " + trigger + ") No mapped function!");
               break;
            case "RECORD":
               GUI.OSD_Components.RecordManager.GetManager().HandleRecordRequest();
               break;
            case "AUTO_WB":
               this.__gpdb.paramSet("GUI.PAINT.WHITE_BALANCE.AUTO","true");
               this.__gpdb.paramSet("GUI.PAINT.AUTO.WBAL.CLEAR",1);
               this.__gpdb.paramSet("PAINT.SLAVE.WHITE_BALANCE.CURRENT",0);
               this.__gpdb.paramSet("PAINT.SLAVE.TINT.CURRENT",0);
               break;
            case "MAGNIFY":
               if(this.__gpdb.paramGetBoolean("IMAGE_ANALYSIS.MAGNIFICATION.ENABLE"))
               {
                  GUI.OSD_Components.RecordManager.GetManager().SelectivelyEnableMagnification(false);
               }
               else
               {
                  GUI.OSD_Components.RecordManager.GetManager().SelectivelyEnableMagnification(true);
               }
               break;
            case "PRE_RECORD":
               this.__gpdb.paramSet("GUI.RECORD.PRERECORD.ENABLED",true);
               GUI.OSD_Components.RecordManager.GetManager().HandlePreRecordRequest();
               break;
            case "BURST":
               GUI.OSD_Components.RecordManager.GetManager().HandleBurstRequest();
               GUI.OSD_Components.HudLowerMC.GetManager().RefreshDisplay();
               break;
            case "RAMP":
               GUI.OSD_Components.RecordManager.GetManager().HandleRampRequest();
               break;
            case "SHUT_DOWN":
               this.__gpdb.paramSet("SYSTEM.RUNLEVEL.REQUESTED","SHUTDOWN");
               break;
            case "PLAY_CLIP":
               GUI.OSD_Components.PlaybackPanel.GetManager().HandlePlayClipRequest();
               break;
            case "NEXT_CLIP":
               GUI.OSD_Components.PlaybackPanel.GetManager().HandleNextClipRequest();
               break;
            case "FALSE_COLOR":
               if(this.__gpdb.paramGetBoolean("GUI.MONITOR.OUTPUT_EFFECTS.ENABLED"))
               {
                  this.__gpdb.paramSet("GUI.MONITOR.OUTPUT_EFFECTS.ENABLED","false");
               }
               else
               {
                  this.__gpdb.paramSet("GUI.MONITOR.OUTPUT_EFFECTS.ENABLED","true");
               }
               break;
            default:
               _global.VxError("GpioManager::HandleGpio() Unimplemented function \'" + _loc3_ + "!");
         }
      }
   }
   function FlagRecordActive(active)
   {
      if("RECORDING" == this.__gpdb.paramGet("SYSTEM.DEV.GPIO.CONFIG.OUTPUT_1.TRIGGER"))
      {
         this.__gpdb.paramSet("SYSTEM.DEV.GPIO.SETTING.OUTPUT_1",active);
      }
      if("RECORDING" == this.__gpdb.paramGet("SYSTEM.DEV.GPIO.CONFIG.OUTPUT_2.TRIGGER"))
      {
         this.__gpdb.paramSet("SYSTEM.DEV.GPIO.SETTING.OUTPUT_2",active);
      }
   }
   function FlagPlaybackActive(active)
   {
      if("AUTO_WB" == this.__gpdb.paramGet("SYSTEM.DEV.GPIO.CONFIG.OUTPUT_1.TRIGGER"))
      {
         this.__gpdb.paramSet("SYSTEM.DEV.GPIO.SETTING.OUTPUT_1",active);
         this.__AUTOWBdelay = setInterval(this,"wait",1000);
      }
      if("AUTO_WB" == this.__gpdb.paramGet("SYSTEM.DEV.GPIO.CONFIG.OUTPUT_2.TRIGGER"))
      {
         this.__gpdb.paramSet("SYSTEM.DEV.GPIO.SETTING.OUTPUT_2",active);
         this.__AUTOWBdelay1 = setInterval(this,"wait1",1000);
      }
      if("PLAYING" == this.__gpdb.paramGet("SYSTEM.DEV.GPIO.CONFIG.OUTPUT_1.TRIGGER"))
      {
         this.__gpdb.paramSet("SYSTEM.DEV.GPIO.SETTING.OUTPUT_1",active);
      }
      if("PLAYING" == this.__gpdb.paramGet("SYSTEM.DEV.GPIO.CONFIG.OUTPUT_2.TRIGGER"))
      {
         this.__gpdb.paramSet("SYSTEM.DEV.GPIO.SETTING.OUTPUT_2",active);
      }
      if("CUED" == this.__gpdb.paramGet("SYSTEM.DEV.GPIO.CONFIG.OUTPUT_1.TRIGGER"))
      {
         this.__gpdb.paramSet("SYSTEM.DEV.GPIO.SETTING.OUTPUT_1",active);
      }
      if("CUED" == this.__gpdb.paramGet("SYSTEM.DEV.GPIO.CONFIG.OUTPUT_2.TRIGGER"))
      {
         this.__gpdb.paramSet("SYSTEM.DEV.GPIO.SETTING.OUTPUT_2",active);
      }
   }
   function wait()
   {
      clearInterval(this.__AUTOWBdelay);
      this.__gpdb.paramSet("SYSTEM.DEV.GPIO.SETTING.OUTPUT_1","false");
   }
   function wait1()
   {
      clearInterval(this.__AUTOWBdelay1);
      this.__gpdb.paramSet("SYSTEM.DEV.GPIO.SETTING.OUTPUT_2","false");
   }
}
