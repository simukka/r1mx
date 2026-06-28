class GUI.OSD_Components.Widget_TCGenlockMC extends MovieClip
{
   var GENLOCK_ICON;
   var __gpdb;
   var errScreen;
   var scrnMgr;
   function Widget_TCGenlockMC()
   {
      super();
      _global.VxDebug("...........................................................................CTOR Widget_TCGenlockMC()");
      this.__gpdb = _global.gpdb;
      this.scrnMgr = GUI.OSD_Components.ScreenMgrMC.GetManager();
      this.errScreen = GUI.OSD_Components.ScrnGenlockFailedMC(this.scrnMgr.AttachScreen("ScrnGenlockFailedMC","GENLOCK FAILED"));
      this.ShowIcon();
      this.AddCallbacks();
   }
   function ShowIcon()
   {
      var _loc2_ = this.__gpdb.paramGet("SYSTEM.DEV.GENLOCK.STATE");
      switch(_loc2_)
      {
         case "NOT_REQUESTED":
            this.GENLOCK_ICON._visible = false;
            this.gotoAndStop("LOCKED");
            break;
         case "LOCKED":
            this.GENLOCK_ICON._visible = true;
            this.gotoAndStop("LOCKED");
            break;
         case "NO_SYNC":
            this.GENLOCK_ICON._visible = true;
            this.gotoAndStop("ERROR");
            break;
         case "NO_REF":
            this.GENLOCK_ICON._visible = true;
            this.gotoAndStop("ERROR");
            break;
         case "NO_GENLOCK":
            this.GENLOCK_ICON._visible = true;
            this.gotoAndStop("ERROR");
            break;
         case "BAD_FRAMERATE":
            this.GENLOCK_ICON._visible = true;
            this.gotoAndStop("ERROR");
         default:
            return;
      }
   }
   function AddCallbacks()
   {
      var _loc2_ = mx.utils.Delegate.create(this,this.Update);
      this.__gpdb.addCallback("SYSTEM.DEV.GENLOCK.STATE",_loc2_);
   }
   function Update(name, value)
   {
      var _loc0_;
      if((_loc0_ = name) === "SYSTEM.DEV.GENLOCK.STATE")
      {
         this.ShowIcon();
         switch(value)
         {
            case "NOT_REQUESTED":
            case "LOCKED":
               break;
            case "NO_SYNC":
               this.ErrorMsg("Unable to acquire genlock sync. Please verify that the","genlock device is working properly, and try again.");
               break;
            case "NO_REF":
               this.ErrorMsg("No Reference. Please verify that the","genlock device is working properly, and try again.");
               break;
            case "NO_GENLOCK":
               this.ErrorMsg("No Genlock. Please verify that the","genlock device is working properly, and try again.");
               break;
            case "BAD_FRAMERATE":
               this.ErrorMsg("The framerate of the genlock source does","not match the current framerate of the camera.");
         }
      }
   }
   function ErrorMsg(line1, line2)
   {
      return undefined;
   }
}
