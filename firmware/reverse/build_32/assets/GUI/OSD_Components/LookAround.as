class GUI.OSD_Components.LookAround extends MovieClip
{
   var __gpdb;
   var __marqueHeight;
   var __marqueWidth;
   var __mc;
   static var __manager;
   var __aspect = "16:9";
   var __marqueColor = 0;
   var __marqueAlpha = 50;
   var __marqueLineColor = 0;
   var __marqueLineThickness = 1;
   var __recordWidth = 1170;
   var __recordHeight = 658;
   var __sensorWidth = 1280;
   var __sensorHeight = 720;
   function LookAround(parent, depth)
   {
      super();
      GUI.OSD_Components.LookAround.__manager = this;
      this.__gpdb = _global.gpdb;
      parent.createEmptyMovieClip("mcLookAround",depth);
      this.__mc = parent.mcLookAround;
      this.UpdateMarque();
      this.UpdateGeom();
      this.AddCallbacks();
      this.SmartEnable();
   }
   static function GetManager()
   {
      if(GUI.OSD_Components.LookAround.__manager === undefined)
      {
         _global.VxError("ERROR! LookAround::GetManager() called before being instantiated");
      }
      return GUI.OSD_Components.LookAround.__manager;
   }
   function AddCallbacks()
   {
      var _loc2_ = mx.utils.Delegate.create(this,this.Update);
      this.__gpdb.addCallback("GUI.USER_PREF.LOOKAROUND.COLOR",_loc2_);
      this.__gpdb.addCallback("GUI.USER_PREF.LOOKAROUND.ALPHA",_loc2_);
      this.__gpdb.addCallback("GUI.USER_PREF.LOOKAROUND.LINE_COLOR",_loc2_);
      this.__gpdb.addCallback("GUI.USER_PREF.LOOKAROUND.LINE_THICKNESS",_loc2_);
      this.__gpdb.addCallback("IMAGE_ANALYSIS.MAGNIFICATION.ENABLE",_loc2_);
      this.__gpdb.addCallback("VIDEO.MONITOR.TEST_PATTERN.ENABLED",_loc2_);
      this.__gpdb.addCallback("PROJECT.MODE_MATRIX.RESOLUTION",_loc2_);
      this.__gpdb.addCallback("GUI.OSD.RETICLE.FRAME_GUIDE.ASPECT",_loc2_);
      this.__gpdb.addCallback("GUI.OSD.RETICLE.FRAME_GUIDE.ASPECT",_loc2_);
      this.__gpdb.addCallback("VIDEO.PLAYBACK.STATE",_loc2_);
   }
   function Update(name, value)
   {
      switch(name)
      {
         case "IMAGE_ANALYSIS.MAGNIFICATION.ENABLE":
         case "VIDEO.MONITOR.TEST_PATTERN.ENABLED":
            this.SmartEnable();
            return;
         case "VIDEO.PLAYBACK.STATE":
            this.UpdateGeom();
            this.SmartEnable();
            return;
         case "PROJECT.MODE_MATRIX.RESOLUTION":
            this.UpdateGeom();
            return;
         case "GUI.OSD.RETICLE.FRAME_GUIDE.ASPECT":
            this.UpdateGeom();
            this.SmartEnable();
            return;
         case "GUI.USER_PREF.LOOKAROUND.COLOR":
         case "GUI.USER_PREF.LOOKAROUND.ALPHA":
         case "GUI.USER_PREF.LOOKAROUND.LINE_COLOR":
         case "GUI.USER_PREF.LOOKAROUND.LINE_THICKNESS":
            this.UpdateMarque();
            return;
         default:
            return;
      }
   }
   function SmartEnable()
   {
      var _loc4_ = "IDLE" != this.__gpdb.paramGet("VIDEO.PLAYBACK.STATE");
      var _loc3_ = "4.5K" == this.__gpdb.paramGet("GUI.OSD.RETICLE.FRAME_GUIDE.ASPECT");
      var _loc5_ = this.__gpdb.paramGetBoolean("IMAGE_ANALYSIS.MAGNIFICATION.ENABLE");
      var _loc6_ = this.__gpdb.paramGetBoolean("VIDEO.MONITOR.TEST_PATTERN.ENABLED");
      var _loc2_ = !_loc4_ && !_loc3_ && !_loc5_ && !_loc6_;
      this.Show(_loc2_);
   }
   function Render()
   {
      this.__mc.beginFill(this.__marqueColor,this.__marqueAlpha);
      this.__mc.moveTo(0,0);
      this.__mc.lineTo(this.__sensorWidth,0);
      this.__mc.lineTo(this.__sensorWidth,this.__sensorHeight);
      this.__mc.lineTo(0,this.__sensorHeight);
      this.__mc.lineTo(0,0);
      this.__mc.moveTo(this.__marqueWidth - 1,this.__marqueHeight - 1);
      this.__mc.lineTo(this.__marqueWidth - 1,this.__marqueHeight + this.__recordHeight - 1);
      this.__mc.lineTo(this.__sensorWidth - this.__marqueWidth - 1,this.__marqueHeight + this.__recordHeight - 1);
      this.__mc.lineTo(this.__sensorWidth - this.__marqueWidth - 1,this.__marqueHeight - 1);
      this.__mc.lineTo(this.__marqueWidth - 1,this.__marqueHeight - 1);
      this.__mc.endFill();
      this.__mc.lineStyle(this.__marqueLineThickness,this.__marqueLineColor,40);
      this.__mc.moveTo(this.__marqueWidth - this.__marqueLineThickness / 2 - 1,this.__marqueHeight - this.__marqueLineThickness / 2 - 1);
      this.__mc.lineTo(this.__marqueWidth - this.__marqueLineThickness / 2 - 1,this.__marqueHeight + this.__recordHeight + this.__marqueLineThickness / 2 - 1);
      this.__mc.lineTo(this.__sensorWidth - this.__marqueWidth + this.__marqueLineThickness / 2 - 1,this.__marqueHeight + this.__recordHeight + this.__marqueLineThickness / 2 - 1);
      this.__mc.lineTo(this.__sensorWidth - this.__marqueWidth + this.__marqueLineThickness / 2 - 1,this.__marqueHeight - this.__marqueLineThickness / 2 - 1);
      this.__mc.lineTo(this.__marqueWidth - this.__marqueLineThickness / 2 - 1,this.__marqueHeight - this.__marqueLineThickness / 2 - 1);
   }
   function Show(show)
   {
      this.__mc._visible = show;
   }
   function UpdateGeom()
   {
      var _loc3_ = this.DisplayedResolution();
      switch(_loc3_)
      {
         case "4.5K":
            this.__aspect = "2.39:1";
            this.__recordWidth = 1280;
            this.__recordHeight = 548;
            break;
         case "2K":
         case "3K":
         case "4K":
            this.__aspect = "16:9";
            this.__recordWidth = 1170;
            this.__recordHeight = 658;
            break;
         case "2K1.2:1":
            this.__aspect = "1.2:1";
            this.__recordWidth = 1152;
            this.__recordHeight = 480;
            break;
         case "3K1.2:1":
            this.__aspect = "1.2:1";
            this.__recordWidth = 1168;
            this.__recordHeight = 486;
            break;
         case "4K1.2:1":
            this.__aspect = "1.2:1";
            this.__recordWidth = 1166;
            this.__recordHeight = 488;
            break;
         case "4KHS":
            this.__aspect = "2.37:1";
            this.__recordWidth = 1170;
            this.__recordHeight = 494;
            break;
         case "2K2:1":
         case "3K2:1":
         case "4K2:1":
            this.__aspect = "2:1";
            this.__recordWidth = 1170;
            this.__recordHeight = 585;
            break;
         case "RGB1080P":
         case "RGB720P":
         case "4KHD":
            this.__aspect = "16:9";
            this.__recordWidth = 1097;
            this.__recordHeight = 617;
            break;
         case "4KOS":
            this.__aspect = "2:1";
            this.__recordWidth = 1244;
            this.__recordHeight = 622;
            break;
         case "4K40":
            this.__aspect = "2.37:1";
            this.__recordWidth = 1098;
            this.__recordHeight = 476;
            break;
         default:
            _global.VxError("LookAround::UpdateGeom() Unknown resolution: " + _loc3_);
      }
      this.__marqueWidth = (this.__sensorWidth - this.__recordWidth) / 2;
      this.__marqueHeight = (this.__sensorHeight - this.__recordHeight) / 2;
      this.__mc.clear();
      this.Render();
   }
   function GetAspect()
   {
      return this.__aspect;
   }
   function GetWidth()
   {
      return this.__marqueWidth + this.__recordWidth;
   }
   function GetHeight()
   {
      return this.__marqueHeight + this.__recordHeight;
   }
   function GetX()
   {
      return this.__mc.Translate(this.__marqueWidth);
   }
   function GetY()
   {
      return this.__mc.Translate(this.__marqueHeight);
   }
   function DisplayedResolution()
   {
      var _loc6_;
      var _loc7_ = "IDLE" != this.__gpdb.paramGet("VIDEO.PLAYBACK.STATE");
      var _loc5_;
      var _loc4_;
      var _loc2_;
      var _loc3_;
      if(_loc7_)
      {
         _loc5_ = {};
         _loc4_ = this.__gpdb.paramGet("VIDEO.PLAYBACK.CLIPPARAMS").split(";");
         _loc2_ = 0;
         while(_loc2_ < _loc4_.length)
         {
            _loc3_ = _loc4_[_loc2_].split("=");
            _loc5_[_loc3_[0]] = _loc3_[1];
            _loc2_ = _loc2_ + 1;
         }
         _loc6_ = _loc5_.RESOLUTION;
      }
      else
      {
         _loc6_ = this.__gpdb.paramGet("PROJECT.MODE_MATRIX.RESOLUTION");
      }
      return _loc6_;
   }
   function UpdateMarque()
   {
      this.__marqueColor = this.__gpdb.paramGetNumber("GUI.USER_PREF.LOOKAROUND.COLOR");
      this.__marqueAlpha = this.__gpdb.paramGetNumber("GUI.USER_PREF.LOOKAROUND.ALPHA");
      this.__marqueLineColor = this.__gpdb.paramGetNumber("GUI.USER_PREF.LOOKAROUND.LINE_COLOR");
      this.__marqueLineThickness = this.__gpdb.paramGetNumber("GUI.USER_PREF.LOOKAROUND.LINE_THICKNESS");
      this.__mc.clear();
      this.Render();
   }
}
