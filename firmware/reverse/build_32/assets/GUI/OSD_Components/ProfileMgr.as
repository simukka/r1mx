class GUI.OSD_Components.ProfileMgr
{
   var __gpdb;
   var __profileTypesToClear;
   var __scrn;
   var clReq;
   static var __manager;
   var __mustReboot = false;
   function ProfileMgr()
   {
      _global.VxDebug("...........................................................................CTOR ProfileMgr()");
      this.__gpdb = _global.gpdb;
      GUI.OSD_Components.ProfileMgr.__manager = this;
      this.__scrn = new Object();
      this.__profileTypesToClear = new Array();
      this.__scrn.NoMedia = GUI.OSD_Components.ScreenMgrMC.GetManager().AttachScreen("ScrnProfileNoMediaMC","No Profile Media");
      this.__scrn.ExportOK = GUI.OSD_Components.ScreenMgrMC.GetManager().AttachScreen("ScrnProfileExportedMC","Profile Exported");
      this.__scrn.ImportOK = GUI.OSD_Components.ScreenMgrMC.GetManager().AttachScreen("ScrnProfileImportedMC","Profile Imported");
      this.__scrn.ImportFailed = GUI.OSD_Components.ScreenMgrMC.GetManager().AttachScreen("ScrnProfileImportFailedMC","Import Failed");
      this.__scrn.ExportFailed = GUI.OSD_Components.ScreenMgrMC.GetManager().AttachScreen("ScrnProfileExportFailedMC","Export Failed");
      this.__scrn.RestoreOK = GUI.OSD_Components.ScreenMgrMC.GetManager().AttachScreen("ScrnProfileRestoredMC","Profile Restored");
      this.__scrn.ViewStatus = GUI.OSD_Components.ScreenMgrMC.GetManager().AttachScreen("ViewStatus","");
      this.__scrn.SensorAdvancedMC = GUI.OSD_Components.ScreenMgrMC.GetManager().AttachScreen("SensorAdvancedMC","");
      this.__scrn.RevertAll = GUI.OSD_Components.ScreenMgrMC.GetManager().AttachScreen("ScrnRevertToFactorySettingsMC","RESTORED: REBOOT");
      this.clReq = false;
      this.AddCallbacks();
   }
   static function GetManager()
   {
      if(GUI.OSD_Components.ProfileMgr.__manager === undefined)
      {
         _global.VxError("ERROR! ProfileMgr::GetManager() called before being instantiated");
      }
      return GUI.OSD_Components.ProfileMgr.__manager;
   }
   function AddCallbacks()
   {
      var _loc2_ = mx.utils.Delegate.create(this,this.Update);
      this.__gpdb.addCallback("SYSTEM.PROFILE.IMPORT.STATUS",_loc2_);
      this.__gpdb.addCallback("SYSTEM.PROFILE.EXPORT.STATUS",_loc2_);
      this.__gpdb.addCallback("SYSTEM.PROFILE.RESTORE.REQUESTED",_loc2_);
      this.__gpdb.addCallback("SYSTEM.PROFILE.RESTORE.STATUS",_loc2_);
      this.__gpdb.addCallback("GUI.PROFILE.IMPORT_PATHNAME.LOOK",_loc2_);
      this.__gpdb.addCallback("GUI.PROFILE.IMPORT_PATHNAME.USER",_loc2_);
      this.__gpdb.addCallback("GUI.PROFILE.IMPORT_PATHNAME.PROJECT",_loc2_);
   }
   function ExportCurrentProfile(type)
   {
      var _loc2_ = this.__gpdb.paramGet("SYSTEM.PROFILE.FILE_LIST.SEARCH_DIRECTORY");
      var _loc3_;
      var _loc4_;
      if(_loc2_ != "")
      {
         _loc3_ = this.NewProfileName(type);
         _loc4_ = _loc2_ + "/" + _loc3_;
         this.__gpdb.paramSet("SYSTEM.PROFILE.EXPORT.PATHNAME",_loc4_);
         this.__gpdb.paramSet("SYSTEM.PROFILE.EXPORT.REQUESTED",true);
      }
      else
      {
         this.__scrn.NoMedia.Activate();
      }
   }
   function HandleClearProfile(type, clearLook, ignoreDynamicLookSettings)
   {
      var _loc2_ = false;
      var _loc3_ = "";
      switch(type)
      {
         case "ALL":
         case "user":
         case "look":
         case "system":
            _loc2_ = true;
      }
      if(clearLook)
      {
         this.clReq = true;
      }
      if(_loc2_)
      {
         this.__gpdb.paramSet("SYSTEM.PROFILE.RESTORE.TYPE",type);
         this.__gpdb.paramSet("SYSTEM.PROFILE.RESTORE.IGNORE_DYNAMIC_SETTINGS",ignoreDynamicLookSettings);
         this.__gpdb.paramSet("SYSTEM.PROFILE.RESTORE.REQUESTED",true);
      }
   }
   function NewProfileName(type)
   {
      var _loc13_;
      var _loc14_ = this.__gpdb.paramGet("PROJECT.SLATE.CAMERA");
      var _loc8_ = 0;
      var _loc11_;
      var _loc12_ = ".UNKNOWN_TYPE";
      switch(type)
      {
         case "look":
            _loc11_ = this.__gpdb.paramGet("SYSTEM.PROFILE.FILE_LIST.LOOK");
            _loc12_ = ".RLK";
            break;
         case "user":
            _loc11_ = this.__gpdb.paramGet("SYSTEM.PROFILE.FILE_LIST.USER");
            _loc12_ = ".RPF";
            break;
         case "system":
            _loc11_ = this.__gpdb.paramGet("SYSTEM.PROFILE.FILE_LIST.SYSTEM");
            _loc12_ = ".RCC";
            break;
         case "project":
            _loc11_ = this.__gpdb.paramGet("SYSTEM.PROFILE.FILE_LIST.PROJECT");
            _loc12_ = ".RPC";
            break;
         default:
            _global.VxError("NewProfileName() unknown type: " + type);
      }
      var _loc10_;
      var _loc5_;
      var _loc4_;
      var _loc9_;
      var _loc3_;
      var _loc7_;
      var _loc6_;
      if(_loc11_ != undefined && _loc11_ != "")
      {
         _loc10_ = _loc11_.split(";");
         _loc5_ = 0;
         while(_loc5_ < _loc10_.length)
         {
            _loc4_ = _loc10_[_loc5_];
            _loc9_ = _loc4_.lastIndexOf(",") + 1;
            _loc3_ = _loc4_.slice(_loc9_,_loc4_.length);
            if(0 == _loc3_.lastIndexOf("PROFILE_"))
            {
               _loc7_ = _loc3_.slice(8,_loc3_.length);
               _loc6_ = Number(_loc7_);
               if(_loc6_ > _loc8_)
               {
                  _loc8_ = _loc6_;
               }
            }
            _loc8_ += 1;
            _loc5_ = _loc5_ + 1;
         }
      }
      else
      {
         _global.VxLog("ProfileMgr::ProfileName() no look profiles exist. Starting at 0.");
         _loc8_ = 0;
      }
      _loc13_ = "PROFILE_" + _loc8_.toString() + _loc12_;
      return _loc13_;
   }
   function ForceGuiReInit()
   {
      this.__gpdb.paramSet("GUI.RUN_STATE","GUI_STATE_3_INITIALIZE_GUI_STATE");
   }
   function Update(name, value)
   {
      var _loc8_;
      var _loc6_;
      var _loc2_;
      var _loc3_;
      var _loc5_;
      switch(name)
      {
         case "SYSTEM.PROFILE.IMPORT.STATUS":
            switch(value)
            {
               case "IDLE":
                  break;
               case "IMPORT_OK":
                  GUI.OSD_Components.MenuManager.GetManager().ExitMenuTree();
                  break;
               case "IMPORT_FAILED":
                  this.__scrn.ImportFailed.Activate();
            }
            this.__gpdb.paramSet("SYSTEM.PROFILE.IMPORT.REQUESTED",false);
            this.__gpdb.paramSet("SYSTEM.PROFILE.IMPORT.PATHNAME","");
            return;
         case "SYSTEM.PROFILE.EXPORT.STATUS":
            switch(value)
            {
               case "IDLE":
                  break;
               case "EXPORT_OK":
                  _loc8_ = this.__gpdb.paramGet("SYSTEM.PROFILE.EXPORT.PATHNAME");
                  this.__scrn.ExportOK.Activate(_loc8_);
                  break;
               case "EXPORT_FAILED":
                  this.__scrn.ExportFailed.Activate();
            }
            this.__gpdb.paramSet("SYSTEM.PROFILE.EXPORT.REQUESTED",false);
            this.__gpdb.paramSet("SYSTEM.PROFILE.EXPORT.PATHNAME","");
            this.__gpdb.paramSet("SYSTEM.PROJECT.PROFILE.EXPORT.REQUESTED",false);
            return;
         case "GUI.PROFILE.IMPORT_PATHNAME.LOOK":
            if(value != "")
            {
               this.__gpdb.paramSet("CAMERA.SLAVE_MODE_IMPORT_LOOK",1);
               this.__gpdb.paramSet("SYSTEM.PROFILE.IMPORT.PATHNAME",value);
               this.__gpdb.paramSet("SYSTEM.PROFILE.IMPORT.REQUESTED",true);
            }
            return;
         case "GUI.PROFILE.IMPORT_PATHNAME.USER":
            if(value != "")
            {
               this.__gpdb.paramSet("SYSTEM.PROFILE.IMPORT.PATHNAME",value);
               this.__gpdb.paramSet("SYSTEM.PROFILE.IMPORT.REQUESTED",true);
            }
            return;
         case "GUI.PROFILE.IMPORT_PATHNAME.PROJECT":
            if(value != "")
            {
               this.__gpdb.paramSet("SYSTEM.PROFILE.IMPORT.PATHNAME",value);
               this.__gpdb.paramSet("SYSTEM.PROFILE.IMPORT.REQUESTED",true);
            }
            return;
         case "SYSTEM.PROFILE.RESTORE.REQUESTED":
            if(value == "true" && "ALL" == this.__gpdb.paramGet("SYSTEM.PROFILE.RESTORE.TYPE"))
            {
               this.__scrn.RevertAll.Activate();
               this.__gpdb.paramSet("GUI.BUTTON_INPUT_ENABLED",false);
               this.__gpdb.callbacksEnabled = false;
               this.__mustReboot = true;
            }
            return;
         case "SYSTEM.PROFILE.RESTORE.STATUS":
            if(!this.__mustReboot)
            {
               switch(value)
               {
                  case "IDLE":
                     break;
                  case "RESTORE_OK":
                     _loc6_ = this.__gpdb.paramGet("SYSTEM.PROFILE.RESTORE.TYPE");
                     if(this.clReq)
                     {
                        this.__scrn.RestoreOK.Activate(_loc6_,true);
                        this.ForceGuiReInit();
                        _loc2_ = new Date();
                        _loc3_ = _loc2_.getSeconds();
                        _loc5_ = _loc3_ + 2;
                        if(_loc5_ > 59)
                        {
                           _loc5_ -= 59;
                        }
                        while(_loc3_ != _loc5_)
                        {
                           _loc2_ = new Date();
                           _loc3_ = _loc2_.getSeconds();
                           false;
                        }
                        this.__scrn.RestoreOK.OK_FNC();
                        this.clReq = false;
                     }
                     else
                     {
                        this.__scrn.RestoreOK.Activate(this.__gpdb.paramGet("SYSTEM.PROFILE.RESTORE.TYPE"),false);
                        this.ForceGuiReInit();
                     }
                     switch(_loc6_)
                     {
                        case "look":
                           this.__gpdb.paramSet("GUI.PROFILE.IMPORT_PATHNAME.LOOK","");
                           break;
                        case "system":
                           this.__gpdb.paramSet("GUI.PROFILE.IMPORT_PATHNAME.USER","");
                           break;
                        case "user":
                           this.__gpdb.paramSet("GUI.PROFILE.IMPORT_PATHNAME.SYSTEM","");
                           break;
                        case "ALL":
                           this.__gpdb.paramSet("GUI.PROFILE.IMPORT_PATHNAME.LOOK","");
                           this.__gpdb.paramSet("GUI.PROFILE.IMPORT_PATHNAME.USER","");
                           this.__gpdb.paramSet("GUI.PROFILE.IMPORT_PATHNAME.SYSTEM","");
                     }
                     break;
                  case "RESTORE_FAILED":
                     this.__scrn.RestoreFailed.Activate(this.__gpdb.paramGet("SYSTEM.PROFILE.RESTORE.TYPE"));
               }
            }
            return;
         default:
            return;
      }
   }
}
