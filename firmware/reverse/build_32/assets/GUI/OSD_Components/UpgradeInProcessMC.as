class GUI.OSD_Components.UpgradeInProcessMC extends MovieClip
{
   var __gpdb;
   var __line1;
   var __line2;
   var __postMortem;
   var __tabInfo;
   var __rotation = 0;
   function UpgradeInProcessMC()
   {
      super();
      this.__gpdb.addCallback("UPGRADE.STATUS",mx.utils.Delegate.create(this,this.handleUpgradeStatus));
      this.__gpdb.paramSet("UPGRADE.APPLYUPGRADE","true");
      this.__line1.text = "Upgrade in process.";
      this.__line2.text = "This may take several minutes.";
   }
   function handleUpgradeStatus(param, value)
   {
      var _loc3_ = 1;
      _global.VxDebug("UpgradeInProgressMC::handleUpgradeStatus()  " + value);
      switch(value)
      {
         case "NONE_REQUESTED":
            this.__line1.text = "Upgrade in process..";
            _loc3_ = 2;
            return;
         case "START_UPGRADE":
            this.__line1.text = "Upgrade in process..";
            _loc3_ = 3;
            return;
         case "UPDATE_IMAGE1":
            this.__line1.text = "Upgrade in process..";
            _loc3_ = 4;
            return;
         case "UPDATE_IMAGE2":
            this.__line1.text = "Upgrade in process...";
            _loc3_ = 5;
            return;
         case "SETUP_DIRECTORY":
            this.__line1.text = "Upgrade in process....";
            _loc3_ = 6;
            return;
         case "UNTAR":
            this.__line1.text = "Upgrade in process.....";
            _loc3_ = 7;
            return;
         case "CHECK4FPGA":
            this.__line1.text = "Upgrade in process......";
            _loc3_ = 8;
            return;
         case "CHECK4VxAPP":
            this.__line1.text = "Upgrade in process.......";
            _loc3_ = 9;
            return;
         case "ERASE_FPGA":
            this.__line1.text = "Upgrade in process........";
            _loc3_ = 10;
            return;
         case "PROGRAM_FPGA":
            this.__line1.text = "Upgrade in process.........";
            _loc3_ = 11;
            return;
         case "ERASE_APP":
            this.__line1.text = "Upgrade in process..........";
            _loc3_ = 12;
            return;
         case "PROGRAM_APP":
            this.__line1.text = "Upgrade in process...........";
            _loc3_ = 13;
            return;
         case "SET_ACTIVE_IMAGE":
            this.__line1.text = "Upgrade in process............";
            _loc3_ = 14;
            return;
         case "INVALID":
            this.__line1.text = "Upgrade failed during step " + _loc3_;
            this.__line2.text = "Current Version: " + this.__gpdb.paramGet("SYSTEM.VERSION.SOFTWARE");
            this.done(false);
            return;
         case "COMPLETE_UPGRADE":
            this.__line1.text = "Upgrade Succeeded!";
            this.__line2.text = "Current Version: " + this.__gpdb.paramGet("SYSTEM.VERSION.SOFTWARE");
            this.done(true);
            return;
         default:
            return;
      }
   }
   function done(success)
   {
      this._parent.__VersionScreenMC.SW_Version.text = this.__gpdb.paramGet("SYSTEM.VERSION.SOFTWARE");
      this._parent.__VersionScreenMC.VPFPGA_Version.text = this.__gpdb.paramGet("SYSTEM.VERSION.VPFPGA");
      this._parent.__VersionScreenMC.IOFPGA_Version.text = this.__gpdb.paramGet("SYSTEM.VERSION.IOFPGA");
      this.__tabInfo = new Array();
      this.NewButton("OK",210,120,this.continueBoot);
      GUI.OSD_Components.TabManager.GetManager().push(this.__tabInfo);
   }
   function continueBoot()
   {
      this.__gpdb.paramSet("GUI.BUTTON_INPUT_ENABLED","false");
      this.cleanup();
      this.__postMortem();
   }
   function NewButton(label, x, y, action)
   {
      var _loc2_ = "button_" + label;
      var _loc3_ = this.attachMovie("PanelButtonMC",_loc2_,this.getNextHighestDepth(),{_x:x,_y:y,__label:label,__buttonType:"oneshot",_onRelease:mx.utils.Delegate.create(this,action)});
      this.__tabInfo.push(_loc3_);
   }
   function cleanup()
   {
      this._visible = false;
      for(var _loc2_ in this.__tabInfo)
      {
         _loc2_.removeMovieClip();
      }
      delete this.__tabInfo;
   }
}
