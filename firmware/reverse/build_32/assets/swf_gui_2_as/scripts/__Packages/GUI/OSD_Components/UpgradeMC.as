class GUI.OSD_Components.UpgradeMC extends MovieClip
{
   var __gpdb;
   var __postOp;
   var __tabInfo;
   static var __mc;
   var __firstUpgrade = true;
   function UpgradeMC()
   {
      super();
      this.__gpdb = _global.gpdb;
      GUI.OSD_Components.UpgradeMC.__mc = this;
      GUI.OSD_Components.UpgradeMC.__mc._visible = false;
   }
   static function GetManager()
   {
      if(GUI.OSD_Components.UpgradeMC.__mc === undefined)
      {
         _global.VxError("UpgradeMC::GetManager(): ERROR! Called before created.");
      }
      return GUI.OSD_Components.UpgradeMC.__mc;
   }
   function Activate()
   {
      this.SmartUpgrade();
   }
   function SmartUpgrade(postOpFnc)
   {
      _global.log("UpgradeMC::SmartUpgrade() envoked...");
      this.__postOp = postOpFnc;
      this.__gpdb.paramSet("GUI.BUTTON_INPUT_ENABLED","false");
      if(postOpFnc === undefined)
      {
         GUI.OSD_Components.MenuManager.GetManager().ExitMenuTree();
         GUI.OSD_Components.HudLowerMC.GetManager().Show(false);
      }
      if(this.__gpdb.paramGet("UPGRADE.AVAILABLE") == "true")
      {
         _global.log("UpgradeMC::SmartUpgrade() Upgrade file \'su.tar\' detected");
         this.gotoAndStop("FRAME_AVAILABLE");
         this.__tabInfo = new Array();
         this.NewButton("Upgrade",380,540,this.DoUpgrade);
         this.NewButton("Later",630,540,this.DoLater);
         GUI.OSD_Components.TabManager.GetManager().push(this.__tabInfo);
         GUI.OSD_Components.StatusLCD.GetManager().SetMenuTab("New Firmware");
         GUI.OSD_Components.StatusLCD.GetManager().GotoUpgradeScreen();
         GUI.OSD_Components.UpgradeMC.__mc._visible = true;
      }
      else
      {
         _global.log("UpgradeMC::SmartUpgrade() NO UPGRADE file \'su.tar\' detected");
         this.gotoAndStop("FRAME_NO_UPGRADE");
         this.__tabInfo = new Array();
         GUI.OSD_Components.StatusLCD.GetManager().SetMenuTab("No Upgrade");
         this.NewButton("OK",525,450,this.DoLater);
         GUI.OSD_Components.TabManager.GetManager().push(this.__tabInfo);
         GUI.OSD_Components.UpgradeMC.__mc._visible = true;
      }
   }
   function NewButton(label, x, y, action)
   {
      var _loc2_ = "button_" + label;
      var _loc3_ = this.attachMovie("PanelButtonMC",_loc2_,GUI.OSD_Components.UpgradeMC.__mc.getNextHighestDepth(),{_x:x,_y:y,__label:label,__buttonType:"oneshot",_onRelease:mx.utils.Delegate.create(GUI.OSD_Components.UpgradeMC.__mc,action)});
      this.__tabInfo.push(_loc3_);
   }
   function DeleteButtons()
   {
      for(var _loc2_ in this.__tabInfo)
      {
         _loc2_.removeMovieClip();
      }
      GUI.OSD_Components.TabManager.GetManager().pop();
   }
   function DoUpgrade()
   {
      GUI.OSD_Components.StatusLCD.GetManager().SetMessage("Upgrading...");
      this.DeleteButtons();
      this.__gpdb.addCallback("UPGRADE.STATUS",mx.utils.Delegate.create(this,this.handleUpgradeStatus));
      this.gotoAndPlay("FRAME_IN_PROCESS");
      this.__gpdb.paramSet("UPGRADE.APPLYUPGRADE","true");
   }
   function DoLater()
   {
      this.cleanup();
      this.__postOp();
   }
   function cleanup()
   {
      var _loc3_ = this.__gpdb.paramGetNumber("CAMERA.SLAVE_MODE_ACTIVE");
      if(_loc3_ == 0 || _loc3_ == 1)
      {
         this.__gpdb.paramSet("GUI.BUTTON_INPUT_ENABLED","true");
      }
      GUI.OSD_Components.UpgradeMC.__mc._visible = false;
      GUI.OSD_Components.StatusLCD.GetManager().SetPane(GUI.OSD_Components.StatusLCD.PANE_STATUS);
      while(GUI.OSD_Components.TabManager.GetManager().pop() == false)
      {
      }
      _global.VxDebug("UpgradeMC.cleanup() showing gadgets...");
      if(this.__postOp === undefined)
      {
         GUI.OSD_Components.HudLowerMC.GetManager().Show(true);
      }
   }
   function handleUpgradeStatus(param, value)
   {
      var _loc4_ = 1;
      _global.VxDebug("UpgradeInProgressMC::handleUpgradeStatus()  " + value);
      switch(value)
      {
         case "INVALID":
         case "COMPLETE_UPGRADE_FAILURE":
            this.UpgradeComplete(false);
            break;
         case "COMPLETE_UPGRADE_SUCCESS":
            this.UpgradeComplete(true);
      }
   }
   function UpgradeComplete(ok)
   {
      if(this.__firstUpgrade)
      {
         if(ok)
         {
            this.gotoAndStop("FRAME_UPGRADE_OK");
            GUI.OSD_Components.StatusLCD.GetManager().SetMessage("OK. Cycle Power.");
         }
         else
         {
            this.gotoAndStop("FRAME_UPGRADE_FAILED");
            GUI.OSD_Components.StatusLCD.GetManager().SetMessage("Upgrade Failed");
         }
         this.__firstUpgrade = false;
      }
   }
}
