class GUI.OSD_Components.EvfCtrlPanelMC extends MovieClip
{
   var ARROW_DOWN;
   var ARROW_UP;
   var BAR_DOWN;
   var BAR_UP;
   var __LedBlinkIntervalID;
   var __blinkCount;
   var __blinkState;
   var __controls;
   var __gpdb;
   var __ndxOfActiveCtrl = 0;
   var __numControls = 0;
   var __mode = "SELECT_CONTROL";
   var __ctrl = "FRAME_OFF";
   function EvfCtrlPanelMC()
   {
      super();
      _global.VxDebug("...........................................................................CTOR EvfCtrlPanelMC()");
      this.__gpdb = _global.gpdb;
      this.NewControl("FRAME_INT","SYSTEM.DEV.EVF.DARK_DETAIL.VALUE");
      var _loc4_ = "LINE" != this.__gpdb.paramGet("AUDIO.INPUT.CHANNEL_1.SOURCE") ? "AUDIO.INPUT.CHANNEL_1.GAIN.MICROPHONE" : "AUDIO.INPUT.CHANNEL_1.GAIN.LINE";
      this.NewControl("FRAME_CH1",_loc4_);
      _loc4_ = "LINE" != this.__gpdb.paramGet("AUDIO.INPUT.CHANNEL_2.SOURCE") ? "AUDIO.INPUT.CHANNEL_2.GAIN.MICROPHONE" : "AUDIO.INPUT.CHANNEL_2.GAIN.LINE";
      this.NewControl("FRAME_CH2",_loc4_);
      if(this.__gpdb.paramGet("GUI.USER_PREF.SHUTTER_SPEED_FORMAT") == "1/SEC")
      {
         this.NewControl("FRAME_EXP","GUI.RECORD.SHUTTER_SPEED");
      }
      else
      {
         this.NewControl("FRAME_EXP","GUI.RECORD.SHUTTER_SPEED_DEG");
      }
      this.NewControl("FRAME_VAR","GUI.RECORD.VARISPEED.FRAME_RATE");
      this.NewControl("FRAME_ISO","GUI.PAINT.EXPOSURE.ISO");
      this.NewControl("FRAME_OFF","NONE");
      this.InitView();
      this.AddCallbacks();
      this.SmartShow();
   }
   function GetAudioParam(ch)
   {
      var _loc2_;
      if(ch == 1)
      {
         _loc2_ = "LINE" != this.__gpdb.paramGet("AUDIO.INPUT.CHANNEL_1.SOURCE") ? "AUDIO.INPUT.CHANNEL_1.GAIN.MICROPHONE" : "AUDIO.INPUT.CHANNEL_1.GAIN.LINE";
         this.__controls[1].param = this.__gpdb.getParam(_loc2_);
      }
      else
      {
         _loc2_ = "LINE" != this.__gpdb.paramGet("AUDIO.INPUT.CHANNEL_2.SOURCE") ? "AUDIO.INPUT.CHANNEL_2.GAIN.MICROPHONE" : "AUDIO.INPUT.CHANNEL_2.GAIN.LINE";
         this.__controls[2].param = this.__gpdb.getParam(_loc2_);
      }
   }
   function SmartShow()
   {
      var _loc3_ = this.__gpdb.paramGetBoolean("GUI.OSD.SHOW.EVF_FUNCTION_LADDER");
      var _loc5_ = this.__gpdb.paramGetBoolean("SYSTEM.DEV.EVF.EXISTS");
      var _loc4_ = this.__gpdb.paramGetBoolean("VIDEO.MONITOR.TEST_PATTERN.ENABLED");
      var _loc2_ = "IDLE" != this.__gpdb.paramGet("VIDEO.PLAYBACK.STATE");
      this._visible = _loc3_ && _loc5_ && !_loc2_ && !_loc4_;
      if(this._visible)
      {
         this.InitView();
      }
      else
      {
         this.__mode = "DISABLED";
      }
   }
   function InitView()
   {
      this.__ctrl = this.__gpdb.paramGet("GUI.EVF.CONTROL_PANEL.CONTROL");
      this.__mode = "SET_VALUE";
      this.__ndxOfActiveCtrl = 0;
      while(this.__ndxOfActiveCtrl <= this.__numControls)
      {
         if(this.__controls[this.__ndxOfActiveCtrl].frame == this.__ctrl)
         {
            break;
         }
         this.__ndxOfActiveCtrl = this.__ndxOfActiveCtrl + 1;
      }
      var _loc2_ = this.__controls[this.__ndxOfActiveCtrl].frame + "_SET";
      this.gotoAndStop(_loc2_);
   }
   function AddCallbacks()
   {
      var _loc2_ = mx.utils.Delegate.create(this,this.Update);
      this.__gpdb.addCallback("GUI.OSD.SHOW.EVF_FUNCTION_LADDER",_loc2_);
      this.__gpdb.addCallback("VIDEO.PLAYBACK.STATE",_loc2_);
      this.__gpdb.addCallback("VIDEO.MONITOR.TEST_PATTERN.ENABLED",_loc2_);
      this.__gpdb.addCallback("SYSTEM.DEV.EVF.EXISTS",_loc2_);
      this.__gpdb.addCallback("SYSTEM.DEV.EVF.RAWINPUT.DIAL.SELECT",_loc2_);
      this.__gpdb.addCallback("SYSTEM.DEV.EVF.RAWINPUT.DIAL.CW",_loc2_);
      this.__gpdb.addCallback("SYSTEM.DEV.EVF.RAWINPUT.DIAL.CCW",_loc2_);
      this.__gpdb.addCallback("AUDIO.INPUT.CHANNEL_1.SOURCE",_loc2_);
      this.__gpdb.addCallback("AUDIO.INPUT.CHANNEL_2.SOURCE",_loc2_);
      this.__gpdb.addCallback("GUI.USER_PREF.SHUTTER_SPEED_FORMAT",_loc2_);
   }
   function Update(name, value)
   {
      var _loc4_;
      switch(name)
      {
         case "SYSTEM.DEV.EVF.EXISTS":
            if(value == "true")
            {
               this.PauseBeforeBlinking();
            }
            this.SmartShow();
            return;
         case "GUI.OSD.SHOW.EVF_FUNCTION_LADDER":
         case "VIDEO.PLAYBACK.STATE":
         case "VIDEO.MONITOR.TEST_PATTERN.ENABLED":
            this.SmartShow();
            return;
         case "AUDIO.INPUT.CHANNEL_1.SOURCE":
            this.GetAudioParam(1);
            return;
         case "AUDIO.INPUT.CHANNEL_2.SOURCE":
            this.GetAudioParam(2);
            return;
         case "SYSTEM.DEV.EVF.RAWINPUT.DIAL.SELECT":
            if(value == "true")
            {
               _loc4_ = this.__controls[this.__ndxOfActiveCtrl].frame;
               switch(this.__mode)
               {
                  case "DISABLED":
                     break;
                  case "SELECT_CONTROL":
                     this.__mode = "SET_VALUE";
                     _loc4_ += "_SET";
                     break;
                  case "SET_VALUE":
                     this.__mode = "SELECT_CONTROL";
               }
               this.gotoAndStop(_loc4_);
               this._visible = this.__mode != "DISABLED";
            }
            return;
         case "SYSTEM.DEV.EVF.RAWINPUT.DIAL.CW":
            switch(this.__mode)
            {
               case "SELECT_CONTROL":
                  this.NextControl();
                  break;
               case "SET_VALUE":
                  this.NextValue(Number(value));
                  break;
               case "DISABLED":
            }
            return;
         case "SYSTEM.DEV.EVF.RAWINPUT.DIAL.CCW":
            switch(this.__mode)
            {
               case "SELECT_CONTROL":
                  this.PrevControl();
                  break;
               case "SET_VALUE":
                  this.PrevValue(Number(value));
                  break;
               case "DISABLED":
            }
            return;
         case "GUI.USER_PREF.SHUTTER_SPEED_FORMAT":
            if(value == "1/SEC")
            {
               this.SetShutterControlParam("GUI.RECORD.SHUTTER_SPEED");
            }
            else
            {
               this.SetShutterControlParam("GUI.RECORD.SHUTTER_SPEED_DEG");
            }
            return;
         default:
            _global.VxError("EvfCtrlPanelMC.Update() ERROR! Unknown parameter, \'" + name + "\'. Ignoring.");
            return;
      }
   }
   function NewControl(frame, paramName)
   {
      var _loc3_;
      if(paramName != "NONE")
      {
         _loc3_ = this.__gpdb.getParam(paramName);
         if(!_loc3_)
         {
            throw new Error("EvfCtrlPanelMC:NewControl() unrecognized parameter: \'" + paramName + "\'");
         }
      }
      if(this.__controls == undefined)
      {
         this.__controls = new Array();
      }
      var _loc2_ = new Object();
      _loc2_.frame = frame;
      if(_loc3_)
      {
         _loc2_.param = _loc3_;
      }
      _loc2_.param.options.SetAndCacheChoices();
      this.__controls.push(_loc2_);
      this.__numControls += 1;
   }
   function NextControl()
   {
      this.__ndxOfActiveCtrl += 1;
      if(this.__ndxOfActiveCtrl >= this.__numControls)
      {
         this.__ndxOfActiveCtrl = this.__numControls - 1;
      }
      var _loc2_ = this.__controls[this.__ndxOfActiveCtrl].frame;
      this.__gpdb.paramSet("GUI.EVF.CONTROL_PANEL.CONTROL",this.__controls[this.__ndxOfActiveCtrl].frame);
      this.__controls[this.__ndxOfActiveCtrl].param.options.SetAndCacheChoices();
      this.gotoAndStop(_loc2_);
   }
   function PrevControl()
   {
      this.__ndxOfActiveCtrl -= 1;
      if(this.__ndxOfActiveCtrl < 0)
      {
         this.__ndxOfActiveCtrl = 0;
      }
      var _loc2_ = this.__controls[this.__ndxOfActiveCtrl].frame;
      this.__gpdb.paramSet("GUI.EVF.CONTROL_PANEL.CONTROL",this.__controls[this.__ndxOfActiveCtrl].frame);
      this.__controls[this.__ndxOfActiveCtrl].param.options.SetAndCacheChoices();
      this.gotoAndStop(_loc2_);
   }
   function NextValue(n)
   {
      var _loc3_ = this.__controls[this.__ndxOfActiveCtrl];
      var _loc4_ = _loc3_.param;
      var _loc2_ = _loc4_.options.SelectNext(n);
      this.FlashDirectionIndicator(!_loc2_ ? "UP_BAR" : "UP_ARROW");
   }
   function PrevValue(n)
   {
      var _loc3_ = this.__controls[this.__ndxOfActiveCtrl];
      var _loc4_ = _loc3_.param;
      var _loc2_ = _loc4_.options.SelectPrev(n);
      this.FlashDirectionIndicator(!_loc2_ ? "DOWN_BAR" : "DOWN_ARROW");
   }
   function FlashDirectionIndicator(direction)
   {
      switch(direction)
      {
         case "UP_ARROW":
            this.ARROW_UP.gotoAndPlay(1);
            this.BAR_UP.gotoAndStop("OFF");
            this.ARROW_DOWN.gotoAndStop("OFF");
            this.BAR_DOWN.gotoAndStop("OFF");
            break;
         case "UP_BAR":
            this.BAR_UP.gotoAndPlay(1);
            this.ARROW_UP.gotoAndStop("OFF");
            this.ARROW_DOWN.gotoAndStop("OFF");
            this.BAR_DOWN.gotoAndStop("OFF");
            break;
         case "DOWN_ARROW":
            this.ARROW_DOWN.gotoAndPlay(1);
            this.ARROW_UP.gotoAndStop("OFF");
            this.BAR_UP.gotoAndStop("OFF");
            this.BAR_DOWN.gotoAndStop("OFF");
            break;
         case "DOWN_BAR":
            this.BAR_DOWN.gotoAndPlay(1);
            this.ARROW_UP.gotoAndStop("OFF");
            this.BAR_UP.gotoAndStop("OFF");
            this.ARROW_DOWN.gotoAndStop("OFF");
         default:
            return;
      }
   }
   function PauseBeforeBlinking()
   {
      if(this.__LedBlinkIntervalID != undefined)
      {
         clearInterval(this.__LedBlinkIntervalID);
      }
      var _loc2_ = 2000;
      this.__LedBlinkIntervalID = setInterval(this,"HandleStart3Blink",_loc2_);
   }
   function HandleStart3Blink()
   {
      this.BlinkEvfLed(3);
   }
   function BlinkEvfLed(n)
   {
      this.__blinkCount = n;
      this.__blinkState = "OFF";
      if(this.__LedBlinkIntervalID != undefined)
      {
         clearInterval(this.__LedBlinkIntervalID);
      }
      if(this.__blinkCount > 0)
      {
         this.__LedBlinkIntervalID = setInterval(this,"HandleBlinkEvfLed",300);
      }
   }
   function HandleBlinkEvfLed()
   {
      if(this.__blinkState == "OFF")
      {
         this.__gpdb.paramSet("SYSTEM.DEV.EVF.RAWOUTPUT.LED_1","ON");
         this.__blinkState = "ON";
         this.__blinkCount -= 1;
      }
      else
      {
         this.__gpdb.paramSet("SYSTEM.DEV.EVF.RAWOUTPUT.LED_1","OFF");
         this.__blinkState = "OFF";
         if(this.__blinkCount <= 0)
         {
            clearInterval(this.__LedBlinkIntervalID);
         }
      }
   }
   function SetShutterControlParam(paramName)
   {
      var _loc3_ = this.__controls[3];
      if(_loc3_.frame == "FRAME_EXP")
      {
         _loc3_.param = this.__gpdb.getParam(paramName);
         _loc3_.param.options.SetAndCacheChoices();
      }
      else
      {
         _global.VxError("SetShutterControlParam: Failed");
      }
   }
   function IndexOfElement(list, element)
   {
      var _loc2_;
      var _loc4_ = false;
      _loc2_ = 0;
      while(_loc2_ < list.length)
      {
         if(list[_loc2_].value == element)
         {
            _loc4_ = true;
            break;
         }
         _loc2_ = _loc2_ + 1;
      }
      if(!_loc4_)
      {
         _global.VxError("EvfCtrlPanelMC:IndexOfElement() Element \'" + element + "\' not found.");
      }
      return _loc2_;
   }
}
