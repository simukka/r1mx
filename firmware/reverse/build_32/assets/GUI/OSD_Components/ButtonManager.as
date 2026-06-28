class GUI.OSD_Components.ButtonManager
{
   var __UserMenuA;
   var __UserMenuB;
   var __UserMenuC;
   var __gpdb;
   var __messagePopup;
   var __overlayPlot;
   var __paramAudio1;
   var __paramAudio2;
   var __paramExposure;
   var __paramISO;
   var __underlayPlot;
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
      this.AddGpdbCallbacks();
   }
   function GetAudioParam(ch)
   {
      var _loc2_;
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
      var _loc5_;
      switch(param)
      {
         case "GUI.MONITOR.ACTIVE_DISPLAY":
            _loc5_ = value == "HDMI";
            this.__gpdb.paramSet("SYSTEM.DEV.MONITOR_HDMI.ENABLE848",_loc5_);
            return;
         case "GUI.MONITOR.VIEW_MODE":
            this.__gpdb.paramSet("VIDEO.MONITOR.VIEW_MODE",value);
            return;
         case "AUDIO.INPUT.CHANNEL_1.GAIN.MICROPHONE":
            _global.VxLog("ButtonManager::Update()Audio channel 1 Mic: " + value);
            return;
         case "AUDIO.INPUT.CHANNEL_1.SOURCE":
            this.GetAudioParam(1);
            return;
         case "AUDIO.INPUT.CHANNEL_2.SOURCE":
            this.GetAudioParam(2);
            return;
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
            return;
         default:
            _global.VxError("ButtonManager::Update() param not handled: \'" + param + "\'");
            return;
      }
   }
   function HandleHardKey(button, value)
   {
      var _loc2_ = value == "true";
      var _loc3_;
      switch(button)
      {
         case "SYSTEM.DEV.SUPERGRIP.RAWINPUT.BUTTON.REC":
         case "GUI.RAWINPUT.BUTTON.RECORD":
            if(_loc2_)
            {
               GUI.OSD_Components.RecordManager.GetManager().HandleRecordRequest();
            }
            return;
         case "GUI.RAWINPUT.BUTTON.MENU.SENSOR":
            if(_loc2_)
            {
               GUI.OSD_Components.MenuManager.GetManager().GotoMenuPanel("Panel_Sensor");
            }
            return;
         case "GUI.RAWINPUT.BUTTON.MENU.VIDEO":
            if(_loc2_)
            {
               GUI.OSD_Components.MenuManager.GetManager().GotoMenuPanel("Panel_AV");
            }
            return;
         case "GUI.RAWINPUT.BUTTON.MENU.SYSTEM":
            if(_loc2_)
            {
               _loc3_ = GUI.OSD_Components.RecordManager.GetManager().IsRecording();
               if(!_loc3_)
               {
                  GUI.OSD_Components.MenuManager.GetManager().GotoMenuPanel("Panel_System");
               }
            }
            return;
         case "GUI.RAWINPUT.BUTTON.MENU.SYSTEM_LONG":
            return;
         case "GUI.RAWINPUT.BUTTON.MENU.SENSOR_LONG":
            return;
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
            return;
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
            return;
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
            return;
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
            return;
         default:
            return;
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
      var _loc2_;
      var _loc3_;
      var _loc4_;
      var _loc7_;
      var _loc8_;
      var _loc9_;
      var _loc6_;
      switch(keyFunction)
      {
         case "KEYFNC_MULTI":
            this.UserKeyMulti();
            return;
         case "KEYFNC_UNMOUNT_MEDIA":
            GUI.OSD_Components.MediaManager.GetManager().Unmount();
            return;
         case "KEYFNC_RECORD":
            if(this.__gpdb.paramGetBoolean("GUI.KEYMAP.SIDE_RECORD.ENABLED"))
            {
               this.RequestRecord();
            }
            return;
         case "KEYFNC_TOGGLE_RECORD":
            if(isKeyEnabled)
            {
               this.RequestRecord();
            }
            return;
         case "KEYFNC_GOTO_MENU_A":
            GUI.OSD_Components.MenuManager.GetManager().GotoMenuPanel(this.__UserMenuA);
            return;
         case "KEYFNC_GOTO_MENU_B":
            GUI.OSD_Components.MenuManager.GetManager().GotoMenuPanel(this.__UserMenuB);
            return;
         case "KEYFNC_GOTO_MENU_C":
            GUI.OSD_Components.MenuManager.GetManager().GotoMenuPanel(this.__UserMenuC);
            return;
         case "KEYFNC_DO_AUTO_WHITE_BALANCE":
            this.__gpdb.paramSet("GUI.PAINT.WHITE_BALANCE.AUTO","true");
            this.__gpdb.paramSet("GUI.PAINT.AUTO.WBAL.CLEAR",1);
            this.__gpdb.paramSet("PAINT.SLAVE.WHITE_BALANCE.CURRENT",0);
            this.__gpdb.paramSet("PAINT.SLAVE.TINT.CURRENT",0);
            return;
         case "KEYFNC_DO_RAMP":
            GUI.OSD_Components.RecordManager.GetManager().HandleRampRequest();
            return;
         case "KEYFNC_DO_BURST":
            GUI.OSD_Components.RecordManager.GetManager().HandleBurstRequest();
            return;
         case "KEYFNC_TOGGLE_MAGNIFICATION":
            if(isKeyEnabled)
            {
               _loc7_ = this.__gpdb.paramGetBoolean("IMAGE_ANALYSIS.MAGNIFICATION.ENABLE");
               GUI.OSD_Components.RecordManager.GetManager().SelectivelyEnableMagnification(!_loc7_);
            }
            else
            {
               GUI.OSD_Components.RecordManager.GetManager().SelectivelyEnableMagnification(false);
            }
            return;
         case "KEYFNC_TOGGLE_COLOR":
            if(isKeyEnabled)
            {
               _loc8_ = this.__gpdb.paramGetBoolean("GUI.MONITOR.OUTPUT_EFFECTS.ENABLED");
               this.__gpdb.paramSet("GUI.MONITOR.OUTPUT_EFFECTS.ENABLED",!_loc8_);
            }
            else
            {
               this.__gpdb.paramSet("GUI.MONITOR.OUTPUT_EFFECTS.ENABLED",false);
            }
            return;
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
            return;
         case "KEYFNC_TOGGLE_VIEW_RAW":
            if(isKeyEnabled)
            {
               _loc9_ = "Raw" == this.__gpdb.paramGet("GUI.MONITOR.VIEW_MODE");
               if(_loc9_)
               {
                  if(this.__RAWuserkeyena == 1)
                  {
                     this.__RAWuserkeyena = 0;
                     this.__gpdb.paramSet("GUI.MONITOR.VIEW_MODE","REDcolor");
                  }
                  else
                  {
                     this.__gpdb.paramSet("VIDEO.MONITOR.VIEW_MODE",this.__gpdb.paramGet("GUI.MONITOR.VIEW_MODE"));
                  }
               }
               else
               {
                  this.__RAWuserkeyena = 1;
                  this.__gpdb.paramSet("GUI.MONITOR.VIEW_MODE","Raw");
               }
            }
            else if(this.__RAWuserkeyena == 1)
            {
               this.__RAWuserkeyena = 0;
               this.__gpdb.paramSet("GUI.MONITOR.VIEW_MODE","REDcolor");
            }
            else
            {
               this.__gpdb.paramSet("VIDEO.MONITOR.VIEW_MODE",this.__gpdb.paramGet("GUI.MONITOR.VIEW_MODE"));
            }
            return;
         case "KEYFNC_TOGGLE_ZEBRA_1":
            if(isKeyEnabled)
            {
               _loc6_ = this.__gpdb.paramGetBoolean("SYSTEM.DEV.EVF.ZEBRA.1_ENABLE");
               this.__gpdb.paramSet("SYSTEM.DEV.EVF.ZEBRA.1_ENABLE",!_loc6_);
            }
            else
            {
               this.__gpdb.paramSet("SYSTEM.DEV.EVF.ZEBRA.1_ENABLE",false);
            }
            return;
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
            return;
         case "KEYFNC_INC_AUDIO_1":
            _loc3_ = "LINE" != this.__gpdb.paramGet("AUDIO.INPUT.CHANNEL_1.SOURCE") ? "AUDIO.INPUT.CHANNEL_1.GAIN.MICROPHONE" : "AUDIO.INPUT.CHANNEL_1.GAIN.LINE";
            _loc4_ = this.__gpdb.getParam(_loc3_);
            _loc2_ = _loc4_.options.SelectNext(1);
            return;
         case "KEYFNC_DEC_AUDIO_1":
            _loc3_ = "LINE" != this.__gpdb.paramGet("AUDIO.INPUT.CHANNEL_1.SOURCE") ? "AUDIO.INPUT.CHANNEL_1.GAIN.MICROPHONE" : "AUDIO.INPUT.CHANNEL_1.GAIN.LINE";
            _loc4_ = this.__gpdb.getParam(_loc3_);
            _loc2_ = _loc4_.options.SelectPrev(1);
            return;
         case "KEYFNC_INC_AUDIO_2":
            _loc3_ = "LINE" != this.__gpdb.paramGet("AUDIO.INPUT.CHANNEL_2.SOURCE") ? "AUDIO.INPUT.CHANNEL_2.GAIN.MICROPHONE" : "AUDIO.INPUT.CHANNEL_2.GAIN.LINE";
            _loc4_ = this.__gpdb.getParam(_loc3_);
            _loc2_ = _loc4_.options.SelectNext(1);
            return;
         case "KEYFNC_DEC_AUDIO_2":
            _loc3_ = "LINE" != this.__gpdb.paramGet("AUDIO.INPUT.CHANNEL_2.SOURCE") ? "AUDIO.INPUT.CHANNEL_2.GAIN.MICROPHONE" : "AUDIO.INPUT.CHANNEL_2.GAIN.LINE";
            _loc4_ = this.__gpdb.getParam(_loc3_);
            _loc2_ = _loc4_.options.SelectPrev(1);
            return;
         case "KEYFNC_INC_ISO":
            _loc2_ = this.__paramISO.options.SelectNext(1);
            if(!_loc2_)
            {
               this.__paramISO.options.SelectFirst();
            }
            return;
         case "KEYFNC_DEC_ISO":
            _loc2_ = this.__paramISO.options.SelectPrev(1);
            if(!_loc2_)
            {
               this.__paramISO.options.SelectLast();
            }
            return;
         case "KEYFNC_INC_SHUTTER_SPEED":
            _loc2_ = this.__paramExposure.options.SelectNext(1);
            if(!_loc2_)
            {
               this.__paramExposure.options.SelectFirst();
            }
            return;
         case "KEYFNC_DEC_SHUTTER_SPEED":
            _loc2_ = this.__paramExposure.options.SelectPrev(1);
            if(!_loc2_)
            {
               this.__paramExposure.options.SelectLast();
            }
            return;
         case "KEYFNC_DISABLED":
         default:
            return;
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
            return;
         case "CONTINUOUS":
         case "TIMELAPSE":
         default:
            GUI.OSD_Components.RecordManager.GetManager().HandleRecordRequest();
            return;
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
      var _loc3_;
      switch(param)
      {
         case "GUI.RAWINPUT.BUTTON.COMBOKEY.RECORD":
            if(_loc2_)
            {
               GUI.OSD_Components.RecordManager.GetManager().HandlePreRecordRequest();
            }
            return;
         case "GUI.RAWINPUT.BUTTON.COMBOKEY.EXIT":
            if(_loc2_)
            {
               GUI.OSD_Components.MediaManager.GetManager().Unmount();
            }
            return;
         case "GUI.RAWINPUT.BUTTON.COMBOKEY.SYSTEM":
            if(_loc2_)
            {
               GUI.OSD_Components.MenuManager.GetManager().ReturnToLastMenu();
            }
            return;
         case "GUI.RAWINPUT.BUTTON.COMBOKEY.SENSOR":
         case "GUI.RAWINPUT.BUTTON.COMBOKEY.VIDEO":
            return;
         case "GUI.RAWINPUT.BUTTON.COMBOKEY.USER_A":
            return;
         case "GUI.RAWINPUT.BUTTON.COMBOKEY.USER_B":
            return;
         case "GUI.RAWINPUT.BUTTON.COMBOKEY.USER_C":
            return;
         case "GUI.RAWINPUT.BUTTON.COMBOKEY.USER_G":
            if(_loc2_)
            {
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
            return;
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
            return;
         case "GUI.RAWINPUT.BUTTON.COMBOKEY.USER_D":
            return;
         case "GUI.RAWINPUT.BUTTON.COMBOKEY.USER_E":
            return;
         case "GUI.RAWINPUT.BUTTON.COMBOKEY.USER_H":
            if(_loc2_)
            {
               GUI.OSD_Components.MenuManager.GetManager().GotoMenuPanel("Panel_Developer");
            }
            return;
         default:
            return;
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
