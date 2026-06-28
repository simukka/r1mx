class GUI.OSD_Components.SplashScreenMC extends MovieClip
{
   var BOOT_PROGRESS;
   var __SplashMX;
   var __SplashRedone;
   var __VersionScreenMC;
   var __gpdb;
   static var __manager;
   var __bootProgress = 5;
   function SplashScreenMC()
   {
      super();
      GUI.OSD_Components.SplashScreenMC.__manager = this;
      this.__VersionScreenMC._visible = false;
      this.__SplashRedone._visible = false;
      this.__SplashMX._visible = false;
   }
   function SetGPDB(gpdb)
   {
      this.__gpdb = gpdb;
      this.__VersionScreenMC._visible = true;
      this.__VersionScreenMC.PIN.text = GUI.OSD_Components.SplashScreenMC.ExtractPIN();
      this.__VersionScreenMC.RED_VERSION.text = GUI.OSD_Components.SplashScreenMC.ExtractVersion();
      this.__VersionScreenMC.RED_BUILD.text = GUI.OSD_Components.SplashScreenMC.ExtractBuild(this.__gpdb.paramGet("SYSTEM.VERSION.RED_RELEASE"));
      if(this.__gpdb.paramGetBoolean("SENSOR.REVISION_NUMBER"))
      {
         this.__SplashMX._visible = true;
      }
      else
      {
         this.__SplashRedone._visible = true;
      }
   }
   static function GetManager()
   {
      if(GUI.OSD_Components.SplashScreenMC.__manager === undefined)
      {
         _global.VxError("ERROR! MenuManager::GetManager() called before being instantiated");
      }
      return GUI.OSD_Components.SplashScreenMC.__manager;
   }
   static function ExtractPIN()
   {
      var _loc2_ = _global.gpdb.paramGet("SYSTEM.MANUFACTURING.CAMERA_SERIAL_NUMBER");
      var _loc3_ = "n/a";
      if(_loc2_.length >= 23 && _loc2_.substr(0,7) == "RED ONE")
      {
         _loc3_ = _loc2_.substr(14,3) + "-" + _loc2_.substr(17,3) + "-" + _loc2_.substr(20,3);
      }
      return _loc3_;
   }
   function IncrementProgress(percent)
   {
      this.__bootProgress += percent;
      this.SetProgress(this.__bootProgress);
   }
   function SetProgress(percent)
   {
      if(percent > 100)
      {
         percent = 100;
      }
      var _loc4_;
      if(percent > this.__bootProgress)
      {
         this.__bootProgress = percent;
         _loc4_ = 1280 * this.__bootProgress / 100;
         this.BOOT_PROGRESS._width = _loc4_;
         _global.VxForceRedraw();
      }
   }
   static function ExtractVersion()
   {
      var _loc2_ = _global.gpdb.paramGet("SYSTEM.VERSION.RED_RELEASE");
      var _loc3_ = "n/a";
      var _loc4_ = _loc2_.indexOf("#");
      if(_loc4_ > 0)
      {
         _loc3_ = _loc2_.substring(0,_loc4_);
      }
      else
      {
         _loc3_ = _loc2_;
      }
      return _loc3_;
   }
   static function ExtractBuild()
   {
      var _loc3_ = _global.gpdb.paramGet("SYSTEM.VERSION.RED_RELEASE");
      var _loc2_ = "n/a";
      var _loc4_ = _loc3_.indexOf("#");
      if(_loc4_ > 0)
      {
         _loc2_ = _loc3_.substring(_loc4_ + 1);
      }
      else
      {
         _loc2_ = "1";
      }
      return _loc2_;
   }
}
