class GUI.OSD_Components.ModelView
{
   var __scaleHD2D;
   var __gr;
   var __thickness = 1;
   function ModelView(parent, displayPixelWidth, recordWidth, sensorWidth)
   {
      _global.VxDebug("...........................................................................CTOR ModelView()");
      this.Create16x9CraphicsPlane(parent,displayPixelWidth,recordWidth,sensorWidth);
   }
   function Create16x9CraphicsPlane(mc, displayPixelWidth, recordWidth, sensorWidth)
   {
      var _loc9_ = sensorWidth / recordWidth;
      var _loc6_ = displayPixelWidth / sensorWidth;
      this.__scaleHD2D = recordWidth / sensorWidth * (displayPixelWidth / 1920);
      var _loc3_ = Math.floor((sensorWidth - recordWidth) / 2 * _loc6_);
      var _loc5_ = Math.floor(_loc3_ / 16 * 9);
      this.__gr = new GUI.OSD_Components.Graphics(mc,mc.getNextHighestDepth());
      this.__gr.setOrigin(_loc3_,_loc5_);
   }
   function ScaleIt(n)
   {
      return Math.floor(n * this.__scaleHD2D);
   }
   function setColor(color)
   {
      this.__gr.setColor(color);
   }
   function setThick(thickness)
   {
      this.__thickness = thickness;
      this.__gr.setThick(thickness);
   }
   function clear()
   {
      this.__gr.clear();
   }
   function Translate(point)
   {
      return this.ScaleIt(point);
   }
   function drawRect(xHD, yHD, wHD, hHD)
   {
      var _loc4_ = this.ScaleIt(xHD) - this.__thickness;
      var _loc2_ = this.ScaleIt(yHD) - this.__thickness;
      var _loc5_ = this.ScaleIt(wHD) + this.__thickness + 1;
      var _loc3_ = this.ScaleIt(hHD) + this.__thickness + 1;
      this.__gr.drawRect(_loc4_,_loc2_,_loc5_,_loc3_);
   }
   function drawLine(x1HD, y1HD, x2HD, y2HD)
   {
      var _loc5_ = this.ScaleIt(x1HD);
      var _loc3_ = this.ScaleIt(y1HD);
      var _loc4_ = this.ScaleIt(x2HD);
      var _loc2_ = this.ScaleIt(y2HD);
      this.__gr.drawLine(_loc5_,_loc3_,_loc4_,_loc2_);
   }
}
