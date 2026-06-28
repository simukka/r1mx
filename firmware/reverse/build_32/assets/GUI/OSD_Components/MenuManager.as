class GUI.OSD_Components.MenuManager
{
   var __currentMenu;
   var __gpdb;
   var __osd;
   var __osdxml;
   var __panelStack;
   var __returnMenuName;
   static var __manager;
   var __panelList = new Object();
   var __numPanels = 0;
   var temp = 0;
   var Tintoffset = 0;
   var Flutoffset = 0;
   function MenuManager()
   {
      _global.VxDebug("...........................................................................CTOR MenuManager()");
      GUI.OSD_Components.MenuManager.__manager = this;
      this.__gpdb = _global.gpdb;
      this.__osd = GUI.OSD_Components.OSD.GetManager();
      this.__panelStack = new Array();
      this.HandleQtProxies();
      this.AddCallbacks();
   }
   function dispatchEvent()
   {
   }
   function addEventListener()
   {
   }
   function removeEventListener()
   {
   }
   static function GetManager()
   {
      if(GUI.OSD_Components.MenuManager.__manager === undefined)
      {
         _global.VxError("ERROR! MenuManager::GetManager() called before being instantiated");
      }
      return GUI.OSD_Components.MenuManager.__manager;
   }
   function AddCallbacks()
   {
      this.__gpdb.addCallback("GUI.SOFTKEY",mx.utils.Delegate.create(this,this.DispatchPanelWidgetPress));
      this.__gpdb.addCallback("GUI.SOFTKEY.GENERATE_QUICKTIME_PROXIES",mx.utils.Delegate.create(this,this.HandleQtProxies));
      this.__gpdb.addCallback("VIDEO.PLAYBACK.STATE",mx.utils.Delegate.create(this,this.HandlePlayback));
      this.__gpdb.addCallback("GUI.SOFTKEY.USER_KEY.MULTI",mx.utils.Delegate.create(this,this.HandleMulti));
      this.__gpdb.addCallback("GUI.USER_PREF.SHUTTER_SPEED_FORMAT",mx.utils.Delegate.create(this,this.HandleShutter));
      this.__gpdb.addCallback("GUI.PAINT.WHITE_BALANCE.SLAVE_MODE",mx.utils.Delegate.create(this,this.HandleSlaveWBMode));
      this.__gpdb.addCallback("PAINT.SLAVE.TINT.CURRENT",mx.utils.Delegate.create(this,this.HandleSlaveTINTcurrent));
      this.__gpdb.addCallback("GUI.PAINT.SLAVE.SHADOWFLUT",mx.utils.Delegate.create(this,this.HandleSlaveShadowFlut));
      this.__gpdb.addCallback("PAINT.SLAVE.WHITE_BALANCE.CURRENT",mx.utils.Delegate.create(this,this.HandleSlaveManualWB));
      this.__gpdb.addCallback("CAMERA.SLAVE_MODE_IMPORT_WHITE_BALANCE",mx.utils.Delegate.create(this,this.HandleSlaveimportWB));
      this.__gpdb.addCallback("CAMERA.SLAVE_MODE_IMPORT_TINT",mx.utils.Delegate.create(this,this.HandleSlaveimportTINT));
      this.__gpdb.addCallback("CAMERA.SLAVE_MODE_IMPORT_FLUT",mx.utils.Delegate.create(this,this.HandleSlaveimportFLUT));
   }
   function HandleShutter(param, value)
   {
      var _loc3_ = this.GetPanel("Panel_Shutter");
      var _loc5_;
      var _loc4_;
      if(_loc3_ == undefined)
      {
         _global.VxError("GetPanel Failed: panel == undefined");
      }
      else if(value == "DEGREES")
      {
         _loc3_.setTabSelParam("SELECT_TAB_SHUTTER_SPEED","GUI.RECORD.SHUTTER_SPEED_DEG");
         _loc5_ = this.__gpdb.paramGetNumber("GUI.RECORD.SHUTTER_SPEED");
         _loc4_ = Math.round(Number(this.__gpdb.paramGet("PROJECT.MODE_MATRIX.FRAME_RATE")));
         if(_loc5_ < _loc4_)
         {
            this.__gpdb.paramSet("GUI.RECORD.SHUTTER_SPEED_DEG",_loc4_);
         }
         else
         {
            this.__gpdb.paramSet("GUI.RECORD.SHUTTER_SPEED_DEG",_loc5_);
         }
      }
      else
      {
         _loc3_.setTabSelParam("SELECT_TAB_SHUTTER_SPEED","GUI.RECORD.SHUTTER_SPEED");
         this.__gpdb.paramSet("GUI.RECORD.SHUTTER_SPEED",this.__gpdb.paramGetNumber("GUI.RECORD.SHUTTER_SPEED_DEG"));
      }
   }
   function HandleMulti(param, value)
   {
      var _loc2_ = Number(value);
      switch(_loc2_)
      {
         case 0:
            this.__gpdb.paramSet("GUI.MONITOR.OUTPUT_EFFECTS.ENABLED",true);
            this.__gpdb.paramSet("GUI.MONITOR.OUTPUT_EFFECTS.MODE","RAWCHECK");
            return;
         case 1:
            this.__gpdb.paramSet("GUI.MONITOR.OUTPUT_EFFECTS.ENABLED",true);
            this.__gpdb.paramSet("GUI.MONITOR.OUTPUT_EFFECTS.MODE","EDGEHIGHLIGHT");
            return;
         case 2:
            this.__gpdb.paramSet("GUI.MONITOR.OUTPUT_EFFECTS.ENABLED",true);
            this.__gpdb.paramSet("GUI.MONITOR.OUTPUT_EFFECTS.MODE","FALSECOLOR");
            return;
         case 3:
         default:
            this.__gpdb.paramSet("GUI.MONITOR.OUTPUT_EFFECTS.ENABLED",false);
            return;
      }
   }
   function HandleSlaveTINTcurrent(param, value)
   {
      var _loc7_;
      var _loc5_;
      var _loc6_;
      var _loc4_;
      var _loc2_;
      var _loc8_;
      var _loc9_;
      var _loc3_;
      _loc7_ = this.__gpdb.paramGetNumber("CAMERA.SLAVE_MODE_ACTIVE");
      _loc5_ = this.__gpdb.paramGetNumber("CAMERA.SLAVE_MODE_ACTIVE_BEFORE_SENDING_PARAMETERS");
      if(_loc7_ == 2 || _loc5_ == 2)
      {
         _loc8_ = this.__gpdb.paramGetNumber("PAINT.SLAVE.TINT.CURRENT");
         _loc9_ = this.__gpdb.paramGetNumber("GUI.PAINT.AUTO.WBAL.CLEAR");
         if(_loc9_ == 1 && _loc8_ == 0)
         {
            this.__gpdb.paramSet("GUI.PAINT.AUTO.WBAL.CLEAR",0);
            this.Tintoffset = 0;
         }
         else
         {
            this.__gpdb.paramSet("GUI.PAINT.AUTO.WBAL.CLEAR",0);
            _loc6_ = this.__gpdb.paramGetNumber("PAINT.SLAVE.TINT.CURRENT");
            _loc4_ = this.__gpdb.paramGetNumber("PAINT.TINT.CURRENT");
            _loc3_ = _loc6_ - this.Tintoffset;
            this.Tintoffset += _loc3_;
            _loc2_ = _loc4_ + _loc3_;
            if(_loc2_ > 100)
            {
               _loc2_ = 100;
            }
            if(_loc2_ < -100)
            {
               _loc2_ = -100;
            }
            this.__gpdb.paramSet("PAINT.TINT.CURRENT",_loc2_);
         }
      }
   }
   function HandleSlaveimportWB(param, value)
   {
      var _loc5_;
      var _loc3_;
      var _loc4_;
      var _loc2_;
      _loc5_ = this.__gpdb.paramGetNumber("CAMERA.SLAVE_MODE_ACTIVE");
      if(_loc5_ == 2)
      {
         _loc3_ = this.__gpdb.paramGetNumber("CAMERA.SLAVE_MODE_IMPORT_WHITE_BALANCE");
         _loc4_ = this.__gpdb.paramGetNumber("PAINT.SLAVE.WHITE_BALANCE.CURRENT");
         _loc2_ = _loc3_ + _loc4_;
         if(_loc2_ < 1700)
         {
            _loc2_ = 1700;
         }
         this.__gpdb.paramSet("PAINT.WHITE_BALANCE.CURRENT",_loc2_);
      }
   }
   function HandleSlaveimportTINT(param, value)
   {
      var _loc3_;
      var _loc5_;
      var _loc4_;
      var _loc2_;
      _loc3_ = this.__gpdb.paramGetNumber("CAMERA.SLAVE_MODE_ACTIVE");
      if(_loc3_ == 2)
      {
         _loc5_ = this.__gpdb.paramGetNumber("CAMERA.SLAVE_MODE_IMPORT_TINT");
         _loc4_ = this.__gpdb.paramGetNumber("PAINT.SLAVE.TINT.CURRENT");
         _loc2_ = _loc5_ + _loc4_;
         if(_loc2_ > 100)
         {
            _loc2_ = 100;
         }
         if(_loc2_ < -100)
         {
            _loc2_ = -100;
         }
         this.__gpdb.paramSet("PAINT.TINT.CURRENT",_loc2_);
      }
   }
   function HandleSlaveimportFLUT(param, value)
   {
      var _loc3_;
      var _loc5_;
      var _loc4_;
      var _loc2_;
      _loc3_ = this.__gpdb.paramGetNumber("CAMERA.SLAVE_MODE_ACTIVE");
      if(_loc3_ == 2)
      {
         _loc5_ = this.__gpdb.paramGetNumber("CAMERA.SLAVE_MODE_IMPORT_FLUT");
         _loc4_ = this.__gpdb.paramGetNumber("GUI.PAINT.SLAVE.SHADOWFLUT");
         _loc2_ = _loc5_ + _loc4_;
         if(_loc2_ > 4)
         {
            _loc2_ = 4;
         }
         if(_loc2_ < -4)
         {
            _loc2_ = -4;
         }
         this.__gpdb.paramSet("GUI.PAINT.EXPOSURE.FLUT",_loc2_);
      }
   }
   function HandleSlaveShadowFlut(param, value)
   {
      var _loc6_;
      var _loc4_;
      var _loc7_;
      var _loc5_;
      var _loc3_;
      var _loc2_;
      _loc6_ = this.__gpdb.paramGetNumber("CAMERA.SLAVE_MODE_ACTIVE");
      _loc4_ = this.__gpdb.paramGetNumber("CAMERA.SLAVE_MODE_ACTIVE_BEFORE_SENDING_PARAMETERS");
      if(_loc6_ == 2 || _loc4_ == 2)
      {
         _loc7_ = this.__gpdb.paramGetNumber("GUI.PAINT.SLAVE.SHADOWFLUT");
         _loc5_ = this.__gpdb.paramGetNumber("GUI.PAINT.EXPOSURE.FLUT");
         _loc3_ = _loc7_ - this.Flutoffset;
         this.Flutoffset += _loc3_;
         _loc2_ = _loc5_ + _loc3_;
         if(_loc2_ > 4)
         {
            _loc2_ = 4;
         }
         if(_loc2_ < -4)
         {
            _loc2_ = -4;
         }
         this.__gpdb.paramSet("GUI.PAINT.EXPOSURE.FLUT",_loc2_);
      }
   }
   function HandleSlaveManualWB(param, value)
   {
      var _loc9_;
      var _loc5_;
      var _loc4_;
      var _loc7_;
      var _loc3_;
      var _loc2_;
      var _loc6_;
      var _loc8_;
      _loc9_ = this.__gpdb.paramGetNumber("CAMERA.SLAVE_MODE_ACTIVE");
      _loc5_ = this.__gpdb.paramGetNumber("CAMERA.SLAVE_MODE_ACTIVE_BEFORE_SENDING_PARAMETERS");
      if(_loc9_ == 2 || _loc5_ == 2)
      {
         _loc4_ = this.__gpdb.paramGetNumber("PAINT.SLAVE.WHITE_BALANCE.CURRENT");
         _loc8_ = this.__gpdb.paramGetNumber("GUI.PAINT.AUTO.WBAL.CLEAR");
         if(_loc8_ == 1 && _loc4_ == 0)
         {
            this.__gpdb.paramSet("GUI.PAINT.AUTO.WBAL.CLEAR",0);
            this.temp = 0;
         }
         else
         {
            this.__gpdb.paramSet("GUI.PAINT.AUTO.WBAL.CLEAR",0);
            _loc6_ = this.__gpdb.paramGetNumber("PAINT.SLAVE.WHITE_BALANCE.CURRENT");
            _loc7_ = this.__gpdb.paramGetNumber("PAINT.WHITE_BALANCE.CURRENT");
            _loc3_ = _loc6_ - this.temp;
            this.temp += _loc3_;
            _loc2_ = _loc7_ + _loc3_;
            if(_loc2_ < 1700)
            {
               _loc2_ = 1700;
            }
            this.__gpdb.paramSet("PAINT.WHITE_BALANCE.CURRENT",_loc2_);
         }
      }
   }
   function HandleSlaveCWManualWB(param, value)
   {
      var _loc5_;
      var _loc4_;
      var _loc3_;
      var _loc2_;
      _loc5_ = this.__gpdb.paramGetNumber("GUI.PAINT.CW.SLAVE.MANUAL_WHITE_BALANCE");
      if(_loc5_ > 0)
      {
         _loc3_ = this.__gpdb.paramGetNumber("CAMERA.SLAVE_MODE_ACTIVE");
         if(_loc3_ == 2)
         {
            _loc4_ = this.__gpdb.paramGetNumber("GUI.PAINT.CW.SLAVE.MANUAL_WHITE_BALANCE");
            _loc2_ = this.__gpdb.paramGetNumber("PAINT.WHITE_BALANCE.CURRENT") + 100 * _loc4_;
            if(_loc2_ > 100000)
            {
               _loc2_ = 100000;
            }
            this.__gpdb.paramSet("PAINT.WHITE_BALANCE.CURRENT",_loc2_.toString());
         }
      }
   }
   function HandleSlaveCCWManualWB(param, value)
   {
      var _loc4_;
      var _loc3_;
      var _loc5_;
      var _loc2_;
      _loc4_ = this.__gpdb.paramGetNumber("GUI.PAINT.CCW.SLAVE.MANUAL_WHITE_BALANCE");
      if(_loc4_ > 0)
      {
         _loc5_ = this.__gpdb.paramGetNumber("CAMERA.SLAVE_MODE_ACTIVE");
         if(_loc5_ == 2)
         {
            _loc3_ = this.__gpdb.paramGetNumber("GUI.PAINT.CCW.SLAVE.MANUAL_WHITE_BALANCE");
            _loc2_ = this.__gpdb.paramGetNumber("PAINT.WHITE_BALANCE.CURRENT") - 100 * _loc3_;
            if(_loc2_ < 1700)
            {
               _loc2_ = 1700;
            }
            this.__gpdb.paramSet("PAINT.WHITE_BALANCE.CURRENT",_loc2_.toString());
         }
      }
   }
   function HandleSlaveWBMode(param, value)
   {
      var _loc6_;
      var _loc11_;
      var _loc2_;
      var _loc9_;
      var _loc12_;
      var _loc10_;
      var _loc13_;
      var _loc14_;
      var _loc8_;
      var _loc7_;
      var _loc3_;
      var _loc4_;
      var _loc5_;
      var _loc15_;
      _loc6_ = this.__gpdb.paramGetNumber("GUI.PAINT.WHITE_BALANCE.SLAVE_MODE");
      if(_loc6_ > 0)
      {
         _loc9_ = this.__gpdb.paramGetNumber("CAMERA.SLAVE_MODE_ACTIVE");
         if(_loc9_ == 2)
         {
            _loc11_ = this.__gpdb.paramGetNumber("GUI.PAINT.WHITE_BALANCE.SLAVE_MODE");
            switch(_loc11_)
            {
               case 1:
                  _loc13_ = 3200;
                  _loc8_ = this.__gpdb.paramGetNumber("PAINT.SLAVE.WHITE_BALANCE.CURRENT");
                  _loc3_ = _loc13_ + _loc8_;
                  if(_loc3_ < 1700)
                  {
                     _loc3_ = 1700;
                  }
                  this.__gpdb.paramSet("PAINT.WHITE_BALANCE.CURRENT",_loc3_);
                  _loc5_ = this.__gpdb.paramGetNumber("PAINT.SLAVE.TINT.CURRENT");
                  this.__gpdb.paramSet("PAINT.TINT.CURRENT",_loc5_);
                  return;
               case 2:
                  _loc14_ = 5600;
                  _loc7_ = this.__gpdb.paramGetNumber("PAINT.SLAVE.WHITE_BALANCE.CURRENT");
                  _loc4_ = _loc14_ + _loc7_;
                  if(_loc4_ < 1700)
                  {
                     _loc4_ = 1700;
                  }
                  this.__gpdb.paramSet("PAINT.WHITE_BALANCE.CURRENT",_loc4_);
                  _loc15_ = this.__gpdb.paramGetNumber("PAINT.SLAVE.TINT.CURRENT");
                  this.__gpdb.paramSet("PAINT.TINT.CURRENT",_loc15_);
                  return;
               case 3:
                  _loc12_ = this.__gpdb.paramGetNumber("GUI.PAINT.CW.STEP.SIZE");
                  _loc2_ = this.__gpdb.paramGetNumber("PAINT.WHITE_BALANCE.CURRENT") + 100 * _loc12_;
                  if(_loc2_ > 100000)
                  {
                     _loc2_ = 100000;
                  }
                  this.__gpdb.paramSet("PAINT.WHITE_BALANCE.CURRENT",_loc2_.toString());
                  return;
               case 4:
                  _loc10_ = this.__gpdb.paramGetNumber("GUI.PAINT.CCW.STEP.SIZE");
                  _loc2_ = this.__gpdb.paramGetNumber("PAINT.WHITE_BALANCE.CURRENT") - 100 * _loc10_;
                  if(_loc2_ < 1700)
                  {
                     _loc2_ = 1700;
                  }
                  this.__gpdb.paramSet("PAINT.WHITE_BALANCE.CURRENT",_loc2_.toString());
                  return;
               case 5:
                  this.__gpdb.paramSet("GUI.PAINT.WHITE_BALANCE.AUTO","true");
                  this.__gpdb.paramSet("GUI.PAINT.AUTO.WBAL.CLEAR",1);
                  return;
               case 0:
               default:
                  return;
            }
         }
      }
   }
   function HandleSensorAdvanced(param, value)
   {
      _global.VxError("MenuManager.HandleSensorAdvanced(): Called");
      GUI.OSD_Components.SensorAdvancedMC.GetManager().SmartAdvance();
   }
   function LoadPanels()
   {
      this.__osdxml = new GUI.OSD_Components.OsdXml("panels.xml",mx.utils.Delegate.create(this,this.RegisterPanel));
      this.__osdxml.addEventListener("xmlPanelLoadComplete",mx.utils.Delegate.create(this,this.HandleLoadComplete));
   }
   function HandleLoadComplete()
   {
      this.InstantiatePanels();
      GUI.OSD_Components.OSD.GetManager().GoReady();
   }
   function RegisterPanel(panel)
   {
      var _loc2_ = panel.getID();
      if(!this.panelExists(_loc2_))
      {
         this.__panelList[_loc2_] = panel;
         this.__numPanels = this.__numPanels + 1;
      }
   }
   function GetPanelWidget(panelId, widgetId)
   {
      var _loc6_ = this.__panelList[panelId];
      var _loc3_;
      if(_loc6_)
      {
         _loc3_ = _loc6_.GetWidget(widgetId);
         if(_loc3_ == undefined)
         {
            _global.VxError("MenuManager::GetPanelWidget(" + panelId + ", " + widgetId + ") widget: " + _loc3_);
         }
      }
      else
      {
         _global.VxError("MenuManager::GetPanelWidget(" + panelId + ", " + widgetId + ") PANEL NOT FOUND");
      }
      return _loc3_;
   }
   function GetPanel(panelId)
   {
      var _loc3_ = this.__panelList[panelId];
      if(_loc3_ == undefined)
      {
         _global.VxError("MenuManager::GetPanelWidget(" + panelId);
      }
      return _loc3_;
   }
   function InstantiatePanels()
   {
      var _loc3_ = 0;
      for(var _loc4_ in this.__panelList)
      {
         try
         {
            this.__panelList[_loc4_].instantiate();
         }
         catch(e)
         {
            _global.VxLog("Error while instantiating panel: " + e.toString());
            _global.VxLog("Continuing in KNOWN BAD STATE...");
         }
         _loc3_ = _loc3_ + 1;
      }
   }
   function CurrentMenu()
   {
      var _loc2_;
      if(this.__currentMenu)
      {
         _loc2_ = this.__currentMenu.getID();
      }
      return _loc2_;
   }
   function PushMenuPanel(name)
   {
      var _loc3_ = this.__panelList[name];
      var _loc5_ = this.__currentMenu;
      var _loc6_;
      if(_loc3_ != null)
      {
         if(_loc3_.IsUnlocked())
         {
            _loc6_ = _loc3_.IsEmptyGizmoGrid();
            if(!_loc6_)
            {
               if(_loc5_ != null)
               {
                  this.__panelStack.push(_loc5_);
               }
               GUI.OSD_Components.HudLowerMC.GetManager().Show(false);
               _loc3_.show();
               if(_loc5_ != null)
               {
                  _loc5_.hide();
               }
               this.__currentMenu = _loc3_;
               GUI.OSD_Components.TabManager.GetManager().push(_loc3_.getTabTargets());
               this.__returnMenuName = name;
            }
            else
            {
               _global.VxError("MenuManager:PushMenuPanel(): panel: \'" + _loc3_.getID() + "\' contains no gizmos. Ignoring.");
            }
         }
         else
         {
            _global.VxError("MenuManager.PushMenuPanel(): panel \'" + name + "\' is LOCKED. No capability. Ignoring.");
         }
      }
      else
      {
         _global.VxError("MenuManager.PushMenuPanel(): UNKNOWN panel named \'" + name + "\'");
      }
   }
   function PopMenuPanel(showHUD)
   {
      var _loc4_ = this.__currentMenu;
      var _loc3_;
      if(_loc4_ != null)
      {
         _loc3_ = GUI.OSD_Components.MenuPanelMC(this.__panelStack.pop());
         if(GUI.OSD_Components.TabManager.GetManager().pop())
         {
            GUI.OSD_Components.StatusLCD.GetManager().SetPane(GUI.OSD_Components.StatusLCD.PANE_STATUS);
         }
         if(_loc3_ != null)
         {
            _loc3_.show();
         }
         _loc4_.hide();
         this.__currentMenu = _loc3_;
         if(this.__currentMenu == null && showHUD)
         {
            _global.VxDebug("MenuManager.PopMenuPanel(): exiting menu tree, so turn Gadgets back on");
            GUI.OSD_Components.HudLowerMC.GetManager().Show(true);
         }
      }
      return this.__currentMenu;
   }
   function GotoMenuPanel(name)
   {
      if(name != undefined && name != "")
      {
         if(this.__currentMenu.getID() != name)
         {
            if(!this.panelExists(name))
            {
               throw new Error("ERROR! MenuManager.GotoMenuPanel(): Failed to find panel[\'" + name + "\']");
            }
            this.ClearMenuStack(false);
            this.PushMenuPanel(name);
         }
      }
   }
   function listMenuPanels()
   {
      for(var _loc2_ in this.__panelList)
      {
      }
   }
   function panelExists(name)
   {
      return this.__panelList[name] != null;
   }
   function ExitMenuTree()
   {
      var _loc3_ = false;
      var _loc4_ = !GUI.OSD_Components.ScreenMgrMC.GetManager().IsScreenActive();
      _global.VxDebug("MenuManager.ExitMenuTree() showHUD: " + _loc4_);
      if(this.__osd.IsActive())
      {
         _loc3_ = this.ClearMenuStack(_loc4_);
         if(_loc3_)
         {
            GUI.OSD_Components.StatusLCD.GetManager().SetPane(GUI.OSD_Components.StatusLCD.PANE_STATUS);
         }
      }
      return _loc3_;
   }
   function ReturnToLastMenu()
   {
      if(this.__currentMenu == null)
      {
         this.GotoMenuPanel(this.__returnMenuName);
      }
   }
   function ClearMenuStack(showHUD)
   {
      var _loc2_ = false;
      var _loc3_;
      while((_loc3_ = this.PopMenuPanel(showHUD)) != null)
      {
         _loc2_ = true;
      }
      return _loc2_;
   }
   function MenuBeingDisplayed()
   {
      return this.__panelStack.length > 0;
   }
   function dumpPanelStack()
   {
      var _loc2_ = 0;
      while(_loc2_ < this.__panelStack.length)
      {
         _loc2_ = _loc2_ + 1;
      }
   }
   function HandlePanelWidgetRelease(cbLabel, cbAction, cbData, arg0, arg1)
   {
      switch(cbAction)
      {
         case "Goto_Panel":
            this.PushMenuPanel(cbData);
            return;
         case "Gen_Event":
            this.generatePanelWidgetEvent(cbData);
            return;
         case "Dispatch":
            this.DispatchPanelWidgetPress(cbLabel,cbData,arg0,arg1);
            return;
         case "Selector_Tab":
            return;
         case "Parameter":
            return;
         default:
            return;
      }
   }
   function generatePanelWidgetEvent(eventName)
   {
      var _loc2_ = {target:this,type:eventName};
      this.dispatchEvent(_loc2_);
   }
   function DispatchPanelWidgetPress(id, item, arg0, arg1)
   {
      _global.VxDebug("MenuManager.DispatchPanelWidgetPress(\'" + id + "\', \'" + item + "\') arg0: \'" + arg0 + "\', arg1: \'" + arg1 + "\'");
      var _loc0_;
      switch(item)
      {
         case "POP_PANEL":
            this.PopMenuPanel(true);
            return;
         case "SHOW_SCREEN":
            if((_loc0_ = id) !== "TestScreen")
            {
               _global.VxError("Error! MenuManager::DispatchPanelWidgetPress(" + id + ") id not registered for Screen");
            }
            else
            {
               GUI.OSD_Components.ScreenMgrMC.GetManager().DisplayScreen("Test");
            }
            return;
         case "FORMAT_DIGMAG":
            GUI.OSD_Components.FormatManager.GetManager().SmartFormat();
            return;
         case "FORMAT_DIGMAG_NEW":
            this.__gpdb.paramSet("PROJECT.SLATE.FORCE_REEL",true);
            GUI.OSD_Components.FormatManager.GetManager().SmartFormat();
            return;
         case "FORMAT_DIGMAG_RESET":
            this.__gpdb.paramSet("PROJECT.SLATE.FORCE_REEL_RESET",true);
            GUI.OSD_Components.FormatManager.GetManager().SmartFormat();
            return;
         case "UPGRADE_SOFTWARE":
            GUI.OSD_Components.UpgradeMC.GetManager().SmartUpgrade();
            return;
         case "VIEW_STATUS":
            GUI.OSD_Components.ViewStatus.GetManager().SmartView(true);
            return;
         case "SENSOR_ADVANCED":
            GUI.OSD_Components.SensorAdvancedMC.GetManager().SmartAdvance();
            return;
         case "UNMOUNT_DIGMAG":
            GUI.OSD_Components.MediaManager.GetManager().Unmount();
            return;
         case "FLUSH_LOG":
            this.__gpdb.paramSet("MEDIA.DIGMAG.FLUSH_LOG",true);
            return;
         case "WHITE_BALANCE":
            this.tmpSetWhiteBalance(id);
            return;
         case "EXPORT_LOOK_PROFILE":
            GUI.OSD_Components.ProfileMgr.GetManager().ExportCurrentProfile("look");
            return;
         case "EXPORT_USER_PROFILE":
            GUI.OSD_Components.ProfileMgr.GetManager().ExportCurrentProfile("user");
            return;
         case "EXPORT_PROJECT_PROFILE":
            this.__gpdb.paramSet("SYSTEM.PROJECT.PROFILE.EXPORT.REQUESTED",true);
            GUI.OSD_Components.ProfileMgr.GetManager().ExportCurrentProfile("project");
            return;
         case "RESET_REEL_COUNT":
            this.__gpdb.paramSet("PROJECT.NUM_REELS_SHOT","0");
            return;
         case "CLEAR_LOOK_DOIT":
            GUI.OSD_Components.ProfileMgr.GetManager().HandleClearProfile("look",true,true);
            return;
         case "RESTORE_LOOK_DOIT":
            GUI.OSD_Components.ProfileMgr.GetManager().HandleClearProfile("look",false,false);
            return;
         case "RESTORE_USER_DOIT":
            GUI.OSD_Components.ProfileMgr.GetManager().HandleClearProfile("user",false,false);
            return;
         case "RESTORE_SYSTEM_DOIT":
            GUI.OSD_Components.ProfileMgr.GetManager().HandleClearProfile("system",false,false);
            return;
         case "RESTORE_ALL_DOIT":
            GUI.OSD_Components.ProfileMgr.GetManager().HandleClearProfile("ALL",false);
            return;
         case "CUSTOM_RETICLE_ACTION":
            GUI.OSD_Components.UserGuideManager.GetManager().CustomizeIt("ACTION");
            return;
         case "CUSTOM_RETICLE_TITLE":
            GUI.OSD_Components.UserGuideManager.GetManager().CustomizeIt("TITLE");
            return;
         case "SET_CLOCK":
            this.ExitMenuTree();
            GUI.OSD_Components.SplatManager.GetManager().ShowMeterSplat(false);
            GUI.OSD_Components.SplatManager.GetManager().ShowAudioSplat(false);
            GUI.OSD_Components.TimeManager.GetManager().HandleSetClock();
            return;
         case "USERCAL_START":
            GUI.OSD_Components.CalibrateMC.GetManager().HandleUserCalRequest();
            return;
         case "USERCAL_RESTORE":
            GUI.OSD_Components.CalibrateMC.GetManager().HandleRestoreRequest();
            return;
         case "CALIBRATE_CAPTURE_LIGHT_F24":
            GUI.OSD_Components.CalibrateMC.GetManager().HandleFactoryCalCaptureRequest("LIGHT_F24");
            return;
         case "CALIBRATE_CAPTURE_LIGHT":
            GUI.OSD_Components.CalibrateMC.GetManager().HandleFactoryCalCaptureRequest("LIGHT");
            return;
         case "CALIBRATE_CAPTURE_DARK":
            GUI.OSD_Components.CalibrateMC.GetManager().HandleFactoryCalCaptureRequest("DARK");
            return;
         case "CALIBRATE_APPLY":
            GUI.OSD_Components.CalibrateMC.GetManager().HandleFactoryCalApplyRequest();
            return;
         case "RAMP_BUTTON":
            if("ACTIVE" != this.__gpdb.paramGet("VIDEO.RECORD.STATE"))
            {
               this.PushMenuPanel("Panel_SpeedRamp");
            }
            else
            {
               GUI.OSD_Components.ErrorManagerMC.GetManager().PopupErrorMessage("RECORDING LOCKOUT.","Feature not available while recording.");
            }
            return;
         case "TIMELAPSE_BUTTON":
            if("ACTIVE" != this.__gpdb.paramGet("VIDEO.RECORD.STATE"))
            {
               this.PushMenuPanel("Panel_TimeLapse");
            }
            else
            {
               GUI.OSD_Components.ErrorManagerMC.GetManager().PopupErrorMessage("RECORDING LOCKOUT.","Feature not available while recording.");
            }
            return;
         case "TEST_CAPABILITY":
            _global.VxLog("MenuManager::DispatchPanelWidgetPress(\'TEST_CAPABILITY\') result:" + _global.VxCapability("SUNDANCE"));
            return;
         default:
            return;
      }
   }
   function tmpSetWhiteBalance(id)
   {
      var _loc3_;
      switch(id)
      {
         case "AutoWB":
            this.__gpdb.paramSet("GUI.PAINT.WHITE_BALANCE.SLAVE_MODE",0);
            this.__gpdb.paramSet("GUI.PAINT.WHITE_BALANCE.SLAVE_MODE",5);
            this.__gpdb.paramSet("GUI.PAINT.WHITE_BALANCE.AUTO","true");
            this.__gpdb.paramSet("PAINT.SLAVE.WHITE_BALANCE.CURRENT",0);
            this.__gpdb.paramSet("PAINT.SLAVE.TINT.CURRENT",0);
            return;
         case "WB_Daylight":
            this.__gpdb.paramSet("GUI.PAINT.WHITE_BALANCE.SLAVE_MODE",0);
            this.__gpdb.paramSet("GUI.PAINT.WHITE_BALANCE.SLAVE_MODE",2);
            this.__gpdb.paramSet("PAINT.WHITE_BALANCE.CURRENT","5600");
            this.__gpdb.paramSet("PAINT.TINT.CURRENT","0");
            return;
         case "WB_Tungsten":
            this.__gpdb.paramSet("GUI.PAINT.WHITE_BALANCE.SLAVE_MODE",0);
            this.__gpdb.paramSet("GUI.PAINT.WHITE_BALANCE.SLAVE_MODE",1);
            this.__gpdb.paramSet("PAINT.WHITE_BALANCE.CURRENT","3200");
            this.__gpdb.paramSet("PAINT.TINT.CURRENT","0");
            return;
         default:
            return;
      }
   }
   function HandleQtProxies(param, value)
   {
      this.__gpdb.paramSet("VIDEO.PROXY.GENERATE_FULL_SCALE","false");
      this.__gpdb.paramSet("VIDEO.PROXY.GENERATE_HALF_SCALE","false");
      this.__gpdb.paramSet("VIDEO.PROXY.GENERATE_QUARTER_SCALE","false");
      this.__gpdb.paramSet("VIDEO.PROXY.GENERATE_EIGHTH_SCALE","false");
      var _loc2_ = this.__gpdb.paramGetBoolean("GUI.SOFTKEY.GENERATE_QUICKTIME_PROXIES");
      if(_loc2_)
      {
         this.__gpdb.paramSet("VIDEO.PROXY.GENERATE_FULL_SCALE","true");
         this.__gpdb.paramSet("VIDEO.PROXY.GENERATE_HALF_SCALE","true");
         this.__gpdb.paramSet("VIDEO.PROXY.GENERATE_QUARTER_SCALE","true");
         this.__gpdb.paramSet("VIDEO.PROXY.GENERATE_EIGHTH_SCALE","true");
      }
   }
   function HandlePlayback(param, value)
   {
      this.ExitMenuTree();
   }
   function onInputEvent(name, value)
   {
      switch(name)
      {
         case GUI.OSD_Components.TabManager.EVENT_UP:
            if(value != "0")
            {
               this.PopMenuPanel(true);
            }
            break;
         case GUI.OSD_Components.TabManager.EVENT_EXIT:
            if(value == "false")
            {
               if(this.__currentMenu != null)
               {
                  this.ExitMenuTree();
               }
               else
               {
                  this.ReturnToLastMenu();
               }
            }
         default:
            return;
      }
   }
}
