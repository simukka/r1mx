class GUI.OSD_Components.Widget_FPS
{
   var __FPS;
   var __fpsSymbol;
   var __gpdb;
   function Widget_FPS()
   {
      _global.VxDebug("...........................................................................CTOR Widget_FPS()");
      this.__gpdb = _global.gpdb;
      this.__gpdb.paramSet("GUI.SOFTKEY.MODE_MATRIX.FRAME_RATE",this.GetGuiFrameRateFromProject());
      this.HandleVarispeedEnable("true" == this.__gpdb.paramGet("VIDEO.RECORD.VARISPEED.ENABLED"));
      this.DisplayFPS();
      this.AddCallbacks();
   }
   function AddCallbacks()
   {
      var _loc2_ = mx.utils.Delegate.create(this,this.Update);
      this.__gpdb.addCallback("GUI.SOFTKEY.MODE_MATRIX.FRAME_RATE",_loc2_);
      this.__gpdb.addCallback("VIDEO.RECORD.VARISPEED.ENABLED",_loc2_);
      this.__gpdb.addCallback("VIDEO.RECORD.FRAME_RATE.ACTUAL",_loc2_);
      this.__gpdb.addCallback("GUI.RECORD.TIMELAPSE.ENABLED",_loc2_);
   }
   function Update(name, value)
   {
      switch(name)
      {
         case "GUI.SOFTKEY.MODE_MATRIX.FRAME_RATE":
            this.SetProjectFramerate(value);
            this.AdoptProjectFrameRate();
            this.DisplayFPS();
            return;
         case "GUI.RECORD.TIMELAPSE.ENABLED":
         case "VIDEO.RECORD.VARISPEED.ENABLED":
         case "VIDEO.RECORD.FRAME_RATE.ACTUAL":
            this.DisplayFPS();
            return;
         case "VIDEO.RECORD.VARISPEED.ENABLED":
            this.HandleVarispeedEnable(value == "true");
            this.DisplayFPS();
            return;
         default:
            return;
      }
   }
   function AdoptProjectFrameRate()
   {
      this.__gpdb.paramSet("VIDEO.RECORD.FRAME_RATE.REQUESTED",this.GetInstantaneousFrameRateFromProject());
      this.__gpdb.paramSet("GUI.SOFTKEY.MODE_MATRIX.FRAME_RATE",this.GetGuiFrameRateFromProject());
   }
   function DisplayFPS()
   {
      var _loc3_;
      var _loc2_;
      var _loc4_;
      if(this.__gpdb.paramGetBoolean("GUI.RECORD.TIMELAPSE.ENABLED"))
      {
         this.__FPS.text = "TL";
         this.__fpsSymbol._visible = false;
      }
      else
      {
         _loc3_ = Math.round(Number(this.__gpdb.paramGet("VIDEO.RECORD.FRAME_RATE.ACTUAL"))).toString();
         this.__FPS.text = _loc3_;
         _loc2_ = this.__FPS.getTextFormat();
         _loc4_ = _loc2_.getTextExtent(_loc3_).width;
         _loc2_ = this.__fpsSymbol.getTextFormat();
         _loc2_.color = !this.__gpdb.paramGetBoolean("VIDEO.RECORD.VARISPEED.ENABLED") ? 16777215 : 16776960;
         this.__fpsSymbol._x = this.__FPS._x + _loc4_ + 4;
         this.__fpsSymbol._visible = true;
         this.__fpsSymbol.setTextFormat(_loc2_);
         _loc2_ = this.__FPS.getTextFormat();
         _loc2_.color = !this.__gpdb.paramGetBoolean("VIDEO.RECORD.VARISPEED.ENABLED") ? 16777215 : 16776960;
         this.__FPS.setTextFormat(_loc2_);
      }
   }
   function GetInstantaneousFrameRateFromProject()
   {
      var _loc2_;
      var _loc3_ = this.__gpdb.paramGet("PROJECT.MODE_MATRIX.FRAME_RATE");
      switch(_loc3_)
      {
         case "23.98":
            _loc2_ = "24";
            break;
         case "29.97":
            _loc2_ = "30";
            break;
         case "59.94":
            _loc2_ = "60";
            break;
         default:
            _loc2_ = _loc3_;
      }
      return _loc2_;
   }
   function GetGuiFrameRateFromProject()
   {
      var _loc2_;
      var _loc4_ = this.__gpdb.paramGet("PROJECT.MODE_MATRIX.FRAME_RATE");
      var _loc3_ = this.__gpdb.paramGetBoolean("PROJECT.MODE_MATRIX.DROPFRAME");
      switch(_loc4_)
      {
         case "23.98":
            _loc2_ = "23.98";
            break;
         case "24":
            _loc2_ = "24";
            break;
         case "25":
            _loc2_ = "25";
            break;
         case "29.97":
            if(_loc3_)
            {
               _loc2_ = "29.97 DF";
            }
            else
            {
               _loc2_ = "29.97";
            }
            break;
         case "30":
            _loc2_ = "30";
            break;
         case "50":
            _loc2_ = "50";
            break;
         case "59.94":
            if(_loc3_)
            {
               _loc2_ = "59.94 DF";
            }
            else
            {
               _loc2_ = "59.94";
            }
            break;
         case "60":
            _loc2_ = "60";
      }
      return _loc2_;
   }
   function SetProjectFramerate(compositeFramerate)
   {
      var _loc3_ = false;
      var _loc4_;
      switch(compositeFramerate)
      {
         case "23.98":
            _loc4_ = "23.98";
            _loc3_ = false;
            break;
         case "24":
            _loc4_ = "24";
            _loc3_ = false;
            break;
         case "25":
            _loc4_ = "25";
            _loc3_ = false;
            break;
         case "29.97":
            _loc4_ = "29.97";
            _loc3_ = false;
            break;
         case "30":
            _loc4_ = "30";
            _loc3_ = false;
            break;
         case "50":
            _loc4_ = "50";
            _loc3_ = false;
            break;
         case "59.94":
            _loc4_ = "59.94";
            _loc3_ = false;
            break;
         case "60":
            _loc4_ = "60";
            _loc3_ = false;
            break;
         default:
            _global.VxError("Widget_FPS::SetProjectFramerate() \'" + compositeFramerate + "\' is NOT supported!");
            _loc4_ = "23.98";
            _loc3_ = false;
      }
      this.__gpdb.paramSet("PROJECT.MODE_MATRIX.FRAME_RATE",_loc4_);
      this.__gpdb.paramSet("PROJECT.MODE_MATRIX.DROPFRAME",_loc3_);
   }
   function HandleVarispeedEnable(varispeedEnabled)
   {
      if(varispeedEnabled)
      {
         this.__gpdb.paramSet("VIDEO.RECORD.FRAME_RATE.REQUESTED",this.__gpdb.paramGet("GUI.RECORD.VARISPEED.FRAME_RATE"));
      }
      else
      {
         this.__gpdb.paramSet("VIDEO.RECORD.FRAME_RATE.REQUESTED",this.GetInstantaneousFrameRateFromProject());
      }
   }
}
