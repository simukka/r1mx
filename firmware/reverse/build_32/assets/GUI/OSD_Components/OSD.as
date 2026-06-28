class GUI.OSD_Components.OSD extends MovieClip
{
   var __GoCameraFnc;
   var __GoSplashFnc;
   var __SplashScreen;
   var __UpgradeMC;
   var __formatMgr;
   var __frameCount;
   var __gadgetMgr;
   var __gpdb;
   var __mcFullScreens;
   var __messagePopup;
   var __overlayPlot;
   var __profileMgr;
   var __sLCD;
   var __sensor;
   var __slate;
   var __underlayPlot;
   var mcBase;
   var mcSplashScreen;
   var mcUpgradeScreen;
   var onKeyDown;
   var slcd;
   static var __mc;
   static var __osd;
   var __isActive = false;
   function OSD()
   {
      super();
      GUI.OSD_Components.OSD.__osd = this;
      _global.VxDebug("...........................................................................CTOR OSD()");
      this.createEmptyMovieClip("mcBase",this.getNextHighestDepth());
      GUI.OSD_Components.OSD.__mc = this.mcBase;
      GUI.OSD_Components.OSD.__mc._visible = false;
      this.__GoSplashFnc = mx.utils.Delegate.create(this,this.GoSplash);
      this.__GoCameraFnc = mx.utils.Delegate.create(this,this.GoCamera);
      this.__frameCount = 0;
      this.setGeom("4k_35mm");
   }
   static function GetManager()
   {
      if(GUI.OSD_Components.OSD.__osd === undefined)
      {
         _global.VxError("OSD::GetManager(): ERROR! Called before created.");
      }
      return GUI.OSD_Components.OSD.__osd;
   }
   static function getVisual()
   {
      return GUI.OSD_Components.OSD.__mc;
   }
   function IsActive()
   {
      return this.__isActive;
   }
   function CreateStatusLCD()
   {
      this.attachMovie("StatusLCD","slcd",this.getNextHighestDepth(),{_x:0,_y:848});
      this.__sLCD = this.slcd;
   }
   function getGoFnc()
   {
      return this.__GoSplashFnc;
   }
   function GoSplash()
   {
      this.__gpdb = _global.gpdb;
      _global.log("GuiBoot(4).......OSD is Initializing");
      this.attachMovie("SplashScreenMC","mcSplashScreen",this.getNextHighestDepth(),{__continueFnc:this.__GoCameraFnc});
      this.__SplashScreen = this.mcSplashScreen;
      this.__SplashScreen.SetGPDB(this.__gpdb);
      this.CreateStatusLCD();
      new GUI.OSD_Components.TabManager();
      new GUI.OSD_Components.ButtonManager();
      new GUI.OSD_Components.MenuManager();
      new GUI.OSD_Components.SplatManager();
      new GUI.OSD_Components.ToneManager();
      this.SetupKeyListeners();
      GUI.OSD_Components.StatusLCD.GetManager().GoSplash();
      this.attachMovie("UpgradeMC","mcUpgradeScreen",this.getNextHighestDepth(),{_x:0,_y:0,__gpdb:_global.gpdb});
      this.__UpgradeMC = this.mcUpgradeScreen;
      var _loc3_;
      if(this.__gpdb.paramGetBoolean("UPGRADE.AVAILABLE"))
      {
         _global.VxLog("OSD::GoSplash() UPGRADE.AVAILABLE! Proceeding with SmartUpgrade()...");
         this.__gpdb.callbacksEnabled = true;
         _global.VxForceRedraw();
         _loc3_ = this.__gpdb.paramGetNumber("CAMERA.SLAVE_MODE_ACTIVE");
         if(_loc3_ == 0 || _loc3_ == 1)
         {
            this.__gpdb.paramSet("GUI.BUTTON_INPUT_ENABLED","true");
         }
         this.__UpgradeMC.SmartUpgrade(this.__GoCameraFnc);
      }
      else
      {
         this.__GoCameraFnc();
      }
   }
   function GoCamera()
   {
      _global.VxForceRedraw();
      this.__slate = new GUI.OSD_Components.Slate();
      GUI.OSD_Components.OSD.__mc.attachMovie("VideoLayer","mcUnderlay",GUI.OSD_Components.OSD.__mc.getNextHighestDepth(),{_x:0,_y:64,__imageParamName:"GUI.LAYERS.UNDERLAY_PLOT_PATHNAME"});
      this.__underlayPlot = GUI.OSD_Components.OSD.__mc.mcUnderlay;
      var _loc3_ = this.__gpdb.paramGet("SYSTEM.DEV.SDCARD.ROOT_PATH");
      if(_loc3_ != "")
      {
         this.__underlayPlot.LoadPlot(_loc3_ + "/PLOTS/UNDERLAY.JPG");
      }
      GUI.OSD_Components.OSD.__mc.attachMovie("Sensor","mcSensor",GUI.OSD_Components.OSD.__mc.getNextHighestDepth(),{_x:0,_y:64});
      this.__sensor = GUI.OSD_Components.OSD.__mc.mcSensor;
      GUI.OSD_Components.OSD.__mc.attachMovie("HudPanelsMC","mcHudPanels",GUI.OSD_Components.OSD.__mc.getNextHighestDepth(),{_x:0,_y:0});
      GUI.OSD_Components.OSD.__mc.attachMovie("VideoLayer","mcOverlay",GUI.OSD_Components.OSD.__mc.getNextHighestDepth(),{_x:0,_y:64,__imageParamName:"GUI.LAYERS.OVERLAY_PLOT_PATHNAME"});
      this.__overlayPlot = GUI.OSD_Components.OSD.__mc.mcOverlay;
      GUI.OSD_Components.OSD.__mc.attachMovie("MessagePopupMC","messagePopupMC",this.getNextHighestDepth(),{_x:290,_y:200,_visible:false});
      this.__messagePopup = GUI.OSD_Components.OSD.__mc.messagePopupMC;
      new GUI.OSD_Components.RecordManager();
      new GUI.OSD_Components.TimeManager();
      new GUI.OSD_Components.LcdManager();
      new GUI.OSD_Components.GpioManager();
      new GUI.OSD_Components.MediaManager();
      this.__gadgetMgr = new GUI.OSD_Components.GadgetManager(GUI.OSD_Components.OSD.__mc);
      GUI.OSD_Components.OSD.__mc.attachMovie("ScreenMgrMC","mcScreenMgr",GUI.OSD_Components.OSD.__mc.getNextHighestDepth());
      this.__mcFullScreens = GUI.OSD_Components.OSD.__mc.mcScreenMgr;
      this.__formatMgr = new GUI.OSD_Components.FormatManager();
      new GUI.OSD_Components.UserGuideManager();
      GUI.OSD_Components.OSD.__mc.attachMovie("ErrorManagerMC","mcErrorManager",GUI.OSD_Components.OSD.__mc.getNextHighestDepth());
      this.__mcFullScreens.AttachScreen("CalibrateMC");
      GUI.OSD_Components.OSD.__mc.attachMovie("ShutdownMC","mcShutdown",GUI.OSD_Components.OSD.__mc.getNextHighestDepth());
      this.__profileMgr = new GUI.OSD_Components.ProfileMgr();
      GUI.OSD_Components.MenuManager.GetManager().LoadPanels();
      this.AddGpdbCallbacks();
   }
   function GoReady()
   {
      GUI.OSD_Components.OSD.__mc._visible = true;
      this._visible = true;
      var _loc3_ = 60000;
      setInterval(this,"handleRuntimeTimer",_loc3_);
      this.__SplashScreen.removeMovieClip();
      _global.VxForceRedraw();
      GUI.OSD_Components.SplatManager.GetManager().AllowSplat(true);
      this.__sLCD.SetPane(GUI.OSD_Components.StatusLCD.PANE_STATUS);
      new GUI.OSD_Components.LedMgr();
      this.__gpdb.paramSet("GUI.RUN_STATE","GUI_STATE_2_ACTIVATE_CALLBACKS");
      this.__gpdb.callbacksEnabled = true;
      this.__gpdb.paramSet("GUI.RUN_STATE","GUI_STATE_3_INITIALIZE_GUI_STATE");
   }
   function InitializeGuiObjects()
   {
      this.__gpdb.paramSet("GUI.GUI_MODE","RECORD");
      GUI.OSD_Components.HudLowerMC.GetManager().RefreshDisplay();
      this.__isActive = true;
      this.__gpdb.paramSet("GUI.RUN_STATE","GUI_STATE_4_ACTIVATE_USER_INPUT");
      var _loc3_ = this.__gpdb.paramGetNumber("CAMERA.SLAVE_MODE_ACTIVE");
      if(_loc3_ == 0 || _loc3_ == 1)
      {
         this.__gpdb.paramSet("GUI.BUTTON_INPUT_ENABLED",true);
      }
      _global.VxSignalSwfInitComplete();
      _global.VxForceRedraw();
      _global.log("GuiBoot(7).......OSD is Active");
      this.__gpdb.paramSet("GUI.RUN_STATE","GUI_STATE_5_READY");
   }
   function AddGpdbCallbacks()
   {
      var _loc2_ = mx.utils.Delegate.create(this,this.Update);
      this.__gpdb.addCallback("GUI.RUN_STATE",_loc2_);
      this.__gpdb.addCallback("VIDEO.RECORD.STATE",_loc2_);
      this.__gpdb.addCallback("UPGRADE.STATUS",_loc2_);
   }
   function traceParam(name, value)
   {
   }
   function postWarning(name, value)
   {
      this.__sensor.hideWarning();
      if(value != "")
      {
         this.__sensor.showWarning(value);
      }
   }
   function dumpGpdbParams(_name, _value)
   {
      var _loc2_ = function(name, type, value)
      {
      };
      this.__gpdb.iterateOverPDB(_loc2_);
   }
   function setGeom(geomStr)
   {
      GUI.OSD_Components.Geom.Configure(geomStr);
      this.__sensor.UpdateGeom();
   }
   function GetUnderlay()
   {
      return this.__underlayPlot;
   }
   function GetOverlay()
   {
      return this.__overlayPlot;
   }
   function GetMessagePopup()
   {
      return this.__messagePopup;
   }
   function warning(msg)
   {
      this.__gpdb.paramSet("SYSTEM.ERROR.WARNING_TEXT",msg);
      this.__gpdb.paramSet("SYSTEM.ERROR.GENERAL","GENERIC");
   }
   function logMsg(msg)
   {
      this.__gpdb.paramSet("GUI.LOGMSG",msg);
   }
   function exploreObject(o)
   {
      for(var _loc2_ in o)
      {
      }
   }
   function getSoftKeyHandler()
   {
      return this.handleSoftKeyCommit;
   }
   function handleSoftKeyCommit(name, value)
   {
   }
   function Update(param, value)
   {
      switch(param)
      {
         case "GUI.RUN_STATE":
            if(value == "GUI_STATE_3_INITIALIZE_GUI_STATE")
            {
               this.InitializeGuiObjects();
            }
            return;
         case "VIDEO.RECORD.STATE":
            if(value == "ACTIVE")
            {
               this.__gpdb.paramSet("VIDEO.MONITOR.TEST_PATTERN.ENABLED","false");
            }
            return;
         case "UPGRADE.STATUS":
            this.handleUpgrade(value);
            return;
         default:
            return;
      }
   }
   function handleUpgrade(state)
   {
      switch(state)
      {
         case "START_UPGRADE":
         case "UPDATE_IMAGE1":
         case "UPDATE_IMAGE2":
         case "SETUP_DIRECTORY":
         case "UNTAR":
         case "CHECK4FPGA":
         case "CHECK4VxAPP":
         case "ERASE_FPGA":
         case "PROGRAM_FPGA":
         case "ERASE_APP":
         case "PROGRAM_APP":
         case "SET_ACTIVE_IMAGE":
         case "INVALID":
         case "COMPLETE_UPGRADE":
         default:
            return;
      }
   }
   function handleRuntimeTimer()
   {
      var _loc3_ = Number(this.__gpdb.paramGet("SYSTEM.MANUFACTURING.RUNTIME"));
      _loc3_ += 1;
      this.__gpdb.paramSet("SYSTEM.MANUFACTURING.RUNTIME",_loc3_.toString());
      var _loc4_ = 10;
      var _loc2_ = _loc4_ * 60;
      var _loc5_ = _loc2_ - this.__frameCount;
      var _loc6_ = Math.floor(_loc5_ / _loc2_ * 100);
      this.__frameCount = 0;
   }
   function onEnterFrame()
   {
      _global.VxLogWvEvent(1,"onEnterFrame()");
      this.__frameCount = this.__frameCount + 1;
   }
   function SetupKeyListeners()
   {
      Key.addListener(this);
      this.onKeyDown = GUI.OSD_Components.ButtonManager.GetManager().handleOnKeyDown;
   }
   static function TRACE(s)
   {
      var _loc3_;
      var _loc2_;
      var _loc1_;
      try
      {
         throw new Error();
      }
      catch(e:Error)
      {
         _loc3_ = e.getStackTrace();
         _loc2_ = _loc3_.split("\n");
         _loc1_ = String(_loc2_[2]);
         _loc1_ = _loc1_.replace("\t","");
         _loc1_ = _loc1_.substr("at ".length);
         _loc1_ = _loc1_.substring(0,_loc1_.indexOf("["));
      }
   }
}
