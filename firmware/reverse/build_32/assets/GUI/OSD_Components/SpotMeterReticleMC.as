class GUI.OSD_Components.SpotMeterReticleMC extends MovieClip
{
   var BOTTOM;
   var CENTER;
   var LEFT;
   var RIGHT;
   var TOP;
   var __gpdb;
   var size;
   var __yPos = 0;
   var __xPos = 0;
   var __height = 720;
   var __width = 1280;
   var __sizePercent = 2;
   function SpotMeterReticleMC()
   {
      super();
      _global.VxDebug("...........................................................................CTOR SpotMeterReticleMC()");
      this.__gpdb = _global.gpdb;
      this.SetSize(Number(this.__gpdb.paramGet("IMAGE_ANALYSIS.SPOT_METER.SIZE")));
   }
   function Activate(enable)
   {
      _global.VxDebug("  SpotMeterReticleMC::Activate(" + enable + ")");
      this._visible = enable;
   }
   function SetSize(sizePercent)
   {
      if(sizePercent == undefined || sizePercent == NaN)
      {
         sizePercent = 2;
      }
      this.__sizePercent = sizePercent;
      if(this.__sizePercent < 1)
      {
         this.__sizePercent = 1;
      }
      else if(this.__sizePercent > 4)
      {
         this.__sizePercent = 4;
      }
      this.size = 720 * this.__sizePercent / 100;
      this.TOP._x = - this.size / 2 - 4 + this.__xPos;
      this.TOP._y = - this.size / 2 - 4 + this.__yPos;
      this.BOTTOM._x = - this.size / 2 - 4 + this.__xPos;
      this.BOTTOM._y = this.size / 2 + this.__yPos;
      this.LEFT._x = - this.size / 2 - 4 + this.__xPos;
      this.LEFT._y = - this.size / 2 - 2 + this.__yPos;
      this.RIGHT._x = this.size / 2 + this.__xPos;
      this.RIGHT._y = - this.size / 2 - 2 + this.__yPos;
      this.CENTER._x = (- this.size) / 2 + this.__xPos;
      this.CENTER._y = (- this.size) / 2 + this.__yPos;
      this.TOP._width = this.size + 8;
      this.BOTTOM._width = this.size + 8;
      this.LEFT._height = this.size + 4;
      this.RIGHT._height = this.size + 4;
      this.CENTER._width = this.size;
      this.CENTER._height = this.size;
      this.__gpdb.paramSet("IMAGE_ANALYSIS.SPOT_METER.POSITION_X",String(Math.abs((this.__xPos + 640) / 1280 * 100)));
      this.__gpdb.paramSet("IMAGE_ANALYSIS.SPOT_METER.POSITION_Y",String(Math.abs((this.__yPos + 360) / 720 * 100)));
      this.__gpdb.paramSet("IMAGE_ANALYSIS.SPOT_METER.SIZE",this.__sizePercent.toString());
   }
   function SetPosition(xPos, yPos)
   {
      this.__yPos = yPos;
      this.__xPos = xPos;
      if(this.__yPos > 360 - this.size * 2 - 4)
      {
         this.__yPos = 360 - this.size * 2 - 4;
      }
      else if(this.__yPos < -360 + this.size * 2 + 4)
      {
         this.__yPos = -360 + this.size * 2 + 4;
      }
      if(this.__xPos > 640 - this.size * 2 - 4)
      {
         this.__xPos = 640 - this.size * 2 - 4;
      }
      else if(this.__xPos < -640 + this.size * 2 + 4)
      {
         this.__xPos = -640 + this.size * 2 + 4;
      }
   }
   function Enlarge()
   {
      this.__sizePercent += 1;
      this.SetPosition(this.__xPos,this.__yPos);
      this.SetSize(this.__sizePercent);
   }
   function Reduce()
   {
      this.__sizePercent -= 1;
      this.SetPosition(this.__xPos,this.__yPos);
      this.SetSize(this.__sizePercent);
   }
   function MoveUp(rows)
   {
      this.__yPos -= rows;
      this.SetPosition(this.__xPos,this.__yPos);
      this.SetSize(this.__sizePercent);
   }
   function MoveDown(rows)
   {
      this.__yPos += rows;
      this.SetPosition(this.__xPos,this.__yPos);
      this.SetSize(this.__sizePercent);
   }
   function MoveRight(rows)
   {
      this.__xPos += rows;
      this.SetPosition(this.__xPos,this.__yPos);
      this.SetSize(this.__sizePercent);
   }
   function MoveLeft(rows)
   {
      this.__xPos -= rows;
      this.SetPosition(this.__xPos,this.__yPos);
      this.SetSize(this.__sizePercent);
   }
   function onInputEvent(name, value)
   {
      var _loc3_ = false;
      _global.VxDebug("....SpotMeterReticleMC::onInputEvent(): " + name + "," + value);
      switch(name)
      {
         case GUI.OSD_Components.TabManager.EVENT_EXIT:
         case GUI.OSD_Components.TabManager.EVENT_SELECT:
            break;
         case GUI.OSD_Components.TabManager.EVENT_RIGHT:
            if(value == "1")
            {
               this.MoveRight(this.size + 2);
               _loc3_ = true;
            }
            break;
         case GUI.OSD_Components.TabManager.EVENT_LEFT:
            if(value == "1")
            {
               this.MoveLeft(this.size + 2);
               _loc3_ = true;
            }
            break;
         case GUI.OSD_Components.TabManager.EVENT_UP:
            if(value == "1")
            {
               this.MoveUp(this.size + 2);
               _loc3_ = true;
            }
            break;
         case GUI.OSD_Components.TabManager.EVENT_DOWN:
            if(value == "1")
            {
               this.MoveDown(this.size + 2);
               _loc3_ = true;
            }
            break;
         case GUI.OSD_Components.TabManager.EVENT_CCW:
            if(value == "1")
            {
               this.Reduce();
               _loc3_ = true;
            }
            break;
         case GUI.OSD_Components.TabManager.EVENT_CW:
            if(value == "1")
            {
               this.Enlarge();
               _loc3_ = true;
            }
      }
      return _loc3_;
   }
}
