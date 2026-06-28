class GUI.OSD_Components.MediaManager
{
   var __activeDrive;
   var __gpdb;
   static var __manager;
   var __mountFlag = false;
   var __emptyMag = false;
   function MediaManager()
   {
      _global.VxDebug("...........................................................................CTOR MediaManager()");
      GUI.OSD_Components.MediaManager.__manager = this;
      this.__gpdb = _global.gpdb;
      this.addGpdbCallbacks();
   }
   static function GetManager()
   {
      if(GUI.OSD_Components.MediaManager.__manager === undefined)
      {
         _global.VxError("ERROR! MediaManager::GetManager() called before being instantiated");
      }
      return GUI.OSD_Components.MediaManager.__manager;
   }
   function addGpdbCallbacks()
   {
      var _loc2_ = mx.utils.Delegate.create(this,this.HandleGPDB);
      this.__gpdb.addCallback("MEDIA.DIGMAG.DRIVE0.EJECT_DONE",_loc2_);
      this.__gpdb.addCallback("MEDIA.DIGMAG.DRIVE1.EJECT_DONE",_loc2_);
      this.__gpdb.addCallback("MEDIA.DIGMAG.MEDIA_PATH",_loc2_);
      this.__gpdb.addCallback("MEDIA.DIGMAG.CLIP_LIST",_loc2_);
   }
   function HandleGPDB(param, value)
   {
      switch(param)
      {
         case "MEDIA.DIGMAG.DRIVE0.EJECT_DONE":
            if(value == "true")
            {
               this.UnmountComplete("DRIVE0");
            }
            return;
         case "MEDIA.DIGMAG.DRIVE1.EJECT_DONE":
            if(value == "true")
            {
               this.UnmountComplete("DRIVE1");
            }
            return;
         case "MEDIA.DIGMAG.MEDIA_PATH":
            if(value != "")
            {
               this.__mountFlag = true;
            }
            return;
         case "MEDIA.DIGMAG.CLIP_LIST":
            if(this.__mountFlag)
            {
               this.__mountFlag = false;
            }
            return;
         default:
            throw new Error("MediaManager::HandleGPDB(" + param + ", " + value + ") unhandled parameter");
      }
   }
   function HandleMount()
   {
      return undefined;
   }
   function GetTargettedDrive()
   {
      var _loc2_;
      var _loc3_ = this.__gpdb.paramGet("MEDIA.DIGMAG.SELECTION_POLICY");
      switch(_loc3_)
      {
         case "Auto":
            switch(this.__gpdb.paramGet("MEDIA.DIGMAG.DRIVE1.GUI_STATE"))
            {
               case "NOTPRESENT":
                  _loc2_ = "DRIVE0";
                  break;
               case "UNCONFIGURED":
               case "INCOMPATIBLE":
               case "MOUNTED":
               case "UNMOUNTED":
               case "NOTMOUNTED":
               case "EXPORTED":
                  _loc2_ = "DRIVE1";
            }
            break;
         case "Internal":
            _loc2_ = "DRIVE0";
            break;
         case "External":
            _loc2_ = "DRIVE1";
            break;
         default:
            throw new Error("Widget_DigMag::GetTargettedDrive() Unknown policy: \'" + _loc3_ + "\'");
      }
      return _loc2_;
   }
   function Unmount()
   {
      _global.log("MediaManager::Unmount()");
      this.__activeDrive = this.GetTargettedDrive();
      var _loc3_ = "MEDIA.DIGMAG." + this.__activeDrive + ".GUI_STATE";
      if(this.__gpdb.paramGet(_loc3_) != "NOTPRESENT")
      {
         _loc3_ = "MEDIA.DIGMAG." + this.__activeDrive + ".EJECT_REQUEST";
         this.__gpdb.paramSet(_loc3_,"true");
      }
      else
      {
         _global.log("MediaManager::Unmount() Cann\'t UNMOUNT, " + _loc3_ + " = false");
      }
   }
   function UnmountComplete(drive)
   {
      var _loc2_;
      if(drive != this.__activeDrive)
      {
         throw new Error("MediaManager::UnmountComplete() " + drive + " ejected, but " + this.__activeDrive + " was requested");
      }
      _loc2_ = "MEDIA.DIGMAG." + this.__activeDrive + ".EJECT_REQUEST";
      this.__gpdb.paramSet(_loc2_,"false");
      _loc2_ = "MEDIA.DIGMAG." + this.__activeDrive + ".EJECT_DONE";
      this.__gpdb.paramSet(_loc2_,"false");
   }
}
