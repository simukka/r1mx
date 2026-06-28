class GUI.OSD_Components.CalibrateMC extends GUI.OSD_Components.FullScreenMC
{
   var Activate;
   var SetLcdBanner;
   var __CALIBRATE;
   var __gpdb;
   var matrix;
   var scrnMgr;
   static var __manager;
   var __autoApplyCal = false;
   var __captureComplete = false;
   var __factoryCal = false;
   function CalibrateMC()
   {
      super();
      _global.VxDebug("...........................................................................CTOR CalibrateMC()");
      GUI.OSD_Components.CalibrateMC.__manager = this;
      this.__gpdb = _global.gpdb;
      this.SetLcdBanner("Calibrating...");
      this.scrnMgr = GUI.OSD_Components.ScreenMgrMC.GetManager();
      GUI.OSD_Components.CalibrateMC.__manager._visible = false;
      var _loc4_;
      _loc4_ = this.scrnMgr.AttachScreen("ScrnFacCalConfirmDarkMC","DARK CAL?",this);
      _loc4_.NewButton("OK",mx.utils.Delegate.create(this,this.CB_FACTORY_CAL_OK),0,600,"DARK");
      _loc4_.NewButton("CANCEL",mx.utils.Delegate.create(this,this.CB_FACTORY_CAL_CANCEL),0,600,"DARK");
      _loc4_ = this.scrnMgr.AttachScreen("ScrnFacCalConfirmLiteF24MC","LIGHT CAL, F24?",this);
      _loc4_.NewButton("OK",mx.utils.Delegate.create(this,this.CB_FACTORY_CAL_OK),0,600,"LIGHT_F24");
      _loc4_.NewButton("CANCEL",mx.utils.Delegate.create(this,this.CB_FACTORY_CAL_CANCEL),0,600,"LIGHT_F24");
      _loc4_ = this.scrnMgr.AttachScreen("ScrnFacCalConfirmLiteMC","LIGHT CAL?",this);
      _loc4_.NewButton("OK",mx.utils.Delegate.create(this,this.CB_FACTORY_CAL_OK),0,600,"LIGHT");
      _loc4_.NewButton("CANCEL",mx.utils.Delegate.create(this,this.CB_FACTORY_CAL_CANCEL),0,600,"LIGHT");
      _loc4_ = this.scrnMgr.AttachScreen("ScrnFacCalDoneDarkMC","DRK CAL DONE",this);
      _loc4_.NewButton("OK",mx.utils.Delegate.create(this,this.CB_OK_EXIT),0,600);
      _loc4_ = this.scrnMgr.AttachScreen("ScrnFacCalDoneLiteMC","LT CAL F24 DONE",this);
      _loc4_.NewButton("OK",mx.utils.Delegate.create(this,this.CB_OK_EXIT),0,600);
      _loc4_ = this.scrnMgr.AttachScreen("ScrnFacCalDoneLiteMC","LT CAL DONE",this);
      _loc4_.NewButton("OK",mx.utils.Delegate.create(this,this.CB_OK_EXIT),0,600);
      _loc4_ = this.scrnMgr.AttachScreen("ScrnFacCalErrNoFileMC","ERR: NO FILE",this);
      _loc4_.NewButton("OK",mx.utils.Delegate.create(this,this.CB_OK_EXIT),0,600);
      _loc4_ = this.scrnMgr.AttachScreen("ScrnFacCalApplyInProgMC","APPLYING CAL",this);
      _loc4_ = this.scrnMgr.AttachScreen("ScrnFacCalApplyDoneMC","CAL COMPLETE",this);
      _loc4_.NewButton("OK",mx.utils.Delegate.create(this,this.CB_OK_EXIT),0,600);
      _loc4_ = this.scrnMgr.AttachScreen("ScrnFacCalApplyFailedMC","CAL FAILED",this);
      _loc4_.NewButton("OK",mx.utils.Delegate.create(this,this.CB_OK_EXIT),0,600);
      _loc4_ = this.scrnMgr.AttachScreen("ScrnCalConfirmMC","CALIBRATE?",this);
      _loc4_.NewButton("OK",mx.utils.Delegate.create(this,this.CB_CAL_OK),0,600);
      _loc4_.NewButton("CANCEL",mx.utils.Delegate.create(this,this.CB_CAL_CANCEL),0,600);
      _loc4_ = this.scrnMgr.AttachScreen("ScrnCalErrMagnify","ERR: MAGNIFY MODE",this);
      _loc4_.NewButton("OK",mx.utils.Delegate.create(this,this.CB_OK_EXIT),0,600);
      _loc4_ = this.scrnMgr.AttachScreen("ScrnCalErrNoMedia","ERR: INSUFFICIENT MEDIA",this);
      _loc4_.NewButton("OK",mx.utils.Delegate.create(this,this.CB_OK_EXIT),0,600);
      _loc4_ = this.scrnMgr.AttachScreen("ScrnCalDoneMC","CAL COMPLETE",this);
      _loc4_.NewButton("OK",mx.utils.Delegate.create(this,this.CB_OK_EXIT),0,600);
      _loc4_ = this.scrnMgr.AttachScreen("ScrnCalErrNoDiskMC","ERR: NO DISK",this);
      _loc4_.NewButton("OK",mx.utils.Delegate.create(this,this.CB_OK_EXIT),0,600);
      _loc4_ = this.scrnMgr.AttachScreen("ScrnCalFailedMC","ERR: FAILURE",this);
      _loc4_.NewButton("OK",mx.utils.Delegate.create(this,this.CB_OK_EXIT),0,600);
      _loc4_ = this.scrnMgr.AttachScreen("ScrnCalRestoreMC","RESTORE CAL?",this);
      _loc4_.NewButton("OK",mx.utils.Delegate.create(this,this.CB_DEL_OK),0,600);
      _loc4_.NewButton("CANCEL",mx.utils.Delegate.create(this,this.CB_DEL_CANCEL),0,600);
      _loc4_ = this.scrnMgr.AttachScreen("ScrnCalRestoreDoneMC","OK. Cycle Power.",this);
      this.AddCallbacks();
   }
   function CB_CAL_OK()
   {
      _global.VxDebug("CalibrateMC::CB_CAL_OK()");
      this.scrnMgr.Activate("CalibrateMC");
      GUI.OSD_Components.CalibrateMC.__manager._visible = true;
      this.CalibrateAndApply();
   }
   function CB_CAL_CANCEL()
   {
      _global.VxDebug("CalibrateMC::CB_CAL_CANCEL()");
      this.Exit();
   }
   function CB_OK_EXIT()
   {
      _global.VxDebug("CalibrateMC::CB_OK_EXIT()");
      this.Exit();
   }
   function CB_FACTORY_CAL_OK(calType)
   {
      _global.VxDebug("CalibrateMC::CB_FACTORY_CAL_OK(\'" + calType + "\')");
      this.scrnMgr.Activate("CalibrateMC");
      GUI.OSD_Components.CalibrateMC.__manager._visible = true;
      this.DoCalibrateCapture(calType);
   }
   function CB_FACTORY_CAL_CANCEL()
   {
      _global.VxDebug("CalibrateMC::CB_FACTORY_CAL_CANCEL()");
      this.Exit();
   }
   function CB_DEL_OK()
   {
      _global.VxDebug("CalibrateMC::CB_DEL_OK()");
      this.Exit();
      this.__gpdb.paramSet("CALIBRATE.USER.DELETE_CAL_FILE","true");
   }
   function CB_DEL_CANCEL()
   {
      _global.VxDebug("CalibrateMC::CB_DEL_CANCEL()");
      this.Exit();
   }
   function CB_DEL_DONE_OK()
   {
      _global.VxDebug("CalibrateMC::CB_DEL_DONE_OK()");
      this.Exit();
   }
   static function GetManager()
   {
      if(GUI.OSD_Components.CalibrateMC.__manager === undefined)
      {
         _global.VxError("CalibrateMC::GetManager() called before being instantiated");
      }
      return GUI.OSD_Components.CalibrateMC.__manager;
   }
   function AddCallbacks()
   {
      var _loc2_ = mx.utils.Delegate.create(this,this.Update);
      this.__gpdb.addCallback("CALIBRATE.CAPTURE_CURRENTFRAME",_loc2_);
      this.__gpdb.addCallback("CALIBRATE.USER.STATE",_loc2_);
      this.__gpdb.addCallback("CALIBRATE.FACTORY.STATE",_loc2_);
      this.__gpdb.addCallback("SYSTEM.ERROR.RECORD",_loc2_);
      this.__gpdb.addCallback("VIDEO.RECORD.STATE",_loc2_);
      this.__gpdb.addCallback("CALIBRATE.USER.DELETE_CAL_FILE",_loc2_);
   }
   function HandleUserCalRequest()
   {
      _global.VxDebug("CalibrateMC::HandleUserCalRequest()");
      var _loc6_;
      var _loc3_;
      var _loc4_;
      var _loc5_;
      if(this.__gpdb.paramGetBoolean("IMAGE_ANALYSIS.MAGNIFICATION.ENABLE"))
      {
         this.scrnMgr.Activate("ScrnCalErrMagnify");
      }
      else
      {
         _loc6_ = "NONE" == this.__gpdb.paramGet("MEDIA.DIGMAG.ACTIVEDRIVE");
         if(_loc6_)
         {
            this.scrnMgr.Activate("ScrnCalErrNoDiskMC");
         }
         else
         {
            _loc3_ = Number(this.__gpdb.paramGet("MEDIA.DIGMAG.CAPACITY.TOTAL_MB"));
            _loc4_ = Number(this.__gpdb.paramGet("MEDIA.DIGMAG.CAPACITY.REMAINING_MB"));
            _loc5_ = Math.floor(100 * _loc4_ / _loc3_);
            if(_loc5_ < 10)
            {
               this.scrnMgr.Activate("ScrnCalErrNoMedia");
            }
            else
            {
               this.scrnMgr.Activate("ScrnCalConfirmMC");
            }
         }
      }
      GUI.OSD_Components.CalibrateMC.__manager._visible = true;
      this.__factoryCal = false;
   }
   function HandleRestoreRequest()
   {
      _global.VxDebug("CalibrateMC::HandleRestoreRequest()");
      this.scrnMgr.Activate("ScrnCalRestoreMC");
      GUI.OSD_Components.CalibrateMC.__manager._visible = true;
      this.__factoryCal = false;
   }
   function HandleRestoreComplete()
   {
      this.scrnMgr.Activate("ScrnCalRestoreDoneMC");
      GUI.OSD_Components.CalibrateMC.__manager._visible = true;
   }
   function CalibrateAndApply()
   {
      this.__CALIBRATE.text = "STARTING BLACK SHADING CALIBRATION.";
      this.matrix.gotoAndPlay(2);
      this.__gpdb.paramSet("CALIBRATE.OUTPUTFORMAT","SUMS");
      this.__gpdb.paramSet("CALIBRATE.CAPTURE_CLIPNAME","calibrationclip");
      this.__gpdb.paramSet("PROJECT.MODE_MATRIX.ENCODING",this.__gpdb.paramGet("MEDIA.DIGMAG.PROJECT.ENCODING"));
      this.__gpdb.paramSet("PROJECT.MODE_MATRIX.FRAME_RATE",this.__gpdb.paramGet("MEDIA.DIGMAG.PROJECT.FRAME_RATE"));
      this.__gpdb.paramSet("PROJECT.MODE_MATRIX.QUALITY",this.__gpdb.paramGet("MEDIA.DIGMAG.PROJECT.QUALITY"));
      this.__autoApplyCal = true;
      this.__gpdb.paramSet("CALIBRATE.CAPTURE_FRAMECOUNT",this.__gpdb.paramGet("GUI.CALIBRATE.CAPTURE_FRAMECOUNT"));
      this.__gpdb.paramSet("CALIBRATE.USER.STATE","SAMPLING_SENSOR");
      this.__gpdb.paramSet("VIDEO.RECORD.REQUESTED","true");
   }
   function HandleFactoryCalCaptureRequest(calType)
   {
      var _loc4_ = "NONE" == this.__gpdb.paramGet("MEDIA.DIGMAG.ACTIVEDRIVE");
      if(_loc4_)
      {
         this.scrnMgr.Activate("ScrnCalErrNoDiskMC");
      }
      else
      {
         switch(calType)
         {
            case "LIGHT":
               this.scrnMgr.Activate("ScrnFacCalConfirmLiteMC");
               break;
            case "LIGHT_F24":
               this.scrnMgr.Activate("ScrnFacCalConfirmLiteF24MC");
               break;
            case "DARK":
               this.scrnMgr.Activate("ScrnFacCalConfirmDarkMC");
               break;
            default:
               _global.VxError("CalibrateMC::HandleFactoryCalCaptureRequest(" + calType + "): unrecognized calibration type!");
         }
      }
      GUI.OSD_Components.CalibrateMC.__manager._visible = true;
      this.__factoryCal = true;
   }
   function DoCalibrateCapture(calType)
   {
      if(calType != undefined)
      {
         _global.VxLog("CalibrateMC::DoCalibrateCapture() requesting \'" + calType + "\'");
         this.Activate();
         this.__CALIBRATE.text = "STARTING " + calType + " SHADING CALIBRATION.";
         this.__gpdb.paramSet("CALIBRATE.OUTPUTFORMAT","SUMS");
         this.__gpdb.paramSet("CALIBRATE.CAPTURE_CLIPNAME","CALDATA_" + calType);
         this.__autoApplyCal = false;
         this.__gpdb.paramSet("CALIBRATE.CAPTURE_FRAMECOUNT",this.__gpdb.paramGet("GUI.CALIBRATE.CAPTURE_FRAMECOUNT"));
         this.__gpdb.paramSet("CALIBRATE.FACTORY.STATE","SAMPLING_SENSOR");
         this.__gpdb.paramSet("VIDEO.RECORD.REQUESTED","true");
      }
      else
      {
         _global.VxError("CalibrateMC::DoCalibrateCapture() Unknown type \'" + calType + "\'");
         this.Exit();
      }
   }
   function HandleFactoryCalApplyRequest()
   {
      if(!this.__gpdb.paramGetBoolean("CALIBRATE.FACTORY.FILE_AVAILABLE"))
      {
         this.scrnMgr.Activate("ScrnFacCalErrNoFileMC");
         GUI.OSD_Components.CalibrateMC.__manager._visible = true;
      }
      else
      {
         this.__gpdb.paramSet("CALIBRATE.FACTORY.APPLY_CAL_FILE","true");
      }
      this.__factoryCal = true;
   }
   function Exit()
   {
      this.matrix.gotoAndStop(1);
      for(var _loc2_ in this.matrix)
      {
      }
      this.matrix.CleanUp();
      for(_loc2_ in this.matrix)
      {
      }
      GUI.OSD_Components.CalibrateMC.__manager._visible = false;
      this.scrnMgr.Deactivate();
      this.__gpdb.paramSet("CALIBRATE.USER.STATE","IDLE");
      this.__gpdb.paramSet("CALIBRATE.FACTORY.STATE","IDLE");
      if(this.__factoryCal)
      {
         GUI.OSD_Components.MenuManager.GetManager().GotoMenuPanel("Panel_Calibrate");
      }
   }
   function Update(name, value)
   {
      var _loc5_;
      var _loc6_;
      switch(name)
      {
         case "CALIBRATE.CAPTURE_CURRENTFRAME":
            if("0" == this.__gpdb.paramGet("CALIBRATE.CAPTURE_FRAMECOUNT"))
            {
               this.__CALIBRATE.text = null;
               GUI.OSD_Components.CalibrateMC.__manager._visible = false;
            }
            else
            {
               _loc5_ = this.__gpdb.paramGetNumber("CALIBRATE.CAPTURE_FRAMECOUNT");
               _loc6_ = _loc5_ - Number(value);
               this.__CALIBRATE.text = "CALIBRATION: ANALYZING SENSOR (" + _loc6_ + ")...";
            }
            return;
         case "SYSTEM.ERROR.RECORD":
            switch(value)
            {
               case "CALCAPTURECOMPLETE":
                  this.__captureComplete = true;
                  this.__gpdb.paramSet("SYSTEM.ERROR.RECORD","NONE");
                  break;
               case "NONE":
                  break;
               case "INCOMPATIBLE_DIGMAG":
               case "NO_DIGMAG":
               case "NO_MEDIA_PATH":
               case "NO_CLIPNAME":
               case "OUT_OF_SPACE":
               case "FRMRATE_TOOHIGH":
               case "CONFIG_FAULT":
               case "CODEC_FAULT":
               case "FILE_FAULT":
               case "ROCKETIO_FAULT":
               case "INTERNAL_FAULT":
                  _global.VxError("CalibrateMC::Update(" + name + ", " + value + ")");
                  if("IDLE" != this.__gpdb.paramGet("CALIBRATE.USER.STATE"))
                  {
                     _global.VxError("CalibrateMC::Update(" + name + ", " + value + ") setting CalUserState to COMPLETE_ERROR");
                     this.__gpdb.paramSet("CALIBRATE.USER.STATE","COMPLETE_ERROR");
                  }
                  if("IDLE" != this.__gpdb.paramGet("CALIBRATE.FACTORY.STATE"))
                  {
                     _global.VxError("CalibrateMC::Update(" + name + ", " + value + ") setting CalFacState to COMPLETE_ERROR");
                     this.__gpdb.paramSet("CALIBRATE.FACTORY.STATE","COMPLETE_ERROR");
                  }
            }
            return;
         case "VIDEO.RECORD.STATE":
            switch(value)
            {
               case "IDLE":
                  if(this.__captureComplete)
                  {
                     this.__captureComplete = false;
                     if(this.__autoApplyCal)
                     {
                        this.__CALIBRATE.text = "BLACK SHADING: ANALYSIS COMPLETE.";
                        this.__gpdb.paramSet("CALIBRATE.USER.CREATE_CAL_FILE","true");
                        this.__autoApplyCal = false;
                     }
                     else
                     {
                        GUI.OSD_Components.CalibrateMC.__manager._visible = false;
                        GUI.OSD_Components.ErrorManagerMC.GetManager().PopupErrorMessage("Calibration Capture","Complete.");
                        this.Exit();
                     }
                  }
               case "ERROR":
            }
            return;
         case "CALIBRATE.USER.STATE":
            switch(value)
            {
               case "IDLE":
                  this.__gpdb.paramSet("CALIBRATE.USER.CREATE_CAL_FILE","false");
                  break;
               case "SAMPLING_SENSOR":
                  this.__CALIBRATE.text = "BLACK SHADING: SAMPLING SENSOR...";
                  GUI.OSD_Components.CalibrateMC.__manager._visible = true;
                  break;
               case "PREPARING":
                  this.__CALIBRATE.text = "BLACK SHADING: ANALYZING DATA...";
                  GUI.OSD_Components.CalibrateMC.__manager._visible = true;
                  break;
               case "CALCDARKLEVEL":
                  this.__CALIBRATE.text = "BLACK SHADING: CALCULATING BLACK LEVEL...";
                  GUI.OSD_Components.CalibrateMC.__manager._visible = true;
                  break;
               case "CALCOFFSETSANDBADS":
                  this.__CALIBRATE.text = "BLACK SHADING: CALCULATING OFFSETS...";
                  GUI.OSD_Components.CalibrateMC.__manager._visible = true;
                  break;
               case "MERGINGFACTORYCAL":
                  this.__CALIBRATE.text = "BLACK SHADING: MERGING...";
                  GUI.OSD_Components.CalibrateMC.__manager._visible = true;
                  break;
               case "CALCCORRECTIONCODES":
                  this.__CALIBRATE.text = "BLACK SHADING: CALCULATING CORRECTIONS...";
                  GUI.OSD_Components.CalibrateMC.__manager._visible = true;
                  break;
               case "WRITINGFILE":
                  this.__CALIBRATE.text = "BLACK SHADING: WRITING...";
                  GUI.OSD_Components.CalibrateMC.__manager._visible = true;
                  break;
               case "INSTALLING":
                  this.__CALIBRATE.text = "BLACK SHADING: INSTALLING...";
                  GUI.OSD_Components.CalibrateMC.__manager._visible = true;
                  break;
               case "COMPLETE_SUCCESS":
                  this.scrnMgr.Activate("ScrnCalDoneMC");
                  GUI.OSD_Components.CalibrateMC.__manager._visible = true;
                  break;
               case "COMPLETE_ERROR":
                  _global.VxError("CalibrateMC::Update(): CALIBRATE.USER.STATE==COMPLETE_ERROR --> Calibration Failed.");
                  this.scrnMgr.Activate("ScrnCalFailedMC");
                  GUI.OSD_Components.CalibrateMC.__manager._visible = true;
                  break;
               default:
                  _global.VxError("CalibrateMC.Update() Unknown USERCALFILEPROGRESS state, \'" + value + "\'. Bailing out.");
                  this.Exit();
            }
            return;
         case "CALIBRATE.FACTORY.STATE":
            switch(value)
            {
               case "IDLE":
                  break;
               case "START":
                  facCalScreen = this.scrnMgr.GetScreen("ScrnFacCalApplyInProgMC");
                  facCalScreen.Activate();
                  facCalScreen.SetStateString("Starting calibration process...");
                  GUI.OSD_Components.CalibrateMC.__manager._visible = true;
                  this.__gpdb.paramSet("CALIBRATE.FACTORY.APPLY_CAL_FILE",false);
                  break;
               case "ERASE_OLD":
                  facCalScreen.SetStateString("Erasing the old calibration file...");
                  break;
               case "WRITE_NEW":
                  facCalScreen.SetStateString("Writing the new calibration file...");
                  break;
               case "COMPLETE_SUCCESS":
                  this.scrnMgr.Activate("ScrnFacCalApplyDoneMC");
                  GUI.OSD_Components.CalibrateMC.__manager._visible = true;
                  break;
               case "COMPLETE_ERROR":
                  this.scrnMgr.Activate("ScrnFacCalApplyFailedMC");
                  GUI.OSD_Components.CalibrateMC.__manager._visible = true;
            }
            return;
         case "CALIBRATE.USER.DELETE_CAL_FILE":
            if(value == "false")
            {
               this.HandleRestoreComplete();
            }
            return;
         default:
            return;
      }
   }
}
