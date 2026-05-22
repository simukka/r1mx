class GUI.OSD_Components.Widget_ShutterSpeed
{
   var __gpdb;
   var __speed;
   var __degreeSymbol;
   var __secSymbol;
   var __oneOver;
   static var __manager;
   function Widget_ShutterSpeed()
   {
      _global.VxDebug("...........................................................................CTOR Widget_ShutterSpeed()");
      this.__gpdb = _global.gpdb;
      GUI.OSD_Components.Widget_ShutterSpeed.__manager = this;
      this.InitGuiShutterSpeed();
      this.DisplaySpeed();
      this.AddCallbacks();
   }
   static function GetManager()
   {
      if(GUI.OSD_Components.Widget_ShutterSpeed.__manager === undefined)
      {
         _global.VxError("ERROR! Widget_ShutterSpeed::GetManager() called before being instantiated");
      }
      return GUI.OSD_Components.Widget_ShutterSpeed.__manager;
   }
   function AddCallbacks()
   {
      var _loc2_ = mx.utils.Delegate.create(this,this.Update);
      this.__gpdb.addCallback("GUI.USER_PREF.SHUTTER_SPEED_FORMAT",_loc2_);
      this.__gpdb.addCallback("VIDEO.RECORD.VARISPEED.ENABLED",_loc2_);
      this.__gpdb.addCallback("GUI.RECORD.TIMELAPSE.ENABLED",_loc2_);
      this.__gpdb.addCallback("GUI.RECORD.SHUTTER_SPEED",_loc2_);
      this.__gpdb.addCallback("GUI.RECORD.TIMELAPSE.SHUTTER_SPEED",_loc2_);
      this.__gpdb.addCallback("VIDEO.RECORD.SHUTTER_SPEED.MODE",_loc2_);
      this.__gpdb.addCallback("VIDEO.RECORD.FRAME_RATE.ACTUAL",_loc2_);
      this.__gpdb.addCallback("VIDEO.RECORD.SHUTTER_SPEED.ACTUAL_NSEC",_loc2_);
      this.__gpdb.addCallback("VIDEO.RECORD.SHUTTER_SPEED.REQUESTED",_loc2_);
      this.__gpdb.addCallback("PROJECT.MODE_MATRIX.FRAME_RATE",_loc2_);
      this.__gpdb.addCallback("GUI.RECORD.SHUTTER_SPEED_DEG",_loc2_);
   }
   function Update(name, value)
   {
      switch(name)
      {
         case "GUI.RECORD.SHUTTER_SPEED_DEG":
            this.SetRequestedSystemShutterSpeed();
            this.DisplaySpeed();
            break;
         case "GUI.RECORD.SHUTTER_SPEED":
            this.SetRequestedSystemShutterSpeed();
            this.DisplaySpeed();
            break;
         case "VIDEO.RECORD.VARISPEED.ENABLED":
         case "GUI.RECORD.TIMELAPSE.ENABLED":
         case "GUI.RECORD.TIMELAPSE.SHUTTER_SPEED":
            this.SetRequestedSystemShutterSpeed();
            this.DisplaySpeed();
            break;
         case "GUI.USER_PREF.SHUTTER_SPEED_FORMAT":
            this.InitGuiShutterSpeed();
            this.DisplaySpeed();
            this.ChangeShutterLabel();
            break;
         case "VIDEO.RECORD.FRAME_RATE.ACTUAL":
         case "VIDEO.RECORD.SHUTTER_SPEED.MODE":
         case "VIDEO.RECORD.SHUTTER_SPEED.REQUESTED":
         case "VIDEO.RECORD.SHUTTER_SPEED.ACTUAL_NSEC":
         case "VIDEO.RECORD.VARISPEED.ENABLED":
            this.DisplaySpeed();
            break;
         case "PROJECT.MODE_MATRIX.FRAME_RATE":
            this.Set180ShutterAngle();
      }
   }
   function DisplaySpeed()
   {
      var _loc6_ = this.__gpdb.paramGet("VIDEO.RECORD.SHUTTER_SPEED.MODE");
      var _loc7_ = this.__gpdb.paramGetBoolean("VIDEO.RECORD.VARISPEED.ENABLED");
      var _loc11_ = this.__gpdb.paramGetBoolean("SYSTEM.DEV.EVF.OPEN_GATE_ENABLED");
      var _loc3_ = this.__gpdb.paramGetNumber("VIDEO.RECORD.FRAME_RATE.ACTUAL");
      var _loc9_ = this.__gpdb.paramGetNumber("PROJECT.MODE_MATRIX.FRAME_RATE");
      var _loc8_ = "DEGREES" == this.__gpdb.paramGet("GUI.USER_PREF.SHUTTER_SPEED_FORMAT");
      var _loc12_ = this.__gpdb.paramGetBoolean("GUI.RECORD.TIMELAPSE.ENABLED");
      var _loc2_ = this.__gpdb.paramGetNumber("VIDEO.RECORD.SHUTTER_SPEED.REQUESTED");
      var _loc10_ = undefined;
      var _loc4_ = undefined;
      var _loc5_ = _loc6_ == "NORMAL";
      switch(_loc6_)
      {
         case "NORMAL":
            break;
         case "SYNCRO":
            _loc10_ = this.__gpdb.paramGetNumber("VIDEO.RECORD.SHUTTER_SPEED.SYNC_ADJUST");
            _loc2_ *= 50 / _loc10_;
            break;
         case "RELATIVE":
            if(_loc7_)
            {
               _loc2_ *= _loc3_ / _loc9_;
            }
      }
      _loc4_ = !_loc5_ ? 16776960 : 16777215;
      if(_loc11_)
      {
         if(_loc2_ < _loc3_ * 2)
         {
            _loc4_ = 16711680;
         }
      }
      else if(!_loc12_ && _loc2_ < _loc3_)
      {
         _loc4_ = 16711680;
         _loc2_ = _loc3_;
      }
      if(_loc8_)
      {
         this.DisplaySpeedAsDegrees(_loc2_,_loc5_);
      }
      else
      {
         this.DisplaySpeedAsSeconds(_loc2_,_loc5_);
      }
      this.SetWidgetColor(_loc4_);
   }
   function PercentDiff(NumA, NumB)
   {
      return 100 * Math.abs((NumA - NumB) / NumA);
   }
   function DisplaySpeedAsDegrees(shutterSpeed, isNormalMode)
   {
      var _loc3_ = this.__gpdb.paramGetNumber("VIDEO.RECORD.FRAME_RATE.REQUESTED");
      var _loc4_ = Math.round(360 / (shutterSpeed / _loc3_));
      var _loc5_ = undefined;
      this.__speed.text = _global.ShowDecimalPlaces(_loc4_,0,false);
      _loc5_ = this.__speed.getTextFormat();
      this.__degreeSymbol._x = this.__speed._x + _loc5_.getTextExtent(this.__speed.text).width;
      this.__degreeSymbol._visible = true;
      this.__secSymbol._visible = false;
      this.__oneOver._visible = false;
   }
   function DisplaySpeedAsSeconds(shutterSpeed, isNormalMode)
   {
      this.__speed.text = _global.ShowDecimalPlaces(shutterSpeed,1,isNormalMode);
      var _loc3_ = this.__speed.getTextFormat();
      this.__secSymbol._x = this.__speed._x + 4 + _loc3_.getTextExtent(this.__speed.text).width;
      this.__secSymbol._visible = true;
      this.__oneOver._visible = true;
      this.__degreeSymbol._visible = false;
   }
   function SetWidgetColor(color)
   {
      var _loc2_ = undefined;
      _loc2_ = this.__secSymbol.getTextFormat();
      _loc2_.color = color;
      this.__secSymbol.setTextFormat(_loc2_);
      _loc2_ = this.__oneOver.getTextFormat();
      _loc2_.color = color;
      this.__oneOver.setTextFormat(_loc2_);
      _loc2_ = this.__speed.getTextFormat();
      _loc2_.color = color;
      this.__speed.setTextFormat(_loc2_);
      _loc2_ = this.__degreeSymbol.getTextFormat();
      _loc2_.color = color;
      this.__degreeSymbol.setTextFormat(_loc2_);
   }
   function InitGuiShutterSpeed()
   {
      var _loc2_ = this.__gpdb.paramGet("VIDEO.RECORD.MODE");
      var _loc3_ = !(_loc2_ == "TIMELAPSE" || _loc2_ == "BURST") ? this.__gpdb.paramGetNumber("VIDEO.RECORD.SHUTTER_SPEED.REQUESTED") : Math.round(this.__gpdb.paramGetNumber("PROJECT.MODE_MATRIX.FRAME_RATE")) * 2;
      if(this.__gpdb.paramGet("GUI.USER_PREF.SHUTTER_SPEED_FORMAT") == "1/SEC")
      {
         this.__gpdb.paramSet("GUI.RECORD.SHUTTER_SPEED",_loc3_);
      }
      else
      {
         this.__gpdb.paramSet("GUI.RECORD.SHUTTER_SPEED_DEG",_loc3_);
      }
      this.SetRequestedSystemShutterSpeed();
   }
   function ChangeShutterLabel()
   {
      var _loc2_ = undefined;
      var _loc4_ = undefined;
      var _loc3_ = undefined;
      _loc2_ = GUI.OSD_Components.PanelButtonMC(GUI.OSD_Components.MenuManager.GetManager().GetPanelWidget("Panel_Shutter","BUTTON_SHUTTER_SPEED"));
      if(this.__gpdb.paramGet("GUI.USER_PREF.SHUTTER_SPEED_FORMAT") == "1/SEC")
      {
         _loc4_ = "SPEED";
         _loc3_ = "SHUTTER SPEED";
      }
      else
      {
         _loc4_ = "ANGLE";
         _loc3_ = "SHUTTER ANGLE";
      }
      _loc2_.SetLabel(_loc4_);
      var _loc5_ = undefined;
      _loc5_ = _loc2_.getTabSelector();
      _loc5_.setLabel(_loc3_);
   }
   function Set180ShutterAngle()
   {
      var _loc3_ = "DEGREES" == this.__gpdb.paramGet("GUI.USER_PREF.SHUTTER_SPEED_FORMAT");
      var _loc2_ = this.ConvertAngleToFracSec(180);
      if(this.__gpdb.paramGetNumber("GUI.USER_PREF.SHUTTER_SPEED_FORMAT") == "1/SEC")
      {
         this.__gpdb.paramSet("GUI.RECORD.SHUTTER_SPEED",_loc2_);
      }
      else
      {
         this.__gpdb.paramSet("GUI.RECORD.SHUTTER_SPEED_DEG",_loc2_);
      }
   }
   function SetRequestedSystemShutterSpeed()
   {
      var _loc2_ = undefined;
      var _loc3_ = undefined;
      var _loc4_ = GUI.OSD_Components.RecordManager.GetManager().GuiRecordMode();
      switch(_loc4_)
      {
         case "NORMAL":
         case "VARISPEED":
            if(this.__gpdb.paramGet("GUI.USER_PREF.SHUTTER_SPEED_FORMAT") == "1/SEC")
            {
               _loc2_ = this.__gpdb.paramGetNumber("GUI.RECORD.SHUTTER_SPEED");
            }
            else
            {
               _loc2_ = this.__gpdb.paramGetNumber("GUI.RECORD.SHUTTER_SPEED_DEG");
            }
            break;
         case "TIMELAPSE":
            _loc2_ = this.__gpdb.paramGetNumber("GUI.RECORD.TIMELAPSE.SHUTTER_SPEED");
            _loc3_ = this.__gpdb.paramGetNumber("PROJECT.MODE_MATRIX.FRAME_RATE");
            if(_loc2_ <= _loc3_)
            {
               this.__gpdb.paramSet("VIDEO.RECORD.FRAME_RATE.REQUESTED",_loc2_);
            }
      }
      this.__gpdb.paramSet("VIDEO.RECORD.SHUTTER_SPEED.REQUESTED",_loc2_);
      return _loc2_;
   }
   function ConvertAngleToFracSec(angle)
   {
      var _loc3_ = Math.round(this.__gpdb.paramGetNumber("PROJECT.MODE_MATRIX.FRAME_RATE"));
      var _loc2_ = Math.round(_loc3_ * (360 / angle));
      return _loc2_;
   }
   function ConvertFracSecToAngle(fracSec)
   {
      var _loc2_ = Math.round(this.__gpdb.paramGetNumber("PROJECT.MODE_MATRIX.FRAME_RATE"));
      var _loc3_ = Math.round(_loc2_ * (360 / fracSec));
      return _loc3_;
   }
}
