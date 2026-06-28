class GUI.OSD_Components.ErrorManagerMC extends MovieClip
{
   var BLINKING_DOT;
   var __ErrorText;
   var __ErrorType;
   var __gpdb;
   var __intervalID;
   var __warningScreenMC;
   var scrnMgr;
   static var __manager;
   function ErrorManagerMC()
   {
      super();
      _global.VxDebug("...........................................................................CTOR ErrorManagerMC()");
      GUI.OSD_Components.ErrorManagerMC.__manager = this;
      this.__gpdb = _global.gpdb;
      this.Show(false);
      this.scrnMgr = GUI.OSD_Components.ScreenMgrMC.GetManager();
      var _loc4_;
      _loc4_ = this.scrnMgr.AttachScreen("ScrnWarnGenericMC","WARNING",this);
      _loc4_.NewButton("OK",mx.utils.Delegate.create(this,this.CB_WARNING_OK),0,600,"OK");
      _loc4_ = this.scrnMgr.AttachScreen("ScrnWarnMediaLostMC","MEDIA LOST",this);
      _loc4_.NewButton("OK",mx.utils.Delegate.create(this,this.CB_WARNING_OK),0,600,"OK");
      _loc4_ = this.scrnMgr.AttachScreen("ScrnWarnMediaUnknownMC","MEDIA UNVERIFIED",this);
      _loc4_.NewButton("OK",mx.utils.Delegate.create(this,this.CB_WARNING_OK),0,600,"OK");
      _loc4_ = this.scrnMgr.AttachScreen("ScrnFlushLogCompleteMC","LOG WRITTEN",this);
      _loc4_.NewButton("OK",mx.utils.Delegate.create(this,this.CB_FLUSH_LOG_EXIT),0,600,"OK");
      _loc4_ = this.scrnMgr.AttachScreen("ScrnFlushLogFailedMC","LOG FAILED",this);
      _loc4_.NewButton("OK",mx.utils.Delegate.create(this,this.CB_FLUSH_LOG_EXIT),0,600,"OK");
      this.AddCallbacks();
   }
   function AddCallbacks()
   {
      this.__gpdb.addCallback("SYSTEM.ERROR.GENERAL",mx.utils.Delegate.create(this,this.Update));
      this.__gpdb.addCallback("MEDIA.DIGMAG.FLUSH_LOG",mx.utils.Delegate.create(this,this.HandleFlushLog));
   }
   function CB_WARNING_OK()
   {
      _global.VxDebug("CalibrateMC::CB_FACTORY_CAL_CANCEL()");
      this.Show(false);
      this.scrnMgr.Deactivate();
      this.__warningScreenMC = null;
      this.__gpdb.paramSet("SYSTEM.ERROR.GENERAL","NONE");
      this.__gpdb.paramSet("SYSTEM.ERROR.WARNING_TEXT","");
   }
   function CB_FLUSH_LOG_EXIT()
   {
      this.Show(false);
      this.scrnMgr.Deactivate();
   }
   function Show(show)
   {
      this._visible = show;
      if(show)
      {
         this.BLINKING_DOT.gotoAndPlay(1);
      }
      else
      {
         this.BLINKING_DOT.gotoAndStop(1);
      }
   }
   static function GetManager()
   {
      if(GUI.OSD_Components.ErrorManagerMC.__manager === undefined)
      {
         _global.VxError("ErrorManagerMC::GetManager() called before being instantiated");
      }
      return GUI.OSD_Components.ErrorManagerMC.__manager;
   }
   function PopupErrorMessage(type, message)
   {
      _global.VxError("ErrorManagerMC::PopupErrorMessage(" + message + ")");
      if(this.__intervalID != undefined)
      {
         clearInterval(this.__intervalID);
      }
      this.__ErrorType.text = type;
      this.__ErrorText.text = message;
      this.Show(true);
      GUI.OSD_Components.StatusLCD.GetManager().SetMessage(message);
      GUI.OSD_Components.LedMgr.GetManager().FlagWarning(true);
      this.__intervalID = setInterval(this,"RemovePopupError",5000);
   }
   function RemovePopupError()
   {
      if(this.__intervalID != null)
      {
         clearInterval(this.__intervalID);
         this.__intervalID = null;
      }
      this.Show(false);
      GUI.OSD_Components.StatusLCD.GetManager().SetPane(GUI.OSD_Components.StatusLCD.PANE_STATUS);
      GUI.OSD_Components.LedMgr.GetManager().FlagWarning(false);
   }
   function Update(name, value)
   {
      var _loc0_;
      if((_loc0_ = name) === "SYSTEM.ERROR.GENERAL")
      {
         this.ProcessWarning(value);
      }
   }
   function ProcessWarning(warning)
   {
      var _loc3_;
      var _loc4_;
      switch(warning)
      {
         case "GENERIC":
            _loc3_ = this.DisplayWarningScreen("ScrnWarnGenericMC");
            _loc4_ = GUI.OSD_Components.ScrnWarnGenericMC(_loc3_);
            warning = this.__gpdb.paramGet("SYSTEM.ERROR.WARNING_TEXT");
            _loc4_.SetWarningText(warning);
            return;
         case "MEDIA_UNMOUNT_FAULT":
            this.DisplayWarningScreen("ScrnWarnMediaLostMC");
            this.__gpdb.paramSet("VIDEO.RECORD.REQUESTED",false);
            this.__gpdb.paramSet("VIDEO.PLAYBACK.REQUESTED",false);
            return;
         case "MEDIA_TYPE_UNKNOWN":
            this.DisplayWarningScreen("ScrnWarnMediaUnknownMC");
            return;
         case "NONE":
         case "":
         default:
            return;
      }
   }
   function DisplayWarningScreen(screenName)
   {
      var _loc3_;
      if(this.__warningScreenMC == undefined)
      {
         if(this._visible)
         {
            this.RemovePopupError();
         }
         _loc3_ = this.scrnMgr.Activate(screenName);
         this.__warningScreenMC = _loc3_;
         this.Show(true);
      }
      else
      {
         _global.VxDebug("DisplayWarningScreen(" + screenName + ") Ignoring because __warningScreenMC is not null - " + this.__warningScreenMC);
      }
      return _loc3_;
   }
   function HandleFlushLog(param, value)
   {
      var _loc3_ = value == "true";
      var _loc5_;
      var _loc4_;
      var _loc2_;
      _loc2_ = this.__gpdb.paramGet("MEDIA.DIGMAG.ACTIVEDRIVE");
      if(_loc2_ == "DRIVE0" || _loc2_ == "DRIVE1")
      {
         if(!_loc3_)
         {
            _loc5_ = this.scrnMgr.Activate("ScrnFlushLogCompleteMC");
            this.Show(true);
         }
      }
      else if(!_loc3_)
      {
         _loc4_ = this.scrnMgr.Activate("ScrnFlushLogFailedMC");
         this.Show(true);
      }
   }
}
