class GUI.OSD_Components.StatusLCD extends MovieClip
{
   var __gpdb;
   var __pane;
   var __SPEED;
   var __MODE;
   var __TIMECODE;
   var __RED_PIN;
   var __RED_VERSION;
   var __RUNTIME;
   var __CHARGE_CYCLES;
   var __IOFPGA;
   var __VPFPGA;
   var __FW;
   var __SENSOR_ID;
   var __Tab;
   var __Menu;
   var __Item;
   var __Value;
   var __CHECKMARK;
   var __Message;
   var __Clip;
   var __clipNameStr;
   var __Timecode;
   var __timecodeStr;
   var __RED_BUILD;
   var __leftArrowMC;
   var __rightArrowMC;
   var __FPS;
   var __FORMAT;
   var __WB;
   var __BANNER18;
   var __BANNER14;
   var __totalMb;
   var __remainingMb;
   var __PowerPercent;
   var __X;
   var __MediaMinutes;
   var __MediaUnits;
   var __ISO;
   static var __manager;
   var DISPLAY_AS_PERCENT = true;
   static var PANE_STATUS = "FRAME_STATUS";
   static var PANE_INFO = "FRAME_INFO";
   static var PANE_MENU = "FRAME_MENU";
   static var PANE_SELECT = "FRAME_SELECT";
   static var PANE_ONESHOT = "FRAME_ONESHOT";
   static var PANE_CHECKBOX = "FRAME_CHECKBOX";
   static var PANE_MESSAGE = "FRAME_MESSAGE";
   static var PANE_PIC = "FRAME_PIC";
   static var PANE_SPLASH = "FRAME_SPLASH";
   static var PANE_PLAYBACK = "FRAME_PLAYBACK";
   var __showInfo = false;
   var __tabStr = "";
   var __menuStr = "";
   var __itemStr = "";
   var __valueStr = "";
   var __messageStr = "";
   var __isChecked = false;
   function StatusLCD()
   {
      super();
      _global.VxDebug("...........................................................................CTOR StatusLCD()");
      this.__gpdb = _global.gpdb;
      this.AddCallbacks();
      this.attachMovie("StatusLcdErrorMC","lcdErrorPanel",this.getNextHighestDepth(),{_x:0,_y:0});
      this.GoSplash();
      GUI.OSD_Components.StatusLCD.__manager = this;
   }
   static function GetManager()
   {
      if(GUI.OSD_Components.StatusLCD.__manager === undefined)
      {
         _global.VxError("StatusLCD::GetManager(): ERROR! Called before created.");
      }
      return GUI.OSD_Components.StatusLCD.__manager;
   }
   function AddCallbacks()
   {
      var _loc2_ = mx.utils.Delegate.create(this,this.Update);
      this.__gpdb.addCallback("GUI.RAWINPUT.JOYSTICK.SHIFT_SELECT",_loc2_);
      this.__gpdb.addCallback("GUI.RAWINPUT.JOYSTICK.SELECT_LONG",_loc2_);
      this.__gpdb.addCallback("GUI.PAINT.EXPOSURE.ISO",_loc2_);
      this.__gpdb.addCallback("PAINT.WHITE_BALANCE.CURRENT",_loc2_);
      this.__gpdb.addCallback("VIDEO.RECORD.SHUTTER_SPEED.REQUESTED",_loc2_);
      this.__gpdb.addCallback("PROJECT.MODE_MATRIX.FRAME_RATE",_loc2_);
      this.__gpdb.addCallback("SYSTEM.DEV.TIMECODE.JAMSYNC.ACTIVE",_loc2_);
      this.__gpdb.addCallback("PROJECT.MODE_MATRIX.RESOLUTION",_loc2_);
      this.__gpdb.addCallback("PROJECT.MODE_MATRIX.ENCODING",_loc2_);
      this.__gpdb.addCallback("VIDEO.RECORD.STATE",_loc2_);
      this.__gpdb.addCallback("SYSTEM.POWER.BATTERY.LEVEL",_loc2_);
      this.__gpdb.addCallback("MEDIA.DIGMAG.CAPACITY.TOTAL_MB",_loc2_);
      this.__gpdb.addCallback("MEDIA.DIGMAG.CAPACITY.REMAINING_MB",_loc2_);
      this.__gpdb.addCallback("MEDIA.DIGMAG.CAPACITY.TIME_REMAINING",_loc2_);
      this.__gpdb.addCallback("MEDIA.DIGMAG.TYPE",_loc2_);
      this.__gpdb.addCallback("MEDIA.DIGMAG.DRIVE0.GUI_STATE",_loc2_);
      this.__gpdb.addCallback("MEDIA.DIGMAG.DRIVE1.GUI_STATE",_loc2_);
   }
   function Update(name, value)
   {
      switch(name)
      {
         case "GUI.RAWINPUT.JOYSTICK.SHIFT_SELECT":
            if(value == "true")
            {
               if(this.__showInfo)
               {
                  this.SetPane(GUI.OSD_Components.StatusLCD.PANE_STATUS);
                  this.__showInfo = false;
               }
               else
               {
                  this.SetPane(GUI.OSD_Components.StatusLCD.PANE_INFO);
                  this.__showInfo = true;
               }
            }
            break;
         case "GUI.RAWINPUT.JOYSTICK.SELECT_LONG":
            if(value == "true")
            {
               if(this._currentframe == 1)
               {
                  this.SetPane(GUI.OSD_Components.StatusLCD.PANE_PIC);
               }
            }
            break;
         case "GUI.PAINT.EXPOSURE.ISO":
         case "PAINT.WHITE_BALANCE.CURRENT":
         case "VIDEO.RECORD.SHUTTER_SPEED.REQUESTED":
         case "PROJECT.MODE_MATRIX.FRAME_RATE":
         case "PROJECT.MODE_MATRIX.RESOLUTION":
         case "PROJECT.MODE_MATRIX.ENCODING":
         case "SYSTEM.POWER.BATTERY.LEVEL":
         case "SYSTEM.DEV.TIMECODE.JAMSYNC.ACTIVE":
         case "VIDEO.RECORD.STATE":
         case "MEDIA.DIGMAG.TYPE":
         case "MEDIA.DIGMAG.CAPACITY.TOTAL_MB":
         case "MEDIA.DIGMAG.CAPACITY.REMAINING_MB":
         case "MEDIA.DIGMAG.CAPACITY.TIME_REMAINING":
         case "MEDIA.DIGMAG.DRIVE0.GUI_STATE":
         case "MEDIA.DIGMAG.DRIVE1.GUI_STATE":
            this.Refresh();
      }
   }
   function SetPane(pane)
   {
      var _loc3_ = false;
      switch(pane)
      {
         case GUI.OSD_Components.StatusLCD.PANE_STATUS:
         case GUI.OSD_Components.StatusLCD.PANE_MENU:
         case GUI.OSD_Components.StatusLCD.PANE_SELECT:
         case GUI.OSD_Components.StatusLCD.PANE_MESSAGE:
         case GUI.OSD_Components.StatusLCD.PANE_ONESHOT:
         case GUI.OSD_Components.StatusLCD.PANE_CHECKBOX:
         case GUI.OSD_Components.StatusLCD.PANE_INFO:
         case GUI.OSD_Components.StatusLCD.PANE_PLAYBACK:
         case GUI.OSD_Components.StatusLCD.PANE_PIC:
         case GUI.OSD_Components.StatusLCD.PANE_SPLASH:
            this.__pane = pane;
            _loc3_ = true;
      }
      if(_loc3_)
      {
         this.Refresh();
      }
      else
      {
         _global.VxError("StatusLCD::SetPane(\'" + pane + "\') is no a valid Pane.");
      }
   }
   function Refresh()
   {
      switch(this.__pane)
      {
         case GUI.OSD_Components.StatusLCD.PANE_STATUS:
            this.gotoAndStop(this.__pane);
            this.SetWhiteBalance(this.__gpdb.paramGet("PAINT.WHITE_BALANCE.CURRENT"));
            this.__SPEED.text = this.__gpdb.paramGet("VIDEO.RECORD.SHUTTER_SPEED.REQUESTED");
            this.__MODE.text = this.Encoding2Text(this.__gpdb.paramGet("PROJECT.MODE_MATRIX.ENCODING"));
            this.SetFormat(this.__gpdb.paramGet("PROJECT.MODE_MATRIX.RESOLUTION"));
            this.SetFrameRate(this.__gpdb.paramGet("PROJECT.MODE_MATRIX.FRAME_RATE"));
            this.__TIMECODE.text = "true" != this.__gpdb.paramGet("SYSTEM.DEV.TIMECODE.JAMSYNC.ACTIVE") ? "INT" : "JAM";
            this.paintEI();
            this.HandleMediaRemaining();
            this.SetPowerLevel(this.__gpdb.paramGet("SYSTEM.POWER.BATTERY.LEVEL"));
            this.HandleStatusBanner();
            break;
         case GUI.OSD_Components.StatusLCD.PANE_INFO:
            this.gotoAndStop(this.__pane);
            this.__RED_PIN.text = GUI.OSD_Components.SplashScreenMC.ExtractPIN();
            this.__RED_VERSION.text = "V" + GUI.OSD_Components.SplashScreenMC.ExtractVersion() + ", B" + GUI.OSD_Components.SplashScreenMC.ExtractBuild();
            this.__RUNTIME.text = Math.round(Number(this.__gpdb.paramGet("SYSTEM.MANUFACTURING.RUNTIME")) / 60).toString();
            this.__CHARGE_CYCLES.text = this.__gpdb.paramGet("SYSTEM.POWER.BATTERY.NUM_CHARGE_CYCLES");
            this.__IOFPGA.text = this.__gpdb.paramGet("SYSTEM.VERSION.IOFPGA");
            this.__VPFPGA.text = this.__gpdb.paramGet("SYSTEM.VERSION.VPFPGA");
            this.__FW.text = this.__gpdb.paramGet("SYSTEM.VERSION.SOFTWARE");
            this.__SENSOR_ID.text = this.__gpdb.paramGet("SYSTEM.MANUFACTURING.IMAGER_SERIAL_NUMBER");
            break;
         case GUI.OSD_Components.StatusLCD.PANE_MENU:
            this.gotoAndStop(this.__pane);
            this.__Tab.text = this.__tabStr;
            this.__Menu.text = this.__menuStr;
            this.DisplayArrows();
            break;
         case GUI.OSD_Components.StatusLCD.PANE_SELECT:
            this.gotoAndStop(this.__pane);
            this.__Tab.text = this.__tabStr;
            this.__Item.text = this.__itemStr;
            this.__Value.text = this.__valueStr;
            this.DisplayArrows();
            break;
         case GUI.OSD_Components.StatusLCD.PANE_ONESHOT:
            this.gotoAndStop(this.__pane);
            this.__Tab.text = this.__tabStr;
            this.__Item.text = this.__itemStr;
            this.DisplayArrows();
            break;
         case GUI.OSD_Components.StatusLCD.PANE_CHECKBOX:
            this.gotoAndStop(this.__pane);
            this.__Tab.text = this.__tabStr;
            this.__Item.text = this.__itemStr;
            this.__CHECKMARK._visible = this.__isChecked;
            this.DisplayArrows();
            break;
         case GUI.OSD_Components.StatusLCD.PANE_MESSAGE:
            this.gotoAndStop(this.__pane);
            this.__Message.text = this.__messageStr;
            break;
         case GUI.OSD_Components.StatusLCD.PANE_PLAYBACK:
            this.gotoAndStop(this.__pane);
            this.__Clip.text = this.__clipNameStr;
            this.__Timecode.text = this.__timecodeStr;
            break;
         case GUI.OSD_Components.StatusLCD.PANE_PIC:
            this.gotoAndStop(this.__pane);
            break;
         case GUI.OSD_Components.StatusLCD.PANE_SPLASH:
            this.gotoAndStop(this.__pane);
            this.__RED_PIN.text = GUI.OSD_Components.SplashScreenMC.ExtractPIN();
            this.__RED_VERSION.text = GUI.OSD_Components.SplashScreenMC.ExtractVersion();
            this.__RED_BUILD.text = GUI.OSD_Components.SplashScreenMC.ExtractBuild();
      }
   }
   function ShowPrevArrow(show)
   {
      this.__leftArrowMC._visible = show;
   }
   function ShowNextArrow(show)
   {
      this.__rightArrowMC._visible = show;
   }
   function SetMenuTab(tabStr)
   {
      this.__tabStr = tabStr;
   }
   function SetMenuItem(menuStr)
   {
      this.__menuStr = menuStr;
      this.SetPane(GUI.OSD_Components.StatusLCD.PANE_MENU);
      this.Refresh();
   }
   function SetCheckboxItem(itemStr)
   {
      this.SetPane(GUI.OSD_Components.StatusLCD.PANE_CHECKBOX);
      this.__itemStr = itemStr;
      this.Refresh();
   }
   function SetCheckmark(isChecked)
   {
      this.SetPane(GUI.OSD_Components.StatusLCD.PANE_CHECKBOX);
      this.__isChecked = isChecked;
      this.Refresh();
   }
   function DisplayArrows()
   {
      var _loc2_ = GUI.OSD_Components.TabManager.GetManager();
      this.ShowPrevArrow(_loc2_.HasPrev());
      this.ShowNextArrow(_loc2_.HasNext());
   }
   function SetOneshotItem(itemStr)
   {
      this.SetPane(GUI.OSD_Components.StatusLCD.PANE_ONESHOT);
      this.__itemStr = itemStr;
      this.Refresh();
   }
   function SetSelectItem(itemStr)
   {
      this.SetPane(GUI.OSD_Components.StatusLCD.PANE_SELECT);
      this.__itemStr = itemStr;
      this.Refresh();
   }
   function SetSelectValue(valueStr)
   {
      this.SetPane(GUI.OSD_Components.StatusLCD.PANE_SELECT);
      this.__valueStr = valueStr;
      this.Refresh();
   }
   function SetMessage(msg)
   {
      this.__messageStr = msg;
      this.SetPane(GUI.OSD_Components.StatusLCD.PANE_MESSAGE);
      this.Refresh();
   }
   function GotoPlayback(clipName, timecode)
   {
      this.__clipNameStr = clipName;
      this.__timecodeStr = timecode;
      this.SetPane(GUI.OSD_Components.StatusLCD.PANE_PLAYBACK);
      this.Refresh();
   }
   function GoSplash()
   {
      this.SetPane(GUI.OSD_Components.StatusLCD.PANE_SPLASH);
      this.Refresh();
   }
   function GotoUpgradeScreen()
   {
      this.SetPane(GUI.OSD_Components.StatusLCD.PANE_ONESHOT);
      this.__Tab.text = "Upgrade Detected";
      this.Refresh();
   }
   function SetFrameRate(frameRate)
   {
      var _loc3_ = frameRate.indexOf(".") != -1 ? frameRate : frameRate + ".00";
      this.__FPS.text = _loc3_;
   }
   function SetFormat(resolution)
   {
      var _loc2_ = "";
      switch(resolution)
      {
         case "RGB1080P":
            _loc2_ = "1080";
            break;
         case "RGB720P":
            _loc2_ = "720";
            break;
         case "2K1.2:1":
            _loc2_ = "2K AN";
            break;
         case "3K1.2:1":
            _loc2_ = "3K AN";
            break;
         case "4K1.2:1":
            _loc2_ = "4K AN";
            break;
         default:
            _loc2_ = resolution;
      }
      this.__FORMAT.text = _loc2_;
   }
   function SetWhiteBalance(wb)
   {
      this.__WB.text = wb;
      var _loc2_ = this.__WB.getTextFormat();
      _loc2_.align = "right";
      this.__WB.setTextFormat(_loc2_);
   }
   function RightEdge(tf)
   {
      var _loc3_ = undefined;
      var _loc2_ = tf.getTextFormat();
      var _loc4_ = _loc2_.getTextExtent(tf.text).width;
      var _loc5_ = _loc2_.getTextExtent(tf.text).textFieldWidth;
      switch(_loc2_.align)
      {
         case "left":
            _loc3_ = tf._x + _loc4_;
            break;
         case "center":
            _loc3_ = tf._x + _loc5_ / 2 + _loc4_;
            break;
         case "right":
            _loc3_ = tf._x;
      }
      return _loc3_;
   }
   function HandleStatusBanner()
   {
      var _loc2_ = this.__gpdb.paramGet("MEDIA.DIGMAG.ACTIVEDRIVE");
      var _loc5_ = !this.__gpdb.paramGetBoolean("MEDIA.DIGMAG.PROJECT_SETTINGS_RECORDABLE");
      this.__BANNER18.text = "";
      this.__BANNER14.text = "";
      if(_loc2_ == "NONE")
      {
         this.__BANNER18.text = "NO DIGMAG";
      }
      else if(_loc5_)
      {
         this.__BANNER18.text = "SLOW MEDIA";
      }
      else
      {
         var _loc3_ = this.__gpdb.paramGet("MEDIA.DIGMAG." + _loc2_ + ".GUI_STATE");
         switch(_loc3_)
         {
            case "NOTPRESENT":
               this.__BANNER14.text = "NO DIGMAG";
               break;
            case "NOTMOUNTED":
               this.__BANNER14.text = "MOUNTING DISK...";
               break;
            case "INCOMPATIBLE":
               this.__BANNER14.text = "DISK INCOMPATIBLE";
               break;
            case "EXPORTED":
               this.__BANNER14.text = "DISK EXPORTED";
               break;
            case "UNMOUNTED":
               this.__BANNER14.text = "DISK UNMOUNTED";
               break;
            case "UNCONFIGURED":
               this.__BANNER14.text = "DISK UNFORMATTED";
               break;
            case "MOUNTED":
               if("ACTIVE" == this.__gpdb.paramGet("VIDEO.RECORD.STATE"))
               {
                  var _loc4_ = this.__gpdb.paramGet("MEDIA.DIGMAG.CURRENT_CLIPNAME").substr(0,9);
                  this.__BANNER18.text = "<" + _loc4_ + ">";
               }
               else
               {
                  this.__BANNER18.text = this.GetTimecode();
               }
               break;
            default:
               this.__BANNER14.text = "Bad drive state!";
         }
      }
      if(this.__BANNER18.text != "")
      {
         this.__BANNER14._visible = false;
         this.__BANNER18._visible = true;
      }
      else
      {
         this.__BANNER14._visible = true;
         this.__BANNER18._visible = false;
      }
   }
   function HandleMediaRemaining()
   {
      var _loc2_ = this.__gpdb.paramGet("MEDIA.DIGMAG.ACTIVEDRIVE");
      if(_loc2_ == "NONE")
      {
         this.SetMediaRemaining("0","NONE");
      }
      else
      {
         var _loc3_ = this.__gpdb.paramGet("MEDIA.DIGMAG." + _loc2_ + ".GUI_STATE");
         if(_loc3_ != "MOUNTED")
         {
            this.SetMediaRemaining("0","NONE");
         }
         else if(this.DISPLAY_AS_PERCENT)
         {
            this.__totalMb = Number(this.__gpdb.paramGet("MEDIA.DIGMAG.CAPACITY.TOTAL_MB"));
            this.__remainingMb = Number(this.__gpdb.paramGet("MEDIA.DIGMAG.CAPACITY.REMAINING_MB"));
            this.SetMediaRemaining(Math.floor(100 * this.__remainingMb / this.__totalMb).toString(),"%");
         }
         else
         {
            var _loc4_ = Math.floor(Number(this.__gpdb.paramGet("MEDIA.DIGMAG.CAPACITY.TIME_REMAINING")) / 60);
            this.SetMediaRemaining(_loc4_.toString(),"min");
         }
      }
   }
   function SetPowerLevel(percent)
   {
      if("AC" == this.__gpdb.paramGet("SYSTEM.POWER.SOURCE"))
      {
         this.__PowerPercent.text = "DC";
      }
      else
      {
         this.__PowerPercent.text = percent;
      }
   }
   function SetMediaRemaining(value, units)
   {
      if(units == "NONE")
      {
         this.__X._visible = true;
         this.__MediaMinutes._visible = false;
         this.__MediaUnits._visible = false;
      }
      else
      {
         this.__X._visible = false;
         this.__MediaMinutes._visible = true;
         this.__MediaUnits._visible = true;
         this.__MediaMinutes.text = value;
         this.__MediaUnits.text = units;
      }
   }
   function paintEI()
   {
      this.__ISO.text = this.__gpdb.paramGet("GUI.PAINT.EXPOSURE.ISO");
   }
   function Encoding2Text(encoding)
   {
      var _loc2_ = "???";
      switch(encoding)
      {
         case "RGB-progressive":
            _loc2_ = "444";
            break;
         case "YCC-progressive":
            _loc2_ = "422";
            break;
         case "RGB-interlaced":
            _loc2_ = "444";
            break;
         case "YCC-interlaced":
            _loc2_ = "422";
            break;
         case "REDCODE":
            _loc2_ = !(this.__gpdb.paramGet("PROJECT.MODE_MATRIX.RESOLUTION") == "RGB1080P" || this.__gpdb.paramGet("PROJECT.MODE_MATRIX.RESOLUTION") == "RGB720P") ? "RAW" : "RGB";
            break;
         default:
            _loc2_ = "???";
      }
      return _loc2_;
   }
   function GetTimecode()
   {
      var _loc2_ = undefined;
      if(this.__gpdb.paramGet("GUI.USER_PREF.TIMECODE_FORMAT") == "TIME")
      {
         _loc2_ = "T " + this.__gpdb.paramGet("VIDEO.TIMECODE.TIME_OF_DAY");
      }
      else
      {
         _loc2_ = "E " + this.__gpdb.paramGet("VIDEO.TIMECODE.RUN_RECORD");
      }
      return _loc2_;
   }
}
