class GUI.OSD_Components.FormatManager
{
   var __gpdb;
   var __scrnMgr;
   static var __manager;
   var __diskBeingFormatted = "NONE";
   var formatInProgress = false;
   function FormatManager()
   {
      GUI.OSD_Components.FormatManager.__manager = this;
      this.__gpdb = _global.gpdb;
      this.__scrnMgr = GUI.OSD_Components.ScreenMgrMC.GetManager();
      _global.VxDebug("...........................................................................CTOR FormatManager()");
      this.__diskBeingFormatted = "NONE";
      var _loc3_ = undefined;
      _loc3_ = this.__scrnMgr.AttachScreen("ScrnFormatConfirmMC","FORMAT?");
      _loc3_.NewButton("CANCEL",mx.utils.Delegate.create(this,this.CB_FORMAT_CANCEL),0,600);
      _loc3_.NewButton("FORMAT",mx.utils.Delegate.create(this,this.CB_FORMAT_OK),0,600);
      _loc3_ = this.__scrnMgr.AttachScreen("ScrnFormatInProgMC","FORMATTING...");
      _loc3_ = this.__scrnMgr.AttachScreen("ScrnFormatDoneMC","FORMAT DONE");
      _loc3_.NewButton("OK",mx.utils.Delegate.create(this,this.CB_FORMAT_EXIT),0,600);
      _loc3_ = this.__scrnMgr.AttachScreen("ScrnFormatFailedMC","FORMAT FAILED");
      _loc3_.NewButton("OK",mx.utils.Delegate.create(this,this.CB_FORMAT_EXIT),0,600);
      this.AddCallbacks();
   }
   function CB_FORMAT_OK()
   {
      _global.VxDebug("CalibrateMC::CB_FORMAT_OK()");
      this.DoFormat();
   }
   function CB_FORMAT_CANCEL()
   {
      _global.VxDebug("CalibrateMC::CB_FORMAT_CANCEL()");
      this.Exit();
   }
   function CB_FORMAT_EXIT()
   {
      _global.VxDebug("CalibrateMC::CB_OK_EXIT()");
      this.Exit();
   }
   function AddCallbacks()
   {
      this.__gpdb.addCallback("MEDIA.DIGMAG.DRIVE0.FORMAT_DONE",mx.utils.Delegate.create(this,this.DoFormatDone));
      this.__gpdb.addCallback("MEDIA.DIGMAG.DRIVE1.FORMAT_DONE",mx.utils.Delegate.create(this,this.DoFormatDone));
   }
   static function GetManager()
   {
      if(!GUI.OSD_Components.FormatManager.__manager)
      {
         throw new Error("FormatManager::GetManager() class not instanciated!");
      }
      return GUI.OSD_Components.FormatManager.__manager;
   }
   function SmartFormat()
   {
      _global.VxDebug("FormatManager::SmartFormat()");
      if(this.__diskBeingFormatted == "NONE")
      {
         this.__diskBeingFormatted = this.__gpdb.paramGet("MEDIA.DIGMAG.ACTIVEDRIVE");
         if(this.__diskBeingFormatted == "NONE")
         {
            this.DoAbort("No digmag was found.","Nothing to Format.");
         }
         if("true" != this.__gpdb.paramGet("MEDIA.DIGMAG.PROJECT_SETTINGS_RECORDABLE"))
         {
            this.DoAbort("The magazine isn\'t fast enough to support the current project.","Please change the project settings before formatting this media.");
         }
         else
         {
            var _loc3_ = this.__diskBeingFormatted != "DRIVE0" ? "EXTERNAL" : "INTERNAL";
            var _loc4_ = this.__gpdb.paramGet("MEDIA.DIGMAG." + this.__diskBeingFormatted + ".GUI_STATE");
            switch(_loc4_)
            {
               case "NOTPRESENT":
                  this.DoAbort("No " + _loc3_ + " drive was found.","Nothing to Format.");
                  break;
               case "EXPORTED":
                  this.DoAbort("The active drive (" + _loc3_ + ") is exported to via USB.","Unable to Format.");
                  break;
               case "UNMOUNTED":
                  this.DoAbort("The active drive (" + _loc3_ + ") is unmounted.","Please re-connect to Format.");
                  break;
               case "UNCONFIGURED":
                  this.DoFormat();
                  break;
               case "MOUNTED":
               case "NOTMOUNTED":
               case "INCOMPATIBLE":
                  if(this.NumClipsOnDigmag() == 0)
                  {
                     this.DoFormat();
                  }
                  else
                  {
                     this.DoConfirm();
                  }
                  break;
               default:
                  _global.VxError("FormatManager::SmartFormat() Unknown drive state \'" + _loc4_ + "\'");
            }
         }
      }
      else
      {
         _global.VxDebug("FormatManager::SmartFormat() Format already in progress. Ignoring new request");
      }
   }
   function BootSmartFormat()
   {
      var _loc2_ = this.__gpdb.paramGet("MEDIA.DIGMAG.ACTIVEDRIVE");
      if(_loc2_ != "NONE")
      {
         var _loc3_ = this.__gpdb.paramGet("MEDIA.DIGMAG." + _loc2_ + ".GUI_STATE");
         switch(_loc3_)
         {
            case "NOTPRESENT":
            case "EXPORTED":
            case "UNMOUNTED":
            case "MOUNTED":
            case "INCOMPATIBLE":
            case "NOTMOUNTED":
               break;
            case "UNCONFIGURED":
               this.SmartFormat();
               break;
            default:
               throw new Error("FormatManager::SmartFormat() Unknown drive state \'" + _loc3_ + "\'");
         }
      }
   }
   function DoAbort(line1, line2)
   {
      var _loc2_ = this.__scrnMgr.Activate("ScrnFormatFailedMC");
      _loc2_.SetErrorString(line1,line2);
   }
   function DoConfirm(message)
   {
      var _loc3_ = this.NumClipsOnDigmag();
      var _loc2_ = this.__scrnMgr.Activate("ScrnFormatConfirmMC");
      _loc2_.SetFormatSubScreen(_loc3_);
   }
   function DoFormat()
   {
      var _loc3_ = this.__diskBeingFormatted != "DRIVE0" ? "EXTERNAL" : "INTERNAL";
      var _loc2_ = this.__scrnMgr.Activate("ScrnFormatInProgMC");
      _loc2_.ShowFormatting(_loc3_);
      this.__gpdb.paramSet("MEDIA.DIGMAG.CAPACITY.TOTAL_MB",5);
      this.__gpdb.paramSet("MEDIA.DIGMAG.CAPACITY.REMAINING_MB",5);
      switch(this.__diskBeingFormatted)
      {
         case "DRIVE0":
            this.__gpdb.paramSet("MEDIA.DIGMAG.DRIVE0.FORMAT_REQUEST",true);
            break;
         case "DRIVE1":
            this.__gpdb.paramSet("MEDIA.DIGMAG.DRIVE1.FORMAT_REQUEST",true);
      }
   }
   function DoFormatDone(param, value)
   {
      if(value == "true")
      {
         var _loc2_ = this.__gpdb.paramGetNumber("CAMERA.FORMAT_COMPLETE_MESSAGE");
         if(_loc2_ == 1)
         {
            this.__gpdb.paramSet("CAMERA.FORMAT_COMPLETE_MESSAGE",0);
            this.__scrnMgr.Activate("ScrnFormatDoneMC");
         }
         this.__gpdb.paramSet(param,false);
         switch(param)
         {
            case "MEDIA.DIGMAG.DRIVE0.FORMAT_DONE":
               this.__gpdb.paramSet("MEDIA.DIGMAG.DRIVE0.FORMAT_REQUEST",false);
               this.__gpdb.paramSet("MEDIA.DIGMAG.DRIVE0.FORMAT_DONE",false);
               break;
            case "MEDIA.DIGMAG.DRIVE1.FORMAT_DONE":
               this.__gpdb.paramSet("MEDIA.DIGMAG.DRIVE1.FORMAT_REQUEST",false);
               this.__gpdb.paramSet("MEDIA.DIGMAG.DRIVE1.FORMAT_DONE",false);
         }
      }
   }
   function DoDiskYanked(name, value)
   {
      if(this.__diskBeingFormatted != "NONE")
      {
         var _loc3_ = "MEDIA.DIGMAG." + this.__diskBeingFormatted + ".GUI_STATE";
         if(name == _loc3_ && value == "NOTPRESENT")
         {
            _global.VxError("FormatManager::DoDiskYanked(" + name + ", " + value + ") Drive was yanked! Aborting format.");
            this.Exit();
         }
      }
   }
   function NumClipsOnDigmag()
   {
      var _loc3_ = 0;
      var _loc2_ = this.__gpdb.paramGet("MEDIA.DIGMAG.CLIP_LIST");
      if(_loc2_.length > 0)
      {
         var _loc4_ = _loc2_.split(",");
         _loc3_ = _loc4_.length;
      }
      return _loc3_;
   }
   function Exit()
   {
      this.__scrnMgr.Deactivate();
      this.__diskBeingFormatted = "NONE";
   }
}
