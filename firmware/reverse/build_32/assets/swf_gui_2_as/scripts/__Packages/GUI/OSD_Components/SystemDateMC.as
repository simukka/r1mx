class GUI.OSD_Components.SystemDateMC extends MovieClip
{
   var __gpdb;
   var __mc;
   var __tabInfo_SetDateButtons;
   var __textField_1;
   var __textField_2;
   var __textField_3;
   function SystemDateMC()
   {
      super();
      this.__gpdb = _global.gpdb;
      this.__mc = this;
      this._visible = false;
      this.__tabInfo_SetDateButtons = new Array();
      this.NewButton(this.__tabInfo_SetDateButtons,"Reboot",370,500,this.DoSetDate);
      this.NewButton(this.__tabInfo_SetDateButtons,"Cancel",680,500,this.DoCancel);
      this.AddCallbacks();
   }
   function AddCallbacks()
   {
      this.__gpdb.addCallback("GUI.SYSTEM_DATE.SET",mx.utils.Delegate.create(this,this.SetSystemDate));
   }
   function SetSystemDate()
   {
      this.__gpdb.paramSet("GUI.BUTTON_INPUT_ENABLED","false");
      GUI.OSD_Components.MenuManager.GetManager().ExitMenuTree();
      GUI.OSD_Components.GadgetManager.GetManager().ShowGadget(false);
      this._visible = true;
      this.__mc.gotoAndStop("FRAME_2_LINES");
      this.__textField_1.text = "Setting the system date/time requires a reboot of the system.";
      this.__textField_2.text = "Do you want to reset the system date?";
      GUI.OSD_Components.StatusLCD.GetManager().SetMenuTab("Set Date?");
      GUI.OSD_Components.StatusLCD.GetManager().SetPane(GUI.OSD_Components.StatusLCD.PANE_ONESHOT);
      GUI.OSD_Components.TabManager.GetManager().push(this.__tabInfo_SetDateButtons);
   }
   function DoSetDate()
   {
      this.__mc.gotoAndStop("FRAME_1_LINE");
      this.__textField_3.text = "Setting System Clock and re-starting the camera...";
      if(!GUI.OSD_Components.TabManager.GetManager().pop())
      {
      }
      GUI.OSD_Components.StatusLCD.GetManager().SetMessage("Setting Date...");
      GUI.OSD_Components.StatusLCD.GetManager().SetPane(GUI.OSD_Components.StatusLCD.PANE_MESSAGE);
      var _loc7_ = this.__gpdb.paramGet("GUI.SYSTEM_DATE.YEAR");
      var _loc3_ = this.__gpdb.paramGet("GUI.SYSTEM_DATE.MONTH");
      var _loc2_ = this.__gpdb.paramGet("GUI.SYSTEM_DATE.DAY");
      var _loc6_ = this.__gpdb.paramGet("GUI.SYSTEM_DATE.HOUR");
      var _loc4_ = this.__gpdb.paramGet("GUI.SYSTEM_DATE.MINUTE");
      var _loc5_ = this.__gpdb.paramGet("GUI.SYSTEM_DATE.SECOND");
      if(_loc3_.length < 2)
      {
         _loc3_ = "0" + _loc3_;
      }
      if(_loc2_.length < 2)
      {
         _loc2_ = "0" + _loc2_;
      }
      if(_loc6_.length < 2)
      {
         _loc6_ = "0" + _loc6_;
      }
      if(_loc4_.length < 2)
      {
         _loc4_ = "0" + _loc4_;
      }
      if(_loc5_.length < 2)
      {
         _loc5_ = "0" + _loc5_;
      }
      this.__gpdb.paramSet("SYSTEM.TIME.SET",_loc7_ + _loc3_ + _loc2_ + "_" + _loc6_ + ":" + _loc4_ + ":" + _loc5_);
   }
   function DoCancel()
   {
      if(GUI.OSD_Components.TabManager.GetManager().pop())
      {
         GUI.OSD_Components.StatusLCD.GetManager().SetPane(GUI.OSD_Components.StatusLCD.PANE_STATUS);
      }
      this.cleanup();
   }
   function cleanup()
   {
      var _loc2_ = this.__gpdb.paramGetNumber("CAMERA.SLAVE_MODE_ACTIVE");
      if(_loc2_ == 0 || _loc2_ == 1)
      {
         this.__gpdb.paramSet("GUI.BUTTON_INPUT_ENABLED","true");
      }
      this.__mc._visible = false;
      GUI.OSD_Components.StatusLCD.GetManager().SetPane(GUI.OSD_Components.StatusLCD.PANE_STATUS);
      while(GUI.OSD_Components.TabManager.GetManager().pop() == false)
      {
      }
      GUI.OSD_Components.GadgetManager.GetManager().ShowGadget(true);
   }
   function NewButton(tabInfo, label, x, y, action)
   {
      if(tabInfo !== undefined && tabInfo instanceof Array)
      {
         var _loc5_ = "button_" + label;
         var _loc4_ = this.attachMovie("PanelButtonMC",_loc5_,this.getNextHighestDepth(),{_x:x,_y:y,__label:label,_onRelease:mx.utils.Delegate.create(this,action)});
         _loc4_._visible = false;
         if(tabInfo == null)
         {
            tabInfo = new Array();
         }
         tabInfo.push(_loc4_);
      }
      else
      {
         _global.VxError("SystemDateMC::NewButton() no tabInfo ARRAY supplied. Ignoring request.");
      }
   }
}
