class GUI.OSD_Components.ButtonManager
{
   var __gpdb;
   var __paramISO;
   var __paramExposure;
   var __paramAudio1;
   var __paramAudio2;
   var __UserMenuA;
   var __UserMenuB;
   var __UserMenuC;
   var __underlayPlot;
   var __overlayPlot;
   var __monitorViewMode;
   var __messagePopup;
   static var __manager;
   var __RAWuserkeyena = 0;
   function ButtonManager()
   {
      _global.VxDebug("...........................................................................CTOR ButtonManager()");
      GUI.OSD_Components.ButtonManager.__manager = this;
      this.__gpdb = _global.gpdb;
      this.__paramISO = this.__gpdb.getParam("GUI.PAINT.EXPOSURE.ISO");
      this.GetAudioParam(1);
      this.GetAudioParam(2);
      if(this.__gpdb.paramGet("GUI.USER_PREF.SHUTTER_SPEED_FORMAT") == "1/SEC")
      {
         this.__paramExposure = this.__gpdb.getParam("GUI.RECORD.SHUTTER_SPEED");
      }
      else
      {
         this.__paramExposure = this.__gpdb.getParam("GUI.RECORD.SHUTTER_SPEED_DEG");
      }
      this.__paramISO.options.SetAndCacheChoices();
      this.__paramAudio1.options.SetAndCacheChoices();
      this.__paramAudio2.options.SetAndCacheChoices();
      this.__paramExposure.options.SetAndCacheChoices();
      this.__UserMenuA = this.__gpdb.paramGet("GUI.KEYMAP.USER_A.MENU");
      this.__UserMenuB = this.__gpdb.paramGet("GUI.KEYMAP.USER_B.MENU");
      this.__UserMenuC = this.__gpdb.paramGet("GUI.KEYMAP.USER_C.MENU");
      this.__gpdb.paramSet("GUI.MONITOR.VIEW_MODE",this.__gpdb.paramGet("VIDEO.MONITOR.VIEW_MODE"));
      this.__gpdb.paramSet("SYSTEM.DEV.MONITOR_HDMI.ENABLE848","HDMI" == this.__gpdb.paramGet("GUI.MONITOR.ACTIVE_DISPLAY"));
      this.__underlayPlot = GUI.OSD_Components.OSD.GetManager().GetUnderlay();
      this.__overlayPlot = GUI.OSD_Components.OSD.GetManager().GetOverlay();
      this.__monitorViewMode = this.__gpdb.paramGet("GUI.MONITOR.VIEW_MODE");
      this.AddGpdbCallbacks();
   }
   function GetAudioParam(ch)
   {
      var _loc2_ = undefined;
      if(ch == 1)
      {
         _loc2_ = "LINE" != this.__gpdb.paramGet("AUDIO.INPUT.CHANNEL_1.SOURCE") ? "AUDIO.INPUT.CHANNEL_1.GAIN.MICROPHONE" : "AUDIO.INPUT.CHANNEL_1.GAIN.LINE";
         this.__paramAudio1 = this.__gpdb.getParam(_loc2_);
      }
      else
      {
         _loc2_ = "LINE" != this.__gpdb.paramGet("AUDIO.INPUT.CHANNEL_2.SOURCE") ? "AUDIO.INPUT.CHANNEL_2.GAIN.MICROPHONE" : "AUDIO.INPUT.CHANNEL_2.GAIN.LINE";
         this.__paramAudio2 = this.__gpdb.getParam(_loc2_);
      }
   }
   static function GetManager()
   {
      if(GUI.OSD_Components.ButtonManager.__manager === undefined)
      {
         _global.VxError("ERROR! ButtonManager::GetManager() called before being instantiated");
      }
      return GUI.OSD_Components.ButtonManager.__manager;
   }
   function AddGpdbCallbacks()
   {
      var _loc6_ = mx.utils.Delegate.create(this,this.Update);
      this.__gpdb.addCallback("GUI.MONITOR.ACTIVE_DISPLAY",_loc6_);
      this.__gpdb.addCallback("GUI.MONITOR.VIEW_MODE",_loc6_);
      this.__gpdb.addCallback("AUDIO.INPUT.CHANNEL_1.SOURCE",_loc6_);
      this.__gpdb.addCallback("AUDIO.INPUT.CHANNEL_2.SOURCE",_loc6_);
      this.__gpdb.addCallback("GUI.USER_PREF.SHUTTER_SPEED_FORMAT",_loc6_);
      var _loc4_ = mx.utils.Delegate.create(this,this.HandleHardKey);
      this.__gpdb.addCallback("GUI.RAWINPUT.BUTTON.RECORD",_loc4_);
      this.__gpdb.addCallback("GUI.RAWINPUT.BUTTON.MENU.SYSTEM",_loc4_);
      this.__gpdb.addCallback("GUI.RAWINPUT.BUTTON.MENU.SYSTEM_LONG",_loc4_);
      this.__gpdb.addCallback("GUI.RAWINPUT.BUTTON.MENU.SENSOR",_loc4_);
      this.__gpdb.addCallback("GUI.RAWINPUT.BUTTON.MENU.VIDEO",_loc4_);
      this.__gpdb.addCallback("GUI.RAWINPUT.BUTTON.USER_DEFINED.SET_A",_loc4_);
      this.__gpdb.addCallback("GUI.RAWINPUT.BUTTON.USER_DEFINED.SET_B",_loc4_);
      this.__gpdb.addCallback("GUI.RAWINPUT.BUTTON.USER_DEFINED.SET_C",_loc4_);
      this.__gpdb.addCallback("SYSTEM.DEV.SUPERGRIP.RAWINPUT.BUTTON.REC",_loc4_);
      var _loc5_ = mx.utils.Delegate.create(this,this.HandleUserKeyEnable);
      this.__gpdb.addCallback("GUI.KEYMAP.USER_D.ENABLED",_loc5_);
      this.__gpdb.addCallback("GUI.KEYMAP.USER_E.ENABLED",_loc5_);
      this.__gpdb.addCallback("GUI.KEYMAP.EVF_B.ENABLED",_loc5_);
      this.__gpdb.addCallback("GUI.KEYMAP.EVF_C.ENABLED",_loc5_);
      this.__gpdb.addCallback("GUI.KEYMAP.LCD_A.ENABLED",_loc5_);
      var _loc3_ = mx.utils.Delegate.create(this,this.HandleMappableKey);
      this.__gpdb.addCallback("GUI.RAWINPUT.BUTTON.SIDE.RECORD",_loc3_);
      this.__gpdb.addCallback("GUI.RAWINPUT.BUTTON.USER_DEFINED.A",_loc3_);
      this.__gpdb.addCallback("GUI.RAWINPUT.BUTTON.USER_DEFINED.B",_loc3_);
      this.__gpdb.addCallback("GUI.RAWINPUT.BUTTON.USER_DEFINED.C",_loc3_);
      this.__gpdb.addCallback("GUI.RAWINPUT.BUTTON.SIDE.USER_DEFINED.D",_loc3_);
      this.__gpdb.addCallback("GUI.RAWINPUT.BUTTON.SIDE.USER_DEFINED.E",_loc3_);
      this.__gpdb.addCallback("SYSTEM.DEV.EVF.RAWINPUT.BUTTON.A",_loc3_);
      this.__gpdb.addCallback("SYSTEM.DEV.EVF.RAWINPUT.BUTTON.B",_loc3_);
      this.__gpdb.addCallback("SYSTEM.DEV.EVF.RAWINPUT.BUTTON.C",_loc3_);
      this.__gpdb.addCallback("SYSTEM.DEV.LCD.RAWINPUT.BUTTON.SW1",_loc3_);
      var _loc2_ = mx.utils.Delegate.create(this,this.HandleComboKey);
      this.__gpdb.addCallback("GUI.RAWINPUT.BUTTON.COMBOKEY.RECORD",_loc2_);
      this.__gpdb.addCallback("GUI.RAWINPUT.BUTTON.COMBOKEY.SYSTEM",_loc2_);
      this.__gpdb.addCallback("GUI.RAWINPUT.BUTTON.COMBOKEY.EXIT",_loc2_);
      this.__gpdb.addCallback("GUI.RAWINPUT.BUTTON.COMBOKEY.USER_A",_loc2_);
      this.__gpdb.addCallback("GUI.RAWINPUT.BUTTON.COMBOKEY.USER_B",_loc2_);
      this.__gpdb.addCallback("GUI.RAWINPUT.BUTTON.COMBOKEY.USER_C",_loc2_);
      this.__gpdb.addCallback("GUI.RAWINPUT.BUTTON.COMBOKEY.USER_D",_loc2_);
      this.__gpdb.addCallback("GUI.RAWINPUT.BUTTON.COMBOKEY.USER_E",_loc2_);
      this.__gpdb.addCallback("GUI.RAWINPUT.BUTTON.COMBOKEY.USER_F",_loc2_);
      this.__gpdb.addCallback("GUI.RAWINPUT.BUTTON.COMBOKEY.USER_G",_loc2_);
      this.__gpdb.addCallback("GUI.RAWINPUT.BUTTON.COMBOKEY.USER_H",_loc2_);
   }
   function Update(param, value)
   {
      var _loc5_ = undefined;
      switch(param)
      {
         case "GUI.MONITOR.ACTIVE_DISPLAY":
            _loc5_ = value == "HDMI";
            this.__gpdb.paramSet("SYSTEM.DEV.MONITOR_HDMI.ENABLE848",_loc5_);
            break;
         case "GUI.MONITOR.VIEW_MODE":
            this.__gpdb.paramSet("VIDEO.MONITOR.VIEW_MODE",value);
            break;
         case "AUDIO.INPUT.CHANNEL_1.GAIN.MICROPHONE":
            _global.VxLog("ButtonManager::Update()Audio channel 1 Mic: " + value);
            break;
         case "AUDIO.INPUT.CHANNEL_1.SOURCE":
            this.GetAudioParam(1);
            break;
         case "AUDIO.INPUT.CHANNEL_2.SOURCE":
            this.GetAudioParam(2);
            break;
         case "GUI.USER_PREF.SHUTTER_SPEED_FORMAT":
            if(value == "1/SEC")
            {
               this.__paramExposure = this.__gpdb.getParam("GUI.RECORD.SHUTTER_SPEED");
            }
            else
            {
               this.__paramExposure = this.__gpdb.getParam("GUI.RECORD.SHUTTER_SPEED_DEG");
            }
            this.__paramExposure.options.SetAndCacheChoices();
            break;
         default:
            _global.VxError("ButtonManager::Update() param not handled: \'" + param + "\'");
      }
   }
   function HandleHardKey(button, value)
   {
      var _loc2_ = value == "true";
      switch(button)
      {
         case "SYSTEM.DEV.SUPERGRIP.RAWINPUT.BUTTON.REC":
         case "GUI.RAWINPUT.BUTTON.RECORD":
            if(_loc2_)
            {
               GUI.OSD_Components.RecordManager.GetManager().HandleRecordRequest();
            }
            break;
         case "GUI.RAWINPUT.BUTTON.MENU.SENSOR":
            if(_loc2_)
            {
               GUI.OSD_Components.MenuManager.GetManager().GotoMenuPanel("Panel_Sensor");
            }
            break;
         case "GUI.RAWINPUT.BUTTON.MENU.VIDEO":
            if(_loc2_)
            {
               GUI.OSD_Components.MenuManager.GetManager().GotoMenuPanel("Panel_AV");
            }
            break;
         case "GUI.RAWINPUT.BUTTON.MENU.SYSTEM":
            if(_loc2_)
            {
               var _loc3_ = GUI.OSD_Components.RecordManager.GetManager().IsRecording();
               if(!_loc3_)
               {
                  GUI.OSD_Components.MenuManager.GetManager().GotoMenuPanel("Panel_System");
               }
            }
            break;
         case "GUI.RAWINPUT.BUTTON.MENU.SYSTEM_LONG":
         case "GUI.RAWINPUT.BUTTON.MENU.SENSOR_LONG":
         case "GUI.RAWINPUT.JOYSTICK.CW":
         case "GUI.RAWINPUT.JOYSTICK.CCW":
         case "GUI.RAWINPUT.JOYSTICK.N":
         case "GUI.RAWINPUT.JOYSTICK.S":
         case "GUI.RAWINPUT.JOYSTICK.E":
         case "GUI.RAWINPUT.JOYSTICK.W":
         case "GUI.RAWINPUT.JOYSTICK.NE":
         case "GUI.RAWINPUT.JOYSTICK.NW":
         case "GUI.RAWINPUT.JOYSTICK.SE":
         case "GUI.RAWINPUT.JOYSTICK.SW":
            break;
         case "GUI.RAWINPUT.BUTTON.USER_DEFINED.SET_A":
            if(_loc2_)
            {
               this.__UserMenuA = GUI.OSD_Components.MenuManager.GetManager().CurrentMenu();
               if(this.__UserMenuA)
               {
                  this.__gpdb.paramSet("GUI.KEYMAP.USER_A.MENU",this.__UserMenuA);
                  this.DisplayMessage("User button A has been assigned to this menu.");
               }
            }
            else
            {
               this.DisplayMessage();
            }
            break;
         case "GUI.RAWINPUT.BUTTON.USER_DEFINED.SET_B":
            if(_loc2_)
            {
               this.__UserMenuB = GUI.OSD_Components.MenuManager.GetManager().CurrentMenu();
               if(this.__UserMenuB)
               {
                  this.__gpdb.paramSet("GUI.KEYMAP.USER_B.MENU",this.__UserMenuB);
                  this.DisplayMessage("User button B has been assigned to this menu.");
               }
            }
            else
            {
               this.DisplayMessage();
            }
            break;
         case "GUI.RAWINPUT.BUTTON.USER_DEFINED.SET_C":
            if(_loc2_)
            {
               this.__UserMenuC = GUI.OSD_Components.MenuManager.GetManager().CurrentMenu();
               if(this.__UserMenuC)
               {
                  this.__gpdb.paramSet("GUI.KEYMAP.USER_C.MENU",this.__UserMenuC);
                  this.DisplayMessage("User button C has been assigned to this menu.");
               }
            }
            else
            {
               this.DisplayMessage();
            }
      }
   }
   function HandleUserKeyEnable(button, value)
   {
      var _loc3_ = value == "true";
      var _loc2_ = "KEYFNC_DISABLED";
      switch(button)
      {
         case "GUI.KEYMAP.USER_D.ENABLED":
            _loc2_ = this.__gpdb.paramGet("GUI.KEYMAP.USER_D.FUNCTION");
            break;
         case "GUI.KEYMAP.USER_E.ENABLED":
            _loc2_ = this.__gpdb.paramGet("GUI.KEYMAP.USER_E.FUNCTION");
            break;
         case "GUI.KEYMAP.EVF_B.ENABLED":
            _loc2_ = this.__gpdb.paramGet("GUI.KEYMAP.EVF_B.FUNCTION");
            break;
         case "GUI.KEYMAP.EVF_C.ENABLED":
            _loc2_ = this.__gpdb.paramGet("GUI.KEYMAP.EVF_C.FUNCTION");
            break;
         case "GUI.KEYMAP.LCD_A.ENABLED":
            _loc2_ = this.__gpdb.paramGet("GUI.KEYMAP.LCD_A.FUNCTION");
      }
      if(!_loc3_)
      {
         this.DoKeyFunction(_loc2_,false);
      }
   }
   function HandleMappableKey(button, value)
   {
      var _loc4_ = value == "true";
      var _loc5_ = false;
      var _loc2_ = "KEYFNC_DISABLED";
      if(_loc4_)
      {
         switch(button)
         {
            case "GUI.RAWINPUT.BUTTON.SIDE.RECORD":
               _loc2_ = this.__gpdb.paramGet("GUI.KEYMAP.SIDE_RECORD.FUNCTION");
               break;
            case "GUI.RAWINPUT.BUTTON.SIDE.USER_DEFINED.D":
               if(this.__gpdb.paramGetBoolean("GUI.KEYMAP.USER_D.ENABLED"))
               {
                  _loc2_ = this.__gpdb.paramGet("GUI.KEYMAP.USER_D.FUNCTION");
               }
               break;
            case "GUI.RAWINPUT.BUTTON.SIDE.USER_DEFINED.E":
               if(this.__gpdb.paramGetBoolean("GUI.KEYMAP.USER_E.ENABLED"))
               {
                  _loc2_ = this.__gpdb.paramGet("GUI.KEYMAP.USER_E.FUNCTION");
               }
               break;
            case "SYSTEM.DEV.EVF.RAWINPUT.BUTTON.A":
               if(this.__gpdb.paramGetBoolean("GUI.KEYMAP.EVF_A.ENABLED"))
               {
                  _loc2_ = this.__gpdb.paramGet("GUI.KEYMAP.EVF_A.FUNCTION");
               }
               break;
            case "SYSTEM.DEV.EVF.RAWINPUT.BUTTON.B":
               if(this.__gpdb.paramGetBoolean("GUI.KEYMAP.EVF_B.ENABLED"))
               {
                  _loc2_ = this.__gpdb.paramGet("GUI.KEYMAP.EVF_B.FUNCTION");
               }
               break;
            case "SYSTEM.DEV.EVF.RAWINPUT.BUTTON.C":
               if(this.__gpdb.paramGetBoolean("GUI.KEYMAP.EVF_C.ENABLED"))
               {
                  _loc2_ = this.__gpdb.paramGet("GUI.KEYMAP.EVF_C.FUNCTION");
               }
               break;
            case "SYSTEM.DEV.LCD.RAWINPUT.BUTTON.SW1":
               if(this.__gpdb.paramGetBoolean("GUI.KEYMAP.LCD_A.ENABLED"))
               {
                  _loc2_ = this.__gpdb.paramGet("GUI.KEYMAP.LCD_A.FUNCTION");
               }
         }
      }
      else
      {
         switch(button)
         {
            case "GUI.RAWINPUT.BUTTON.USER_DEFINED.A":
               _loc2_ = "KEYFNC_GOTO_MENU_A";
               break;
            case "GUI.RAWINPUT.BUTTON.USER_DEFINED.B":
               _loc2_ = "KEYFNC_GOTO_MENU_B";
               break;
            case "GUI.RAWINPUT.BUTTON.USER_DEFINED.C":
               _loc2_ = "KEYFNC_GOTO_MENU_C";
         }
      }
      if(_loc2_ != "KEYFNC_DISABLED")
      {
         this.DoKeyFunction(_loc2_,true);
      }
   }
   function DoKeyFunction(keyFunction, isKeyEnabled)
   {
      var _loc2_ = undefined;
      var _loc3_ = undefined;
      var _loc4_ = undefined;
      switch(keyFunction)
      {
         case "KEYFNC_MULTI":
            this.UserKeyMulti();
            break;
         case "KEYFNC_UNMOUNT_MEDIA":
            GUI.OSD_Components.MediaManager.GetManager().Unmount();
            break;
         case "KEYFNC_RECORD":
            if(this.__gpdb.paramGetBoolean("GUI.KEYMAP.SIDE_RECORD.ENABLED"))
            {
               this.RequestRecord();
            }
            break;
         case "KEYFNC_TOGGLE_RECORD":
            if(isKeyEnabled)
            {
               this.RequestRecord();
            }
            break;
         case "KEYFNC_GOTO_MENU_A":
            GUI.OSD_Components.MenuManager.GetManager().GotoMenuPanel(this.__UserMenuA);
            break;
         case "KEYFNC_GOTO_MENU_B":
            GUI.OSD_Components.MenuManager.GetManager().GotoMenuPanel(this.__UserMenuB);
            break;
         case "KEYFNC_GOTO_MENU_C":
            GUI.OSD_Components.MenuManager.GetManager().GotoMenuPanel(this.__UserMenuC);
            break;
         case "KEYFNC_DO_AUTO_WHITE_BALANCE":
            this.__gpdb.paramSet("GUI.PAINT.WHITE_BALANCE.AUTO","true");
            this.__gpdb.paramSet("GUI.PAINT.AUTO.WBAL.CLEAR",1);
            this.__gpdb.paramSet("PAINT.SLAVE.WHITE_BALANCE.CURRENT",0);
            this.__gpdb.paramSet("PAINT.SLAVE.TINT.CURRENT",0);
            break;
         case "KEYFNC_DO_RAMP":
            GUI.OSD_Components.RecordManager.GetManager().HandleRampRequest();
            break;
         case "KEYFNC_DO_BURST":
            GUI.OSD_Components.RecordManager.GetManager().HandleBurstRequest();
            break;
         case "KEYFNC_TOGGLE_MAGNIFICATION":
            if(isKeyEnabled)
            {
               var _loc7_ = this.__gpdb.paramGetBoolean("IMAGE_ANALYSIS.MAGNIFICATION.ENABLE");
               GUI.OSD_Components.RecordManager.GetManager().SelectivelyEnableMagnification(!_loc7_);
            }
            else
            {
               GUI.OSD_Components.RecordManager.GetManager().SelectivelyEnableMagnification(false);
            }
            break;
         case "KEYFNC_TOGGLE_COLOR":
            if(isKeyEnabled)
            {
               var _loc8_ = this.__gpdb.paramGetBoolean("GUI.MONITOR.OUTPUT_EFFECTS.ENABLED");
               this.__gpdb.paramSet("GUI.MONITOR.OUTPUT_EFFECTS.ENABLED",!_loc8_);
            }
            else
            {
               this.__gpdb.paramSet("GUI.MONITOR.OUTPUT_EFFECTS.ENABLED",false);
            }
            break;
         case "KEYFNC_TOGGLE_METER":
            if(isKeyEnabled)
            {
               _loc8_ = this.__gpdb.paramGetBoolean("GUI.SOFTKEY.IMAGE_ANALYSIS.ASSIST_METER_ENABLED");
               this.__gpdb.paramSet("GUI.SOFTKEY.IMAGE_ANALYSIS.ASSIST_METER_ENABLED",!_loc8_);
            }
            else
            {
               this.__gpdb.paramSet("GUI.SOFTKEY.IMAGE_ANALYSIS.ASSIST_METER_ENABLED",false);
            }
            break;
         case "KEYFNC_TOGGLE_VIEW_RAW":
            if(isKeyEnabled)
            {
               var _loc9_ = "Raw" == this.__gpdb.paramGet("GUI.MONITOR.VIEW_MODE");
               if(_loc9_)
               {
                  if(this.__RAWuserkeyena == 1)
                  {
                     this.__RAWuserkeyena = 0;
                     this.__gpdb.paramSet("GUI.MONITOR.VIEW_MODE",this.__monitorViewMode);
                  }
                  else
                  {
                     this.__gpdb.paramSet("VIDEO.MONITOR.VIEW_MODE",this.__gpdb.paramGet("GUI.MONITOR.VIEW_MODE"));
                  }
               }
               else
               {
                  this.__RAWuserkeyena = 1;
                  this.__monitorViewMode = this.__gpdb.paramGet("GUI.MONITOR.VIEW_MODE");
                  this.__gpdb.paramSet("GUI.MONITOR.VIEW_MODE","Raw");
               }
            }
            else if(this.__RAWuserkeyena == 1)
            {
               this.__RAWuserkeyena = 0;
               this.__gpdb.paramSet("GUI.MONITOR.VIEW_MODE",this.__monitorViewMode);
            }
            else
            {
               this.__gpdb.paramSet("VIDEO.MONITOR.VIEW_MODE",this.__gpdb.paramGet("GUI.MONITOR.VIEW_MODE"));
            }
            break;
         case "KEYFNC_TOGGLE_ZEBRA_1":
            if(isKeyEnabled)
            {
               var _loc6_ = this.__gpdb.paramGetBoolean("SYSTEM.DEV.EVF.ZEBRA.1_ENABLE");
               this.__gpdb.paramSet("SYSTEM.DEV.EVF.ZEBRA.1_ENABLE",!_loc6_);
            }
            else
            {
               this.__gpdb.paramSet("SYSTEM.DEV.EVF.ZEBRA.1_ENABLE",false);
            }
            break;
         case "KEYFNC_TOGGLE_ZEBRA_2":
            if(isKeyEnabled)
            {
               _loc6_ = this.__gpdb.paramGetBoolean("SYSTEM.DEV.EVF.ZEBRA.2_ENABLE");
               this.__gpdb.paramSet("SYSTEM.DEV.EVF.ZEBRA.2_ENABLE",!_loc6_);
            }
            else
            {
               this.__gpdb.paramSet("SYSTEM.DEV.EVF.ZEBRA.2_ENABLE",false);
            }
            break;
         case "KEYFNC_INC_AUDIO_1":
            _loc3_ = "LINE" != this.__gpdb.paramGet("AUDIO.INPUT.CHANNEL_1.SOURCE") ? "AUDIO.INPUT.CHANNEL_1.GAIN.MICROPHONE" : "AUDIO.INPUT.CHANNEL_1.GAIN.LINE";
            _loc4_ = this.__gpdb.getParam(_loc3_);
            _loc2_ = _loc4_.options.SelectNext(1);
            break;
         case "KEYFNC_DEC_AUDIO_1":
            _loc3_ = "LINE" != this.__gpdb.paramGet("AUDIO.INPUT.CHANNEL_1.SOURCE") ? "AUDIO.INPUT.CHANNEL_1.GAIN.MICROPHONE" : "AUDIO.INPUT.CHANNEL_1.GAIN.LINE";
            _loc4_ = this.__gpdb.getParam(_loc3_);
            _loc2_ = _loc4_.options.SelectPrev(1);
            break;
         case "KEYFNC_INC_AUDIO_2":
            _loc3_ = "LINE" != this.__gpdb.paramGet("AUDIO.INPUT.CHANNEL_2.SOURCE") ? "AUDIO.INPUT.CHANNEL_2.GAIN.MICROPHONE" : "AUDIO.INPUT.CHANNEL_2.GAIN.LINE";
            _loc4_ = this.__gpdb.getParam(_loc3_);
            _loc2_ = _loc4_.options.SelectNext(1);
            break;
         case "KEYFNC_DEC_AUDIO_2":
            _loc3_ = "LINE" != this.__gpdb.paramGet("AUDIO.INPUT.CHANNEL_2.SOURCE") ? "AUDIO.INPUT.CHANNEL_2.GAIN.MICROPHONE" : "AUDIO.INPUT.CHANNEL_2.GAIN.LINE";
            _loc4_ = this.__gpdb.getParam(_loc3_);
            _loc2_ = _loc4_.options.SelectPrev(1);
            break;
         case "KEYFNC_INC_ISO":
            _loc2_ = this.__paramISO.options.SelectNext(1);
            if(!_loc2_)
            {
               this.__paramISO.options.SelectFirst();
            }
            break;
         case "KEYFNC_DEC_ISO":
            _loc2_ = this.__paramISO.options.SelectPrev(1);
            if(!_loc2_)
            {
               this.__paramISO.options.SelectLast();
            }
            break;
         case "KEYFNC_INC_SHUTTER_SPEED":
            _loc2_ = this.__paramExposure.options.SelectNext(1);
            if(!_loc2_)
            {
               this.__paramExposure.options.SelectFirst();
            }
            break;
         case "KEYFNC_DEC_SHUTTER_SPEED":
            _loc2_ = this.__paramExposure.options.SelectPrev(1);
            if(!_loc2_)
            {
               this.__paramExposure.options.SelectLast();
            }
            break;
         case "KEYFNC_DISABLED":
      }
   }
   function UserKeyMulti()
   {
      var _loc3_ = this.__gpdb.paramGet("GUI.SOFTKEY.USER_KEY.MULTI");
      var _loc2_ = Number(_loc3_);
      switch(_loc2_)
      {
         case 0:
         case 1:
         case 2:
            _loc2_ += 1;
            break;
         case 3:
         default:
            _loc2_ = 0;
      }
      this.__gpdb.paramSet("GUI.SOFTKEY.USER_KEY.MULTI",_loc2_);
   }
   function RequestRecord()
   {
      var _loc2_ = this.__gpdb.paramGet("VIDEO.RECORD.MODE");
      switch(_loc2_)
      {
         case "BURST":
            GUI.OSD_Components.RecordManager.GetManager().HandleBurstRequest();
            break;
         case "CONTINUOUS":
         case "TIMELAPSE":
         default:
            GUI.OSD_Components.RecordManager.GetManager().HandleRecordRequest();
      }
   }
   function DisplayMessage(msg)
   {
      this.__messagePopup = GUI.OSD_Components.OSD.GetManager().GetMessagePopup();
      if(msg && msg != "")
      {
         this.__messagePopup.MESSAGE.text = msg;
         this.__messagePopup._visible = true;
      }
      else
      {
         this.__messagePopup._visible = false;
      }
   }
   function HandleComboKey(param, value)
   {
      var _loc2_ = value == "true";
      switch(param)
      {
         case "GUI.RAWINPUT.BUTTON.COMBOKEY.RECORD":
            if(_loc2_)
            {
               GUI.OSD_Components.RecordManager.GetManager().HandlePreRecordRequest();
            }
            break;
         case "GUI.RAWINPUT.BUTTON.COMBOKEY.EXIT":
            if(_loc2_)
            {
               GUI.OSD_Components.MediaManager.GetManager().Unmount();
            }
            break;
         case "GUI.RAWINPUT.BUTTON.COMBOKEY.SYSTEM":
            if(_loc2_)
            {
               GUI.OSD_Components.MenuManager.GetManager().ReturnToLastMenu();
            }
            break;
         case "GUI.RAWINPUT.BUTTON.COMBOKEY.SENSOR":
         case "GUI.RAWINPUT.BUTTON.COMBOKEY.VIDEO":
         case "GUI.RAWINPUT.BUTTON.COMBOKEY.USER_A":
         case "GUI.RAWINPUT.BUTTON.COMBOKEY.USER_B":
         case "GUI.RAWINPUT.BUTTON.COMBOKEY.USER_C":
            break;
         case "GUI.RAWINPUT.BUTTON.COMBOKEY.USER_G":
            if(_loc2_)
            {
               var _loc3_ = undefined;
               _loc3_ = this.__gpdb.paramGet("GUI.MONITOR.ACTIVE_DISPLAY");
               if(_loc3_ == "HD-SDI")
               {
                  this.__gpdb.paramSet("GUI.MONITOR.ACTIVE_DISPLAY","HDMI");
               }
               else
               {
                  this.__gpdb.paramSet("GUI.MONITOR.ACTIVE_DISPLAY","HD-SDI");
               }
            }
            break;
         case "GUI.RAWINPUT.BUTTON.COMBOKEY.USER_F":
            if(_loc2_ && this.__gpdb.paramGetBoolean("SYSTEM.DEV.LCD.ENABLED"))
            {
               if("false" == this.__gpdb.paramGet("SYSTEM.DEV.LCD.ENABLE54SCALING"))
               {
                  this.__gpdb.paramSet("SYSTEM.DEV.LCD.ENABLE54SCALING","true");
               }
               else
               {
                  this.__gpdb.paramSet("SYSTEM.DEV.LCD.ENABLE54SCALING","false");
               }
            }
            break;
         case "GUI.RAWINPUT.BUTTON.COMBOKEY.USER_D":
         case "GUI.RAWINPUT.BUTTON.COMBOKEY.USER_E":
            break;
         case "GUI.RAWINPUT.BUTTON.COMBOKEY.USER_H":
            if(_loc2_)
            {
               GUI.OSD_Components.MenuManager.GetManager().GotoMenuPanel("Panel_Developer");
            }
      }
   }
   function handleOnKeyDown()
   {
      var _loc2_ = Key.getCode();
      if(Key.isDown(27))
      {
         GUI.OSD_Components.MenuManager.GetManager().PopMenuPanel();
      }
      if(Key.getCode() == 77)
      {
      }
      if(Key.getCode() == 67)
      {
      }
      if(Key.getCode() == 68)
      {
         this.__gpdb.dump();
      }
   }
}
