class GUI.OSD_Components.AspectBoxMC extends MovieClip
{
   var ASPECT_RATIO;
   var BOX_GRAPHIC;
   var BOX_HEIGHT;
   var BOX_ORIGIN;
   var BOX_WIDTH;
   var OFFSET_X;
   var OFFSET_Y;
   var __pixelHeight;
   var __pixelOffsetX;
   var __pixelOffsetY;
   var __pixelWidth;
   function AspectBoxMC()
   {
      super();
   }
   function Configure(width, height, offsetX, offsetY)
   {
      this.__pixelWidth = width;
      this.__pixelHeight = height;
      this.__pixelOffsetX = offsetX;
      this.__pixelOffsetY = offsetY;
      this.UpdatePosition();
      this.UpdateOffsets();
      this.UpdateAspectText();
      this.UpdateOffsetText();
   }
   function UpdatePosition()
   {
      this.BOX_ORIGIN.text = "(" + this.__pixelOffsetX + ", " + this.__pixelOffsetY + ")";
      this._x = this.__pixelOffsetX;
      this._y = this.__pixelOffsetY + 64;
      this.BOX_GRAPHIC._width = this.__pixelWidth;
      this.BOX_GRAPHIC._height = this.__pixelHeight;
      this.BOX_WIDTH.text = this.__pixelWidth + " px";
      this.BOX_WIDTH._x = this.__pixelWidth / 2 - this.BOX_WIDTH._width / 2;
      this.BOX_WIDTH._y = this.__pixelHeight - this.BOX_WIDTH._height;
      this.BOX_HEIGHT.text = this.__pixelHeight + " px";
      this.BOX_HEIGHT._x = this.__pixelWidth - this.BOX_HEIGHT._width - 10;
      this.BOX_HEIGHT._y = this.__pixelHeight / 2 + 20;
   }
   function UpdateOffsets()
   {
      this.OFFSET_Y._x = this.__pixelWidth / 2 - this.OFFSET_Y._width / 2;
      this.OFFSET_X._x = this._x >= this.OFFSET_X._width ? - this.OFFSET_X._width : - this._x;
      this.OFFSET_X._y = this.__pixelHeight / 2 - this.OFFSET_X._width / 2;
      this.OFFSET_Y._y = this._y - 64 >= this.OFFSET_Y._height ? - this.OFFSET_Y._height : - (this._y - 64);
   }
   function UpdateAspectText()
   {
      var _loc5_ = this.__pixelWidth / this.__pixelHeight;
      var _loc3_ = _global.ShowDecimalPlaces(_loc5_,2,true);
      var _loc4_;
      switch(_loc3_)
      {
         case "1.77":
            _loc4_ = "Aspect Ratio: " + _loc3_ + " = 16:9";
            break;
         case "1.55":
            _loc4_ = "Aspect Ratio: " + _loc3_ + " = 14:9";
            break;
         case "1.33":
            _loc4_ = "Aspect Ratio: " + _loc3_ + " = 4:3";
            break;
         default:
            _loc4_ = "Aspect Ratio: " + _loc3_;
      }
      this.ASPECT_RATIO.text = _loc4_;
      this.ASPECT_RATIO._x = this.__pixelWidth / 2 - this.ASPECT_RATIO._width / 2;
      this.ASPECT_RATIO._y = this.__pixelHeight / 2 - 20;
   }
   function UpdateOffsetText()
   {
      var _loc6_ = this.__pixelOffsetX != 0 ? this.__pixelOffsetX / (1280 - this.__pixelWidth) * 100 - 50 : 0;
      var _loc5_ = this.__pixelOffsetY != 0 ? this.__pixelOffsetY / (720 - this.__pixelHeight) * 100 - 50 : 0;
      var _loc4_ = _global.ShowDecimalPlaces(_loc6_,0,true);
      var _loc3_ = _global.ShowDecimalPlaces(_loc5_,0,true);
      this.OFFSET_X.text = "Horizontal\rOffset\r" + _loc4_ + "%";
      this.OFFSET_Y.text = "Vertical Offset " + _loc3_ + "%";
   }
}
