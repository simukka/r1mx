class GUI.OSD_Components.ShutdownMC extends MovieClip
{
   var __gpdb;
   var CYLON_TWEEN;
   var __COUNT;
   function ShutdownMC()
   {
      super();
      _global.VxDebug("...........................................................................CTOR ShutdownMC()");
      this.__gpdb = _global.gpdb;
      this.addCallbacks();
      this.Show(false);
   }
   function addCallbacks()
   {
      var _loc2_ = mx.utils.Delegate.create(this,this.update);
      this.__gpdb.addCallback("SYSTEM.POWER.POWERDOWN_COUNTDOWN",_loc2_);
      this.__gpdb.addCallback("SYSTEM.THERMAL.POWERDOWN_COUNTDOWN",_loc2_);
      this.__gpdb.addCallback("SYSTEM.RUNLEVEL.REQUESTED",_loc2_);
      this.__gpdb.addCallback("SYSTEM.TIME.SET",_loc2_);
   }
   function update(name, value)
   {
      switch(name)
      {
         case "SYSTEM.POWER.POWERDOWN_COUNTDOWN":
            this.HandleCountdown("FRAME_POWER_COUNT",value);
            break;
         case "SYSTEM.THERMAL.POWERDOWN_COUNTDOWN":
            this.HandleCountdown("FRAME_TEMP_COUNT",value);
            break;
         case "SYSTEM.RUNLEVEL.REQUESTED":
            if(value == "SHUTDOWN")
            {
               this.HandleShutdown("FRAME_SHUTDOWN");
            }
            break;
         case "SYSTEM.TIME.SET":
            this.HandleShutdown("FRAME_SET_TIME");
      }
   }
   function Show(show)
   {
      this._visible = show;
      if(show)
      {
         this.CYLON_TWEEN.gotoAndPlay(1);
      }
      else
      {
         this.CYLON_TWEEN.gotoAndStop(1);
      }
   }
   function HandleCountdown(frame, count)
   {
      if(count != "-1")
      {
         this.Show(true);
         this.gotoAndStop(frame);
         this.__COUNT.text = count;
         GUI.OSD_Components.StatusLCD.GetManager().SetMessage("Shut Down in: " + count);
      }
      else
      {
         this.Show(false);
         GUI.OSD_Components.StatusLCD.GetManager().SetPane(GUI.OSD_Components.StatusLCD.PANE_STATUS);
      }
   }
   function HandleShutdown(frame)
   {
      this.__gpdb.paramSet("GUI.BUTTON_INPUT_ENABLED","false");
      this.gotoAndStop(frame);
      this.Show(true);
      GUI.OSD_Components.StatusLCD.GetManager().SetMessage("Powering Down...");
   }
}
