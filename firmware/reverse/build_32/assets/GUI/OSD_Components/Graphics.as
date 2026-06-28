class GUI.OSD_Components.Graphics extends MovieClip
{
   var __mc;
   var alpha;
   var color;
   var fill;
   var thick;
   function Graphics(parent, depth)
   {
      super();
      parent.createEmptyMovieClip("mcGraphics",depth);
      this.__mc = parent.mcGraphics;
      this.color = "0x000000";
      this.thick = 1;
      this.fill = "0x666666";
   }
   function clear()
   {
      this.__mc.clear();
   }
   function setOrigin(xOrig, yOrig)
   {
      this.__mc._x = xOrig;
      this.__mc._y = yOrig;
   }
   function setColor(_color)
   {
      this.color = _color;
   }
   function setThick(_thick)
   {
      this.thick = _thick;
   }
   function setFill(_fill)
   {
      this.fill = _fill;
   }
   function setAlpha(_alpha)
   {
      this.alpha = _alpha;
      this.__mc._alpha = _alpha;
   }
   function changeDepth(_depth)
   {
      this.__mc.swapDepths(_depth);
   }
   function drawLine(x1, y1, x2, y2)
   {
      this.__mc.lineStyle(this.thick,this.color);
      this.__mc.moveTo(x1,y1);
      this.__mc.lineTo(x2,y2);
   }
   function drawRect(x1, y1, width, height)
   {
      this.__mc.lineStyle(this.thick,this.color);
      this.__mc.moveTo(x1,y1);
      this.__mc.lineTo(x1 + width,y1);
      this.__mc.lineTo(x1 + width,y1 + height);
      this.__mc.lineTo(x1,y1 + height);
      this.__mc.lineTo(x1,y1);
   }
   function fillRect(x1, y1, width, height)
   {
      this.__mc.lineStyle(this.thick,this.color);
      this.__mc.moveTo(x1,y1);
      this.__mc.beginFill(this.fill);
      this.__mc.lineTo(x1 + width,y1);
      this.__mc.lineTo(x1 + width,y1 + height);
      this.__mc.lineTo(x1,y1 + height);
      this.__mc.lineTo(x1,y1);
      this.__mc.endFill();
   }
   function drawCurve(startX, startY, curveControlX, curveControlY, endX, endY)
   {
      this.__mc.lineStyle(this.thick,this.color);
      this.__mc.moveTo(startX,startY);
      this.__mc.curveTo(curveControlX,curveControlY,endX,endY);
   }
   function drawOval(x, y, width, height)
   {
      var _loc7_ = width * 0.70711;
      var _loc6_ = height * 0.70711;
      var _loc9_ = _loc7_ - (height - _loc6_) * width / height;
      var _loc8_ = _loc6_ - (width - _loc7_) * height / width;
      this.__mc.lineStyle(this.thick,this.color);
      this.__mc.moveTo(x + width,y);
      this.__mc.curveTo(x + width,y - _loc8_,x + _loc7_,y - _loc6_);
      this.__mc.curveTo(x + _loc9_,y - height,x,y - height);
      this.__mc.curveTo(x - _loc9_,y - height,x - _loc7_,y - _loc6_);
      this.__mc.curveTo(x - width,y - _loc8_,x - width,y);
      this.__mc.curveTo(x - width,y + _loc8_,x - _loc7_,y + _loc6_);
      this.__mc.curveTo(x - _loc9_,y + height,x,y + height);
      this.__mc.curveTo(x + _loc9_,y + height,x + _loc7_,y + _loc6_);
      this.__mc.curveTo(x + width,y + _loc8_,x + width,y);
   }
   function fillOval(x, y, width, height)
   {
      this.__mc.lineStyle(this.thick,this.color);
      this.__mc.moveTo(x,y + height / 2);
      this.__mc.beginFill(this.fill);
      this.__mc.curveTo(x,y,x + width / 2,y);
      this.__mc.curveTo(x + width,y,x + width,y + height / 2);
      this.__mc.curveTo(x + width,y + height,x + width / 2,y + height);
      this.__mc.curveTo(x,y + height,x,y + height / 2);
      this.__mc.endFill();
   }
   function drawCircle(r, x, y)
   {
      var _loc11_ = 22.5;
      this.__mc.moveTo(x + r,y);
      this.__mc.lineStyle(this.thick,this.color);
      var _loc8_ = Math.tan(_loc11_ * 3.141592653589793 / 180);
      var _loc2_ = 45;
      var _loc5_;
      var _loc4_;
      var _loc7_;
      var _loc6_;
      while(_loc2_ <= 360)
      {
         _loc5_ = r * Math.cos(_loc2_ * 3.141592653589793 / 180);
         _loc4_ = r * Math.sin(_loc2_ * 3.141592653589793 / 180);
         _loc7_ = _loc5_ + r * _loc8_ * Math.cos((_loc2_ - 90) * 3.141592653589793 / 180);
         _loc6_ = _loc4_ + r * _loc8_ * Math.sin((_loc2_ - 90) * 3.141592653589793 / 180);
         this.__mc.curveTo(_loc7_ + x,_loc6_ + y,_loc5_ + x,_loc4_ + y);
         _loc2_ += 45;
      }
   }
   function fillCircle(r, x, y)
   {
      var _loc11_ = 22.5;
      this.__mc.moveTo(x + r,y);
      this.__mc.lineStyle(this.thick,this.color);
      this.__mc.beginFill(this.fill);
      var _loc8_ = Math.tan(_loc11_ * 3.141592653589793 / 180);
      var _loc2_ = 45;
      var _loc5_;
      var _loc4_;
      var _loc7_;
      var _loc6_;
      while(_loc2_ <= 360)
      {
         _loc5_ = r * Math.cos(_loc2_ * 3.141592653589793 / 180);
         _loc4_ = r * Math.sin(_loc2_ * 3.141592653589793 / 180);
         _loc7_ = _loc5_ + r * _loc8_ * Math.cos((_loc2_ - 90) * 3.141592653589793 / 180);
         _loc6_ = _loc4_ + r * _loc8_ * Math.sin((_loc2_ - 90) * 3.141592653589793 / 180);
         this.__mc.curveTo(_loc7_ + x,_loc6_ + y,_loc5_ + x,_loc4_ + y);
         _loc2_ += 45;
      }
      this.__mc.endFill();
   }
   function drawHelix(r, x, y, styleMaker)
   {
      this.__mc.moveTo(x + r,y);
      this.__mc.lineStyle(this.thick,this.color);
      var _loc8_ = Math.tan(styleMaker * 3.141592653589793 / 180);
      var _loc2_ = 45;
      var _loc5_;
      var _loc4_;
      var _loc7_;
      var _loc6_;
      while(_loc2_ <= 360)
      {
         _loc5_ = r * Math.cos(_loc2_ * 3.141592653589793 / 180);
         _loc4_ = r * Math.sin(_loc2_ * 3.141592653589793 / 180);
         _loc7_ = _loc5_ + r * _loc8_ * Math.cos((_loc2_ - 90) * 3.141592653589793 / 180);
         _loc6_ = _loc4_ + r * _loc8_ * Math.sin((_loc2_ - 90) * 3.141592653589793 / 180);
         this.__mc.curveTo(_loc7_ + x,_loc6_ + y,_loc5_ + x,_loc4_ + y);
         _loc2_ += 45;
      }
   }
   function fillHelix(r, x, y, styleMaker)
   {
      this.__mc.moveTo(x + r,y);
      this.__mc.lineStyle(this.thick,this.color);
      this.__mc.beginFill(this.fill);
      var _loc8_ = Math.tan(styleMaker * 3.141592653589793 / 180);
      var _loc2_ = 45;
      var _loc5_;
      var _loc4_;
      var _loc7_;
      var _loc6_;
      while(_loc2_ <= 360)
      {
         _loc5_ = r * Math.cos(_loc2_ * 3.141592653589793 / 180);
         _loc4_ = r * Math.sin(_loc2_ * 3.141592653589793 / 180);
         _loc7_ = _loc5_ + r * _loc8_ * Math.cos((_loc2_ - 90) * 3.141592653589793 / 180);
         _loc6_ = _loc4_ + r * _loc8_ * Math.sin((_loc2_ - 90) * 3.141592653589793 / 180);
         this.__mc.curveTo(_loc7_ + x,_loc6_ + y,_loc5_ + x,_loc4_ + y);
         _loc2_ += 45;
      }
      this.__mc.endFill();
   }
   function drawGradientShape(r, x, y, styleMaker, col1, col2, fa1, fa2, matrixX, matrixY, matrixW, matrixH)
   {
      this.__mc.lineStyle(this.thick,this.color);
      this.__mc.moveTo(x + r,y);
      var _loc13_ = [col1,col2];
      var _loc11_ = [fa1,fa2];
      var _loc14_ = [7,255];
      var _loc12_ = {matrixType:"box",x:matrixX,y:matrixY,w:matrixW,h:matrixH,r:0.7853981633974483};
      this.__mc.beginGradientFill("linear",_loc13_,_loc11_,_loc14_,_loc12_);
      var _loc8_ = Math.tan(styleMaker * 3.141592653589793 / 180);
      var _loc2_ = 45;
      var _loc5_;
      var _loc4_;
      var _loc7_;
      var _loc6_;
      while(_loc2_ <= 360)
      {
         _loc5_ = r * Math.cos(_loc2_ * 3.141592653589793 / 180);
         _loc4_ = r * Math.sin(_loc2_ * 3.141592653589793 / 180);
         _loc7_ = _loc5_ + r * _loc8_ * Math.cos((_loc2_ - 90) * 3.141592653589793 / 180);
         _loc6_ = _loc4_ + r * _loc8_ * Math.sin((_loc2_ - 90) * 3.141592653589793 / 180);
         this.__mc.curveTo(_loc7_ + x,_loc6_ + y,_loc5_ + x,_loc4_ + y);
         _loc2_ += 45;
      }
      this.__mc.endFill();
   }
   function gradientRect(x1, y1, width, height, col1, col2, fa1, fa2, matrixX, matrixY, matrixW, matrixH)
   {
      this.__mc.lineStyle(this.thick,this.color);
      var _loc6_ = [col1,col2];
      var _loc4_ = [fa1,fa2];
      var _loc7_ = [7,255];
      var _loc5_ = {matrixType:"box",x:matrixX,y:matrixY,w:matrixW,h:matrixH,r:0.7853981633974483};
      this.__mc.moveTo(x1,y1);
      this.__mc.beginGradientFill("linear",_loc6_,_loc4_,_loc7_,_loc5_);
      this.__mc.lineTo(x1 + width,y1);
      this.__mc.lineTo(x1 + width,y1 + height);
      this.__mc.lineTo(x1,y1 + height);
      this.__mc.lineTo(x1,y1);
      this.__mc.endFill();
   }
   function drawHexagon(hexRadius, startX, startY)
   {
      var _loc4_ = hexRadius;
      var _loc7_ = 0.5 * _loc4_;
      var _loc5_ = Math.sqrt(hexRadius * hexRadius - 0.5 * hexRadius * (0.5 * hexRadius));
      this.__mc.lineStyle(this.thick,this.color,100);
      this.__mc.moveTo(startX,startY);
      this.__mc.lineTo(startX,_loc4_ + startY);
      this.__mc.lineTo(_loc5_ + startX,startY + _loc7_ + _loc4_);
      this.__mc.lineTo(2 * _loc5_ + startX,startY + _loc4_);
      this.__mc.lineTo(2 * _loc5_ + startX,startY);
      this.__mc.lineTo(_loc5_ + startX,startY - _loc7_);
      this.__mc.lineTo(startX,startY);
   }
   function fillHexagon(hexRadius, startX, startY)
   {
      var _loc4_ = hexRadius;
      var _loc7_ = 0.5 * _loc4_;
      var _loc5_ = Math.sqrt(hexRadius * hexRadius - 0.5 * hexRadius * (0.5 * hexRadius));
      this.__mc.lineStyle(this.thick,this.color,100);
      this.__mc.beginFill(this.fill);
      this.__mc.moveTo(startX,startY);
      this.__mc.lineTo(startX,_loc4_ + startY);
      this.__mc.lineTo(_loc5_ + startX,startY + _loc7_ + _loc4_);
      this.__mc.lineTo(2 * _loc5_ + startX,startY + _loc4_);
      this.__mc.lineTo(2 * _loc5_ + startX,startY);
      this.__mc.lineTo(_loc5_ + startX,startY - _loc7_);
      this.__mc.lineTo(startX,startY);
      this.__mc.endFill();
   }
}
