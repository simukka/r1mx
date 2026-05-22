class GUI.OSD_Components.FocusAssistMC extends MovieClip
{
   var __gpdb;
   var MIN_CHEVRON;
   var MAX_CHEVRON;
   var TOP;
   var MIDDLE;
   var BOTTOM;
   var NUM_SAMPLES = 6;
   var CONFIG_STATE = 0;
   var RUN_STATE = 1;
   var __state = GUI.OSD_Components.FocusAssistMC.prototype.CONFIG_STATE;
   var __isOverlay = false;
   var __separation = 6;
   var __height = GUI.OSD_Components.FocusAssistMC.prototype.NUM_SAMPLES * GUI.OSD_Components.FocusAssistMC.prototype.__separation;
   var __yPos = 360;
   function FocusAssistMC()
   {
      super();
      this.__gpdb = _global.gpdb;
      this.SetPosition(Number(this.__gpdb.paramGet("IMAGE_ANALYSIS.FOCUS_ASSIST.SAMPLE_Y")));
      this.SetSeparation(Number(this.__gpdb.paramGet("IMAGE_ANALYSIS.FOCUS_ASSIST.SAMPLE_STRIDE")));
      this.Show(false);
      this.EnableConfigMode(true);
   }
   function EnableConfigMode(config)
   {
      _global.VxDebug("FocusAssistMC::EnableConfigMode(" + config + ")");
      var _loc3_ = this.__gpdb.paramGet("GUI.SOFTKEY.IMAGE_ANALYSIS.ASSIST_METER");
      if(config)
      {
         this.__state = this.CONFIG_STATE;
         this.gotoAndStop("FRAME_CONFIG");
         _global.VxDebug("FocusAssistMC::EnableConfigMode() frame=CONFIG");
         this.MIN_CHEVRON._y = - this.__height / 2;
         this.MAX_CHEVRON._y = this.__height / 2;
         this.TOP._y = - (this.__height / 2 + 3);
         this.MIDDLE._y = - this.__height / 2;
         this.BOTTOM._y = this.__height / 2;
         this.MIDDLE._height = this.__height;
         if(_loc3_ == "Focus Assist Overlay")
         {
            GUI.OSD_Components.SplatManager.GetManager().ShowMeterSplat(false);
         }
      }
      else
      {
         this.__state = this.RUN_STATE;
         this.gotoAndStop("FRAME_RUN");
         _global.VxDebug("FocusAssistMC::EnableConfigMode() frame=RUN");
         this.MIN_CHEVRON._y = - this.__height / 2;
         this.MAX_CHEVRON._y = this.__height / 2;
         if(_loc3_ == "Focus Assist Overlay")
         {
            GUI.OSD_Components.SplatManager.GetManager().ShowMeterSplat(true);
         }
      }
   }
   function SetSeparation(separation)
   {
      _global.VxDebug("...FocusAssistMC::SetPosition() Setting CONFIG state and size");
      this.__separation = separation;
      if(this.__separation < 1)
      {
         this.__separation = 1;
      }
      else if(this.__separation > 40)
      {
         this.__separation = 40;
      }
      this.__height = this.__separation * (this.NUM_SAMPLES - 1) + 1;
      this.MIN_CHEVRON._y = - this.__height / 2;
      this.MAX_CHEVRON._y = this.__height / 2;
      this.TOP._y = - (this.__height / 2 + 3);
      this.MIDDLE._y = - this.__height / 2;
      this.BOTTOM._y = this.__height / 2;
      this.MIDDLE._height = this.__height;
      this.__gpdb.paramSet("IMAGE_ANALYSIS.FOCUS_ASSIST.SAMPLE_STRIDE",String(this.__separation));
      this.SetPosition(this.__yPos);
   }
   function SetPosition(yPos)
   {
      _global.VxDebug("FocusAssistMC::SetPosition() Setting CONFIG state and position");
      this.__yPos = yPos;
      if(this.__yPos + this.__height / 2 > 720)
      {
         this.__yPos = 720 - this.__height / 2;
      }
      else if(this.__yPos - this.__height / 2 < 0)
      {
         this.__yPos = this.__height / 2;
      }
      this.__gpdb.paramSet("IMAGE_ANALYSIS.FOCUS_ASSIST.SAMPLE_Y",String(this.__yPos - this.__height / 2));
      this._y = 64 + this.__yPos;
   }
   function Enlarge()
   {
      if(this.__state == this.CONFIG_STATE)
      {
         this.__separation += 6;
         this.SetSeparation(this.__separation);
      }
      else
      {
         _global.VxError("FocusAssistMC::Enlarge() Attempt to change size while in RUN state");
      }
   }
   function Reduce()
   {
      if(this.__state == this.CONFIG_STATE)
      {
         this.__separation -= 6;
         this.SetSeparation(this.__separation);
      }
      else
      {
         _global.VxError("FocusAssistMC::Reduce() Attempt to change size while in RUN state");
      }
   }
   function MoveUp(rows)
   {
      if(this.__state == this.CONFIG_STATE)
      {
         this.__yPos -= rows;
         this.SetPosition(this.__yPos);
      }
      else
      {
         _global.VxError("FocusAssistMC::MoveUp() Attempt to change position while in RUN state");
      }
   }
   function MoveDown(rows)
   {
      if(this.__state == this.CONFIG_STATE)
      {
         this.__yPos += rows;
         this.SetPosition(this.__yPos);
      }
      else
      {
         _global.VxError("FocusAssistMC::MoveDown() Attempt to change position while in RUN state");
      }
   }
   function Activate(acceptInput)
   {
      _global.VxDebug("FocusAssistMC::Activate(" + acceptInput + ")");
      this.Show(acceptInput);
      if(acceptInput)
      {
         this.SetSeparation(this.__separation);
      }
      else
      {
         _global.VxForceRedraw();
      }
   }
   function Show(visible)
   {
      _global.VxDebug("  FocusAssistMC::Show(" + visible + ")");
      var _loc3_ = this.__gpdb.paramGet("GUI.SOFTKEY.IMAGE_ANALYSIS.ASSIST_METER");
      this._visible = visible;
      if(visible)
      {
         this.EnableConfigMode(true);
         if(_loc3_ == "Focus Assist" || _loc3_ == "Focus Assist Overlay" && this.__state == this.RUN_STATE)
         {
            GUI.OSD_Components.SplatManager.GetManager().ShowMeterSplat(true);
         }
      }
      else
      {
         GUI.OSD_Components.SplatManager.GetManager().ShowMeterSplat(false);
      }
   }
   function onInputEvent(name, value)
   {
      var _loc3_ = false;
      if(this.__state == this.RUN_STATE)
      {
         var _loc0_ = null;
         if((_loc0_ = name) !== GUI.OSD_Components.TabManager.EVENT_SELECT)
         {
            _global.VxDebug("FocusAssistMC::onInputEvent() RUN_STATE, ignoring input.");
         }
         else if(value == "true")
         {
            this.EnableConfigMode(true);
            _loc3_ = true;
         }
      }
      else
      {
         switch(name)
         {
            case GUI.OSD_Components.TabManager.EVENT_EXIT:
               break;
            case GUI.OSD_Components.TabManager.EVENT_SELECT:
               if(value == "true")
               {
                  this.EnableConfigMode(false);
                  _loc3_ = true;
               }
               break;
            case GUI.OSD_Components.TabManager.EVENT_RIGHT:
               if(value == "1")
               {
                  this.Enlarge();
                  _loc3_ = true;
               }
               break;
            case GUI.OSD_Components.TabManager.EVENT_LEFT:
               if(value == "1")
               {
                  this.Reduce();
                  _loc3_ = true;
               }
               break;
            case GUI.OSD_Components.TabManager.EVENT_UP:
               if(value == "1")
               {
                  this.MoveDown(4);
                  _loc3_ = true;
               }
               break;
            case GUI.OSD_Components.TabManager.EVENT_DOWN:
               if(value == "1")
               {
                  this.MoveUp(4);
                  _loc3_ = true;
               }
               break;
            case GUI.OSD_Components.TabManager.EVENT_CCW:
               if(value == "1")
               {
                  this.MoveUp(12);
                  _loc3_ = true;
               }
               break;
            case GUI.OSD_Components.TabManager.EVENT_CW:
               if(value == "1")
               {
                  this.MoveDown(12);
                  _loc3_ = true;
               }
         }
      }
      return _loc3_;
   }
}
