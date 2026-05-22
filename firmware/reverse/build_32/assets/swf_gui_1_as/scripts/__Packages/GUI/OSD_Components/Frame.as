class GUI.OSD_Components.Frame extends MovieClip
{
   var __gpdb;
   var __mc;
   var __mv;
   var __frameColor;
   var __frameAspect;
   var __resolution;
   var __safeA_X;
   var __safeA_Y;
   var __safeA_W;
   var __safeA_H;
   var __safeT_X;
   var __safeT_Y;
   var __safeT_W;
   var __safeT_H;
   static var __manager;
   var __hdWidth = 1920;
   var __hdHeight = 1080;
   var SENSOR_WIDTH = 2240;
   var SENSOR_HEIGHT = 1260;
   var WIDTH_SENSOR = 4480;
   var WIDTH_RECORD = 4096;
   var LINE_THICKNESS = 2;
   function Frame(parent, depth)
   {
      super();
      this.__gpdb = _global.gpdb;
      parent.createEmptyMovieClip("mcFrame",depth);
      this.__mc = parent.mcFrame;
      this.__mc._alpha = 100;
      this.__mv = new GUI.OSD_Components.ModelView(this.__mc,1280,this.WIDTH_RECORD,this.WIDTH_SENSOR);
      this.__frameColor = this.__gpdb.paramGet("GUI.OSD.RETICLE.TV_SAFE_AREA.COLOR");
      this.__frameAspect = this.__gpdb.paramGet("GUI.OSD.RETICLE.TV_SAFE_AREA.ASPECT");
      this.SetResolution(this.__gpdb.paramGet("PROJECT.MODE_MATRIX.RESOLUTION"));
      GUI.OSD_Components.Frame.__manager = this;
      this.addCallbacks();
      this.SetAspect(this.__frameAspect);
      this.SmartEnable();
   }
   static function GetManager()
   {
      if(GUI.OSD_Components.Frame.__manager === undefined)
      {
         throw new Error("Frame::getManager() Called before created");
      }
      return GUI.OSD_Components.Frame.__manager;
   }
   function addCallbacks()
   {
      var _loc2_ = mx.utils.Delegate.create(this,this.update);
      this.__gpdb.addCallback("GUI.OSD.RETICLE.TV_SAFE_AREA.ASPECT",_loc2_);
      this.__gpdb.addCallback("GUI.OSD.RETICLE.TV_SAFE_AREA.COLOR",_loc2_);
      this.__gpdb.addCallback("GUI.OSD.RETICLE.TV_SAFE_AREA.ENABLE",_loc2_);
      this.__gpdb.addCallback("GUI.OSD.RETICLE.TV_SAFE_AREA.CENTER_CURSOR.SHOW",_loc2_);
      this.__gpdb.addCallback("GUI.OSD.RETICLE.TV_SAFE_AREA.CENTER_CURSOR.STYLE",_loc2_);
      this.__gpdb.addCallback("GUI.OSD.RETICLE.TV_SAFE_AREA.ACTION.SHOW",_loc2_);
      this.__gpdb.addCallback("GUI.OSD.RETICLE.TV_SAFE_AREA.ACTION.STYLE",_loc2_);
      this.__gpdb.addCallback("GUI.OSD.RETICLE.TV_SAFE_AREA.TITLE.SHOW",_loc2_);
      this.__gpdb.addCallback("GUI.OSD.RETICLE.TV_SAFE_AREA.TITLE.STYLE",_loc2_);
      this.__gpdb.addCallback("IMAGE_ANALYSIS.MAGNIFICATION.ENABLE",_loc2_);
      this.__gpdb.addCallback("VIDEO.MONITOR.TEST_PATTERN.ENABLED",_loc2_);
      this.__gpdb.addCallback("VIDEO.PLAYBACK.STATE",_loc2_);
      this.__gpdb.addCallback("PROJECT.MODE_MATRIX.RESOLUTION",_loc2_);
      this.__gpdb.addCallback("GUI.OSD.RETICLE.TV_SAFE_AREA.USER_DEFINED.ACTION.SIZE",_loc2_);
      this.__gpdb.addCallback("GUI.OSD.RETICLE.TV_SAFE_AREA.USER_DEFINED.ACTION.ASPECT",_loc2_);
      this.__gpdb.addCallback("GUI.OSD.RETICLE.TV_SAFE_AREA.USER_DEFINED.ACTION.OFFSET.WIDTH",_loc2_);
      this.__gpdb.addCallback("GUI.OSD.RETICLE.TV_SAFE_AREA.USER_DEFINED.ACTION.OFFSET.HEIGHT",_loc2_);
      this.__gpdb.addCallback("GUI.OSD.RETICLE.TV_SAFE_AREA.USER_DEFINED.TITLE.SIZE",_loc2_);
      this.__gpdb.addCallback("GUI.OSD.RETICLE.TV_SAFE_AREA.USER_DEFINED.TITLE.ASPECT",_loc2_);
      this.__gpdb.addCallback("GUI.OSD.RETICLE.TV_SAFE_AREA.USER_DEFINED.TITLE.OFFSET.WIDTH",_loc2_);
      this.__gpdb.addCallback("GUI.OSD.RETICLE.TV_SAFE_AREA.USER_DEFINED.TITLE.OFFSET.HEIGHT",_loc2_);
   }
   function update(name, value)
   {
      switch(name)
      {
         case "GUI.OSD.RETICLE.TV_SAFE_AREA.ASPECT":
            this.SetAspect(value);
            break;
         case "GUI.OSD.RETICLE.TV_SAFE_AREA.COLOR":
            this.SetColor(value);
            break;
         case "PROJECT.MODE_MATRIX.RESOLUTION":
            this.SetResolution(value);
            break;
         case "GUI.OSD.RETICLE.TV_SAFE_AREA.ENABLE":
         case "IMAGE_ANALYSIS.MAGNIFICATION.ENABLE":
         case "VIDEO.MONITOR.TEST_PATTERN.ENABLED":
         case "VIDEO.PLAYBACK.STATE":
            this.SmartEnable();
            break;
         case "GUI.OSD.RETICLE.TV_SAFE_AREA.CENTER_CURSOR.SHOW":
         case "GUI.OSD.RETICLE.TV_SAFE_AREA.CENTER_CURSOR.STYLE":
         case "GUI.OSD.RETICLE.TV_SAFE_AREA.ACTION.SHOW":
         case "GUI.OSD.RETICLE.TV_SAFE_AREA.ACTION.STYLE":
         case "GUI.OSD.RETICLE.TV_SAFE_AREA.TITLE.SHOW":
         case "GUI.OSD.RETICLE.TV_SAFE_AREA.TITLE.STYLE":
            this.Render();
            break;
         case "GUI.OSD.RETICLE.TV_SAFE_AREA.USER_DEFINED.ACTION.SIZE":
         case "GUI.OSD.RETICLE.TV_SAFE_AREA.USER_DEFINED.ACTION.ASPECT":
         case "GUI.OSD.RETICLE.TV_SAFE_AREA.USER_DEFINED.ACTION.OFFSET.WIDTH":
         case "GUI.OSD.RETICLE.TV_SAFE_AREA.USER_DEFINED.ACTION.OFFSET.HEIGHT":
         case "GUI.OSD.RETICLE.TV_SAFE_AREA.USER_DEFINED.TITLE.SIZE":
         case "GUI.OSD.RETICLE.TV_SAFE_AREA.USER_DEFINED.TITLE.ASPECT":
         case "GUI.OSD.RETICLE.TV_SAFE_AREA.USER_DEFINED.TITLE.OFFSET.WIDTH":
         case "GUI.OSD.RETICLE.TV_SAFE_AREA.USER_DEFINED.TITLE.OFFSET.HEIGHT":
            this.SetAspect(this.__frameAspect);
      }
   }
   function SmartEnable()
   {
      var _loc4_ = this.__gpdb.paramGetBoolean("GUI.OSD.RETICLE.TV_SAFE_AREA.ENABLE");
      var _loc6_ = this.__gpdb.paramGetBoolean("IMAGE_ANALYSIS.MAGNIFICATION.ENABLE");
      var _loc5_ = this.__gpdb.paramGetBoolean("VIDEO.MONITOR.TEST_PATTERN.ENABLED");
      var _loc3_ = "IDLE" != this.__gpdb.paramGet("VIDEO.PLAYBACK.STATE");
      var _loc2_ = _loc4_ && !_loc5_ && !_loc3_;
      this.Show(_loc2_);
   }
   function ForceRedraw()
   {
      this.Render();
   }
   function SetColor(color)
   {
      this.__frameColor = color;
      this.Render();
   }
   function SetResolution(resolution)
   {
      this.__resolution = resolution;
      switch(this.__resolution)
      {
         case "4.5K":
         case "4KOS":
            this.__mv = new GUI.OSD_Components.ModelView(this.__mc,1280,4480,4480);
            this.__hdWidth = 1920;
            this.__hdHeight = 1080;
            break;
         case "4K2:1":
         case "3K2:1":
         case "2K2:1":
            this.__mv = new GUI.OSD_Components.ModelView(this.__mc,1280,4096,4096);
            this.__hdWidth = 1920;
            this.__hdHeight = 960;
            break;
         case "4KHS":
            this.__mv = new GUI.OSD_Components.ModelView(this.__mc,1280,4096,4096);
            this.__hdWidth = 1920;
            this.__hdHeight = 810;
            break;
         case "4K40":
            this.__mv = new GUI.OSD_Components.ModelView(this.__mc,1280,4096,4096);
            this.__hdWidth = 1920;
            this.__hdHeight = 796;
            break;
         case "4KHD":
         case "RGB1080P":
         case "RGB720P":
            this.__mv = new GUI.OSD_Components.ModelView(this.__mc,1280,4096,4096);
            this.__hdWidth = 1920;
            this.__hdHeight = 1080;
            break;
         case "4K":
         case "3K":
         case "2K":
            this.__mv = new GUI.OSD_Components.ModelView(this.__mc,1280,4096,4096);
            this.__hdWidth = 1920;
            this.__hdHeight = 1080;
            break;
         case "4K1.2:1":
         case "3K1.2:1":
         case "2K1.2:1":
            this.__mv = new GUI.OSD_Components.ModelView(this.__mc,1280,4096,4096);
            this.__hdWidth = 1920;
            this.__hdHeight = 800;
            break;
         default:
            _global.VxError("Frame::SetResolution() ERROR! Unknown resolution, \'" + resolution + "\'. Ignoring.");
      }
      this.SetAspect(this.__frameAspect);
   }
   function Show(show)
   {
      if(show)
      {
         this.Render();
         this.__mc._visible = true;
      }
      else
      {
         this.__mc._visible = false;
      }
   }
   function Render()
   {
      var _loc2_ = "0xff0000";
      switch(this.__frameColor)
      {
         case "RED":
            _loc2_ = "0xff0000";
            break;
         case "YELLOW":
            _loc2_ = "0xffff00";
            break;
         case "WHITE":
            _loc2_ = "0xffffff";
            break;
         case "BLACK":
            _loc2_ = "0x000000";
            break;
         case "BLUE":
            _loc2_ = "0x0000ff";
            break;
         default:
            _loc2_ = "0xffffff";
      }
      this.__mv.clear();
      this.__mv.setColor(_loc2_);
      this.__mv.setThick(this.LINE_THICKNESS);
      if(this.__gpdb.paramGetBoolean("GUI.OSD.RETICLE.TV_SAFE_AREA.CENTER_CURSOR.SHOW"))
      {
         var _loc3_ = this.__gpdb.paramGet("GUI.OSD.RETICLE.TV_SAFE_AREA.CENTER_CURSOR.STYLE");
         this.DrawNamedFrame("CENTER",_loc3_);
      }
      if(this.__gpdb.paramGetBoolean("GUI.OSD.RETICLE.TV_SAFE_AREA.ACTION.SHOW"))
      {
         _loc3_ = this.__gpdb.paramGet("GUI.OSD.RETICLE.TV_SAFE_AREA.ACTION.STYLE");
         this.DrawNamedFrame("SAFE_ACTION",_loc3_);
      }
      if(this.__gpdb.paramGetBoolean("GUI.OSD.RETICLE.TV_SAFE_AREA.TITLE.SHOW"))
      {
         _loc3_ = this.__gpdb.paramGet("GUI.OSD.RETICLE.TV_SAFE_AREA.TITLE.STYLE");
         this.DrawNamedFrame("SAFE_TITLE",_loc3_);
      }
   }
   function SetAspect(aspect)
   {
      var _loc12_ = undefined;
      var _loc15_ = undefined;
      var _loc14_ = undefined;
      var _loc16_ = undefined;
      var _loc9_ = undefined;
      var _loc8_ = undefined;
      var _loc7_ = undefined;
      var _loc11_ = undefined;
      var _loc4_ = undefined;
      var _loc6_ = undefined;
      var _loc3_ = undefined;
      var _loc5_ = undefined;
      var _loc13_ = undefined;
      _loc9_ = 0.5;
      _loc8_ = 0.5;
      _loc7_ = 0.5;
      _loc11_ = 0.5;
      this.__frameAspect = aspect;
      switch(aspect)
      {
         case "16:9":
            _loc6_ = 1.7777;
            _loc5_ = 1.58;
            _loc4_ = 0.86;
            _loc3_ = 0.83;
            break;
         case "14:9":
            _loc6_ = 1.527;
            _loc5_ = 1.382;
            _loc4_ = 0.86;
            _loc3_ = 0.83;
            break;
         case "4:3":
            _loc6_ = 1.3333;
            _loc5_ = 1.284;
            _loc4_ = 0.86;
            _loc3_ = 0.83;
            break;
         case "1.85":
            _loc6_ = 1.85;
            _loc5_ = 1.85;
            _loc4_ = 0.88;
            _loc3_ = 0.85;
            break;
         case "2.39":
            _loc6_ = 2.39;
            _loc5_ = 2.39;
            _loc4_ = 0.68;
            _loc3_ = 0.65;
            break;
         case "USER_DEFINED":
            _loc4_ = this.__gpdb.paramGetNumber("GUI.OSD.RETICLE.TV_SAFE_AREA.USER_DEFINED.ACTION.SIZE");
            _loc6_ = this.__gpdb.paramGetNumber("GUI.OSD.RETICLE.TV_SAFE_AREA.USER_DEFINED.ACTION.ASPECT");
            _loc9_ = this.__gpdb.paramGetNumber("GUI.OSD.RETICLE.TV_SAFE_AREA.USER_DEFINED.ACTION.OFFSET.WIDTH");
            _loc8_ = this.__gpdb.paramGetNumber("GUI.OSD.RETICLE.TV_SAFE_AREA.USER_DEFINED.ACTION.OFFSET.HEIGHT");
            _loc3_ = this.__gpdb.paramGetNumber("GUI.OSD.RETICLE.TV_SAFE_AREA.USER_DEFINED.TITLE.SIZE");
            _loc5_ = this.__gpdb.paramGetNumber("GUI.OSD.RETICLE.TV_SAFE_AREA.USER_DEFINED.TITLE.ASPECT");
            _loc7_ = this.__gpdb.paramGetNumber("GUI.OSD.RETICLE.TV_SAFE_AREA.USER_DEFINED.TITLE.OFFSET.WIDTH");
            _loc11_ = this.__gpdb.paramGetNumber("GUI.OSD.RETICLE.TV_SAFE_AREA.USER_DEFINED.TITLE.OFFSET.HEIGHT");
            _loc13_ = this.__gpdb.paramGetNumber("CAMERA.SLAVE_MODE_ACTIVE");
            break;
         default:
            _global.VxError("Frame::SetAspect(): Unknown aspect \'" + aspect + "\'");
            _loc6_ = 1.7777;
            _loc5_ = 1.7777;
            _loc4_ = 0.5;
            _loc3_ = 0.5;
      }
      switch(this.__resolution)
      {
         case "4K2:1":
         case "3K2:1":
         case "2K2:1":
            var _loc0_ = null;
            if((_loc0_ = aspect) === "2.39")
            {
               _loc4_ = 0.83;
               _loc3_ = 0.8;
            }
            break;
         case "4K1.2:1":
         case "3K1.2:1":
         case "2K1.2:1":
            switch(aspect)
            {
               case "1.85":
               case "2.39":
                  _loc4_ = 1;
                  _loc3_ = 0.97;
            }
            break;
         case "4.5K":
            switch(aspect)
            {
               case "1.85":
               case "2.39":
                  _loc4_ = 0.83;
                  _loc3_ = 0.8;
            }
      }
      _loc15_ = (1 - _loc4_) / 2;
      _loc12_ = (1 - _loc4_ * this.__hdHeight * _loc6_ / this.__hdWidth) / 2;
      _loc16_ = (1 - _loc3_) / 2;
      _loc14_ = (1 - _loc3_ * this.__hdHeight * _loc5_ / this.__hdWidth) / 2;
      this.__safeA_X = Math.floor(_loc12_ * this.__hdWidth);
      this.__safeA_Y = Math.floor(_loc15_ * this.__hdHeight);
      this.__safeA_W = this.__hdWidth - this.__safeA_X * 2;
      this.__safeA_H = this.__hdHeight - this.__safeA_Y * 2;
      if(_loc13_ == 2)
      {
         _loc9_ = 1 - _loc9_;
         _loc8_ = 1 - _loc8_;
      }
      if(_loc9_ != 0.5 || _loc8_ != 0.5)
      {
         this.__safeA_X = Math.floor(_loc12_ * 2 * this.__hdWidth * _loc9_);
         this.__safeA_Y = Math.floor(_loc15_ * 2 * this.__hdHeight * _loc8_);
      }
      this.__safeA_X += (1920 - this.__hdWidth) / 2;
      this.__safeA_Y += (1080 - this.__hdHeight) / 2;
      this.__safeT_X = Math.floor(_loc14_ * this.__hdWidth);
      this.__safeT_Y = Math.floor(_loc16_ * this.__hdHeight);
      this.__safeT_W = this.__hdWidth - this.__safeT_X * 2;
      this.__safeT_H = this.__hdHeight - this.__safeT_Y * 2;
      if(_loc13_ == 2)
      {
         _loc7_ = 1 - _loc7_;
         _loc11_ = 1 - _loc11_;
      }
      if(_loc7_ != 0.5 || _loc11_ != 0.5)
      {
         this.__safeT_X = Math.floor(_loc14_ * 2 * this.__hdWidth * _loc7_);
         this.__safeT_Y = Math.floor(_loc16_ * 2 * this.__hdHeight * _loc11_);
      }
      this.__safeT_X += (1920 - this.__hdWidth) / 2;
      this.__safeT_Y += (1080 - this.__hdHeight) / 2;
      this.Render();
      this.WriteGuideToPDB1(this.__safeA_X,this.__safeA_Y,this.__safeA_W,this.__safeA_H);
      this.WriteGuideToPDB2(this.__safeT_X,this.__safeT_Y,this.__safeT_W,this.__safeT_H);
   }
   function DrawNamedFrame(name, style)
   {
      var _loc5_ = 1;
      var _loc4_ = 1;
      var _loc2_ = 1;
      var _loc3_ = 1;
      var _loc10_ = 1;
      var _loc9_ = 1;
      var _loc6_ = 80;
      switch(name)
      {
         case "SAFE_ACTION":
            _loc5_ = this.__safeA_X;
            _loc4_ = this.__safeA_Y;
            _loc2_ = this.__safeA_W;
            _loc3_ = this.__safeA_H;
            if(this.__frameAspect == "1.85" || this.__frameAspect == "2.39")
            {
               style = "RECTANGLE";
            }
            break;
         case "SAFE_TITLE":
            _loc5_ = this.__safeT_X;
            _loc4_ = this.__safeT_Y;
            _loc2_ = this.__safeT_W;
            _loc3_ = this.__safeT_H;
            break;
         case "CENTER":
            _loc2_ = _loc6_;
            _loc3_ = _loc6_;
            switch(style)
            {
               case "CROSS":
               default:
                  _loc5_ = this.__hdWidth / 2 + (1920 - this.__hdWidth) / 2;
                  _loc4_ = this.__hdHeight / 2 + (1080 - this.__hdHeight) / 2;
                  break;
               case "RECTANGLE":
                  _loc5_ = this.__hdWidth / 2 + (1920 - this.__hdWidth) / 2 - _loc2_ / 2;
                  _loc4_ = this.__hdHeight / 2 + (1080 - this.__hdHeight) / 2 - _loc3_ / 2;
            }
      }
      this.DrawFrame(_loc5_,_loc4_,_loc2_,_loc3_,style);
   }
   function DrawFrame(x, y, width, height, shape)
   {
      var _loc2_ = this.LINE_THICKNESS;
      switch(shape)
      {
         case "CORNERS":
            if(!this.__gpdb.paramGetBoolean("IMAGE_ANALYSIS.MAGNIFICATION.ENABLE"))
            {
               var _loc8_ = width / 10;
               var _loc11_ = height / 10;
               var _loc12_ = x - _loc2_ + 1;
               var _loc10_ = y - _loc2_;
               this.__mv.drawLine(_loc12_,_loc10_,_loc12_ + _loc8_,_loc10_);
               this.__mv.drawLine(_loc12_,_loc10_,_loc12_,_loc10_ + _loc11_);
               var _loc7_ = x + width - 1 + _loc2_ + 1;
               var _loc9_ = y - _loc2_;
               this.__mv.drawLine(_loc7_,_loc9_,_loc7_ - _loc8_,_loc9_);
               this.__mv.drawLine(_loc7_,_loc9_,_loc7_,_loc9_ + _loc11_);
               var _loc16_ = x + width - 1 + _loc2_ + 1;
               var _loc13_ = y + height + _loc2_ + 1;
               this.__mv.drawLine(_loc16_,_loc13_,_loc16_,_loc13_ - _loc11_);
               this.__mv.drawLine(_loc16_,_loc13_,_loc7_ - _loc8_,_loc13_);
               var _loc15_ = x - _loc2_ + 1;
               var _loc14_ = y + height + _loc2_ + 1;
               this.__mv.drawLine(_loc15_,_loc14_,_loc15_ + _loc8_,_loc14_);
               this.__mv.drawLine(_loc15_,_loc14_,_loc15_,_loc14_ - _loc11_);
            }
            break;
         case "RECTANGLE":
            if(!this.__gpdb.paramGetBoolean("IMAGE_ANALYSIS.MAGNIFICATION.ENABLE"))
            {
               this.__mv.drawRect(x + _loc2_,y + _loc2_,width - _loc2_,height - _loc2_);
            }
            break;
         case "CROSS":
            if(this.__gpdb.paramGetBoolean("IMAGE_ANALYSIS.MAGNIFICATION.ENABLE"))
            {
               this.__mv.drawLine(x - width / 2,y - height / 2,x + width / 2,y + height / 2);
               this.__mv.drawLine(x - width / 2,y + height / 2,x + width / 2,y - height / 2);
            }
            else
            {
               this.__mv.drawLine(x,y - height / 2,x,y + height / 2);
               this.__mv.drawLine(x - width / 2,y,x + width / 2,y);
            }
      }
   }
   function WriteGuideToPDB2(x, y, width, height)
   {
      var _loc4_ = undefined;
      var _loc5_ = undefined;
      var _loc6_ = undefined;
      var _loc3_ = undefined;
      switch(this.__resolution)
      {
         case "4.5K":
            _loc4_ = Math.floor(2.3333333333333335 * x);
            _loc6_ = Math.floor(2.3333333333333335 * width);
            _loc5_ = Math.floor(1.737037037037037 * y);
            _loc3_ = Math.floor(1.737037037037037 * height);
            break;
         case "4KHD":
         case "RGB1080P":
         case "RGB720P":
            _loc4_ = Math.floor(2 * x);
            _loc6_ = Math.floor(2 * width);
            _loc5_ = Math.floor(2 * y);
            _loc3_ = Math.floor(2 * height);
            break;
         case "4KOS":
            _loc4_ = Math.floor(2.2666666666666666 * x);
            _loc6_ = Math.floor(2.2666666666666666 * width);
            _loc5_ = Math.floor(2.0148148148148146 * y);
            _loc3_ = Math.floor(2.0148148148148146 * height);
            break;
         case "4K40":
            _loc4_ = Math.floor(2 * x);
            _loc6_ = Math.floor(2 * width);
            _loc5_ = Math.floor(2.090452261306533 * y);
            _loc3_ = Math.floor(2.090452261306533 * height);
            break;
         case "4K":
            _loc4_ = Math.floor(2.1333333333333333 * x);
            _loc6_ = Math.floor(2.1333333333333333 * width);
            _loc5_ = Math.floor(2.1333333333333333 * y);
            _loc3_ = Math.floor(2.1333333333333333 * height);
            break;
         case "4K2:1":
            _loc4_ = Math.floor(2.1333333333333333 * x);
            _loc6_ = Math.floor(2.1333333333333333 * width);
            _loc5_ = Math.floor(2.1333333333333333 * y);
            _loc3_ = Math.floor(2.1333333333333333 * height);
            break;
         case "4KHS":
            _loc4_ = Math.floor(2.1333333333333333 * x);
            _loc6_ = Math.floor(2.1333333333333333 * width);
            _loc5_ = Math.floor(1.9666666666666666 * y);
            _loc3_ = Math.floor(1.9666666666666666 * height);
            break;
         case "3K":
            _loc4_ = Math.floor(1.6 * x);
            _loc6_ = Math.floor(1.6 * width);
            _loc5_ = Math.floor(1.6 * y);
            _loc3_ = Math.floor(1.6 * height);
            break;
         case "3K2:1":
            _loc4_ = Math.floor(1.6 * x);
            _loc6_ = Math.floor(1.6 * width);
            _loc5_ = Math.floor(1.6 * y);
            _loc3_ = Math.floor(1.6 * height);
            break;
         case "2K":
            _loc4_ = Math.floor(1.0666666666666667 * x);
            _loc6_ = Math.floor(1.0666666666666667 * width);
            _loc5_ = Math.floor(1.0666666666666667 * y);
            _loc3_ = Math.floor(1.0666666666666667 * height);
            break;
         case "2K2:1":
            _loc4_ = Math.floor(1.0666666666666667 * x);
            _loc6_ = Math.floor(1.0666666666666667 * width);
            _loc5_ = Math.floor(1.0666666666666667 * y);
            _loc3_ = Math.floor(1.0666666666666667 * height);
            break;
         case "2K1.2:1":
            _loc4_ = Math.floor(1.0666666666666667 * x);
            _loc6_ = Math.floor(1.0666666666666667 * width);
            _loc5_ = Math.floor(1.28 * y);
            _loc3_ = Math.floor(1.28 * height);
            break;
         case "3K1.2:1":
            _loc4_ = Math.floor(1.6 * x);
            _loc6_ = Math.floor(1.6 * width);
            _loc5_ = Math.floor(1.92 * y);
            _loc3_ = Math.floor(1.92 * height);
            break;
         case "4K1.2:1":
            _loc4_ = Math.floor(2.1333333333333333 * x);
            _loc6_ = Math.floor(2.1333333333333333 * width);
            _loc5_ = Math.floor(2.56 * y);
            _loc3_ = Math.floor(2.56 * height);
            break;
         default:
            _global.VxError("ERROR! Reticle::DrawNamedReticle() Unhandled resolution: " + this.__resolution);
            _loc4_ = 0;
            _loc6_ = 1920;
            _loc5_ = 0;
            _loc3_ = 1080;
      }
      this.__gpdb.paramSet("GUI.OSD.RETICLE.FRAME_GUIDE.DETAILS.XPOS2",_loc4_);
      this.__gpdb.paramSet("GUI.OSD.RETICLE.FRAME_GUIDE.DETAILS.YPOS2",_loc5_);
      this.__gpdb.paramSet("GUI.OSD.RETICLE.FRAME_GUIDE.DETAILS.WIDTH2",_loc6_);
      this.__gpdb.paramSet("GUI.OSD.RETICLE.FRAME_GUIDE.DETAILS.HEIGHT2",_loc3_);
   }
   function WriteGuideToPDB1(x, y, width, height)
   {
      var _loc4_ = undefined;
      var _loc5_ = undefined;
      var _loc6_ = undefined;
      var _loc3_ = undefined;
      switch(this.__resolution)
      {
         case "4.5K":
            _loc4_ = Math.floor(2.3333333333333335 * x);
            _loc6_ = Math.floor(2.3333333333333335 * width);
            _loc5_ = Math.floor(1.737037037037037 * y);
            _loc3_ = Math.floor(1.737037037037037 * height);
            break;
         case "4KHD":
         case "RGB1080P":
         case "RGB720P":
            _loc4_ = Math.floor(2 * x);
            _loc6_ = Math.floor(2 * width);
            _loc5_ = Math.floor(2 * y);
            _loc3_ = Math.floor(2 * height);
            break;
         case "4KOS":
            _loc4_ = Math.floor(2.2666666666666666 * x);
            _loc6_ = Math.floor(2.2666666666666666 * width);
            _loc5_ = Math.floor(2.0148148148148146 * y);
            _loc3_ = Math.floor(2.0148148148148146 * height);
            break;
         case "4K40":
            _loc4_ = Math.floor(2 * x);
            _loc6_ = Math.floor(2 * width);
            _loc5_ = Math.floor(2.090452261306533 * y);
            _loc3_ = Math.floor(2.090452261306533 * height);
            break;
         case "4K":
            _loc4_ = Math.floor(2.1333333333333333 * x);
            _loc6_ = Math.floor(2.1333333333333333 * width);
            _loc5_ = Math.floor(2.1333333333333333 * y);
            _loc3_ = Math.floor(2.1333333333333333 * height);
            break;
         case "4K2:1":
            _loc4_ = Math.floor(2.1333333333333333 * x);
            _loc6_ = Math.floor(2.1333333333333333 * width);
            _loc5_ = Math.floor(2.1333333333333333 * y);
            _loc3_ = Math.floor(2.1333333333333333 * height);
            break;
         case "4KHS":
            _loc4_ = Math.floor(2.1333333333333333 * x);
            _loc6_ = Math.floor(2.1333333333333333 * width);
            _loc5_ = Math.floor(1.9666666666666666 * y);
            _loc3_ = Math.floor(1.9666666666666666 * height);
            break;
         case "3K":
            _loc4_ = Math.floor(1.6 * x);
            _loc6_ = Math.floor(1.6 * width);
            _loc5_ = Math.floor(1.6 * y);
            _loc3_ = Math.floor(1.6 * height);
            break;
         case "3K2:1":
            _loc4_ = Math.floor(1.6 * x);
            _loc6_ = Math.floor(1.6 * width);
            _loc5_ = Math.floor(1.6 * y);
            _loc3_ = Math.floor(1.6 * height);
            break;
         case "2K":
            _loc4_ = Math.floor(1.0666666666666667 * x);
            _loc6_ = Math.floor(1.0666666666666667 * width);
            _loc5_ = Math.floor(1.0666666666666667 * y);
            _loc3_ = Math.floor(1.0666666666666667 * height);
            break;
         case "2K2:1":
            _loc4_ = Math.floor(1.0666666666666667 * x);
            _loc6_ = Math.floor(1.0666666666666667 * width);
            _loc5_ = Math.floor(1.0666666666666667 * y);
            _loc3_ = Math.floor(1.0666666666666667 * height);
            break;
         case "2K1.2:1":
            _loc4_ = Math.floor(1.0666666666666667 * x);
            _loc6_ = Math.floor(1.0666666666666667 * width);
            _loc5_ = Math.floor(1.28 * y);
            _loc3_ = Math.floor(1.28 * height);
            break;
         case "3K1.2:1":
            _loc4_ = Math.floor(1.6 * x);
            _loc6_ = Math.floor(1.6 * width);
            _loc5_ = Math.floor(1.92 * y);
            _loc3_ = Math.floor(1.92 * height);
            break;
         case "4K1.2:1":
            _loc4_ = Math.floor(2.1333333333333333 * x);
            _loc6_ = Math.floor(2.1333333333333333 * width);
            _loc5_ = Math.floor(2.56 * y);
            _loc3_ = Math.floor(2.56 * height);
            break;
         default:
            _global.VxError("ERROR! Reticle::DrawNamedReticle() Unhandled resolution: " + this.__resolution);
            _loc4_ = 0;
            _loc6_ = 1920;
            _loc5_ = 0;
            _loc3_ = 1080;
      }
      this.__gpdb.paramSet("GUI.OSD.RETICLE.FRAME_GUIDE.DETAILS.XPOS1",_loc4_);
      this.__gpdb.paramSet("GUI.OSD.RETICLE.FRAME_GUIDE.DETAILS.YPOS1",_loc5_);
      this.__gpdb.paramSet("GUI.OSD.RETICLE.FRAME_GUIDE.DETAILS.WIDTH1",_loc6_);
      this.__gpdb.paramSet("GUI.OSD.RETICLE.FRAME_GUIDE.DETAILS.HEIGHT1",_loc3_);
   }
}
