class GUI.OSD_Components.Reticle extends MovieClip
{
   var __gpdb;
   var __mc;
   var __mv;
   var __fguideAspects;
   var __fguideColors;
   var __resolution;
   var __fguideWidth;
   var __fguideHeight;
   static var __manager;
   var __centerYOf1080Frame = 540;
   var __fguideAspect = "2.35";
   var __fguideColor = "Red";
   var WIDTH_SENSOR = 4480;
   var WIDTH_RECORD = 4096;
   function Reticle(parent, depth)
   {
      super();
      this.__gpdb = _global.gpdb;
      parent.createEmptyMovieClip("mcReticle",depth);
      this.__mc = parent.mcReticle;
      this.__mc._alpha = 60;
      this.__mv = new GUI.OSD_Components.ModelView(this.__mc,1280,this.WIDTH_RECORD,this.WIDTH_SENSOR);
      this.__fguideAspects = new Array();
      this.__fguideAspects.push("NONE");
      this.__fguideAspects.push("4:3");
      this.__fguideAspects.push("16:9");
      this.__fguideAspects.push("2.39");
      this.__fguideAspects.push("1.85");
      this.__fguideAspects.push("RECORD_AREA");
      this.__fguideAspect = this.__fguideAspects[0];
      this.__fguideColors = new Array();
      this.__fguideColors.push("RED");
      this.__fguideColors.push("YELLOW");
      this.__fguideColors.push("BLACK");
      this.__fguideColors.push("BLUE");
      this.__fguideColor = this.__fguideColors[0];
      this.SetResolution(this.__gpdb.paramGet("PROJECT.MODE_MATRIX.RESOLUTION"));
      this.SetAspect(this.__gpdb.paramGet("GUI.OSD.RETICLE.FRAME_GUIDE.ASPECT"));
      this.SetColor(this.__gpdb.paramGet("GUI.OSD.RETICLE.FRAME_GUIDE.COLOR"));
      this.Render();
      GUI.OSD_Components.Reticle.__manager = this;
      this.SmartEnable();
      this.AddCallbacks();
   }
   static function GetManager()
   {
      if(GUI.OSD_Components.Reticle.__manager === undefined)
      {
         throw new Error("Reticle::GetManager() Called before created");
      }
      return GUI.OSD_Components.Reticle.__manager;
   }
   function AddCallbacks()
   {
      var _loc2_ = mx.utils.Delegate.create(this,this.Update);
      this.__gpdb.addCallback("GUI.OSD.RETICLE.FRAME_GUIDE.ASPECT",_loc2_);
      this.__gpdb.addCallback("GUI.OSD.RETICLE.FRAME_GUIDE.COLOR",_loc2_);
      this.__gpdb.addCallback("GUI.OSD.RETICLE.FRAME_GUIDE.ENABLE",_loc2_);
      this.__gpdb.addCallback("PROJECT.MODE_MATRIX.RESOLUTION",_loc2_);
      this.__gpdb.addCallback("IMAGE_ANALYSIS.MAGNIFICATION.ENABLE",_loc2_);
      this.__gpdb.addCallback("VIDEO.MONITOR.TEST_PATTERN.ENABLED",_loc2_);
      this.__gpdb.addCallback("VIDEO.PLAYBACK.STATE",_loc2_);
   }
   function Update(name, value)
   {
      switch(name)
      {
         case "GUI.OSD.RETICLE.FRAME_GUIDE.ASPECT":
            this.SetAspect(value);
            this.Render();
            break;
         case "PROJECT.MODE_MATRIX.RESOLUTION":
            this.SetResolution(value);
            this.Render();
            break;
         case "GUI.OSD.RETICLE.FRAME_GUIDE.COLOR":
            this.SetColor(value);
            this.Render();
            break;
         case "GUI.OSD.RETICLE.FRAME_GUIDE.ENABLE":
         case "IMAGE_ANALYSIS.MAGNIFICATION.ENABLE":
         case "VIDEO.MONITOR.TEST_PATTERN.ENABLED":
         case "VIDEO.PLAYBACK.STATE":
            this.SmartEnable();
      }
   }
   function SmartEnable()
   {
      var _loc3_ = this.__gpdb.paramGetBoolean("GUI.OSD.RETICLE.FRAME_GUIDE.ENABLE");
      var _loc2_ = this.__gpdb.paramGetBoolean("IMAGE_ANALYSIS.MAGNIFICATION.ENABLE");
      var _loc4_ = this.__gpdb.paramGetBoolean("VIDEO.MONITOR.TEST_PATTERN.ENABLED");
      var _loc6_ = "IDLE" != this.__gpdb.paramGet("VIDEO.PLAYBACK.STATE");
      var _loc5_ = _loc3_ && !_loc2_ && !_loc4_ && !_loc6_;
      this.Show(_loc5_);
   }
   function Show(show)
   {
      this.__centerYOf1080Frame = 540;
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
   function SetAspect(aspect)
   {
      this.__fguideAspect = aspect;
   }
   function SetColor(color)
   {
      this.__fguideColor = color;
   }
   function SetResolution(resolution)
   {
      this.__resolution = resolution;
   }
   function visible()
   {
      return this.__mc._visible;
   }
   function nextAspect()
   {
      var _loc2_ = this.__fguideAspects.shift();
      this.__fguideAspects.push(_loc2_);
      this.SetAspect(this.__fguideAspects[0]);
      this.Render();
   }
   function nextColor()
   {
      var _loc2_ = this.__fguideColors.shift();
      this.__fguideColors.push(_loc2_);
      this.__fguideColor = this.__fguideColors[0];
      this.Render();
   }
   function Render()
   {
      this.__mv.clear();
      switch(this.__fguideAspect)
      {
         case "4:3":
         case "16:9":
         case "1.85":
         case "2.35":
         case "2.39":
         case "RECORD_AREA":
            this.DrawNamedReticle(this.__fguideAspect);
            break;
         case "None":
         default:
            _global.VxError("Reticle::Render() Unknown reticle aspect: \'" + this.__fguideAspect + "\'");
      }
      var _loc3_ = this.__gpdb.paramGetBoolean("GUI.OSD.RETICLE.TV_SAFE_AREA.ENABLE");
      this.__gpdb.paramSet("GUI.OSD.RETICLE.TV_SAFE_AREA.ENABLE",false);
      this.__gpdb.paramSet("GUI.OSD.RETICLE.TV_SAFE_AREA.ENABLE",_loc3_);
   }
   function DrawNamedReticle(aspect)
   {
      var _loc7_ = this.HexColorString(this.__fguideColor);
      var _loc6_ = 3;
      switch(this.__resolution)
      {
         case "4K2:1":
         case "3K2:1":
         case "2K2:1":
            switch(aspect)
            {
               case "RECORD_AREA":
                  this.__fguideWidth = 1920;
                  this.__fguideHeight = 960;
                  break;
               case "4:3":
                  this.__fguideWidth = 1280;
                  this.__fguideHeight = 960;
                  break;
               case "16:9":
                  this.__fguideWidth = 1706;
                  this.__fguideHeight = 960;
                  break;
               case "1.85":
                  this.__fguideWidth = 1776;
                  this.__fguideHeight = 960;
                  break;
               case "2.35":
                  this.__fguideWidth = 1920;
                  this.__fguideHeight = this.__fguideWidth / 2.35;
                  break;
               case "2.39":
                  this.__fguideWidth = 1920;
                  this.__fguideHeight = this.__fguideWidth / 2.39;
                  break;
               case "4:3":
               case "16:9":
               default:
                  _global.VxError("Reticle::DrawNamedReticle(" + aspect + ") Unrecognized reticle for " + this.__resolution);
                  return undefined;
            }
            break;
         case "4KHS":
            switch(aspect)
            {
               case "RECORD_AREA":
                  this.__fguideHeight = 810.126582278481;
                  this.__fguideWidth = this.__fguideHeight * 2.37;
                  break;
               case "4:3":
                  this.__fguideHeight = 761.5189873417721;
                  this.__fguideWidth = this.__fguideHeight * 4 / 3;
                  break;
               case "16:9":
                  this.__fguideHeight = 761.5189873417721;
                  this.__fguideWidth = this.__fguideHeight * 16 / 9;
                  break;
               case "1.85":
                  this.__fguideHeight = 761.5189873417721;
                  this.__fguideWidth = this.__fguideHeight * 1.85;
                  break;
               case "2.39":
                  this.__fguideHeight = 761.5189873417721;
                  this.__fguideWidth = this.__fguideHeight * 2.39;
                  break;
               default:
                  _global.VxError("Reticle::DrawNamedReticle(" + aspect + ") Unrecognized reticle for " + this.__resolution);
                  return undefined;
            }
            break;
         case "4KHD":
         case "RGB1080P":
         case "RGB720P":
            switch(aspect)
            {
               case "RECORD_AREA":
                  this.__fguideWidth = 1800;
                  this.__fguideHeight = 1012;
                  break;
               case "4:3":
                  this.__fguideWidth = 1350;
                  this.__fguideHeight = 1012;
                  break;
               case "16:9":
                  this.__fguideWidth = 1800;
                  this.__fguideHeight = 1012;
                  break;
               case "1.85":
                  this.__fguideWidth = 1800;
                  this.__fguideHeight = 972;
                  break;
               case "2.35":
                  this.__fguideWidth = 1800;
                  this.__fguideHeight = this.__fguideWidth / 2.35;
                  break;
               case "2.39":
                  this.__fguideWidth = 1800;
                  this.__fguideHeight = this.__fguideWidth / 2.39;
                  break;
               default:
                  _global.VxError("Reticle::DrawNamedReticle(" + aspect + ") Unrecognized reticle for " + this.__resolution);
                  return undefined;
            }
            break;
         case "4K1.2:1":
         case "3K1.2:1":
         case "2K1.2:1":
            switch(aspect)
            {
               case "RECORD_AREA":
                  this.__fguideHeight = 803.347280334728;
                  this.__fguideWidth = this.__fguideHeight * 2.39;
                  break;
               case "4:3":
                  this.__fguideHeight = 755.1464435146443;
                  this.__fguideWidth = this.__fguideHeight * 4 / 3;
                  break;
               case "16:9":
                  this.__fguideHeight = 755.1464435146443;
                  this.__fguideWidth = this.__fguideHeight * 16 / 9;
                  break;
               case "1.85":
                  this.__fguideHeight = 755.1464435146443;
                  this.__fguideWidth = this.__fguideHeight * 1.85;
                  break;
               case "2.39":
                  this.__fguideHeight = 803.347280334728;
                  this.__fguideWidth = this.__fguideHeight * 2.39;
                  break;
               default:
                  _global.VxError("Reticle::DrawNamedReticle(" + aspect + ") Unrecognized reticle for " + this.__resolution);
                  return undefined;
            }
            break;
         case "4.5K":
            switch(aspect)
            {
               case "RECORD_AREA":
                  this.__fguideHeight = 896.9957081545064;
                  this.__fguideWidth = this.__fguideHeight * 2.33;
                  break;
               case "4:3":
                  this.__fguideHeight = 843.1759656652359;
                  this.__fguideWidth = this.__fguideHeight * 4 / 3;
                  break;
               case "16:9":
                  this.__fguideHeight = 843.1759656652359;
                  this.__fguideWidth = this.__fguideHeight * 16 / 9;
                  break;
               case "1.85":
                  this.__fguideHeight = 843.1759656652359;
                  this.__fguideWidth = this.__fguideHeight * 1.85;
                  break;
               case "2.39":
                  this.__fguideHeight = 843.1759656652359;
                  this.__fguideWidth = this.__fguideHeight * 2.39;
                  break;
               default:
                  _global.VxError("Reticle::DrawNamedReticle(" + aspect + ") Unrecognized reticle for " + this.__resolution);
                  return undefined;
            }
            break;
         case "4K":
         case "3K":
         case "2K":
            switch(aspect)
            {
               case "RECORD_AREA":
                  this.__fguideWidth = 1920;
                  this.__fguideHeight = 1080;
                  break;
               case "4:3":
                  this.__fguideWidth = 1349;
                  this.__fguideHeight = 1014;
                  break;
               case "16:9":
                  this.__fguideWidth = 1801;
                  this.__fguideHeight = 1014;
                  break;
               case "1.85":
                  this.__fguideWidth = 1873;
                  this.__fguideHeight = 1010;
                  break;
               case "2.35":
                  this.__fguideWidth = 1920;
                  this.__fguideHeight = this.__fguideWidth / 2.35;
                  break;
               case "2.39":
                  this.__fguideWidth = 1920;
                  this.__fguideHeight = this.__fguideWidth / 2.39;
                  break;
               default:
                  _global.VxError("Reticle::DrawNamedReticle(" + aspect + ") Unrecognized reticle for " + this.__resolution);
                  return undefined;
            }
            break;
         default:
            _global.VxError("Reticle::DrawNamedReticle(" + aspect + ") Unrecognized __resolution: " + this.__resolution);
            return undefined;
      }
      this.__mv.setColor(_loc7_);
      this.__mv.setThick(_loc6_);
      var _loc5_ = (1920 - this.__fguideWidth) / 2;
      var _loc4_ = (1080 - this.__fguideHeight) / 2;
      this.__mv.drawRect(_loc5_ + _loc6_,_loc4_ + _loc6_,this.__fguideWidth - 1,this.__fguideHeight - 3);
      if(this.__resolution == "4K2:1" || this.__resolution == "3K2:1" || this.__resolution == "2K2:1")
      {
         _loc4_ = (960 - this.__fguideHeight) / 2;
      }
      if(this.__resolution == "4KHD" || this.__resolution == "RGB1080P" || this.__resolution == "RGB720P")
      {
         _loc5_ = (1800 - this.__fguideWidth) / 2;
         _loc4_ = (1012 - this.__fguideHeight) / 2;
      }
      if(this.__resolution == "4.5K")
      {
         _loc5_ = (2090 - this.__fguideWidth) / 2;
         _loc4_ = (897 - this.__fguideHeight) / 2;
      }
      this.WriteGuideToPDB(aspect,_loc5_,_loc4_,this.__fguideWidth,this.__fguideHeight);
   }
   function HexColorString(colorName)
   {
      var _loc1_ = undefined;
      switch(colorName)
      {
         case "RED":
            _loc1_ = "0xff0000";
            break;
         case "YELLOW":
            _loc1_ = "0xffff00";
            break;
         case "WHITE":
            _loc1_ = "0xffffff";
            break;
         case "BLACK":
            _loc1_ = "0x000000";
            break;
         case "BLUE":
            _loc1_ = "0x0000ff";
            break;
         default:
            _loc1_ = "0xffffff";
      }
      return _loc1_;
   }
   function WriteGuideToPDB(guideName, x, y, width, height)
   {
      var _loc4_ = undefined;
      var _loc5_ = undefined;
      var _loc6_ = undefined;
      var _loc3_ = undefined;
      switch(this.__resolution)
      {
         case "4.5K":
            _loc4_ = Math.floor(2.1435406698564594 * x);
            _loc6_ = Math.floor(2.1435406698564594 * width);
            _loc5_ = Math.floor(2.091415830546265 * y);
            _loc3_ = Math.floor(2.091415830546265 * height);
            break;
         case "4KHD":
         case "RGB1080P":
         case "RGB720P":
            _loc4_ = Math.floor(2.1333333333333333 * x);
            _loc6_ = Math.floor(2.1333333333333333 * width);
            _loc5_ = Math.floor(2.1343873517786562 * y);
            _loc3_ = Math.floor(2.1343873517786562 * height);
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
            _loc4_ = 0;
            _loc6_ = 2048;
            _loc5_ = 0;
            _loc3_ = 1024;
            break;
         case "3K1.2:1":
            _loc4_ = 0;
            _loc6_ = 3072;
            _loc5_ = 0;
            _loc3_ = 1536;
            break;
         case "4K1.2:1":
            _loc4_ = 0;
            _loc6_ = 4096;
            _loc5_ = 0;
            _loc3_ = 2048;
            break;
         default:
            _global.VxError("ERROR! Reticle::DrawNamedReticle() Unhandled resolution: " + this.__resolution);
            _loc4_ = 0;
            _loc6_ = 1920;
            _loc5_ = 0;
            _loc3_ = 1080;
      }
      this.__gpdb.paramSet("GUI.OSD.RETICLE.FRAME_GUIDE.DETAILS.XPOS",_loc4_);
      this.__gpdb.paramSet("GUI.OSD.RETICLE.FRAME_GUIDE.DETAILS.YPOS",_loc5_);
      this.__gpdb.paramSet("GUI.OSD.RETICLE.FRAME_GUIDE.DETAILS.WIDTH",_loc6_);
      this.__gpdb.paramSet("GUI.OSD.RETICLE.FRAME_GUIDE.DETAILS.HEIGHT",_loc3_);
      this.__gpdb.paramSet("GUI.OSD.RETICLE.FRAME_GUIDE.DETAILS.GUIDE_NAME",guideName);
   }
   function scale720(n)
   {
      return Math.floor(n * 1.5);
   }
   function CenterOfFrame()
   {
      return this.__centerYOf1080Frame;
   }
}
